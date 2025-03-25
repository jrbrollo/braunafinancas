-- Corrigir coluna data_inicial na tabela de investimentos
ALTER TABLE public.investimentos 
DROP COLUMN IF EXISTS data_inicial;

ALTER TABLE public.investimentos 
ADD COLUMN IF NOT EXISTS data_inicio DATE NOT NULL DEFAULT CURRENT_DATE;

-- Atualizar o cache do schema
NOTIFY pgrst, 'reload schema'; 