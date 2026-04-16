// static/js/dashboard.js

import { apiRequest, getUser } from "./api.js";
import { verificarAuth, logout } from "./auth.js";
import { toastError, toastSuccess, toastGold } from "./toast.js";

verificarAuth();
const user = getUser();

// ── Nome ─────────────────────────────────────────────────────
function preencherNome() {
    const n = document.getElementById("user-nome");
    const k = document.getElementById("user-nickname");
    if (n && user.nome)     n.textContent = user.nome;
    if (k && user.nickname) k.textContent = "@" + user.nickname;
}

// ── Saldo ─────────────────────────────────────────────────────
async function carregarSaldo() {
    const res = await apiRequest("/api/pontos/saldo");
    if (res.ok) {
        const el = document.getElementById("saldo-valor");
        if (el) animarNumero(el, 0, res.saldo, 700);
    }
}

function animarNumero(el, de, para, ms) {
    const inicio = performance.now();
    const fmt    = v => Number(v).toFixed(2).replace(".", ",");
    function tick(agora) {
        const p = Math.min((agora - inicio) / ms, 1);
        const e = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(de + (para - de) * e);
        if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

// ── Comanda ativa (do localStorage — salvo pelo QR) ─────────
function mostrarComandaAtiva() {
    const numero = localStorage.getItem("club_numero_comanda");
    const sec    = document.getElementById("comanda-ativa-section");
    if (!numero || !sec) return;

    sec.innerHTML = `
        <div class="card" style="padding:16px 20px; border-color:var(--border-glow);
             background:linear-gradient(135deg,#1a1608,#241d0a);">
            <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
                <div>
                    <div style="font-size:10px; font-weight:600; letter-spacing:2px;
                                text-transform:uppercase; color:var(--gold); opacity:.7; margin-bottom:4px;">
                        Comanda Ativa
                    </div>
                    <div style="font-family:var(--font-display); font-size:32px; letter-spacing:2px;
                                color:var(--gold-light);">#${numero}</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <a href="/catalogo" class="btn btn-gold btn-sm">✦ Resgatar</a>
                    <button class="btn btn-ghost btn-sm" id="btn-desassociar"
                            style="font-size:10px;">Desassociar</button>
                </div>
            </div>
        </div>`;
    sec.style.display = "block";

    document.getElementById("btn-desassociar")?.addEventListener("click", () => {
        localStorage.removeItem("club_numero_comanda");
        sec.style.display = "none";
        toastSuccess("Comanda desassociada da visualização.");
    });

    // Pré-preenche o input de vinculação
    const inp = document.getElementById("comanda-input");
    if (inp && !inp.value) inp.value = numero;
}

// ── Vincular comanda ──────────────────────────────────────────
async function vincularComanda() {
    const input = document.getElementById("comanda-input");
    const numero = input?.value?.trim();
    if (!numero || isNaN(numero)) { toastError("Informe um número de comanda válido"); return; }

    const btn = document.getElementById("btn-vincular");
    btn.disabled = true;
    btn.textContent = "Vinculando…";

    const res = await apiRequest(`/api/comanda/${numero}/vincular`, "POST");
    btn.disabled = false;
    btn.textContent = "Vincular";

    if (res.ok) {
        toastGold("✦ Comanda vinculada! Pontos serão creditados ao fechar.");
        localStorage.setItem("club_numero_comanda", numero);
        mostrarComandaAtiva();
        input.value = "";
    } else {
        toastError(res.message || "Erro ao vincular comanda");
    }
}

// ── Histórico ─────────────────────────────────────────────────
async function carregarHistorico() {
    const c = document.getElementById("historico-lista");
    if (!c) return;
    const res = await apiRequest("/api/pontos/historico");
    if (!res.ok || !res.historico.length) {
        c.innerHTML = `<p class="text-sub text-center" style="padding:24px 0;">Sem movimentações ainda.</p>`;
        return;
    }
    c.innerHTML = res.historico.map(h => {
        const ganho = h.tipo === "ganho";
        const data  = new Date(h.data_criacao).toLocaleDateString("pt-BR", { day:"2-digit", month:"short" });
        const pts   = Number(h.valor);
        const ptsStr = pts % 1 === 0 ? pts.toFixed(0) : pts.toFixed(2);
        return `
        <div class="historico-item">
            <div class="historico-icon ${h.tipo}">${ganho ? "⬆" : "⬇"}</div>
            <div class="historico-desc">
                <div class="desc">${h.descricao || "Movimentação"}</div>
                <div class="data">${data}</div>
            </div>
            <div class="historico-valor ${h.tipo}">${ganho ? "+" : "-"}${ptsStr} pts</div>
        </div>`;
    }).join("");
}

// ── Resgates recentes ────────────────────────────────────────
async function carregarResgates() {
    const c = document.getElementById("resgates-lista");
    if (!c) return;
    const res = await apiRequest("/api/resgates/usuario");
    if (!res.ok || !res.resgates.length) {
        c.innerHTML = `<p class="text-sub text-center" style="padding:24px 0;">Nenhum resgate ainda.</p>`;
        return;
    }
    c.innerHTML = res.resgates.slice(0, 5).map(r => {
        const data = new Date(r.data_criacao).toLocaleDateString("pt-BR", { day:"2-digit", month:"short" });
        const sc   = r.status === "entregue" ? "pill-success" : "pill-gold";
        const img  = r.foto_url
            ? `<img class="resgate-img" src="${r.foto_url}" alt="" onerror="this.style.display='none'">`
            : `<div class="resgate-img" style="display:flex;align-items:center;justify-content:center;font-size:24px;">🎁</div>`;
        return `
        <div class="resgate-card">
            ${img}
            <div class="resgate-info">
                <div class="resgate-nome">${r.produto_nome}</div>
                <div class="resgate-meta">${data} · ${Number(r.pontos_gastos).toFixed(2)} pts</div>
            </div>
            <span class="pill ${sc}">${r.status}</span>
        </div>`;
    }).join("");
}

// ── Eventos ────────────────────────────────────────────────
document.getElementById("btn-vincular")?.addEventListener("click", vincularComanda);
document.getElementById("comanda-input")?.addEventListener("keydown", e => {
    if (e.key === "Enter") vincularComanda();
});
document.getElementById("btn-logout")?.addEventListener("click", logout);

// ── Init ───────────────────────────────────────────────────
preencherNome();
mostrarComandaAtiva();
carregarSaldo();
carregarHistorico();
carregarResgates();
