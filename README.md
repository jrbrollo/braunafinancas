# Brauna Finanças - Gerenciador Financeiro Pessoal

<p align="center">
  <img src="app/static/brauna_logo.png" alt="Brauna Finanças Logo" width="200"/>
</p>

Brauna Finanças é um aplicativo de gerenciamento financeiro pessoal desenvolvido em Python com Streamlit, projetado para ajudar na organização das finanças pessoais com uma interface intuitiva e funcionalidades completas.

## 🌟 Recursos

- **Autenticação de Usuários**: Sistema completo de login, registro e recuperação de senha
- **Dashboard Financeiro**: Visão geral da sua saúde financeira com gráficos e indicadores
- **Controle de Gastos**: Acompanhe e categorize despesas mensais
- **Gestão de Investimentos**: Monitore seu portfólio de investimentos
- **Controle de Dívidas**: Acompanhe dívidas e planeje estratégias de pagamento
- **Gerenciamento de Seguros**: Organize suas apólices e datas de vencimento
- **Objetivos Financeiros**: Defina e acompanhe metas financeiras
- **Multi-usuário**: Cada usuário tem acesso apenas aos seus próprios dados
- **Backup e Restauração**: Exporte e importe seus dados com facilidade
- **Tema Claro/Escuro**: Interface personalizável para seu conforto visual

## 📋 Requisitos

- Python 3.8 ou superior
- Bibliotecas: 
  - streamlit
  - pandas
  - plotly
  - numpy
  - supabase
  - python-dotenv

## 🔌 Tecnologias Utilizadas

- **Frontend**: Streamlit para interface interativa
- **Backend**: Supabase para autenticação e armazenamento de dados
- **Banco de Dados**: PostgreSQL (fornecido pelo Supabase)
- **Visualização de Dados**: Plotly e Matplotlib
- **Análise de Dados**: Pandas e NumPy

## 🚀 Instalação e Execução

### Windows

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/brauna-financas.git
   cd brauna-financas
   ```

2. Execute o script de instalação:
   ```
   pip install -r requirements.txt
   ```

3. Configure o Supabase:
   - Crie uma conta no [Supabase](https://supabase.com)
   - Siga as instruções em [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
   - Crie um arquivo `.env` baseado no `.env.example`

4. Inicie a aplicação com o arquivo batch:
   ```
   abrir_app.bat
   ```

### Linux/Mac

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/brauna-financas.git
   cd brauna-financas
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure o Supabase:
   - Crie uma conta no [Supabase](https://supabase.com)
   - Siga as instruções em [SUPABASE_SETUP.md](SUPABASE_SETUP.md)
   - Crie um arquivo `.env` baseado no `.env.example`

4. Execute a aplicação:
   ```
   streamlit run run.py
   ```

## ☁️ Deployment no Streamlit Cloud

Este aplicativo pode ser facilmente implantado no Streamlit Cloud para acesso online:

1. Crie uma conta no [Streamlit Cloud](https://streamlit.io/cloud)
2. Conecte sua conta ao GitHub
3. Selecione este repositório e configure o arquivo principal como `run.py`
4. Adicione as secrets do Supabase nas configurações
5. Clique em "Deploy" e aguarde a implantação ser concluída

Para um guia detalhado de deployment, consulte o arquivo [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) incluído neste repositório.

## 🔧 Estrutura do Projeto

```
brauna-financas/
├── app/
│   ├── data/
│   │   ├── data_handler.py   # Gerenciamento de dados
│   │   └── init_data.py      # Inicialização de dados de exemplo
│   ├── database/
│   │   └── supabase_client.py # Cliente e funções do Supabase
│   ├── static/
│   │   ├── styles.css        # Estilos CSS
│   │   └── brauna_logo.png   # Logo do aplicativo
│   ├── ui/
│   │   ├── auth_page.py      # Interface de autenticação
│   │   ├── dashboard_page.py # Interface do dashboard
│   │   ├── gastos_page.py    # Interface de controle de gastos
│   │   └── ...               # Outras interfaces
│   └── main.py               # Ponto de entrada da aplicação
├── migrations/
│   └── create_tables.sql     # Script SQL para criar tabelas no Supabase
├── .streamlit/
│   └── secrets.toml.example  # Exemplo de configuração de secrets
├── docs/
│   └── test_plan.md          # Plano de testes
├── .env.example              # Exemplo de variáveis de ambiente
├── abrir_app.bat             # Script de inicialização para Windows
├── requirements.txt          # Dependências do projeto
├── LICENSE                   # Licença do software
├── DEPLOYMENT_GUIDE.md       # Guia de implantação
├── SUPABASE_SETUP.md         # Guia de configuração do Supabase
└── README.md                 # Este arquivo
```

## 🛡️ Segurança e Privacidade

- **Autenticação Segura**: Gerenciada pelo Supabase com práticas modernas
- **Row Level Security**: Cada usuário só pode acessar seus próprios dados
- **Dados Criptografados**: Comunicação segura via HTTPS
- **Flexível**: Pode funcionar em modo offline com armazenamento local ou online com persistência no Supabase

### Modos de Operação

- **Modo Local**: Dados armazenados em arquivos JSON locais, sem necessidade de autenticação
- **Modo Produção**: Autenticação via Supabase, dados persistidos em banco PostgreSQL

## 📊 Exemplos de Uso

- **Dashboard**: Visualização geral de receitas, despesas e patrimônio
- **Controle de Gastos**: Acompanhamento mensal com categorização e análise temporal
- **Investimentos**: Acompanhamento de rentabilidade e distribuição por categorias
- **Dívidas**: Estratégias de pagamento (snowball/avalanche) e simulações
- **Seguros**: Alertas de vencimento e cobertura total
- **Objetivos**: Acompanhamento visual do progresso das metas financeiras

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias.

## Configuração do Ambiente

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente:
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione suas credenciais do Supabase:
     ```
     SUPABASE_URL=sua_url_do_supabase
     SUPABASE_KEY=sua_chave_do_supabase
     ```

## Deploy no Streamlit Cloud

1. Crie uma conta em [Streamlit Cloud](https://share.streamlit.io/)
2. Conecte sua conta do GitHub
3. Clique em "New app"
4. Selecione o repositório e o arquivo principal (`app/main.py`)
5. Configure as variáveis de ambiente no Streamlit Cloud:
   - SUPABASE_URL
   - SUPABASE_KEY

## Configuração do Supabase

1. Crie uma conta em [Supabase](https://supabase.com)
2. Crie um novo projeto
3. Execute o script SQL em `scripts/supabase_tables_completo.sql`
4. Configure as políticas de segurança (RLS)

## Desenvolvimento Local

Para rodar localmente:
```bash
streamlit run app/main.py
```

## Estrutura do Projeto

```
brauna_financas/
├── app/
│   ├── main.py
│   ├── database/
│   └── data/
├── scripts/
│   └── supabase_tables_completo.sql
├── .streamlit/
│   └── config.toml
├── requirements.txt
└── README.md
``` 