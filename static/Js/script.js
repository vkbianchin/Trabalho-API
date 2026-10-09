const form = document.getElementById("form-cliente");
const mensagemEl = document.getElementById("mensagem");
const btnCadastrar = document.getElementById("btn-cadastrar");

const campoNome = document.getElementById("nome");
const campoEmail = document.getElementById("email");
const campoSenha = document.getElementById("senha");
const campoTelefone = document.getElementById("telefone");
const campoCidade = document.getElementById("cidade");
const listaCidadesEl = document.getElementById("lista-cidades");
const listaRequisitosEl = document.getElementById("requisitos-senha");

const CHAVE_CIDADES_SALVAS = "cadastroClientes.cidadesSalvas";

let timeoutMensagem = null;
let cadastrando = false;

/* ============================================================
   SISTEMA DE HABILITAÇÃO PROGRESSIVA DOS CAMPOS
   Nome -> E-mail -> Senha -> Telefone -> Cidade -> Botão Cadastrar
   (validarEmail, validarSenha e atualizarRequisitosSenha vêm de validacoes.js)
   ============================================================ */

function nomeValido() {
    return campoNome.value.trim().length > 0;
}

function telefoneCompleto() {
    const digitos = campoTelefone.value.replace(/\D/g, "");
    return digitos.length === 11;
}

function cidadeValida() {
    return campoCidade.value.trim().length > 0;
}

function atualizarEstadoCampos() {
    const nomeOk = nomeValido();
    campoEmail.disabled = !nomeOk;

    const emailOk = nomeOk && validarEmail(campoEmail.value);
    campoSenha.disabled = !emailOk;

    const senhaOk = emailOk && validarSenha(campoSenha.value);
    campoTelefone.disabled = !senhaOk;

    const telefoneOk = senhaOk && telefoneCompleto();
    campoCidade.disabled = !telefoneOk;

    const cidadeOk = telefoneOk && cidadeValida();
    btnCadastrar.disabled = cadastrando || !cidadeOk;
}

function formatarTelefone(valor) {
    const digitos = valor.replace(/\D/g, "").slice(0, 11);
    const tamanho = digitos.length;

    if (tamanho === 0) return "";
    if (tamanho < 2) return `(${digitos}`;
    if (tamanho < 7) return `(${digitos.slice(0, 2)}) ${digitos.slice(2)}`;
    return `(${digitos.slice(0, 2)}) ${digitos.slice(2, 7)}-${digitos.slice(7)}`;
}

/* ============================================================
   CIDADES SALVAS (caixa de opção com informações já usadas)
   ============================================================ */

function obterCidadesSalvas() {
    try {
        const dados = localStorage.getItem(CHAVE_CIDADES_SALVAS);
        return dados ? JSON.parse(dados) : [];
    } catch (erro) {
        return [];
    }
}

function renderizarListaCidades(cidades) {
    listaCidadesEl.textContent = "";
    cidades.forEach((cidade) => {
        const option = document.createElement("option");
        option.value = cidade;
        listaCidadesEl.appendChild(option);
    });
}

function salvarCidade(cidade) {
    const cidadeNormalizada = cidade.trim();
    if (!cidadeNormalizada) return;

    const cidades = obterCidadesSalvas();
    const jaExiste = cidades.some(
        (c) => c.toLowerCase() === cidadeNormalizada.toLowerCase()
    );

    if (!jaExiste) {
        cidades.push(cidadeNormalizada);
        try {
            localStorage.setItem(CHAVE_CIDADES_SALVAS, JSON.stringify(cidades));
        } catch (erro) {
            console.error("Não foi possível salvar a cidade:", erro);
        }
    }

    renderizarListaCidades(cidades);
}

function mostrarMensagem(texto, tipo) {
    mensagemEl.textContent = texto;
    mensagemEl.className = `mensagem visivel ${tipo}`;

    if (timeoutMensagem) {
        clearTimeout(timeoutMensagem);
    }

    timeoutMensagem = setTimeout(() => {
        mensagemEl.classList.remove("visivel");
    }, 3500);
}

function limparFormulario() {
    form.reset();
    atualizarRequisitosSenha("", listaRequisitosEl);
    atualizarEstadoCampos();
    campoNome.focus();
}

async function cadastrarCliente(dados) {
    const resposta = await fetch("/api/clientes", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(dados),
    });

    const resultado = await resposta.json();
    return { ok: resposta.ok, resultado };
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (cadastrando) return;

    const nome = campoNome.value.trim();
    const email = campoEmail.value.trim();
    const senha = campoSenha.value;
    const telefone = campoTelefone.value.trim();
    const cidade = campoCidade.value.trim();

    if (!nome || !email || !senha || !telefone || !cidade) {
        mostrarMensagem("Preencha todos os campos.", "erro");
        return;
    }

    const erroEmail = mensagemErroEmail(email);
    if (erroEmail) {
        mostrarMensagem(erroEmail, "erro");
        return;
    }

    if (!validarSenha(senha)) {
        mostrarMensagem("A senha não atende aos requisitos.", "erro");
        return;
    }

    cadastrando = true;
    btnCadastrar.disabled = true;
    btnCadastrar.textContent = "Cadastrando...";
    let redirecionando = false;

    try {
        const { ok, resultado } = await cadastrarCliente({ nome, email, senha, telefone, cidade });

        if (ok && resultado.success) {
            salvarCidade(resultado.cliente.cidade);
            mostrarMensagem(resultado.message || "Cadastro realizado com sucesso!", "sucesso");
            limparFormulario();
            // Cadastro concluído: leva para o login para a pessoa entrar.
            redirecionando = true;
            setTimeout(() => window.location.assign("/login?cadastro=ok"), 1200);
        } else {
            mostrarMensagem(resultado.message || "Não foi possível cadastrar o cliente.", "erro");
        }
    } catch (erro) {
        console.error("Erro ao cadastrar cliente:", erro);
        mostrarMensagem("Erro de conexão com o servidor.", "erro");
    } finally {
        btnCadastrar.textContent = "Cadastrar";
        if (!redirecionando) {
            cadastrando = false;
        }
        atualizarEstadoCampos();
    }
});

campoNome.addEventListener("input", atualizarEstadoCampos);
campoEmail.addEventListener("input", atualizarEstadoCampos);
campoCidade.addEventListener("input", atualizarEstadoCampos);

campoSenha.addEventListener("input", () => {
    atualizarRequisitosSenha(campoSenha.value, listaRequisitosEl);
    atualizarEstadoCampos();
});

campoTelefone.addEventListener("input", () => {
    campoTelefone.value = formatarTelefone(campoTelefone.value);
    atualizarEstadoCampos();
});

document.addEventListener("DOMContentLoaded", () => {
    renderizarListaCidades(obterCidadesSalvas());
    atualizarRequisitosSenha("", listaRequisitosEl);
    atualizarEstadoCampos();
    campoNome.focus();
});
