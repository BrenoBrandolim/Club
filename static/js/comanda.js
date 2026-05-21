// static/js/comanda.js
// Landing page do QR Code: /comanda/<numero>
// Persiste numero no localStorage para recuperar após login/cadastro

import { apiRequest, getToken, getUser, setComandaAtiva,
         setPendingComanda, clearPendingComanda } from "./api.js";
import { toastSuccess, toastError, toastGold } from "./toast.js";

const numero = window.COMANDA_NUMERO;  // injetado pelo template

async function init() {
    const statusEl   = document.getElementById("comanda-status");
    const infoEl     = document.getElementById("comanda-info");
    const actionEl   = document.getElementById("comanda-action");

    statusEl.textContent = "Verificando comanda…";

    // 1. Valida comanda no Caixa via Club
    const res = await apiRequest(`/api/comanda/${numero}`);

    if (!res.ok) {
        statusEl.textContent = "Comanda não encontrada";
        infoEl.textContent   = `Não existe comanda com o número #${numero}.`;
        actionEl.innerHTML   = `<a href="/dashboard" class="btn btn-ghost btn-full">Ir para o Dashboard</a>`;
        return;
    }

    if (!res.aberta) {
        statusEl.textContent = `Comanda #${numero} está ${res.status}`;
        infoEl.textContent   = "Esta comanda não pode ser vinculada.";
        actionEl.innerHTML   = `<a href="/dashboard" class="btn btn-ghost btn-full">Ver meu Dashboard</a>`;
        return;
    }

    // Comanda aberta ✓
    statusEl.textContent = `Comanda #${numero} ✦ Aberta`;
    infoEl.textContent   = "Vincule esta comanda para acumular pontos e resgatar produtos!";

    // 2. Usuário já está logado?
    const token = getToken();
    if (token) {
        const user = getUser();
        actionEl.innerHTML = `
            <p style="font-size:13px; color:var(--text-sub); margin-bottom:16px;">
                Logado como <strong style="color:var(--gold);">${user.nome || user.nickname || "você"}</strong>
            </p>
            <button class="btn btn-gold btn-full btn-lg" id="btn-vincular">
                ✦ Vincular Comanda #${numero}
            </button>
            <div style="margin-top:12px; text-align:center; font-size:12px; color:var(--text-dim);">
                Não é você? <a href="#" id="trocar-conta" style="color:var(--gold);">Usar outra conta</a>
            </div>`;

        document.getElementById("btn-vincular")?.addEventListener("click", vincularLogado);
        document.getElementById("trocar-conta")?.addEventListener("click", (e) => {
            e.preventDefault();
            setPendingComanda(numero);
            import("./auth.js").then(m => m.logout());
        });
    } else {
        // Não logado — salva numero e manda para login
        actionEl.innerHTML = `
            <p style="font-size:13px; color:var(--text-sub); margin-bottom:20px;">
                Faça login ou crie sua conta para vincular esta comanda e ganhar pontos.
            </p>
            <a href="/login" class="btn btn-gold btn-full btn-lg" id="btn-login">
                Entrar e Vincular
            </a>
            <a href="/cadastro" class="btn btn-outline btn-full mt-8" id="btn-cadastro">
                Criar conta gratuita
            </a>`;

        // Salva comanda pendente antes de redirecionar para login/cadastro
        document.getElementById("btn-login")?.addEventListener("click", (e) => {
            e.preventDefault();
            setPendingComanda(numero);
            window.location.href = "/login";
        });
        document.getElementById("btn-cadastro")?.addEventListener("click", (e) => {
            e.preventDefault();
            setPendingComanda(numero);
            window.location.href = "/cadastro";
        });
    }
}

async function vincularLogado() {
    const btn = document.getElementById("btn-vincular");
    btn.disabled = true;
    btn.textContent = "Vinculando…";

    const res = await apiRequest(`/api/comanda/${numero}/vincular`, "POST");

    if (res.ok) {
        setComandaAtiva(numero);
        clearPendingComanda();
        toastGold(res.message);
        setTimeout(() => window.location.href = "/catalogo", 1400);
    } else {
        toastError(res.message || "Erro ao vincular");
        btn.disabled = false;
        btn.textContent = `✦ Vincular Comanda #${numero}`;
    }
}

document.addEventListener("DOMContentLoaded", init);
