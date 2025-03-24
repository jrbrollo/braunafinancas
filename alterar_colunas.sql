-- Script para alterar as tabelas substituindo usuario_id por user_id

-- Alterar tabela de gastos
ALTER TABLE gastos
RENAME COLUMN usuario_id TO user_id;

-- Alterar tabela de receitas
ALTER TABLE receitas
RENAME COLUMN usuario_id TO user_id;

-- Alterar tabela de investimentos
ALTER TABLE investimentos
RENAME COLUMN usuario_id TO user_id;

-- Alterar tabela de metas
ALTER TABLE metas
RENAME COLUMN usuario_id TO user_id;

-- Alterar tabela de dividas
ALTER TABLE dividas
RENAME COLUMN usuario_id TO user_id;

-- Remover as políticas antigas (que usam usuario_id)
DROP POLICY IF EXISTS "Usuários podem ver apenas seus próprios gastos" ON gastos;
DROP POLICY IF EXISTS "Usuários podem inserir seus próprios gastos" ON gastos;
DROP POLICY IF EXISTS "Usuários podem atualizar seus próprios gastos" ON gastos;
DROP POLICY IF EXISTS "Usuários podem excluir seus próprios gastos" ON gastos;

DROP POLICY IF EXISTS "Usuários podem ver apenas suas próprias receitas" ON receitas;
DROP POLICY IF EXISTS "Usuários podem inserir suas próprias receitas" ON receitas;
DROP POLICY IF EXISTS "Usuários podem atualizar suas próprias receitas" ON receitas;
DROP POLICY IF EXISTS "Usuários podem excluir suas próprias receitas" ON receitas;

DROP POLICY IF EXISTS "Usuários podem ver apenas seus próprios investimentos" ON investimentos;
DROP POLICY IF EXISTS "Usuários podem inserir seus próprios investimentos" ON investimentos;
DROP POLICY IF EXISTS "Usuários podem atualizar seus próprios investimentos" ON investimentos;
DROP POLICY IF EXISTS "Usuários podem excluir seus próprios investimentos" ON investimentos;

DROP POLICY IF EXISTS "Usuários podem ver apenas suas próprias metas" ON metas;
DROP POLICY IF EXISTS "Usuários podem inserir suas próprias metas" ON metas;
DROP POLICY IF EXISTS "Usuários podem atualizar suas próprias metas" ON metas;
DROP POLICY IF EXISTS "Usuários podem excluir suas próprias metas" ON metas;

DROP POLICY IF EXISTS "Usuários podem ver apenas suas próprias dívidas" ON dividas;
DROP POLICY IF EXISTS "Usuários podem inserir suas próprias dívidas" ON dividas;
DROP POLICY IF EXISTS "Usuários podem atualizar suas próprias dívidas" ON dividas;
DROP POLICY IF EXISTS "Usuários podem excluir suas próprias dívidas" ON dividas;

-- Com as colunas renomeadas, você poderá usar as políticas pré-definidas do Supabase
-- que usam automaticamente user_id como coluna de referência 