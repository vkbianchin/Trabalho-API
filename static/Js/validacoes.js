/* ============================================================
   Validações compartilhadas (login e cadastro).
   O back-end (utils/validacoes.py) aplica as mesmas regras.
   ============================================================ */

const TAMANHO_MIN_SENHA = 8;
const TAMANHO_MAX_SENHA = 128;
const TAMANHO_MAX_EMAIL = 150;

// texto@dominio.com (aceita também .com.br, .com.pt etc.)
const REGEX_EMAIL =
    /^[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.com(?:\.[A-Za-z]{2})?$/;

const CARACTERES_ESPECIAIS = "!@#$%^&*()_+-=[]{};':\"\\|,.<>/?`~";

/** Retorna "" se o e-mail é válido, ou a mensagem de erro. */
function mensagemErroEmail(emailBruto) {
    const email = emailBruto.trim(); // espaços nas pontas são ignorados

    if (!email) return "O e-mail é obrigatório.";
    if (/\s/.test(email)) return "O e-mail não pode conter espaços.";
    if (!email.includes("@") || !email.toLowerCase().includes(".com")) {
        return "O e-mail deve possuir @ e .com.";
    }
    if (email.length > TAMANHO_MAX_EMAIL || !REGEX_EMAIL.test(email)) {
        return "Digite um e-mail válido.";
    }
    return "";
}

function validarEmail(email) {
    return mensagemErroEmail(email) === "";
}

/** Diz quais requisitos a senha cumpre. */
function avaliarSenha(senha) {
    return {
        tamanho: senha.length >= TAMANHO_MIN_SENHA,
        maiuscula: /[A-Z]/.test(senha),
        minuscula: /[a-z]/.test(senha),
        numero: /[0-9]/.test(senha),
        especial: [...senha].some((c) => CARACTERES_ESPECIAIS.includes(c)),
    };
}

function validarSenha(senha) {
    return (
        senha.length <= TAMANHO_MAX_SENHA &&
        Object.values(avaliarSenha(senha)).every(Boolean)
    );
}

/** Marca (☐ -> ✓) os requisitos da lista. Retorna true se todos foram cumpridos. */
function atualizarRequisitosSenha(senha, listaEl) {
    const resultado = avaliarSenha(senha);
    listaEl.querySelectorAll("li[data-regra]").forEach((li) => {
        const ok = resultado[li.dataset.regra];
        li.classList.toggle("ok", ok);
        li.querySelector(".icone").textContent = ok ? "✓" : "☐";
    });
    return Object.values(resultado).every(Boolean);
}
