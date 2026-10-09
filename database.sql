CREATE DATABASE IF NOT EXISTS cadastro_clientes;

USE cadastro_clientes;

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    senha_hash VARCHAR(255) NULL,
    telefone VARCHAR(30) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_clientes_email (email)
);

-- ==========================================================================
-- MIGRAÇÃO para quem JÁ TEM a tabela "clientes" criada (rode uma vez):
--
-- 1) Veja se há e-mails repetidos (o resultado deve ser vazio):
--      SELECT email, COUNT(*) FROM clientes GROUP BY email HAVING COUNT(*) > 1;
--    Se aparecer algum, apague ou altere os repetidos antes do passo 3.
--
-- 2) Coluna que guarda o HASH da senha (a senha nunca é salva em texto puro):
--      ALTER TABLE clientes ADD COLUMN senha_hash VARCHAR(255) NULL AFTER email;
--
-- 3) E-mail único (o login procura o usuário pelo e-mail):
--      ALTER TABLE clientes ADD UNIQUE KEY uq_clientes_email (email);
--
-- Clientes antigos ficam com senha_hash NULL e não conseguem entrar até se
-- cadastrarem de novo (ou ganharem uma senha).
-- ==========================================================================
