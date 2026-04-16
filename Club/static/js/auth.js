// static/js/auth.js

import { apiRequest, setToken, setUser, getToken, clearToken } from "./api.js";
import { toastError, toastSuccess } from "./toast.js";

export function verificarAuth() {
    if (!getToken()) {
        // Preserva a URL atual para redirecionar após login
        const atual = window.location.pathname;
        if (atual !== "/login" && atual !== "/cadastro") {
            sessionStorage.setItem("club_redirect_after_login", atual);
        }
        window.location.href = "/login";
        return false;
    }
    return true;
}

export async function login(nickname, senha) {
    const res = await apiRequest("/api/usuarios/login", "POST", { nickname, senha });
    if (res.ok) {
        setToken(res.token);
        setUser({ nome: res.nome, nickname: res.nickname });

        // Redireciona de volta para onde estava (ex: página de comanda)
        const redirecionarPara = sessionStorage.getItem("club_redirect_after_login");
        sessionStorage.removeItem("club_redirect_after_login");

        if (redirecionarPara && redirecionarPara !== "/login") {
            // Se vem de página de comanda, adiciona flag de auto-vincular
            const destino = redirecionarPara.startsWith("/comanda/")
                ? redirecionarPara + "?auto_vincular=1"
                : redirecionarPara;
            window.location.href = destino;
        } else {
            window.location.href = "/dashboard";
        }
    } else {
        toastError(res.message || "Erro ao fazer login");
    }
}

export async function cadastrar(nome, nickname, senha) {
    const res = await apiRequest("/api/usuarios/", "POST", { nome, nickname, senha });
    if (res.ok) {
        setToken(res.token);
        setUser({ nome, nickname });
        toastSuccess("Conta criada com sucesso!");

        const redirecionarPara = sessionStorage.getItem("club_redirect_after_login");
        sessionStorage.removeItem("club_redirect_after_login");

        setTimeout(() => {
            if (redirecionarPara && redirecionarPara !== "/cadastro") {
                const destino = redirecionarPara.startsWith("/comanda/")
                    ? redirecionarPara + "?auto_vincular=1"
                    : redirecionarPara;
                window.location.href = destino;
            } else {
                window.location.href = "/dashboard";
            }
        }, 800);
    } else {
        toastError(res.message || "Erro ao criar conta");
    }
}

export function logout() {
    clearToken();
    window.location.href = "/login";
}
