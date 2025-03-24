"""
Módulo para dados de exemplo que podem ser usados para demonstração
ou para preencher o aplicativo com valores iniciais para testes.
"""

# Usuário de exemplo
SAMPLE_USER = {
    "nome": "Maria Silva",
    "idade": 35,
    "renda_mensal": 8000.00,
    "despesas_fixas": 4500.00,
    "reserva_emergencia": 25000.00,
    "perfil_investidor": "Moderado"
}

# Objetivos financeiros de exemplo
SAMPLE_GOALS = [
    {
        "id": 1,
        "nome": "Comprar Apartamento",
        "valor_total": 500000.00,
        "valor_atual": 120000.00,
        "data_inicio": "2022-01-01",
        "data_alvo": "2027-12-31",
        "prioridade": "Alta",
        "contribuicao_mensal": 3500.00,
        "taxa_retorno_estimada": 0.07
    },
    {
        "id": 2,
        "nome": "Aposentadoria",
        "valor_total": 2000000.00,
        "valor_atual": 150000.00,
        "data_inicio": "2019-06-01",
        "data_alvo": "2045-12-31",
        "prioridade": "Média",
        "contribuicao_mensal": 2000.00,
        "taxa_retorno_estimada": 0.09
    },
    {
        "id": 3,
        "nome": "Viagem Internacional",
        "valor_total": 30000.00,
        "valor_atual": 15000.00,
        "data_inicio": "2023-01-01",
        "data_alvo": "2024-12-31",
        "prioridade": "Baixa",
        "contribuicao_mensal": 1000.00,
        "taxa_retorno_estimada": 0.05
    }
]

# Investimentos de exemplo
SAMPLE_INVESTMENTS = [
    {
        "id": 1,
        "nome": "Tesouro Direto",
        "tipo": "Renda Fixa",
        "valor": 100000.00,
        "data_inicio": "2020-01-15",
        "taxa_retorno_anual": 0.065,
        "risco": "Baixo",
        "liquidez": "Média",
        "objetivo_id": 2  # Vinculado à Aposentadoria
    },
    {
        "id": 2,
        "nome": "Fundo Imobiliário XYZ",
        "tipo": "Fundos Imobiliários",
        "valor": 80000.00,
        "data_inicio": "2021-03-10",
        "taxa_retorno_anual": 0.085,
        "risco": "Médio",
        "liquidez": "Média",
        "objetivo_id": 1  # Vinculado ao Apartamento
    },
    {
        "id": 3,
        "nome": "Ações PETR4",
        "tipo": "Renda Variável",
        "valor": 40000.00,
        "data_inicio": "2022-07-05",
        "taxa_retorno_anual": 0.11,
        "risco": "Alto",
        "liquidez": "Alta",
        "objetivo_id": None  # Não vinculado a objetivo específico
    },
    {
        "id": 4,
        "nome": "Poupança",
        "tipo": "Renda Fixa",
        "valor": 15000.00,
        "data_inicio": "2023-02-01",
        "taxa_retorno_anual": 0.05,
        "risco": "Baixo",
        "liquidez": "Alta",
        "objetivo_id": 3  # Vinculado à Viagem
    }
]

# Histórico de transações de exemplo
SAMPLE_TRANSACTIONS = [
    {
        "id": 1,
        "data": "2023-01-15",
        "tipo": "Aporte",
        "valor": 3500.00,
        "objetivo_id": 1,
        "investimento_id": 2,
        "descricao": "Aporte mensal para objetivo de compra de apartamento"
    },
    {
        "id": 2,
        "data": "2023-02-15",
        "tipo": "Aporte",
        "valor": 3500.00,
        "objetivo_id": 1,
        "investimento_id": 2,
        "descricao": "Aporte mensal para objetivo de compra de apartamento"
    },
    {
        "id": 3,
        "data": "2023-01-20",
        "tipo": "Aporte",
        "valor": 2000.00,
        "objetivo_id": 2,
        "investimento_id": 1,
        "descricao": "Aporte mensal para aposentadoria"
    },
    {
        "id": 4,
        "data": "2023-02-20",
        "tipo": "Aporte",
        "valor": 2000.00,
        "objetivo_id": 2,
        "investimento_id": 1,
        "descricao": "Aporte mensal para aposentadoria"
    },
    {
        "id": 5,
        "data": "2023-01-25",
        "tipo": "Aporte",
        "valor": 1000.00,
        "objetivo_id": 3,
        "investimento_id": 4,
        "descricao": "Aporte mensal para viagem internacional"
    },
    {
        "id": 6,
        "data": "2023-02-25",
        "tipo": "Aporte",
        "valor": 1000.00,
        "objetivo_id": 3,
        "investimento_id": 4,
        "descricao": "Aporte mensal para viagem internacional"
    },
    {
        "id": 7,
        "data": "2023-03-01",
        "tipo": "Dividendos",
        "valor": 450.00,
        "objetivo_id": None,
        "investimento_id": 3,
        "descricao": "Dividendos recebidos de ações PETR4"
    }
]

# Dados para projeções financeiras
SAMPLE_PROJECTIONS = {
    "inflacao_anual": 0.045,
    "crescimento_salarial_anual": 0.03,
    "expectativa_vida": 85,
    "taxa_media_poupanca": 0.05,
    "taxa_media_renda_fixa": 0.08,
    "taxa_media_acoes": 0.10
} 