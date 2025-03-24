# Guia de Implantação do Brauna Finanças

Este guia detalha os passos necessários para implantar o aplicativo Brauna Finanças no Streamlit Cloud, incluindo a configuração do banco de dados Supabase para autenticação e armazenamento de dados.

## Pré-requisitos

Antes de iniciar a implantação, você precisará:

1. Uma conta no [GitHub](https://github.com/)
2. Uma conta no [Streamlit Cloud](https://streamlit.io/cloud)
3. Uma conta no [Supabase](https://supabase.com/) (gratuita ou paga)
4. O código-fonte do Brauna Finanças

## Configuração do Supabase

O Supabase é uma plataforma de banco de dados PostgreSQL como serviço que fornece autenticação e armazenamento de dados para o aplicativo.

### Passo 1: Criar um projeto no Supabase

1. Acesse [https://app.supabase.com/](https://app.supabase.com/) e faça login
2. Clique em "New Project" e preencha:
   - **Nome do projeto**: "brauna-financas" (ou outro nome de sua escolha)
   - **Database Password**: Crie uma senha segura
   - **Region**: Escolha a região mais próxima de seus usuários
3. Clique em "Create New Project"

### Passo 2: Criar as tabelas do banco de dados

1. No dashboard do Supabase, vá para a seção "SQL Editor"
2. Clique em "New Query"
3. Cole o conteúdo do arquivo `migrations/create_tables.sql` 
4. Clique em "Run" para executar o script e criar as tabelas

### Passo 3: Configurar a autenticação

1. No dashboard do Supabase, vá para "Authentication" > "Providers"
2. Garanta que "Email" esteja habilitado
3. Você pode ajustar as configurações de acordo com suas preferências:
   - **Disable Signup**: Desative se quiser limitar quem pode criar contas
   - **Confirmação de Email**: Recomendado habilitar em produção

### Passo 4: Obter as credenciais de API

1. No dashboard do Supabase, vá para "Settings" > "API"
2. Você precisará das seguintes informações:
   - **URL**: O URL do projeto (ex: `https://abcdefghijklm.supabase.co`)
   - **anon key**: A chave pública para operações do cliente
   - **service_role key**: A chave com permissões administrativas (mantenha segura)

## Implantação no Streamlit Cloud

### Passo 1: Preparar o código para implantação

1. Certifique-se de que todo o código está funcionando localmente
2. Faça commit do código para um repositório GitHub (público ou privado)
3. NÃO inclua arquivos com informações sensíveis como `.env` ou `.streamlit/secrets.toml`

### Passo 2: Configurar o aplicativo no Streamlit Cloud

1. Acesse [https://share.streamlit.io/](https://share.streamlit.io/) e faça login
2. Clique em "New app"
3. Selecione seu repositório GitHub
4. Insira:
   - **Repository**: URL do seu repositório
   - **Branch**: `main` (ou a branch que você deseja implantar)
   - **Main file path**: `run.py`

### Passo 3: Configurar secrets no Streamlit Cloud

1. Depois de criar o aplicativo, vá para "Settings" > "Secrets"
2. Clique em "Add secrets"
3. Adicione o seguinte conteúdo, substituindo com suas credenciais do Supabase:

```toml
[supabase]
url = "https://seu-projeto.supabase.co"
key = "sua-chave-anon-key" 
service_key = "sua-chave-service-role"

[app]
name = "Brauna Finanças"
version = "1.0.0"
environment = "production"
```

4. Clique em "Save"

### Passo 4: Verificar a implantação

1. Após salvar as secrets, o Streamlit Cloud irá reimplantar automaticamente seu aplicativo
2. Acesse seu aplicativo pela URL fornecida pelo Streamlit Cloud
3. Teste o registro de usuário e login para garantir que a autenticação está funcionando
4. Verifique se todas as funcionalidades estão operando corretamente

## Estrutura de Dados do Supabase

O Brauna Finanças utiliza as seguintes tabelas no Supabase:

1. **perfis**: Armazena informações básicas dos usuários
2. **gastos**: Registra todas as despesas dos usuários
3. **investimentos**: Armazena os investimentos dos usuários
4. **dividas**: Registra as dívidas dos usuários
5. **objetivos**: Armazena os objetivos financeiros dos usuários
6. **seguros**: Registra os seguros dos usuários

Todas as tabelas incluem Row Level Security (RLS) para garantir que os usuários só possam acessar seus próprios dados.

## Resolução de Problemas

### Problemas de autenticação:
- Verifique se as credenciais do Supabase estão corretas nas secrets do Streamlit
- Consulte os logs de autenticação no painel do Supabase

### Erro 500 ou falhas na API:
- Verifique a configuração das tabelas no Supabase
- Confirme se as políticas de RLS estão configuradas corretamente

### Dados não aparecem:
- Verifique se o usuário está autenticado corretamente
- Verifique se os dados estão sendo salvos com o ID de usuário correto

## Recursos Adicionais

- [Documentação do Streamlit](https://docs.streamlit.io/)
- [Documentação do Supabase](https://supabase.com/docs)
- [GitHub do Brauna Finanças](https://github.com/seu-usuario/brauna-financas)

## Suporte

Para suporte adicional, entre em contato com o desenvolvedor em email@exemplo.com 