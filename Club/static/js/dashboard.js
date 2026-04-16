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

// ── Saldo (Com animação original) ──────────────────────────────
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

// ── Comanda Ativa (Agora via API - Sem localStorage manual) ──
async function gerenciarComandaAtiva() {
    const secAtiva = document.getElementById("comanda-ativa-section");
    const secSem   = document.getElementById("sem-comanda-section");
    
    if (!secAtiva || !secSem) return;

    // Busca no servidor se há uma comanda aberta para este CPF/ID
    const res = await apiRequest("/api/comanda/ativa");

    if (res.ok && res.ativa) {
        secSem.style.display = "none";
        secAtiva.innerHTML = `
            <div class="card" style="padding:24px; border-color:var(--border-glow);
                 background: linear-gradient(135deg, #1a1608 0%, #241d0a 100%);
                 box-shadow: var(--gold-glow);">
                <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div>
                        <div class="label" style="color:var(--gold); margin-bottom:8px;">Comanda Ativa</div>
                        <div style="font-family:var(--font-display); font-size:48px; color:var(--gold-light); line-height:1;">
                            #${res.numero_comanda}
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div class="label">Mesa</div>
                        <div style="font-size:20px; font-weight:600; color:var(--text);">${res.mesa || '--'}</div>
                    </div>
                </div>
                <div style="margin-top:20px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.05); display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:12px; color:var(--text-sub);">Acumulando pontos automaticamente</span>
                    <a href="/catalogo" class="btn btn-gold btn-sm">✦ Resgatar</a>
                </div>
            </div>`;
        secAtiva.style.display = "block";
    } else {
        secAtiva.style.display = "none";
        secSem.style.display = "block";
    }
}

// ── Histórico (Resumo para o Dashboard) ───────────────────────
async function carregarHistorico() {
    const c = document.getElementById("historico-lista");
    if (!c) return;
    const res = await apiRequest("/api/pontos/historico");
    if (!res.ok || !res.historico.length) {
        c.innerHTML = `<p class="text-sub text-center" style="padding:24px 0;">Sem movimentações ainda.</p>`;
        return;
    }
    // Mostra apenas as 3 últimas no dashboard
    c.innerHTML = res.historico.slice(0, 3).map(h => {
        const ganho = h.tipo === "ganho";
        const data  = new Date(h.data_criacao).toLocaleDateString("pt-BR", { day:"2-digit", month:"short" });
        const pts   = Number(h.valor);
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

// ── Resgates Recentes ────────────────────────────────────────
async function carregarResgates() {
    const c = document.getElementById("resgates-lista");
    if (!c) return;
    const res = await apiRequest("/api/resgates/usuario");
    if (!res.ok || !res.resgates.length) {
        c.innerHTML = `<p class="text-sub text-center" style="padding:24px 0;">Nenhum resgate ainda.</p>`;
        return;
    }
    // Mostra os 2 últimos no dashboard
    c.innerHTML = res.resgates.slice(0, 2).map(r => {
        const data = new Date(r.data_criacao).toLocaleDateString("pt-BR", { day:"2-digit", month:"short" });
        const sc   = r.status === "entregue" ? "pill-success" : "pill-gold";
        return `
        <div class="resgate-card">
            <div class="resgate-info">
                <div class="resgate-nome">${r.produto_nome}</div>
                <div class="resgate-meta">${data} · ${Number(r.pontos_gastos).toFixed(0)} pts</div>
            </div>
            <span class="pill ${sc}">${r.status}</span>
        </div>`;
    }).join("");
}

// ── Init ───────────────────────────────────────────────────
preencherNome();
gerenciarComandaAtiva(); // Chama a nova função via API
carregarSaldo();
carregarHistorico();
carregarResgates();