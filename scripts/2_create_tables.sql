-- Criar ou atualizar tabela de objetivos
CREATE TABLE IF NOT EXISTS public.objetivos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    titulo TEXT NOT NULL,
    nome TEXT NOT NULL,
    valor_meta DECIMAL(15,2) NOT NULL,
    valor_total DECIMAL(15,2) NOT NULL,
    valor_atual DECIMAL(15,2) DEFAULT 0,
    data_meta DATE,
    data_alvo DATE,
    data_inicio DATE DEFAULT CURRENT_DATE,
    nivel_prioridade INTEGER DEFAULT 1,
    prioridade INTEGER DEFAULT 1,
    categoria TEXT DEFAULT 'outros',
    investimentos_vinculados UUID[] DEFAULT ARRAY[]::UUID[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Criar ou atualizar tabela de investimentos
CREATE TABLE IF NOT EXISTS public.investimentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    categoria TEXT NOT NULL,
    valor_inicial DECIMAL(15,2) NOT NULL,
    valor_atual DECIMAL(15,2) NOT NULL,
    data_inicio DATE NOT NULL,
    data_vencimento DATE,
    rentabilidade_anual DECIMAL(10,4),
    instituicao TEXT DEFAULT '',
    notas TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Criar ou atualizar tabela de dividas
CREATE TABLE IF NOT EXISTS public.dividas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    valor_total DECIMAL(15,2) NOT NULL,
    valor_inicial DECIMAL(15,2) NOT NULL,
    valor_restante DECIMAL(15,2) NOT NULL,
    valor_atual DECIMAL(15,2) NOT NULL,
    parcelas_total INTEGER,
    parcelas INTEGER,
    parcelas_pagas INTEGER DEFAULT 0,
    data_inicio DATE NOT NULL,
    data_vencimento DATE,
    tipo TEXT DEFAULT 'outros',
    taxa_juros DECIMAL(10,4) DEFAULT 0,
    notas TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Criar ou atualizar tabela de gastos
CREATE TABLE IF NOT EXISTS public.gastos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    descricao TEXT NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    data DATE NOT NULL,
    data_gasto DATE NOT NULL,
    tipo TEXT DEFAULT 'outros',
    categoria TEXT DEFAULT 'outros',
    notas TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Criar ou atualizar tabela de seguros
CREATE TABLE IF NOT EXISTS public.seguros (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users NOT NULL,
    tipo TEXT NOT NULL,
    descricao TEXT NOT NULL,
    valor_premio DECIMAL(15,2) NOT NULL,
    valor_cobertura DECIMAL(15,2),
    data_inicio DATE NOT NULL,
    data_contratacao DATE NOT NULL,
    data_vencimento DATE,
    data_renovacao DATE,
    seguradora TEXT,
    notas TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
); 