"""
modules/admin/routes.py — Painel administrativo do Club
Login por nickname + senha. Super admin gerencia outros admins.
"""
import bcrypt
from flask import (
    Blueprint, request, render_template,
    session, redirect, url_for, flash, jsonify,
)
from modules.auth.repository import listar_todos_usuarios_db, redefinir_senha_db
from modules.produtos.repository import editar_produto_db
from db.connection import get_connection

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ── Helpers ───────────────────────────────────────────────────

def _admin_logado():
    return session.get("admin_id") is not None

def _is_super():
    return session.get("admin_super") is True

def _buscar_admin_por_nickname(nickname):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM admins WHERE nickname = %s", (nickname,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()

def _listar_admins():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id, nome, nickname, is_super, data_criacao FROM admins ORDER BY is_super DESC, nome")
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


# ── Login / Logout ────────────────────────────────────────────

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nickname = request.form.get("nickname", "").strip().lstrip("@")
        senha    = request.form.get("senha", "")
        admin    = _buscar_admin_por_nickname(nickname)
        if admin and bcrypt.checkpw(senha.encode(), admin["senha_hash"].encode()):
            session["admin_id"]    = admin["id"]
            session["admin_nome"]  = admin["nome"]
            session["admin_super"] = bool(admin["is_super"])
            return redirect(url_for("admin.usuarios"))
        flash("Nickname ou senha incorretos.", "erro")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_id",    None)
    session.pop("admin_nome",  None)
    session.pop("admin_super", None)
    return redirect(url_for("admin.login"))


# ── Minha senha (qualquer admin logado) ──────────────────────

@admin_bp.route("/minha-senha", methods=["POST"])
def minha_senha():
    if not _admin_logado():
        return redirect(url_for("admin.login"))
    atual    = request.form.get("senha_atual", "")
    nova     = request.form.get("nova_senha", "").strip()
    confirma = request.form.get("confirma_senha", "").strip()
    if len(nova) < 4:
        flash("Nova senha deve ter ao menos 4 caracteres.", "erro")
        return redirect(request.referrer or url_for("admin.usuarios"))
    if nova != confirma:
        flash("As senhas não coincidem.", "erro")
        return redirect(request.referrer or url_for("admin.usuarios"))
    # Verifica senha atual
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT senha_hash FROM admins WHERE id = %s", (session["admin_id"],))
        row = cur.fetchone()
    finally:
        cur.close(); conn.close()
    if not row or not bcrypt.checkpw(atual.encode(), row["senha_hash"].encode()):
        flash("Senha atual incorreta.", "erro")
        return redirect(request.referrer or url_for("admin.usuarios"))
    nova_hash = bcrypt.hashpw(nova.encode(), bcrypt.gensalt()).decode()
    conn2 = get_connection()
    cur2  = conn2.cursor()
    try:
        cur2.execute("UPDATE admins SET senha_hash = %s WHERE id = %s",
                     (nova_hash, session["admin_id"]))
        conn2.commit()
    finally:
        cur2.close(); conn2.close()
    flash("Senha alterada com sucesso.", "sucesso")
    return redirect(request.referrer or url_for("admin.usuarios"))


# ── Usuários do Clube ─────────────────────────────────────────

@admin_bp.route("/usuarios")
def usuarios():
    if not _admin_logado():
        return redirect(url_for("admin.login"))
    lista = listar_todos_usuarios_db()
    return render_template("admin/usuarios.html",
                           usuarios=lista,
                           admin_nome=session.get("admin_nome"),
                           is_super=_is_super())


@admin_bp.route("/usuarios/<int:usuario_id>/historico")
def historico_usuario(usuario_id):
    if not _admin_logado():
        return jsonify({"ok": False}), 401
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT tipo, valor, descricao,
                   DATE_FORMAT(data_criacao, '%d/%m/%Y %H:%i') AS data
            FROM pontos WHERE usuario_id = %s
            ORDER BY data_criacao DESC LIMIT 50
            """,
            (usuario_id,),
        )
        pontos = cur.fetchall()
        cur.execute(
            """
            SELECT r.id, pc.nome AS produto_nome, r.pontos_gastos,
                   r.tipo, r.status,
                   DATE_FORMAT(r.data_criacao, '%d/%m/%Y %H:%i') AS data
            FROM resgates r
            INNER JOIN produtos_clube pc ON pc.id = r.produto_id
            WHERE r.usuario_id = %s
            ORDER BY r.data_criacao DESC LIMIT 50
            """,
            (usuario_id,),
        )
        resgates = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return jsonify({
        "ok":      True,
        "pontos":  [{**p, "valor": float(p["valor"])} for p in pontos],
        "resgates":[{**r, "pontos_gastos": float(r["pontos_gastos"])} for r in resgates],
    })


@admin_bp.route("/usuarios/<int:usuario_id>/reset-senha", methods=["POST"])
def reset_senha(usuario_id):
    if not _admin_logado():
        return redirect(url_for("admin.login"))
    nova_senha = request.form.get("nova_senha", "").strip()
    if len(nova_senha) < 4:
        flash("Senha deve ter ao menos 4 caracteres.", "erro")
        return redirect(url_for("admin.usuarios"))
    redefinir_senha_db(usuario_id, bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()))
    flash("Senha redefinida com sucesso.", "sucesso")
    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/usuarios/<int:usuario_id>/deletar", methods=["POST"])
def deletar_usuario(usuario_id):
    if not _admin_logado():
        return redirect(url_for("admin.login"))
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        conn.commit()
    finally:
        cur.close(); conn.close()
    flash("Usuário removido.", "sucesso")
    return redirect(url_for("admin.usuarios"))


# ── Produtos ──────────────────────────────────────────────────

@admin_bp.route("/produtos")
def produtos():
    if not _admin_logado():
        return redirect(url_for("admin.login"))
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id, nome, foto_url, pontos_necessarios, preco_dinheiro, ativo, item_id FROM produtos_clube ORDER BY nome")
        lista = cur.fetchall()
    finally:
        cur.close(); conn.close()
    return render_template("admin/produtos.html",
                           produtos=lista,
                           admin_nome=session.get("admin_nome"),
                           is_super=_is_super())


@admin_bp.route("/produtos/<int:produto_id>/editar", methods=["POST"])
def editar_produto(produto_id):
    if not _admin_logado():
        return redirect(url_for("admin.login"))
    nome  = request.form.get("nome", "").strip()
    pontos = float(request.form.get("pontos_necessarios", 0) or 0)
    preco  = float(request.form.get("preco_dinheiro", 0) or 0)
    ativo  = request.form.get("ativo") == "1"
    foto   = request.form.get("foto_url", "").strip()
    editar_produto_db(produto_id, nome, foto, pontos, preco, ativo)
    flash(f'Produto "{nome}" atualizado.', "sucesso")
    return redirect(url_for("admin.produtos"))


# ── Gerenciar Admins (apenas super admin) ─────────────────────

@admin_bp.route("/admins")
def admins():
    if not _admin_logado() or not _is_super():
        return redirect(url_for("admin.usuarios"))
    lista = _listar_admins()
    return render_template("admin/admins.html",
                           admins=lista,
                           admin_nome=session.get("admin_nome"),
                           is_super=True)


@admin_bp.route("/admins/criar", methods=["POST"])
def criar_admin():
    if not _admin_logado() or not _is_super():
        return redirect(url_for("admin.usuarios"))
    nome     = request.form.get("nome", "").strip()
    nickname = request.form.get("nickname", "").strip().lstrip("@")
    senha    = request.form.get("senha", "")
    if not nome or not nickname or len(senha) < 4:
        flash("Preencha todos os campos (senha mín. 4 chars).", "erro")
        return redirect(url_for("admin.admins"))
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO admins (nome, nickname, senha_hash, is_super) VALUES (%s, %s, %s, FALSE)",
            (nome, nickname, senha_hash),
        )
        conn.commit()
        flash(f'Admin "@{nickname}" criado.', "sucesso")
    except Exception:
        flash("Nickname já existe.", "erro")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("admin.admins"))


@admin_bp.route("/admins/<int:admin_id>/deletar", methods=["POST"])
def deletar_admin(admin_id):
    if not _admin_logado() or not _is_super():
        return redirect(url_for("admin.usuarios"))
    if admin_id == session.get("admin_id"):
        flash("Você não pode se remover.", "erro")
        return redirect(url_for("admin.admins"))
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM admins WHERE id = %s AND is_super = FALSE", (admin_id,))
        conn.commit()
        flash("Admin removido.", "sucesso")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("admin.admins"))


@admin_bp.route("/admins/<int:admin_id>/reset-senha", methods=["POST"])
def reset_senha_admin(admin_id):
    if not _admin_logado() or not _is_super():
        return redirect(url_for("admin.usuarios"))
    nova = request.form.get("nova_senha", "").strip()
    if len(nova) < 4:
        flash("Senha mínima de 4 caracteres.", "erro")
        return redirect(url_for("admin.admins"))
    nova_hash = bcrypt.hashpw(nova.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE admins SET senha_hash = %s WHERE id = %s", (nova_hash, admin_id))
        conn.commit()
        flash("Senha do admin redefinida.", "sucesso")
    finally:
        cur.close(); conn.close()
    return redirect(url_for("admin.admins"))
