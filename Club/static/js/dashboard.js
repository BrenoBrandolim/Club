// static/js/dashboard.js

import { apiRequest, getUser } from "./api.js";
import { verificarAuth, logout } from "./auth.js";
import { toastError, toastGold } from "./toast.js";

verificarAuth();
const user = getUser();

// ── Nome ─────────────────────────────────────────────────────
function preencherNome() {
    const n = document.getElementById("user-nome");
    const k = document.getElementById("user-nickname");
    if (n && user.nome)     n.textContent = user.nome;
    if (k && user.nickname) k.textContent = "@" + user.nickname;
}

// ── Saldo (animação) ──────────────────────────────────────────
async function carregarSaldo() {
    const res = await apiRequest("/api/pontos/saldo");
    if (res.ok) {
        const el = document.getElementById("saldo-valor");
        if (el) animarNumero(el, 0, res.saldo, 700);
    }
}

function animarNumero(el, de, para, ms) {
    const inicio = performance.now();
    const fmt    = v => Number(v).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    function tick(agora) {
        const p = Math.min((agora - inicio) / ms, 1);
        const e = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(de + (para - de) * e);
        if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

// ── Comanda Ativa ─────────────────────────────────────────────
// BUG FIX: API retorna res.comanda (não res.ativa) e res.comanda.numero (não res.numero_comanda)
async function gerenciarComandaAtiva() {
    const secAtiva = document.getElementById("comanda-ativa-section");
    const secSem   = document.getElementById("sem-comanda-section");
    if (!secAtiva || !secSem) return;

    const res = await apiRequest("/api/comanda/ativa");

    // FIX: verifica res.comanda (objeto), não res.ativa (boolean inexistente)
    if (res.ok && res.comanda) {
        const numero = res.comanda.numero;   // FIX: era res.numero_comanda
        secSem.style.display   = "none";
        secAtiva.style.display = "block";
    // Localize esta parte no seu dashboard.js e substitua o innerHTML:

   secAtiva.innerHTML = `
    <div class="comanda-card">
        <div class="comanda-content">
            <div class="comanda-badge">
                <span class="comanda-label">Nº</span>
                <span class="comanda-numero">${numero}</span>
            </div>
            <div class="comanda-info">
                <div class="label-gold">Comanda Ativa</div>
                <div class="comanda-status">Acumulando pontos automaticamente</div>
            </div>
            <a href="/catalogo" class="btn-resgate">✦ Resgatar</a>
        </div>
        ${res.aviso ? `
            <div style="margin-top: 12px; color: var(--gold); font-weight: 700; font-size: 11px; display: flex; align-items: center; gap: 6px;">
                <span>⚠️</span> ${res.aviso}
            </div>` : ""}
    </div>`;

    } else {
        secAtiva.style.display = "none";
        secSem.style.display   = "block";
    }
}

// ── Histórico (resumo — 3 últimas) ───────────────────────────
async function carregarHistorico() {
    const c = document.getElementById("historico-lista");
    if (!c) return;
    const res = await apiRequest("/api/pontos/historico");
    if (!res.ok || !res.historico.length) {
        c.innerHTML = `<p class="text-sub text-center" style="padding:24px 0;">Sem movimentações ainda.</p>`;
        return;
    }
    c.innerHTML = res.historico.slice(0, 3).map(h => {
        const ganho  = h.tipo === "ganho";
        const data   = new Date(h.data_criacao).toLocaleDateString("pt-BR", { day:"2-digit", month:"short" });
        const pts    = Number(h.valor);
        const ptsStr = pts.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
        return `
        <div class="historico-item">
            <div class="historico-icon ${h.tipo}">${ganho ? "⬆" : "⬇"}</div>
            <div class="historico-desc">
                <div class="desc">${h.descricao || "Movimentação"}</div>
                <div class="data">${data}</div>
            </div>
            <div class="historico-valor ${h.tipo}">${ganho ? "+" : "-"}${ptsStr}</div>
        </div>`;
    }).join("");
}

// ── Resgates recentes (2 últimos) ────────────────────────────
async function carregarResgates() {
    const c = document.getElementById("resgates-lista");
    if (!c) return;
    const res = await apiRequest("/api/resgates/usuario");
    if (!res.ok || !res.resgates.length) {
        c.innerHTML = `<p class="text-sub text-center" style="padding:24px 0;">Nenhum resgate ainda.</p>`;
        return;
    }
    c.innerHTML = res.resgates.slice(0, 2).map(r => {
        const data = new Date(r.data_criacao).toLocaleDateString("pt-BR", { day:"2-digit", month:"short" });
        const sc   = r.status === "entregue" ? "pill-success" : "pill-gold";
        return `
        <div class="resgate-card">
            <div class="resgate-info">
                <div class="resgate-nome">${r.produto_nome}</div>
                <div class="resgate-meta">${data} · ${Number(r.pontos_gastos).toFixed(0)} pts</div>
            </div>
        </div>`;
    }).join("");
}

// ── Init ──────────────────────────────────────────────────────
document.getElementById("btn-logout")?.addEventListener("click", logout);
preencherNome();
gerenciarComandaAtiva();
carregarSaldo();
carregarHistorico();
carregarResgates();
