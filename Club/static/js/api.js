// static/js/api.js
const API_URL = "";

export function getToken()        { return localStorage.getItem("club_token"); }
export function setToken(t)       { localStorage.setItem("club_token", t); }
export function clearToken()      { localStorage.removeItem("club_token"); localStorage.removeItem("club_user"); }
export function getUser()         { try { return JSON.parse(localStorage.getItem("club_user") || "{}"); } catch { return {}; } }
export function setUser(u)        { localStorage.setItem("club_user", JSON.stringify(u)); }

// Comanda pendente — persiste após login/cadastro
export function setPendingComanda(numero) { localStorage.setItem("club_comanda_pendente", String(numero)); }
export function getPendingComanda()       { return localStorage.getItem("club_comanda_pendente"); }
export function clearPendingComanda()     { localStorage.removeItem("club_comanda_pendente"); }

// Comanda ativa vinculada
export function setComandaAtiva(numero)   { localStorage.setItem("club_comanda_ativa", String(numero)); }
export function getComandaAtiva()         { return localStorage.getItem("club_comanda_ativa"); }
export function clearComandaAtiva()       { localStorage.removeItem("club_comanda_ativa"); }

export async function apiRequest(endpoint, method = "GET", body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) headers["Authorization"] = "Bearer " + token;

    try {
        const res = await fetch(`${API_URL}${endpoint}`, {
            method,
            headers,
            body: body ? JSON.stringify(body) : null,
        });
        if (res.status === 401) { clearToken(); window.location.href = "/login"; return { ok: false }; }
        return await res.json();
    } catch (err) {
        return { ok: false, message: "Erro de conexao" };
    }
}
