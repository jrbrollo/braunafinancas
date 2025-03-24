# Plano de Testes - Brauna Finanças

## 1. Introdução

Este documento descreve o plano de testes para o aplicativo Brauna Finanças, um sistema de gerenciamento financeiro pessoal. O objetivo é garantir que todas as funcionalidades estejam operando corretamente e que a experiência do usuário seja consistente.

## 2. Escopo de Testes

### 2.1 Estrutura Básica do Aplicativo
- Inicialização correta da aplicação
- Navegação entre páginas
- Alternância entre temas claro/escuro
- Layout responsivo

### 2.2 Gerenciamento de Dados
- Inicialização de dados de exemplo
- Carregamento e salvamento de dados
- Backup e restauração

### 2.3 Dashboard
- Exibição correta de métricas financeiras
- Gráficos de tendências
- Distribuição de gastos

### 2.4 Controle de Gastos
- Adição de novos gastos
- Edição de gastos existentes
- Exclusão de gastos
- Filtros e categorização
- Visualizações analíticas

### 2.5 Página de Investimentos
- Adição de investimentos
- Cálculo correto de rendimentos
- Visualização da carteira
- Projeções financeiras

### 2.6 Página de Dívidas
- Registro e monitoramento de dívidas
- Estratégias de pagamento (Snowball/Avalanche)
- Cálculo de juros e prazos

### 2.7 Página de Seguros
- Registro de apólices
- Alertas de vencimento
- Cálculo de cobertura total

### 2.8 Página de Configurações
- Gestão de perfil do usuário
- Configurações de tema
- Backup e restauração de dados

## 3. Problemas Conhecidos

### 3.1 Problemas Visuais
- Inconsistências no tema em alguns componentes
- Problemas de layout em resoluções muito baixas
- Sobreposição de elementos em visualizações de gráficos

### 3.2 Problemas Funcionais
- Duplicação de funções em data_handler.py
- Inconsistência em campos de data (data_vencimento vs data_renovacao)
- Duplicação de IDs ao adicionar novos registros
- Falha na inicialização de dados em determinados casos

## 4. Correções Aplicadas

### 4.1 Em 22/03/2025:
- Removida duplicação de funções em data_handler.py
- Implementado UUID para IDs
- Melhorada manipulação de campos de data
- Corrigido algoritmo de cálculo de dias para vencimento
- Implementado inicializador de dados mais robusto

## 5. Procedimentos de Teste

### 5.1 Inicialização
1. Execute `python run.py --init` para inicializar dados de exemplo
2. Verifique se todos os dados são carregados corretamente
3. Verifique se a aplicação inicia sem erros

### 5.2 Teste de Funcionalidades Básicas
1. Alterne entre as diferentes páginas do aplicativo
2. Mude entre os temas claro e escuro
3. Verifique se todos os elementos da interface estão visíveis e funcionais

### 5.3 Teste de Modificação de Dados
1. Adicione um novo gasto e verifique se aparece na lista
2. Adicione um novo investimento e verifique os cálculos de rendimento
3. Adicione uma nova dívida e teste as estratégias de pagamento
4. Adicione um novo seguro e teste os alertas de vencimento

### 5.4 Teste de Importação/Exportação
1. Faça backup dos dados através da página de configurações
2. Restaure os dados usando o arquivo de backup
3. Verifique se todos os dados foram preservados corretamente

## 6. Critérios de Sucesso

- Todas as funcionalidades principais estão operacionais
- Não há erros de console ou exceções não tratadas
- A experiência do usuário é consistente em diferentes navegadores
- Os dados são salvos e carregados corretamente
- Backup e restauração funcionam conforme esperado