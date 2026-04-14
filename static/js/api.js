const API_URL = "http://localhost:5001/api";

function getToken() {
    return localStorage.getItem("token");
}

export async function apiRequest(endpoint, method = "GET", body = null) {
    const headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + getToken()
    };

    const response = await fetch(`${API_URL}${endpoint}`, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null
    });

    // ✅ AGORA está no lugar certo
    if (!response.ok) {
        return { ok: false, message: "Erro na requisição" };
    }

    return response.json();
}