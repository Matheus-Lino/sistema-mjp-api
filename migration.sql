-- =====================================================
-- MIGRATION: Multi-Tenancy - Oficinas
-- =====================================================
-- Este script adiciona suporte para múltiplas oficinas
-- Cada oficina terá seus próprios dados isolados
-- =====================================================

-- 1. Criar tabela de oficinas
CREATE TABLE IF NOT EXISTS oficinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(20),
    telefone VARCHAR(20),
    email VARCHAR(255),
    endereco TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Adicionar oficina_id nas tabelas existentes
ALTER TABLE clientes ADD COLUMN oficina_id INT;
ALTER TABLE veiculos ADD COLUMN oficina_id INT;
ALTER TABLE servicos ADD COLUMN oficina_id INT;
ALTER TABLE pecas ADD COLUMN oficina_id INT;
ALTER TABLE ordens_servico ADD COLUMN oficina_id INT;
ALTER TABLE usuarios ADD COLUMN oficina_id INT;
ALTER TABLE financeiro ADD COLUMN oficina_id INT;

-- 3. Adicionar índices para melhor performance
CREATE INDEX idx_clientes_oficina ON clientes(oficina_id);
CREATE INDEX idx_veiculos_oficina ON veiculos(oficina_id);
CREATE INDEX idx_servicos_oficina ON servicos(oficina_id);
CREATE INDEX idx_pecas_oficina ON pecas(oficina_id);
CREATE INDEX idx_ordens_oficina ON ordens_servico(oficina_id);
CREATE INDEX idx_usuarios_oficina ON usuarios(oficina_id);
CREATE INDEX idx_financeiro_oficina ON financeiro(oficina_id);

-- 4. Adicionar foreign keys (relacionamentos)
ALTER TABLE clientes ADD CONSTRAINT fk_clientes_oficina FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE CASCADE;
ALTER TABLE veiculos ADD CONSTRAINT fk_veiculos_oficina FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE CASCADE;
ALTER TABLE servicos ADD CONSTRAINT fk_servicos_oficina FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE CASCADE;
ALTER TABLE pecas ADD CONSTRAINT fk_pecas_oficina FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE CASCADE;
ALTER TABLE ordens_servico ADD CONSTRAINT fk_ordens_oficina FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE CASCADE;
ALTER TABLE usuarios ADD CONSTRAINT fk_usuarios_oficina FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE CASCADE;
ALTER TABLE financeiro ADD CONSTRAINT fk_financeiro_oficina FOREIGN KEY (oficina_id) REFERENCES oficinas(id) ON DELETE CASCADE;

-- 5. (OPCIONAL) Migrar dados existentes para uma oficina padrão
-- Se você já tem dados no sistema, descomente as linhas abaixo:

-- INSERT INTO oficinas (nome, cnpj, telefone, email) VALUES ('Oficina Principal', '', '', '');
-- SET @oficina_default_id = LAST_INSERT_ID();
-- UPDATE clientes SET oficina_id = @oficina_default_id WHERE oficina_id IS NULL;
-- UPDATE veiculos SET oficina_id = @oficina_default_id WHERE oficina_id IS NULL;
-- UPDATE servicos SET oficina_id = @oficina_default_id WHERE oficina_id IS NULL;
-- UPDATE pecas SET oficina_id = @oficina_default_id WHERE oficina_id IS NULL;
-- UPDATE ordens_servico SET oficina_id = @oficina_default_id WHERE oficina_id IS NULL;
-- UPDATE usuarios SET oficina_id = @oficina_default_id WHERE oficina_id IS NULL;
-- UPDATE financeiro SET oficina_id = @oficina_default_id WHERE oficina_id IS NULL;

-- 6. Tornar oficina_id obrigatório (NOT NULL) após migração
-- Descomente após garantir que todos os registros têm oficina_id:
-- ALTER TABLE clientes MODIFY oficina_id INT NOT NULL;
-- ALTER TABLE veiculos MODIFY oficina_id INT NOT NULL;
-- ALTER TABLE servicos MODIFY oficina_id INT NOT NULL;
-- ALTER TABLE pecas MODIFY oficina_id INT NOT NULL;
-- ALTER TABLE ordens_servico MODIFY oficina_id INT NOT NULL;
-- ALTER TABLE usuarios MODIFY oficina_id INT NOT NULL;
-- ALTER TABLE financeiro MODIFY oficina_id INT NOT NULL;
