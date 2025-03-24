-- Tabelas para o sistema Brauna Finanças
-- Execute este script no editor SQL do Supabase

-- Tabela de perfis de usuários
CREATE TABLE IF NOT EXISTS public.perfis (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  nome TEXT,
  email TEXT,
  renda_mensal DECIMAL(15,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ative a segurança por linha (RLS - Row Level Security)
ALTER TABLE public.perfis ENABLE ROW LEVEL SECURITY;

-- Política para permitir acesso apenas aos dados do próprio usuário
CREATE POLICY "Usuários podem ver apenas seus próprios perfis" ON public.perfis
  FOR ALL USING (auth.uid() = user_id);

-- Tabela de objetivos financeiros
CREATE TABLE IF NOT EXISTS public.objetivos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  titulo TEXT NOT NULL,
  descricao TEXT,
  valor_meta DECIMAL(15,2) NOT NULL,
  valor_atual DECIMAL(15,2) DEFAULT 0,
  data_inicio DATE DEFAULT CURRENT_DATE,
  data_meta DATE,
  data_alvo DATE,
  categoria TEXT,
  icone TEXT DEFAULT '🎯',
  cor TEXT DEFAULT '#1E88E5',
  concluido BOOLEAN DEFAULT FALSE,
  prioridade INTEGER DEFAULT 1,
  investimentos_vinculados JSONB DEFAULT '[]',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  nome TEXT
);

-- Ative a segurança por linha (RLS)
ALTER TABLE public.objetivos ENABLE ROW LEVEL SECURITY;

-- Política para permitir acesso apenas aos dados do próprio usuário
CREATE POLICY "Usuários podem ver apenas seus próprios objetivos" ON public.objetivos
  FOR ALL USING (auth.uid() = user_id);

-- Mapear 'titulo' para 'nome' para compatibilidade
UPDATE public.objetivos SET nome = titulo WHERE nome IS NULL AND titulo IS NOT NULL;

-- Mapear 'valor_meta' para compatibilidade com 'valor_total'
ALTER TABLE public.objetivos ADD COLUMN IF NOT EXISTS valor_total DECIMAL(15,2);
UPDATE public.objetivos SET valor_total = valor_meta WHERE valor_total IS NULL AND valor_meta IS NOT NULL;

-- Tabela de despesas/gastos
CREATE TABLE IF NOT EXISTS public.gastos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  descricao TEXT NOT NULL,
  valor DECIMAL(15,2) NOT NULL,
  data DATE DEFAULT CURRENT_DATE,
  categoria TEXT,
  tipo TEXT,
  metodo_pagamento TEXT,
  fixa BOOLEAN DEFAULT FALSE,
  notas TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ative a segurança por linha (RLS)
ALTER TABLE public.gastos ENABLE ROW LEVEL SECURITY;

-- Política para permitir acesso apenas aos dados do próprio usuário
CREATE POLICY "Usuários podem ver apenas seus próprias despesas" ON public.gastos
  FOR ALL USING (auth.uid() = user_id);

-- Tabela de investimentos
CREATE TABLE IF NOT EXISTS public.investimentos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  nome TEXT NOT NULL,
  tipo TEXT,
  categoria TEXT,
  valor_inicial DECIMAL(15,2) NOT NULL,
  valor_atual DECIMAL(15,2),
  rendimento_mensal DECIMAL(8,4),
  data_inicio DATE DEFAULT CURRENT_DATE,
  data_vencimento DATE,
  instituicao TEXT,
  notas TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ative a segurança por linha (RLS)
ALTER TABLE public.investimentos ENABLE ROW LEVEL SECURITY;

-- Política para permitir acesso apenas aos dados do próprio usuário
CREATE POLICY "Usuários podem ver apenas seus próprios investimentos" ON public.investimentos
  FOR ALL USING (auth.uid() = user_id);

-- Tabela de dívidas
CREATE TABLE IF NOT EXISTS public.dividas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  descricao TEXT NOT NULL,
  valor_total DECIMAL(15,2) NOT NULL,
  valor_restante DECIMAL(15,2),
  valor_inicial DECIMAL(15,2),
  valor_atual DECIMAL(15,2),
  tipo TEXT,
  parcelas INTEGER,
  taxa_juros DECIMAL(8,4),
  data_inicio DATE DEFAULT CURRENT_DATE,
  data_vencimento DATE,
  parcelas_total INTEGER,
  parcelas_pagas INTEGER DEFAULT 0,
  credor TEXT,
  detalhes TEXT,
  notas TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ative a segurança por linha (RLS)
ALTER TABLE public.dividas ENABLE ROW LEVEL SECURITY;

-- Política para permitir acesso apenas aos dados do próprio usuário
CREATE POLICY "Usuários podem ver apenas suas próprias dívidas" ON public.dividas
  FOR ALL USING (auth.uid() = user_id);

-- Tabela de seguros
CREATE TABLE IF NOT EXISTS public.seguros (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  tipo TEXT NOT NULL,
  descricao TEXT NOT NULL,
  valor_premio DECIMAL(15,2) NOT NULL,
  valor_cobertura DECIMAL(15,2),
  data_inicio DATE DEFAULT CURRENT_DATE,
  data_vencimento DATE,
  seguradora TEXT,
  numero_apolice TEXT,
  beneficiarios TEXT,
  notas TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ative a segurança por linha (RLS)
ALTER TABLE public.seguros ENABLE ROW LEVEL SECURITY;

-- Política para permitir acesso apenas aos dados do próprio usuário
CREATE POLICY "Usuários podem ver apenas seus próprios seguros" ON public.seguros
  FOR ALL USING (auth.uid() = user_id); 