// static/js/catalogo.js

import { apiRequest, getUser } from "./api.js";
import { verificarAuth } from "./auth.js";
import { toastError, toastSuccess, toastGold } from "./toast.js";

verificarAuth();

let produtos = [];
let produtoSelecionado = null;
let saldoAtual = 0;
let comandaAtivaGlobal = ""; // Armazena a comanda vinculada para preenchimento rápido

// Adiciona o estilo da animação dinamicamente
const style = document.createElement('style');
style.innerHTML = `
    .btn-loading-state {
        background: linear-gradient(90deg, #ff8c00 0%, #ff8c00 50%, #b26200 50%, #b26200 100%);
        background-size: 200% 100%;
        background-position: 100% 0;
        animation: loading-fill 3.5s forwards;
        color: white !important;
        pointer-events: none;
        border: none;
    }
    @keyframes loading-fill {
        from { background-position: 100% 0; }
        to { background-position: 0% 0; }
    }
    .spinner-arrows {
        display: inline-block;
        animation: spin 1s linear infinite;
        margin-right: 8px;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// ── Catálogo ─────────────────────────────────────────────────
async function carregarProdutos() {
    const grid = document.getElementById("produto-grid");
    if (!grid) return;

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
    if (!grid) return;

    if (!lista.length) {
        grid.innerHTML = `<p class="text-sub text-center" style="padding:40px 0;grid-column:1/-1;">Nenhum produto disponível.</p>`;
        return;
    }

    grid.innerHTML = lista.map(p => {
        const pode = saldoAtual >= p.pontos_necessarios;
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
                    <span class="pontos-badge">${Number(p.pontos_necessarios).toLocaleString('pt-BR')}</span>
                    <span class="pontos-label">pts</span>
                </div>
                ${!pode ? `<div style="margin-top:6px;font-size:10px;color:var(--danger);">⚠ Pontos insuficientes</div>` : ""}
            </div>
        </div>`;
    }).join("");
}

// ── Saldo e Comanda ───────────────────────────────────────────
async function carregarDadosIniciais() {
    const resSaldo = await apiRequest("/api/pontos/saldo");
    if (resSaldo.ok) {
        saldoAtual = resSaldo.saldo;
        const el = document.getElementById("saldo-topo");
        if (el) el.textContent = `${Number(resSaldo.saldo).toLocaleString('pt-BR')} pts`;
    }

    const resComanda = await apiRequest("/api/comanda/ativa");
    if (resComanda.ok && resComanda.ativa) {
        comandaAtivaGlobal = resComanda.numero_comanda;
    }
    
    if (produtos.length) renderProdutos(filtrarProdutos());
}

// ── Busca ─────────────────────────────────────────────────────
function filtrarProdutos() {
    const q = document.getElementById("busca")?.value.toLowerCase() || "";
    return produtos.filter(p => p.nome.toLowerCase().includes(q));
}
document.getElementById("busca")?.addEventListener("input", () => renderProdutos(filtrarProdutos()));

// ── Modal (Abertura e Verificação Automática) ────────────────
window.abrirModal = async function(id) {
    produtoSelecionado = produtos.find(p => p.id === id);
    if (!produtoSelecionado) return;

    const p = produtoSelecionado;
    const btnResgate = document.getElementById("btn-confirmar-resgate");
    const inputComanda = document.getElementById("comanda-resgate");

    // Preencher informações do modal
    document.getElementById("modal-nome").textContent = p.nome;
    document.getElementById("modal-pontos").textContent = Number(p.pontos_necessarios).toLocaleString('pt-BR');
    document.getElementById("modal-saldo").textContent = Number(saldoAtual).toLocaleString('pt-BR');

    const imgEl = document.getElementById("modal-img");
    if (p.foto_url) { imgEl.src = p.foto_url; imgEl.style.display = "block"; }
    else { imgEl.style.display = "none"; }

    // Resetar estados
    btnResgate.classList.remove("btn-loading-state");
    btnResgate.innerHTML = "✦ Resgatar Agora";
    const pode = saldoAtual >= p.pontos_necessarios;
    btnResgate.disabled = !pode;
    document.getElementById("modal-aviso").style.display = pode ? "none" : "block";
    document.getElementById("substituicao-area").style.display = "none";
    
    // Preenchimento automático da comanda vinculada
    inputComanda.value = comandaAtivaGlobal;

    document.getElementById("modal-overlay").classList.add("open");
    document.body.style.overflow = "hidden";

    if (inputComanda.value) {
        await verificarItemNaComanda();
    }
};

function fecharModal() {
    document.getElementById("modal-overlay").classList.remove("open");
    document.body.style.overflow = "";
    produtoSelecionado = null;
}

// ── Verificar item na comanda (Lógica de Preço e Animação) ──
async function verificarItemNaComanda() {
    if (!produtoSelecionado) return;
    const numero = document.getElementById("comanda-resgate").value.trim();
    if (!numero) return;

    const btn = document.getElementById("btn-confirmar-resgate");
    
    // Inicia animação visual (Laranja escuro para claro com setinhas)
    btn.classList.add("btn-loading-state");
    btn.innerHTML = `<span class="spinner-arrows">↻</span> Verificando...`;

    try {
        const res = await apiRequest(`/api/resgates/verificar-item?numero_comanda=${numero}&item_id=${produtoSelecionado.item_id}`);
        const areaSubst = document.getElementById("substituicao-area");
        
        if (res.ok && res.tem_item) {
            areaSubst.style.display = "block";
            areaSubst.innerHTML = `
            <div class="subst-box">
                <p>✨ <strong>Este item pode sair de graça!</strong></p>
                <p>Você já pediu este item. Que tal usar seu saldo de pontos para que ele não custe nada na sua comanda?</p>
                <label class="substituicao-check">
                    <input type="checkbox" id="check-substituir">
                    <span>Transformar este item em um presente (usar pontos)</span>
                </label>
            </div>
            `;

            document.getElementById("check-substituir").addEventListener("change", e => {
                btn.dataset.substituir = e.target.checked ? "true" : "false";
                btn.innerHTML = e.target.checked ? "↺ Substituir e Resgatar" : "✦ Resgatar Agora";
            });

            btn.dataset.commandaItemId = res.comanda_item_id || "";
        } else {
            areaSubst.style.display = "none";
        }
    } catch (e) {
        console.error(e);
    } finally {
        // Remove animação e restaura estado original
        btn.classList.remove("btn-loading-state");
        btn.disabled = saldoAtual < produtoSelecionado.pontos_necessarios;
        if (btn.dataset.substituir !== "true") {
            btn.innerHTML = "✦ Resgatar Agora";
        }
    }
}

// ── Confirmar resgate ─────────────────────────────────────────
async function confirmarResgate() {
    if (!produtoSelecionado) return;

    const numero = document.getElementById("comanda-resgate").value.trim();
    const btn = document.getElementById("btn-confirmar-resgate");
    const substituir = btn.dataset.substituir === "true";
    const cItemId = btn.dataset.commandaItemId;

    if (!numero) { toastError("Informe o número da sua comanda"); return; }

    btn.classList.add("btn-loading-state");
    btn.innerHTML = `<span class="spinner-arrows">↻</span> Processando...`;

    const payload = {
        produto_id: produtoSelecionado.id,
        numero_comanda: parseInt(numero),
        tipo: document.querySelector("input[name='tipo_consumo']:checked")?.value.toUpperCase() || "LOCAL",
        substituir
    };

    if (substituir && cItemId) payload.comanda_item_id = parseInt(cItemId);

    try {
        const res = await apiRequest("/api/resgates/resgatar", "POST", payload);
        if (res.ok) {
            toastGold(`🎉 ${res.message}`);
            fecharModal();
            await carregarDadosIniciais();
        } else {
            toastError(res.message || "Erro ao realizar resgate");
            btn.classList.remove("btn-loading-state");
            btn.innerHTML = substituir ? "↺ Substituir e Resgatar" : "✦ Resgatar Agora";
        }
    } catch (e) {
        toastError("Erro na conexão.");
        btn.classList.remove("btn-loading-state");
    }
}

// ── Eventos ───────────────────────────────────────────────────
document.getElementById("btn-fechar-modal")?.addEventListener("click", fecharModal);
document.getElementById("btn-confirmar-resgate")?.addEventListener("click", confirmarResgate);
document.getElementById("comanda-resgate")?.addEventListener("blur", verificarItemNaComanda);

document.getElementById("modal-overlay")?.addEventListener("click", e => {
    if (e.target.id === "modal-overlay") fecharModal();
});

// ── Init ──────────────────────────────────────────────────────
carregarProdutos();
carregarDadosIniciais();