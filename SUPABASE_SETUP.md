# Configuração do Supabase para Brauna Finanças

Este guia fornece instruções para configurar o Supabase para funcionar com o aplicativo Brauna Finanças.

## 1. Criar uma conta no Supabase

1. Acesse [https://supabase.com/](https://supabase.com/)
2. Clique em "Start your project" e crie uma conta ou faça login
3. Clique em "New Project" para criar um novo projeto

## 2. Configuração do Projeto

1. Dê um nome ao seu projeto (ex: "brauna-financas")
2. Escolha uma senha forte para o banco de dados
3. Selecione a região mais próxima de você
4. Clique em "Create new project"
5. Aguarde a criação do projeto (pode levar alguns minutos)

## 3. Configurar Autenticação

1. No menu lateral, vá para "Authentication" > "Providers"
2. Certifique-se que o "Email" está habilitado
3. Se quiser permitir login sem confirmação de e-mail:
   - Habilite "Enable auto confirm" (para desenvolvimento)
   - Para produção, é recomendado manter desativado para maior segurança

## 4. Criar as Tabelas do Banco de Dados

1. No menu lateral, vá para "Table Editor" ou "SQL Editor"
2. Para criar as tabelas, use o SQL Editor:
   - Clique em "SQL Editor"
   - Clique em "New Query"
   - Cole o conteúdo do arquivo `scripts/supabase_tables.sql`
   - Clique em "Run" para executar o script

O script criará as seguintes tabelas:
- `perfis`: informações dos usuários
- `objetivos`: objetivos financeiros
- `despesas`: controle de gastos
- `investimentos`: investimentos
- `dividas`: dívidas
- `seguros`: seguros

Todas as tabelas são protegidas por Row Level Security (RLS), garantindo que cada usuário só acesse seus próprios dados.

## 5. Configurar o Aplicativo para Usar o Supabase

1. No menu lateral do Supabase, vá para "Project Settings" > "API"
2. Copie o "URL" e a "anon key" (chave pública)
3. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_anon_do_supabase
```

4. Substitua `sua_url_do_supabase` e `sua_chave_anon_do_supabase` pelos valores copiados

## 6. Testando a Conexão

1. Reinicie o aplicativo
2. Tente fazer login ou registro
3. Verifique se os dados estão sendo salvos no Supabase

Se encontrar problemas:
- Verifique se as credenciais no `.env` estão corretas
- Certifique-se que o script SQL foi executado com sucesso
- Verifique se há erros no console do aplicativo

## 7. Visualizando Dados no Supabase

1. Acesse o "Table Editor" no Supabase
2. Selecione a tabela que deseja visualizar
3. Você poderá ver todos os dados inseridos pelo aplicativo

## Configurações adicionais (opcional)

### Personalizar e-mails de confirmação

1. Vá para "Authentication" > "Email Templates"
2. Personalize os modelos de e-mail para combinar com sua marca

### Configurar um domínio personalizado

Se você tiver um domínio próprio:

1. Vá para "Project Settings" > "General"
2. Configure seu domínio personalizado seguindo as instruções

### Monitoramento e análise

O Supabase oferece ferramentas para monitorar o uso:

1. Vá para "Reports" na navegação lateral
2. Explore as métricas de uso de banco de dados e autenticação

## Solução de problemas

### Problemas de autenticação

- Verifique se as chaves da API estão corretas
- Confira o log de autenticação em "Authentication" > "Logs"

### Problemas de permissão

- Verifique se as políticas RLS estão configuradas corretamente
- Teste as consultas diretamente no SQL Editor

### Problemas de conexão

- Verifique a conectividade com o Supabase
- Certifique-se de que não há bloqueios de firewall

## Recursos adicionais

- [Documentação do Supabase](https://supabase.com/docs)
- [Guia de autenticação](https://supabase.com/docs/guides/auth)
- [Guia de RLS](https://supabase.com/docs/guides/auth/row-level-security)
- [Tutoriais da comunidade](https://supabase.com/blog) 