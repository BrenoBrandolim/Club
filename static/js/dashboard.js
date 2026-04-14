import { apiRequest } from "/static/js/api.js";

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "/login";
}

async function carregarSaldo() {
    const data = await apiRequest("/pontos/saldo");

    if (data.ok) {
        document.getElementById("saldo").innerText = data.saldo;
    } else {
        alert(data.message);
    }
}

async function carregarResgates() { // Função para carregar os resgates do usuário
    const data = await apiRequest("/resgates/usuario");

    const lista = document.getElementById("resgates");
    lista.innerHTML = "";

    if (data.ok) {
        data.resgates.forEach(r => {
            const li = document.createElement("li");
            li.innerText = `Produto ${r.produto_id} - ${r.pontos_gastos} pontos`;
            lista.appendChild(li);
        });
    } else {
        alert(data.message);
    }
}

window.resgatar = async () => { // Função para resgatar um produto usando os pontos
    const produto_id = document.getElementById("produto_id").value;
    const comanda_id = document.getElementById("comanda_resgate").value;

    const res = await apiRequest("/resgates/resgatar", "POST", {
        produto_id,
        comanda_id
    });

    alert(res.message);

    if (res.ok) {
        carregarSaldo();
        carregarResgates();
    }
};

window.onload = () => {
    carregarSaldo();
    carregarResgates();
};