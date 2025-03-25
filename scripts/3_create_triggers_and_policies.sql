-- Criar triggers para updated_at
DROP TRIGGER IF EXISTS set_objetivos_updated_at ON objetivos;
CREATE TRIGGER set_objetivos_updated_at
BEFORE UPDATE ON objetivos
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

DROP TRIGGER IF EXISTS set_investimentos_updated_at ON investimentos;
CREATE TRIGGER set_investimentos_updated_at
BEFORE UPDATE ON investimentos
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

DROP TRIGGER IF EXISTS set_dividas_updated_at ON dividas;
CREATE TRIGGER set_dividas_updated_at
BEFORE UPDATE ON dividas
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

DROP TRIGGER IF EXISTS set_gastos_updated_at ON gastos;
CREATE TRIGGER set_gastos_updated_at
BEFORE UPDATE ON gastos
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

DROP TRIGGER IF EXISTS set_seguros_updated_at ON seguros;
CREATE TRIGGER set_seguros_updated_at
BEFORE UPDATE ON seguros
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- Criar políticas RLS
ALTER TABLE objetivos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "objetivos_policy" ON objetivos;
CREATE POLICY "objetivos_policy" ON objetivos
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

ALTER TABLE investimentos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "investimentos_policy" ON investimentos;
CREATE POLICY "investimentos_policy" ON investimentos
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

ALTER TABLE dividas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "dividas_policy" ON dividas;
CREATE POLICY "dividas_policy" ON dividas
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

ALTER TABLE gastos ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "gastos_policy" ON gastos;
CREATE POLICY "gastos_policy" ON gastos
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);

ALTER TABLE seguros ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "seguros_policy" ON seguros;
CREATE POLICY "seguros_policy" ON seguros
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id); 