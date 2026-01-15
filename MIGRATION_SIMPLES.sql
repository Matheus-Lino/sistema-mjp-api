-- =====================================================
-- INSTRUÇÕES: Execute este script no MySQL PRIMEIRO
-- =====================================================
-- 1. Abra MySQL Workbench ou terminal MySQL
-- 2. Conecte ao banco oficina_mjp
-- 3. Execute os comandos abaixo LINHA POR LINHA

-- PASSO 1: Criar tabela oficinas
CREATE TABLE IF NOT EXISTS oficinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(20),
    telefone VARCHAR(20),
    email VARCHAR(255),
    endereco TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PASSO 2: Adicionar oficina_id nas tabelas (copie e execute bloco inteiro)
ALTER TABLE clientes ADD COLUMN oficina_id INT;
ALTER TABLE veiculos ADD COLUMN oficina_id INT;
ALTER TABLE servicos ADD COLUMN oficina_id INT;
ALTER TABLE pecas ADD COLUMN oficina_id INT;
ALTER TABLE ordens_servico ADD COLUMN oficina_id INT;
ALTER TABLE usuarios ADD COLUMN oficina_id INT;
ALTER TABLE financeiro ADD COLUMN oficina_id INT;

-- PASSO 3: Criar índices (copie e execute bloco inteiro)
CREATE INDEX idx_clientes_oficina ON clientes(oficina_id);
CREATE INDEX idx_veiculos_oficina ON veiculos(oficina_id);
CREATE INDEX idx_servicos_oficina ON servicos(oficina_id);
CREATE INDEX idx_pecas_oficina ON pecas(oficina_id);
CREATE INDEX idx_ordens_oficina ON ordens_servico(oficina_id);
CREATE INDEX idx_usuarios_oficina ON usuarios(oficina_id);
CREATE INDEX idx_financeiro_oficina ON financeiro(oficina_id);

-- =====================================================
-- ⚠️ ATENÇÃO: Se você JÁ TEM DADOS no sistema
-- =====================================================
-- Execute os comandos abaixo para migrar dados existentes
-- para uma "Oficina Principal" padrão

-- Inserir oficina padrão
INSERT INTO oficinas (nome, cnpj, telefone, email) 
VALUES ('Oficina Principal', '', '', '');

-- Pegar o ID da oficina criada e atualizar todas as tabelas
-- ⚠️ SUBSTITUA @oficina_id pelo ID que apareceu após o INSERT
SET @oficina_id = LAST_INSERT_ID();

UPDATE clientes SET oficina_id = @oficina_id WHERE oficina_id IS NULL;
UPDATE veiculos SET oficina_id = @oficina_id WHERE oficina_id IS NULL;
UPDATE servicos SET oficina_id = @oficina_id WHERE oficina_id IS NULL;
UPDATE pecas SET oficina_id = @oficina_id WHERE oficina_id IS NULL;
UPDATE ordens_servico SET oficina_id = @oficina_id WHERE oficina_id IS NULL;
UPDATE usuarios SET oficina_id = @oficina_id WHERE oficina_id IS NULL;
UPDATE financeiro SET oficina_id = @oficina_id WHERE oficina_id IS NULL;

-- =====================================================
-- PRONTO! Agora volte para o VS Code
-- =====================================================
-- A migração do banco está completa
-- Próximo passo: atualizar o código backend e frontend
