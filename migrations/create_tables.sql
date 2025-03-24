-- Versão do banco de dados: PostgreSQL (Supabase)
-- Criação das tabelas principais do Brauna Finanças

-- Tabela de perfis de usuários (extensão da tabela auth.users do Supabase)
CREATE TABLE IF NOT EXISTS public.perfis (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    renda_mensal DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Função para atualizar o timestamp de atualização automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar o timestamp em perfis
CREATE TRIGGER update_perfis_updated_at
BEFORE UPDATE ON public.perfis
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Tabela de gastos
CREATE TABLE IF NOT EXISTS public.gastos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    data_gasto DATE NOT NULL,
    valor DECIMAL(12,2) NOT NULL,
    categoria TEXT NOT NULL,
    descricao TEXT NOT NULL,
    fixo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger para atualizar o timestamp em gastos
CREATE TRIGGER update_gastos_updated_at
BEFORE UPDATE ON public.gastos
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Tabela de investimentos
CREATE TABLE IF NOT EXISTS public.investimentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valor_inicial DECIMAL(12,2) NOT NULL,
    valor_atual DECIMAL(12,2) NOT NULL,
    data_inicio DATE NOT NULL,
    rentabilidade_anual DECIMAL(6,2),
    data_vencimento DATE,
    instituicao TEXT,
    notas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger para atualizar o timestamp em investimentos
CREATE TRIGGER update_investimentos_updated_at
BEFORE UPDATE ON public.investimentos
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Tabela de dívidas
CREATE TABLE IF NOT EXISTS public.dividas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    nome TEXT NOT NULL,
    valor_inicial DECIMAL(12,2) NOT NULL,
    valor_atual DECIMAL(12,2) NOT NULL,
    data_inicio DATE NOT NULL,
    data_vencimento DATE,
    juros_mensal DECIMAL(6,2),
    parcelas_total INTEGER,
    parcelas_pagas INTEGER DEFAULT 0,
    categoria TEXT NOT NULL,
    instituicao TEXT,
    notas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger para atualizar o timestamp em dívidas
CREATE TRIGGER update_dividas_updated_at
BEFORE UPDATE ON public.dividas
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Tabela de objetivos financeiros
CREATE TABLE IF NOT EXISTS public.objetivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    valor_alvo DECIMAL(12,2) NOT NULL,
    valor_atual DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    data_inicio DATE NOT NULL,
    data_alvo DATE,
    categoria TEXT NOT NULL,
    finalizado BOOLEAN DEFAULT FALSE,
    prioridade TEXT DEFAULT 'média',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger para atualizar o timestamp em objetivos
CREATE TRIGGER update_objetivos_updated_at
BEFORE UPDATE ON public.objetivos
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Tabela de seguros
CREATE TABLE IF NOT EXISTS public.seguros (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valor_anual DECIMAL(12,2) NOT NULL,
    valor_cobertura DECIMAL(12,2),
    data_inicio DATE NOT NULL,
    data_vencimento DATE NOT NULL,
    seguradora TEXT,
    beneficiarios TEXT,
    notas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger para atualizar o timestamp em seguros
CREATE TRIGGER update_seguros_updated_at
BEFORE UPDATE ON public.seguros
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Criar políticas de Row Level Security (RLS)

-- Habilitar RLS em todas as tabelas
ALTER TABLE public.perfis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.gastos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.investimentos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dividas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.objetivos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.seguros ENABLE ROW LEVEL SECURITY;

-- Políticas para perfis
CREATE POLICY "Usuários podem ver seus próprios perfis" ON public.perfis
    FOR SELECT USING (auth.uid() = id);
    
CREATE POLICY "Usuários podem atualizar seus próprios perfis" ON public.perfis
    FOR UPDATE USING (auth.uid() = id);

-- Políticas para gastos
CREATE POLICY "Usuários podem ver seus próprios gastos" ON public.gastos
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem inserir seus próprios gastos" ON public.gastos
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem atualizar seus próprios gastos" ON public.gastos
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem excluir seus próprios gastos" ON public.gastos
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para investimentos
CREATE POLICY "Usuários podem ver seus próprios investimentos" ON public.investimentos
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem inserir seus próprios investimentos" ON public.investimentos
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem atualizar seus próprios investimentos" ON public.investimentos
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem excluir seus próprios investimentos" ON public.investimentos
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para dívidas
CREATE POLICY "Usuários podem ver suas próprias dívidas" ON public.dividas
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem inserir suas próprias dívidas" ON public.dividas
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem atualizar suas próprias dívidas" ON public.dividas
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem excluir suas próprias dívidas" ON public.dividas
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para objetivos
CREATE POLICY "Usuários podem ver seus próprios objetivos" ON public.objetivos
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem inserir seus próprios objetivos" ON public.objetivos
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem atualizar seus próprios objetivos" ON public.objetivos
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem excluir seus próprios objetivos" ON public.objetivos
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para seguros
CREATE POLICY "Usuários podem ver seus próprios seguros" ON public.seguros
    FOR SELECT USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem inserir seus próprios seguros" ON public.seguros
    FOR INSERT WITH CHECK (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem atualizar seus próprios seguros" ON public.seguros
    FOR UPDATE USING (auth.uid() = user_id);
    
CREATE POLICY "Usuários podem excluir seus próprios seguros" ON public.seguros
    FOR DELETE USING (auth.uid() = user_id); 