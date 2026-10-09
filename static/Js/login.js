/* ============================================================
   Tela de login.
   Depende de validacoes.js (validarEmail, validarSenha, ...).
   ============================================================ */

const formLogin = document.getElementById("form-login");
const campoEmail = document.getElementById("email");
const campoSenha = document.getElementById("senha");
const erroEmailEl = document.getElementById("erro-email");
const erroSenhaEl = document.getElementById("erro-senha");
const listaRequisitosEl = document.getElementById("requisitos-senha");
const mensagemGeralEl = document.getElementById("mensagem-geral");
const btnEntrar = document.getElementById("btn-entrar");
const textoBtnEl = btnEntrar.querySelector(".texto-btn");

const TEMPO_LIMITE_MS = 15000;

let enviando = false;
let emailTocado = false;

function mostrarMensagemGeral(texto, tipo) {
    mensagemGeralEl.textContent = texto;
    mensagemGeralEl.className = `mensagem-geral visivel ${tipo}`;
}

function limparMensagemGeral() {
    mensagemGeralEl.textContent = "";
    mensagemGeralEl.className = "mensagem-geral";
}

function mostrarErroCampo(input, erroEl, texto) {
    erroEl.textContent = texto;
    input.classList.toggle("invalido", Boolean(texto));
    input.setAttribute("aria-invalid", texto ? "true" : "false");
}

/* Valida o e-mail. Só mostra o erro depois que o usuário mexeu no campo. */
function validarCampoEmail(forcarExibicao = false) {
    const erro = mensagemErroEmail(campoEmail.value);
    if (emailTocado || forcarExibicao) {
        mostrarErroCampo(campoEmail, erroEmailEl, erro);
    }
    return erro === "";
}

/* Valida a senha e atualiza a lista de requisitos em tempo real. */
function validarCampoSenha(forcarExibicao = false) {
    const senha = campoSenha.value;
    const requisitosOk = atualizarRequisitosSenha(senha, listaRequisitosEl);
    const valida = requisitosOk && validarSenha(senha);

    if (forcarExibicao && !senha) {
        mostrarErroCampo(campoSenha, erroSenhaEl, "A senha é obrigatória.");
    } else if (forcarExibicao && !valida) {
        mostrarErroCampo(campoSenha, erroSenhaEl, "A senha não atende aos requisitos.");
    } else {
        mostrarErroCampo(campoSenha, erroSenhaEl, "");
    }
    return valida;
}

function atualizarBotao() {
    const emailOk = validarEmail(campoEmail.value);
    const senhaOk = validarSenha(campoSenha.value);
    btnEntrar.disabled = enviando || !(emailOk && senhaOk);
}

function definirCarregando(carregando) {
    enviando = carregando;
    btnEntrar.classList.toggle("carregando", carregando);
    textoBtnEl.textContent = carregando ? "ENTRANDO..." : "ENTRAR";
    campoEmail.readOnly = carregando;
    campoSenha.readOnly = carregando;
    btnEntrar.setAttribute("aria-busy", carregando ? "true" : "false");
    atualizarBotao();
}

function destinoSeguro(destino) {
    // Só aceita caminhos internos do próprio site.
    return typeof destino === "string" && destino.startsWith("/") && !destino.startsWith("//")
        ? destino
        : "/dashboard";
}

async function realizarLogin() {
    if (enviando) return; // evita requisições simultâneas

    // Última validação antes de enviar
    emailTocado = true;
    const emailOk = validarCampoEmail(true);
    const senhaOk = validarCampoSenha(true);
    if (!emailOk || !senhaOk) {
        atualizarBotao();
        return;
    }

    limparMensagemGeral();
    definirCarregando(true);

    const controle = new AbortController();
    const timer = setTimeout(() => controle.abort(), TEMPO_LIMITE_MS);

    try {
        const resposta = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            signal: controle.signal,
            body: JSON.stringify({
                email: campoEmail.value.trim(),
                senha: campoSenha.value,
            }),
        });

        let resultado = null;
        try {
            resultado = await resposta.json();
        } catch (erroJson) {
            resultado = null;
        }

        if (resposta.ok && resultado && resultado.success) {
            mostrarMensagemGeral("Login realizado com sucesso! Redirecionando...", "sucesso");
            window.location.replace(destinoSeguro(resultado.redirect));
            return; // mantém o botão bloqueado até a página mudar
        }

        const mensagem =
            (resultado && resultado.message) ||
            "Não foi possível realizar o login no momento. Tente novamente mais tarde.";

        // Erros de campo vindos do servidor (validação do back-end)
        if (resultado && resultado.errors) {
            if (resultado.errors.email) mostrarErroCampo(campoEmail, erroEmailEl, resultado.errors.email);
            if (resultado.errors.senha) mostrarErroCampo(campoSenha, erroSenhaEl, resultado.errors.senha);
        }

        mostrarMensagemGeral(mensagem, "erro");
        campoSenha.value = "";
        validarCampoSenha();
        definirCarregando(false);
        campoSenha.focus();
    } catch (erro) {
        const expirou = erro && erro.name === "AbortError";
        mostrarMensagemGeral(
            expirou
                ? "O servidor demorou para responder. Tente novamente."
                : "Erro de conexão com o servidor. Verifique sua internet e tente novamente.",
            "erro"
        );
        definirCarregando(false);
    } finally {
        clearTimeout(timer);
    }
}

formLogin.addEventListener("submit", (event) => {
    event.preventDefault();
    realizarLogin();
});

campoEmail.addEventListener("input", () => {
    emailTocado = true;
    validarCampoEmail();
    atualizarBotao();
});

campoEmail.addEventListener("blur", () => {
    if (campoEmail.value !== "") {
        emailTocado = true;
        validarCampoEmail();
    }
});

campoSenha.addEventListener("input", () => {
    validarCampoSenha();
    atualizarBotao();
});

// Se a página voltar do cache do navegador (botão "Voltar"), recarrega
// para o servidor decidir se o usuário já está logado.
window.addEventListener("pageshow", (event) => {
    if (event.persisted) window.location.reload();
});

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("cadastro") === "ok") {
        mostrarMensagemGeral("Cadastro realizado com sucesso! Faça login para continuar.", "sucesso");
        window.history.replaceState(null, "", "/login");
    }

    atualizarRequisitosSenha(campoSenha.value, listaRequisitosEl);
    atualizarBotao();
});
