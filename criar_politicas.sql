-- Políticas para tabela gastos
CREATE POLICY "Enable read for users based on user_id" ON gastos
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Enable insert for users based on user_id" ON gastos
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for users based on user_id" ON gastos
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Enable delete for users based on user_id" ON gastos
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para tabela receitas
CREATE POLICY "Enable read for users based on user_id" ON receitas
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Enable insert for users based on user_id" ON receitas
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for users based on user_id" ON receitas
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Enable delete for users based on user_id" ON receitas
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para tabela investimentos
CREATE POLICY "Enable read for users based on user_id" ON investimentos
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Enable insert for users based on user_id" ON investimentos
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for users based on user_id" ON investimentos
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Enable delete for users based on user_id" ON investimentos
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para tabela metas
CREATE POLICY "Enable read for users based on user_id" ON metas
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Enable insert for users based on user_id" ON metas
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for users based on user_id" ON metas
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Enable delete for users based on user_id" ON metas
    FOR DELETE USING (auth.uid() = user_id);

-- Políticas para tabela dividas
CREATE POLICY "Enable read for users based on user_id" ON dividas
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Enable insert for users based on user_id" ON dividas
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Enable update for users based on user_id" ON dividas
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Enable delete for users based on user_id" ON dividas
    FOR DELETE USING (auth.uid() = user_id); 