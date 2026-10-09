/* ============================================================
   Dashboard (área logada): lista de clientes e botão Sair.
   ============================================================ */

const corpoTabela = document.getElementById("corpo-tabela");
const mensagemEl = document.getElementById("mensagem");
const btnSair = document.getElementById("btn-sair");

const CHAVE_CIDADES_SALVAS = "cadastroClientes.cidadesSalvas";

function mostrarMensagem(texto, tipo) {
    mensagemEl.textContent = texto;
    mensagemEl.className = `mensagem visivel ${tipo}`;
}

function irParaLogin() {
    window.location.replace("/login");
}

function mostrarLinhaVazia() {
    corpoTabela.innerHTML = "";
    const tr = document.createElement("tr");
    tr.className = "tabela-vazia";
    const td = document.createElement("td");
    td.colSpan = 4;
    td.textContent = "Nenhum cliente cadastrado.";
    tr.appendChild(td);
    corpoTabela.appendChild(tr);
}

function criarLinhaCliente(cliente) {
    const tr = document.createElement("tr");
    [cliente.nome, cliente.email, cliente.telefone, cliente.cidade].forEach((valor) => {
        const td = document.createElement("td");
        td.textContent = valor;
        tr.appendChild(td);
    });
    return tr;
}

/* Mantém a lista de cidades sugeridas na tela de cadastro (mesma chave de antes). */
function guardarCidades(clientes) {
    try {
        const dados = localStorage.getItem(CHAVE_CIDADES_SALVAS);
        const salvas = dados ? JSON.parse(dados) : [];
        clientes.forEach((c) => {
            const cidade = (c.cidade || "").trim();
            if (cidade && !salvas.some((s) => s.toLowerCase() === cidade.toLowerCase())) {
                salvas.push(cidade);
            }
        });
        localStorage.setItem(CHAVE_CIDADES_SALVAS, JSON.stringify(salvas));
    } catch (erro) {
        /* localStorage indisponível: apenas ignora */
    }
}

async function carregarClientes() {
    try {
        const resposta = await fetch("/api/clientes", { credentials: "same-origin" });

        if (resposta.status === 401) {
            irParaLogin(); // sessão expirada
            return;
        }

        const clientes = await resposta.json();

        if (!resposta.ok || !Array.isArray(clientes)) {
            mostrarMensagem((clientes && clientes.message) || "Não foi possível carregar os clientes.", "erro");
            return;
        }

        if (clientes.length === 0) {
            mostrarLinhaVazia();
            return;
        }

        corpoTabela.innerHTML = "";
        clientes.forEach((cliente) => corpoTabela.appendChild(criarLinhaCliente(cliente)));
        guardarCidades(clientes);
    } catch (erro) {
        console.error("Erro ao carregar clientes:", erro);
        mostrarMensagem("Erro de conexão com o servidor.", "erro");
    }
}

async function sair() {
    btnSair.disabled = true;
    try {
        await fetch("/logout", { method: "POST", credentials: "same-origin" });
    } catch (erro) {
        console.error("Erro ao sair:", erro);
    }
    irParaLogin(); // replace: o "Voltar" não retorna para a página protegida
}

btnSair.addEventListener("click", sair);

// Página restaurada do cache (botão "Voltar"): recarrega para o servidor checar o login.
window.addEventListener("pageshow", (event) => {
    if (event.persisted) window.location.reload();
});

document.addEventListener("DOMContentLoaded", carregarClientes);
