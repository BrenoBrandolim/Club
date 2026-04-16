// static/js/catalogo.js

import { apiRequest, getUser } from "./api.js";
import { verificarAuth } from "./auth.js";
import { toastError, toastSuccess, toastGold } from "./toast.js";

verificarAuth();

let produtos        = [];
let produtoSelecionado = null;
let saldoAtual      = 0;
// Comanda pré-preenchida pelo QR ou vínculo anterior
let numeroComandaAtual = localStorage.getItem("club_numero_comanda") || "";

// ── Catálogo ─────────────────────────────────────────────────
async function carregarProdutos() {
    const grid = document.getElementById("produto-grid");
    grid.innerHTML = Array(6).fill(`
        <div class="produto-card">
            <div class="skeleton" style="aspect-ratio:1;width:100%"></div>
            <div style="padding:12px">
                <div class="skeleton" style="height:14px;margin-bottom:8px;width:80%"></div>
                <div class="skeleton" style="height:20px;width:50%"></div>
            </div>
        </div>`).join("");

    const res = await apiRequest("/api/produtos/");
    if (!res.ok) {
        grid.innerHTML = `<p class="text-sub text-center" style="padding:40px 0;grid-column:1/-1;">Erro ao carregar produtos.</p>`;
        return;
    }
    produtos = res.produtos;
    renderProdutos(produtos);
}

function renderProdutos(lista) {
    const grid = document.getElementById("produto-grid");
    if (!lista.length) {
        grid.innerHTML = `<p class="text-sub text-center" style="padding:40px 0;grid-column:1/-1;">Nenhum produto disponível.</p>`;
        return;
    }
    grid.innerHTML = lista.map(p => {
        const pode  = saldoAtual >= p.pontos_necessarios;
        const imgEl = p.foto_url
            ? `<img class="produto-card-img" src="${p.foto_url}" alt="${p.nome}" loading="lazy"
                    onerror="this.outerHTML='<div class=\\'produto-card-img-placeholder\\'>🍽️</div>'">`
            : `<div class="produto-card-img-placeholder">🍽️</div>`;
        return `
        <div class="produto-card ${!pode ? 'produto-card-sem-pontos' : ''}"
             data-id="${p.id}" onclick="abrirModal(${p.id})">
            ${imgEl}
            <div class="produto-card-body">
                <div class="produto-card-nome">${p.nome}</div>
                <div class="produto-card-pontos">
                    <span class="pontos-badge">${Number(p.pontos_necessarios).toFixed(2).replace(".",",")}</span>
                    <span class="pontos-label">pts</span>
                </div>
                ${!pode ? `<div style="margin-top:6px;font-size:10px;color:var(--text-dim);">⚠ Pontos insuficientes</div>` : ""}
            </div>
        </div>`;
    }).join("");
}

// ── Saldo ─────────────────────────────────────────────────────
async function carregarSaldo() {
    const res = await apiRequest("/api/pontos/saldo");
    if (res.ok) {
        saldoAtual = res.saldo;
        const el = document.getElementById("saldo-topo");
        if (el) el.textContent = `${Number(res.saldo).toFixed(2).replace(".",",")} pts`;
        if (produtos.length) renderProdutos(filtrarProdutos());
    }
}

// ── Busca ─────────────────────────────────────────────────────
function filtrarProdutos() {
    const q = document.getElementById("busca")?.value.toLowerCase() || "";
    return produtos.filter(p => p.nome.toLowerCase().includes(q));
}
document.getElementById("busca")?.addEventListener("input", () => renderProdutos(filtrarProdutos()));

// ── Modal ─────────────────────────────────────────────────────
window.abrirModal = function(id) {
    produtoSelecionado = produtos.find(p => p.id === id);
    if (!produtoSelecionado) return;

    const p = produtoSelecionado;
    document.getElementById("modal-nome").textContent   = p.nome;
    document.getElementById("modal-pontos").textContent  = Number(p.pontos_necessarios).toFixed(2).replace(".",",");
    document.getElementById("modal-saldo").textContent   = Number(saldoAtual).toFixed(2).replace(".",",");

    const imgEl = document.getElementById("modal-img");
    if (p.foto_url) { imgEl.src = p.foto_url; imgEl.style.display = "block"; imgEl.onerror = () => imgEl.style.display = "none"; }
    else imgEl.style.display = "none";

    const pode = saldoAtual >= p.pontos_necessarios;
    document.getElementById("btn-confirmar-resgate").disabled = !pode;
    document.getElementById("modal-aviso").style.display      = pode ? "none" : "block";

    // Pré-preenche comanda do QR
    if (numeroComandaAtual) document.getElementById("comanda-resgate").value = numeroComandaAtual;

    // Esconde modal de substituição até verificar
    document.getElementById("substituicao-area").style.display = "none";
    document.getElementById("btn-confirmar-resgate").dataset.substituir    = "false";
    document.getElementById("btn-confirmar-resgate").dataset.commandaItemId = "";

    document.getElementById("modal-overlay").classList.add("open");
    document.body.style.overflow = "hidden";
};

function fecharModal() {
    document.getElementById("modal-overlay").classList.remove("open");
    document.body.style.overflow = "";
    document.getElementById("comanda-resgate").value = "";
    produtoSelecionado = null;
}

// ── Verificar item na comanda (substituição) ──────────────────
async function verificarItemNaComanda() {
    if (!produtoSelecionado) return;
    const numero = document.getElementById("comanda-resgate").value.trim();
    if (!numero || isNaN(numero)) return;

    const res = await apiRequest(
        `/api/resgates/verificar-item?numero_comanda=${numero}&item_id=${produtoSelecionado.item_id}`
    );

    const areaSubst = document.getElementById("substituicao-area");
    if (res.ok && res.tem_item) {
        areaSubst.style.display = "block";
        document.getElementById("btn-confirmar-resgate").dataset.substituir     = "false";
        document.getElementById("btn-confirmar-resgate").dataset.commandaItemId  = res.comanda_item_id || "";
    } else {
        areaSubst.style.display = "none";
    }
}

// ── Confirmar resgate ─────────────────────────────────────────
async function confirmarResgate() {
    if (!produtoSelecionado) return;

    const numero    = document.getElementById("comanda-resgate").value.trim();
    const tipoEl    = document.querySelector("input[name='tipo_consumo']:checked");
    const tipo      = tipoEl ? tipoEl.value : "local";
    const btn       = document.getElementById("btn-confirmar-resgate");
    const substituir = btn.dataset.substituir === "true";
    const cItemId   = btn.dataset.commandaItemId;

    if (!numero || isNaN(numero)) { toastError("Informe o número da sua comanda"); return; }

    btn.disabled = true;
    btn.textContent = "Resgatando…";

    const payload = {
        produto_id:     produtoSelecionado.id,
        numero_comanda: parseInt(numero),
        tipo,
        substituir,
    };
    if (substituir && cItemId) payload.comanda_item_id = parseInt(cItemId);

    const res = await apiRequest("/api/resgates/resgatar", "POST", payload);

    btn.disabled = false;
    btn.textContent = "✦ Resgatar Agora";

    if (res.ok) {
        toastGold(`🎉 ${res.message}`);
        localStorage.setItem("club_numero_comanda", numero);
        numeroComandaAtual = numero;
        fecharModal();
        await carregarSaldo();
    } else {
        toastError(res.message || "Erro ao resgatar");
    }
}

// ── Eventos ───────────────────────────────────────────────────
document.getElementById("modal-overlay")?.addEventListener("click", e => {
    if (e.target === document.getElementById("modal-overlay")) fecharModal();
});
document.getElementById("btn-fechar-modal")?.addEventListener("click", fecharModal);
document.getElementById("btn-confirmar-resgate")?.addEventListener("click", confirmarResgate);

// Ao digitar/sair do campo da comanda, verifica substituição
document.getElementById("comanda-resgate")?.addEventListener("blur", verificarItemNaComanda);

// Substituir: checkbox controla dataset do botão
document.getElementById("check-substituir")?.addEventListener("change", e => {
    document.getElementById("btn-confirmar-resgate").dataset.substituir = e.target.checked ? "true" : "false";
    const btnEl = document.getElementById("btn-confirmar-resgate");
    btnEl.textContent = e.target.checked ? "↺ Substituir e Resgatar" : "✦ Resgatar Agora";
});

// ── Init ──────────────────────────────────────────────────────
carregarSaldo();
carregarProdutos();
