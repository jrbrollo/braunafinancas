-- Script SQL completo e consolidado para o sistema Brauna Finanças
-- Este script contém todas as tabelas, colunas e políticas de segurança necessárias
-- Versão: 1.0.1 - Data: 2025-03-23 (Revisado)

-- Ativar a extensão para gerar UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============== VERIFICAÇÃO INICIAL DE TABELAS =================
-- Verificar se todas as tabelas necessárias existem e criar se não existirem
DO $$
BEGIN
    -- Verificar e criar a tabela perfis
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'perfis') THEN
        CREATE TABLE public.perfis (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            nome TEXT,
            email TEXT,
            renda_mensal DECIMAL(15,2) DEFAULT 0,
            avatar_url TEXT,
            tema TEXT DEFAULT 'claro',
            moeda TEXT DEFAULT 'BRL',
            configuracoes JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END IF;

    -- Verificar e criar a tabela objetivos
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'objetivos') THEN
        CREATE TABLE public.objetivos (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            titulo TEXT,
            descricao TEXT,
            valor_meta DECIMAL(15,2),
            data_meta DATE,
            categoria TEXT,
            icone TEXT DEFAULT '🎯',
            cor TEXT DEFAULT '#1E88E5',
            concluido BOOLEAN DEFAULT FALSE,
            prioridade INTEGER DEFAULT 1,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END IF;

    -- Verificar e criar a tabela gastos
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'gastos') THEN
        CREATE TABLE public.gastos (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            descricao TEXT NOT NULL,
            valor DECIMAL(15,2) NOT NULL,
            data DATE DEFAULT CURRENT_DATE,
            categoria TEXT,
            tipo TEXT,
            metodo_pagamento TEXT,
            notas TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END IF;

    -- Verificar e criar a tabela investimentos
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'investimentos') THEN
        CREATE TABLE public.investimentos (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            nome TEXT NOT NULL,
            valor_inicial DECIMAL(15,2) NOT NULL,
            categoria TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END IF;

    -- Verificar e criar a tabela dividas
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'dividas') THEN
        CREATE TABLE public.dividas (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            descricao TEXT NOT NULL,
            valor_total DECIMAL(15,2) NOT NULL,
            valor_restante DECIMAL(15,2),
            taxa_juros DECIMAL(8,4),
            data_inicio DATE DEFAULT CURRENT_DATE,
            data_vencimento DATE,
            credor TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END IF;

    -- Verificar e criar a tabela seguros
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'seguros') THEN
        CREATE TABLE public.seguros (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            tipo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor_premio DECIMAL(15,2) NOT NULL,
            valor_cobertura DECIMAL(15,2),
            data_inicio DATE DEFAULT CURRENT_DATE,
            data_vencimento DATE,
            seguradora TEXT,
            beneficiarios TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END IF;
END $$;

-- =============== ADIÇÃO DE COLUNAS FALTANTES =================
-- Adicionar todas as colunas que podem estar faltando nas tabelas
DO $$
BEGIN
    -- Adicionar colunas na tabela perfis
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'perfis' AND column_name = 'configuracoes') THEN
        ALTER TABLE public.perfis ADD COLUMN configuracoes JSONB DEFAULT '{}';
    END IF;

    -- Adicionar colunas na tabela objetivos
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'nome') THEN
        ALTER TABLE public.objetivos ADD COLUMN nome TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'valor_total') THEN
        ALTER TABLE public.objetivos ADD COLUMN valor_total DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'valor_atual') THEN
        ALTER TABLE public.objetivos ADD COLUMN valor_atual DECIMAL(15,2) DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'data_inicio') THEN
        ALTER TABLE public.objetivos ADD COLUMN data_inicio DATE DEFAULT CURRENT_DATE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'data_alvo') THEN
        ALTER TABLE public.objetivos ADD COLUMN data_alvo DATE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'investimentos_vinculados') THEN
        ALTER TABLE public.objetivos ADD COLUMN investimentos_vinculados JSONB DEFAULT '[]';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'taxa_retorno') THEN
        ALTER TABLE public.objetivos ADD COLUMN taxa_retorno DECIMAL(8,4) DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'progresso') THEN
        ALTER TABLE public.objetivos ADD COLUMN progresso DECIMAL(5,2) DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'objetivos' AND column_name = 'prazo_meses') THEN
        ALTER TABLE public.objetivos ADD COLUMN prazo_meses INTEGER;
    END IF;
    
    -- Adicionar colunas na tabela gastos
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'gastos' AND column_name = 'tipo') THEN
        ALTER TABLE public.gastos ADD COLUMN tipo TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'gastos' AND column_name = 'fixa') THEN
        ALTER TABLE public.gastos ADD COLUMN fixa BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'gastos' AND column_name = 'recorrente') THEN
        ALTER TABLE public.gastos ADD COLUMN recorrente BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'gastos' AND column_name = 'periodo_recorrencia') THEN
        ALTER TABLE public.gastos ADD COLUMN periodo_recorrencia TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'gastos' AND column_name = 'tags') THEN
        ALTER TABLE public.gastos ADD COLUMN tags TEXT[];
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'gastos' AND column_name = 'comprovante_url') THEN
        ALTER TABLE public.gastos ADD COLUMN comprovante_url TEXT;
    END IF;
    
    -- Adicionar colunas na tabela investimentos
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'tipo') THEN
        ALTER TABLE public.investimentos ADD COLUMN tipo TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'valor_atual') THEN
        ALTER TABLE public.investimentos ADD COLUMN valor_atual DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'rendimento_mensal') THEN
        ALTER TABLE public.investimentos ADD COLUMN rendimento_mensal DECIMAL(8,4);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'rendimento_anual') THEN
        ALTER TABLE public.investimentos ADD COLUMN rendimento_anual DECIMAL(8,4);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'data_inicio') THEN
        ALTER TABLE public.investimentos ADD COLUMN data_inicio DATE DEFAULT CURRENT_DATE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'data_vencimento') THEN
        ALTER TABLE public.investimentos ADD COLUMN data_vencimento DATE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'data_resgate') THEN
        ALTER TABLE public.investimentos ADD COLUMN data_resgate DATE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'instituicao') THEN
        ALTER TABLE public.investimentos ADD COLUMN instituicao TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'risco') THEN
        ALTER TABLE public.investimentos ADD COLUMN risco TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'liquidez') THEN
        ALTER TABLE public.investimentos ADD COLUMN liquidez TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'objetivo_id') THEN
        ALTER TABLE public.investimentos ADD COLUMN objetivo_id UUID;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'ativo') THEN
        ALTER TABLE public.investimentos ADD COLUMN ativo BOOLEAN DEFAULT TRUE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'investimentos' AND column_name = 'notas') THEN
        ALTER TABLE public.investimentos ADD COLUMN notas TEXT;
    END IF;
    
    -- Adicionar colunas na tabela dividas
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dividas' AND column_name = 'valor_inicial') THEN
        ALTER TABLE public.dividas ADD COLUMN valor_inicial DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dividas' AND column_name = 'valor_atual') THEN
        ALTER TABLE public.dividas ADD COLUMN valor_atual DECIMAL(15,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dividas' AND column_name = 'tipo') THEN
        ALTER TABLE public.dividas ADD COLUMN tipo TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dividas' AND column_name = 'parcelas') THEN
        ALTER TABLE public.dividas ADD COLUMN parcelas INTEGER;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dividas' AND column_name = 'parcelas_total') THEN
        ALTER TABLE public.dividas ADD COLUMN parcelas_total INTEGER;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dividas' AND column_name = 'parcelas_pagas') THEN
        ALTER TABLE public.dividas ADD COLUMN parcelas_pagas INTEGER DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dividas' AND column_name = 'detalhes') THEN
        ALTER TABLE public.dividas ADD COLUMN detalhes TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'dividas' AND column_name = 'notas') THEN
        ALTER TABLE public.dividas ADD COLUMN notas TEXT;
    END IF;
    
    -- Adicionar colunas na tabela seguros
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'seguros' AND column_name = 'numero_apolice') THEN
        ALTER TABLE public.seguros ADD COLUMN numero_apolice TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'seguros' AND column_name = 'notas') THEN
        ALTER TABLE public.seguros ADD COLUMN notas TEXT;
    END IF;
END $$;

-- =============== CONFIGURAR SEGURANÇA E ÍNDICES =================
-- Ativar segurança por linha e adicionar índices
DO $$
BEGIN
    -- Perfis: segurança e índices
    ALTER TABLE public.perfis ENABLE ROW LEVEL SECURITY;

    -- Objetivos: segurança e índices
    ALTER TABLE public.objetivos ENABLE ROW LEVEL SECURITY;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_objetivos_user_id') THEN
        CREATE INDEX idx_objetivos_user_id ON public.objetivos(user_id);
    END IF;

    -- Gastos: segurança e índices
    ALTER TABLE public.gastos ENABLE ROW LEVEL SECURITY;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_gastos_user_id') THEN
        CREATE INDEX idx_gastos_user_id ON public.gastos(user_id);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_gastos_data') THEN
        CREATE INDEX idx_gastos_data ON public.gastos(data);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_gastos_categoria') THEN
        CREATE INDEX idx_gastos_categoria ON public.gastos(categoria);
    END IF;

    -- Investimentos: segurança e índices
    ALTER TABLE public.investimentos ENABLE ROW LEVEL SECURITY;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_investimentos_user_id') THEN
        CREATE INDEX idx_investimentos_user_id ON public.investimentos(user_id);
    END IF;

    -- Dívidas: segurança e índices
    ALTER TABLE public.dividas ENABLE ROW LEVEL SECURITY;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_dividas_user_id') THEN
        CREATE INDEX idx_dividas_user_id ON public.dividas(user_id);
    END IF;

    -- Seguros: segurança e índices
    ALTER TABLE public.seguros ENABLE ROW LEVEL SECURITY;
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_seguros_user_id') THEN
        CREATE INDEX idx_seguros_user_id ON public.seguros(user_id);
    END IF;
END $$;

-- =============== CONFIGURAR POLÍTICAS DE SEGURANÇA =================
-- Remover e criar políticas de segurança
DO $$
BEGIN
    -- Perfis: políticas
    DROP POLICY IF EXISTS "Usuários podem ver apenas seus próprios perfis" ON public.perfis;
    CREATE POLICY "Usuários podem ver apenas seus próprios perfis" ON public.perfis
        FOR ALL USING (auth.uid() = user_id);

    -- Objetivos: políticas
    DROP POLICY IF EXISTS "Usuários podem ver apenas seus próprios objetivos" ON public.objetivos;
    CREATE POLICY "Usuários podem ver apenas seus próprios objetivos" ON public.objetivos
        FOR ALL USING (auth.uid() = user_id);

    -- Gastos: políticas
    DROP POLICY IF EXISTS "Usuários podem ver apenas seus próprias despesas" ON public.gastos;
    CREATE POLICY "Usuários podem ver apenas seus próprias despesas" ON public.gastos
        FOR ALL USING (auth.uid() = user_id);

    -- Investimentos: políticas
    DROP POLICY IF EXISTS "Usuários podem ver apenas seus próprios investimentos" ON public.investimentos;
    CREATE POLICY "Usuários podem ver apenas seus próprios investimentos" ON public.investimentos
        FOR ALL USING (auth.uid() = user_id);

    -- Dívidas: políticas
    DROP POLICY IF EXISTS "Usuários podem ver apenas suas próprias dívidas" ON public.dividas;
    CREATE POLICY "Usuários podem ver apenas suas próprias dívidas" ON public.dividas
        FOR ALL USING (auth.uid() = user_id);

    -- Seguros: políticas
    DROP POLICY IF EXISTS "Usuários podem ver apenas seus próprios seguros" ON public.seguros;
    CREATE POLICY "Usuários podem ver apenas seus próprios seguros" ON public.seguros
        FOR ALL USING (auth.uid() = user_id);
END $$;

-- =============== CONFIGURAR TRIGGERS =================
-- Função para atualizar o timestamp de atualização
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Triggers para cada tabela
DO $$
BEGIN
    -- Perfis: trigger
    DROP TRIGGER IF EXISTS set_perfis_updated_at ON perfis;
    CREATE TRIGGER set_perfis_updated_at
    BEFORE UPDATE ON perfis
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

    -- Objetivos: trigger
    DROP TRIGGER IF EXISTS set_objetivos_updated_at ON objetivos;
    CREATE TRIGGER set_objetivos_updated_at
    BEFORE UPDATE ON objetivos
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

    -- Gastos: trigger
    DROP TRIGGER IF EXISTS set_gastos_updated_at ON gastos;
    CREATE TRIGGER set_gastos_updated_at
    BEFORE UPDATE ON gastos
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

    -- Investimentos: trigger
    DROP TRIGGER IF EXISTS set_investimentos_updated_at ON investimentos;
    CREATE TRIGGER set_investimentos_updated_at
    BEFORE UPDATE ON investimentos
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

    -- Dividas: trigger
    DROP TRIGGER IF EXISTS set_dividas_updated_at ON dividas;
    CREATE TRIGGER set_dividas_updated_at
    BEFORE UPDATE ON dividas
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

    -- Seguros: trigger
    DROP TRIGGER IF EXISTS set_seguros_updated_at ON seguros;
    CREATE TRIGGER set_seguros_updated_at
    BEFORE UPDATE ON seguros
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();
END $$;

-- =============== MAPEAMENTOS DE COMPATIBILIDADE =================
-- Mapeamentos para garantir que campos equivalentes estejam preenchidos
DO $$
BEGIN
    -- Objetivos: mapeamentos
    UPDATE public.objetivos SET nome = titulo WHERE nome IS NULL AND titulo IS NOT NULL;
    UPDATE public.objetivos SET titulo = nome WHERE titulo IS NULL AND nome IS NOT NULL;
    UPDATE public.objetivos SET valor_total = valor_meta WHERE valor_total IS NULL AND valor_meta IS NOT NULL;
    UPDATE public.objetivos SET valor_meta = valor_total WHERE valor_meta IS NULL AND valor_total IS NOT NULL;
    UPDATE public.objetivos SET data_alvo = data_meta WHERE data_alvo IS NULL AND data_meta IS NOT NULL;
    UPDATE public.objetivos SET data_meta = data_alvo WHERE data_meta IS NULL AND data_alvo IS NOT NULL;

    -- Dívidas: mapeamentos
    UPDATE public.dividas SET valor_atual = valor_restante WHERE valor_atual IS NULL AND valor_restante IS NOT NULL;
    UPDATE public.dividas SET valor_restante = valor_atual WHERE valor_restante IS NULL AND valor_atual IS NOT NULL;
    UPDATE public.dividas SET valor_inicial = valor_total WHERE valor_inicial IS NULL AND valor_total IS NOT NULL;
    UPDATE public.dividas SET parcelas_total = parcelas WHERE parcelas_total IS NULL AND parcelas IS NOT NULL;
    UPDATE public.dividas SET parcelas = parcelas_total WHERE parcelas IS NULL AND parcelas_total IS NOT NULL;
END $$; 