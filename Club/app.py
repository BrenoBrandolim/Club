"""
Club — app.py  |  porta 5001
"""
from flask import Flask, render_template, redirect, url_for
from modules.auth.routes       import auth_bp
from modules.produtos.routes   import produtos_bp
from modules.pontos.routes     import pontos_bp
from modules.resgates.routes   import resgates_bp
from modules.integracao.routes import integracao_bp
from modules.comandas.routes    import comanda_bp

app = Flask(__name__)
app.secret_key = "club_secret_key_troque_em_producao"

for bp in [auth_bp, produtos_bp, pontos_bp, resgates_bp, integracao_bp, comanda_bp]:
    app.register_blueprint(bp)

# ── Páginas ────────────────────────────────────────────────
@app.route("/")
def index():          return render_template("index.html")

@app.route("/login")
def login_page():     return render_template("login.html")

@app.route("/cadastro")
def cadastro_page():  return render_template("cadastro.html")

@app.route("/dashboard")
def dashboard_page(): return render_template("dashboard.html")

@app.route("/catalogo")
def catalogo_page():  return render_template("catalogo.html")

# ── NOVAS ROTAS ADICIONADAS ──────────────────────────────
@app.route("/menu")
def menu_page():      
    return render_template("menu.html")

@app.route("/placar")
def placar_page():     
    return render_template("placar.html")

@app.route("/historico")
def historico_page():  
    return render_template("historico.html")

@app.route("/resgates")
def resgates_page():   
    return render_template("resgates.html")

@app.route("/comanda/<int:numero>")
def comanda_page(numero):
    """Landing page do QR Code. Flask passa o número para o Jinja."""
    return render_template("comanda.html", numero_comanda=numero)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
