# Resolução de Erros do Brauna Finanças

## Problema: Tabelas não encontradas no Supabase

Você está recebendo erros como:
```
Erro ao carregar dados de perfis: {'code': '42P01', 'details': None, 'hint': None, 'message': 'relation "public.perfis" does not exist'}
Erro ao carregar dados de objetivos: {'code': '42P01', 'details': None, 'hint': None, 'message': 'relation "public.objetivos" does not exist'}
```

Estes erros ocorrem porque as tabelas necessárias (`perfis` e `objetivos`) ainda não foram criadas no seu banco de dados Supabase.

## Solução:

### 1. Execute o Script SQL para Criar as Tabelas

1. Faça login na sua conta do Supabase em [https://app.supabase.com/](https://app.supabase.com/)
2. Selecione o projeto que você está usando para o Brauna Finanças
3. No menu lateral, clique em "SQL Editor"
4. Clique em "New Query"
5. Cole o conteúdo do arquivo `scripts/supabase_tables.sql` no editor
6. Clique em "Run" para executar o script e criar as tabelas

### 2. Verifique se as Tabelas Foram Criadas

1. No menu lateral do Supabase, clique em "Table Editor"
2. Verifique se as tabelas `perfis`, `objetivos`, `despesas`, `investimentos`, `dividas` e `seguros` estão listadas

### 3. Reinicie o Aplicativo

1. Feche o aplicativo se ele estiver em execução
2. Execute novamente com `streamlit run app/main.py`

### 4. Configuração do Supabase

Certifique-se que seu arquivo `.env` tem as credenciais corretas do Supabase:

```
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_anon_do_supabase
```

Você pode encontrar essas informações no Supabase em:
1. Acesse seu projeto
2. Vá para "Project Settings" > "API"
3. Copie a URL e a "anon key" (chave pública)

### Suporte a Modo Offline

O aplicativo está configurado para funcionar mesmo sem conexão com o Supabase, usando armazenamento local como fallback. Mas para utilizar todas as funcionalidades, incluindo sincronização entre dispositivos, é recomendado configurar o Supabase corretamente.

## Possíveis Problemas e Soluções

### Erro de Autenticação

Se você encontrar erros relacionados à autenticação:
1. Verifique se as credenciais no arquivo `.env` estão corretas
2. No Supabase, vá para "Authentication" > "Providers" e certifique-se que o Email Auth está habilitado

### Erros de Permissão

Se você conseguir se autenticar mas não conseguir acessar os dados:
1. Verifique se as políticas RLS (Row Level Security) foram criadas corretamente
2. Execute novamente o script SQL que cria as tabelas e políticas

### Dados não são salvos

Se você conseguir autenticar, mas os dados não são salvos:
1. Verifique os logs de erro no console do aplicativo
2. Certifique-se que as tabelas foram criadas corretamente
3. Verifique se há erros de esquema (nomes de colunas incorretos)

## Contato para Suporte

Se você continuar enfrentando problemas após seguir estas instruções, entre em contato com o suporte técnico. 