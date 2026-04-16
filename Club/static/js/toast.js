// static/js/toast.js

let container = null;

function getContainer() {
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    return container;
}

export function toast(message, type = "info", duration = 3500) {
    const icons = { success: "✓", error: "✕", info: "i", gold: "★" };
    const c = getContainer();

    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${icons[type] || "i"}</span><span>${message}</span>`;
    c.appendChild(el);

    setTimeout(() => {
        el.style.opacity = "0";
        el.style.transform = "translateY(-8px)";
        el.style.transition = "all 0.3s ease";
        setTimeout(() => el.remove(), 300);
    }, duration);
}

export const toastSuccess = (msg) => toast(msg, "success");
export const toastError   = (msg) => toast(msg, "error");
export const toastGold    = (msg) => toast(msg, "gold");
