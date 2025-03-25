-- Adicionar coluna rentabilidade_anual à tabela de investimentos
ALTER TABLE public.investimentos 
ADD COLUMN IF NOT EXISTS rentabilidade_anual DECIMAL(10,4);

-- Atualizar o cache do schema
NOTIFY pgrst, 'reload schema'; 