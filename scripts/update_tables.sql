-- Script para atualizar as tabelas do sistema
DO $$
BEGIN
    -- Atualizar tabela de objetivos
    IF NOT EXISTS (
        SELECT FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'objetivos'
    ) THEN
        CREATE TABLE public.objetivos (
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
    ELSE
        -- Adicionar colunas que podem estar faltando
        BEGIN ALTER TABLE public.objetivos ADD COLUMN titulo TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.objetivos ADD COLUMN nome TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.objetivos ADD COLUMN valor_meta DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.objetivos ADD COLUMN valor_total DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.objetivos ADD COLUMN valor_atual DECIMAL(15,2) DEFAULT 0; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.objetivos ADD COLUMN data_meta DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.objetivos ADD COLUMN data_alvo DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.objetivos ADD COLUMN nivel_prioridade INTEGER DEFAULT 1; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.objetivos ADD COLUMN prioridade INTEGER DEFAULT 1; EXCEPTION WHEN duplicate_column THEN END;
    END IF;

    -- Atualizar tabela de investimentos
    IF NOT EXISTS (
        SELECT FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'investimentos'
    ) THEN
        CREATE TABLE public.investimentos (
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
    ELSE
        -- Adicionar colunas que podem estar faltando
        BEGIN ALTER TABLE public.investimentos ADD COLUMN nome TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN tipo TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN categoria TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN valor_inicial DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN valor_atual DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN data_inicio DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN data_vencimento DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN rentabilidade_anual DECIMAL(10,4); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN instituicao TEXT DEFAULT ''; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.investimentos ADD COLUMN notas TEXT DEFAULT ''; EXCEPTION WHEN duplicate_column THEN END;
    END IF;

    -- Atualizar tabela de dividas
    IF NOT EXISTS (
        SELECT FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'dividas'
    ) THEN
        CREATE TABLE public.dividas (
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
    ELSE
        -- Adicionar colunas que podem estar faltando
        BEGIN ALTER TABLE public.dividas ADD COLUMN nome TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN descricao TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN valor_total DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN valor_inicial DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN valor_restante DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN valor_atual DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN parcelas_total INTEGER; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN parcelas INTEGER; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN parcelas_pagas INTEGER DEFAULT 0; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.dividas ADD COLUMN taxa_juros DECIMAL(10,4) DEFAULT 0; EXCEPTION WHEN duplicate_column THEN END;
    END IF;

    -- Atualizar tabela de gastos
    IF NOT EXISTS (
        SELECT FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'gastos'
    ) THEN
        CREATE TABLE public.gastos (
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
    ELSE
        -- Adicionar colunas que podem estar faltando
        BEGIN ALTER TABLE public.gastos ADD COLUMN descricao TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.gastos ADD COLUMN valor DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.gastos ADD COLUMN data DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.gastos ADD COLUMN data_gasto DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.gastos ADD COLUMN tipo TEXT DEFAULT 'outros'; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.gastos ADD COLUMN categoria TEXT DEFAULT 'outros'; EXCEPTION WHEN duplicate_column THEN END;
    END IF;

    -- Atualizar tabela de seguros
    IF NOT EXISTS (
        SELECT FROM pg_tables 
        WHERE schemaname = 'public' AND tablename = 'seguros'
    ) THEN
        CREATE TABLE public.seguros (
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
    ELSE
        -- Adicionar colunas que podem estar faltando
        BEGIN ALTER TABLE public.seguros ADD COLUMN tipo TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.seguros ADD COLUMN descricao TEXT; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.seguros ADD COLUMN valor_premio DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.seguros ADD COLUMN valor_cobertura DECIMAL(15,2); EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.seguros ADD COLUMN data_inicio DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.seguros ADD COLUMN data_contratacao DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.seguros ADD COLUMN data_vencimento DATE; EXCEPTION WHEN duplicate_column THEN END;
        BEGIN ALTER TABLE public.seguros ADD COLUMN data_renovacao DATE; EXCEPTION WHEN duplicate_column THEN END;
    END IF;

    -- Criar ou atualizar triggers para updated_at
    FOR table_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('objetivos', 'investimentos', 'dividas', 'gastos', 'seguros')
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS set_%I_updated_at ON %I;
            CREATE TRIGGER set_%I_updated_at
            BEFORE UPDATE ON %I
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_column();
        ', table_name, table_name, table_name, table_name);
    END LOOP;

    -- Criar função para atualizar updated_at se não existir
    IF NOT EXISTS (SELECT FROM pg_proc WHERE proname = 'update_modified_column') THEN
        CREATE OR REPLACE FUNCTION update_modified_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = timezone('utc'::text, now());
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    END IF;

    -- Criar políticas RLS para todas as tabelas
    FOR table_name IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename IN ('objetivos', 'investimentos', 'dividas', 'gastos', 'seguros')
    LOOP
        EXECUTE format('
            ALTER TABLE %I ENABLE ROW LEVEL SECURITY;
            
            DROP POLICY IF EXISTS "%I_policy" ON %I;
            CREATE POLICY "%I_policy" ON %I
            FOR ALL
            USING (auth.uid() = user_id)
            WITH CHECK (auth.uid() = user_id);
        ', table_name, table_name, table_name, table_name, table_name);
    END LOOP;

END $$; 