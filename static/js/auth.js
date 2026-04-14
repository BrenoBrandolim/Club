import { apiRequest } from "./api.js";

export async function login(nickname, senha) {
    const res = await fetch("http://localhost:5001/api/usuarios/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ nickname, senha })
    }); 

    const data = await res.json();

    if (data.ok) {
        localStorage.setItem("token", data.token); // Salva o token depois do Login
        window.location.href = "/dashboard"; // mantem o usuário na tela principal
    } else {
        alert(data.message);
    }
}