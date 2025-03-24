"""
Módulo com dados de exemplo para o aplicativo de Controle Financeiro Pessoal.
"""
from datetime import datetime, timedelta
import uuid

# Data atual para gerar dados relativos
hoje = datetime.now()
mes_atual = hoje.strftime("%Y-%m")
mes_anterior = (hoje.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

# Usuário de exemplo
SAMPLE_USER = {
    "nome": "Maria Silva",
    "email": "maria.silva@exemplo.com",
    "telefone": "(11) 98765-4321",
    "renda_mensal": 8000.00,
    "data_nascimento": "1985-06-15",
    "perfil_financeiro": "Moderado"
}

# Gastos de exemplo
SAMPLE_GASTOS = [
    # Gastos do mês atual
    {
        "id": 1,
        "descricao": "Aluguel",
        "valor": 2000.00,
        "data": f"{mes_atual}-05",
        "categoria": "Moradia",
        "tipo": "Fixo"
    },
    {
        "id": 2,
        "descricao": "Supermercado",
        "valor": 1200.00,
        "data": f"{mes_atual}-10",
        "categoria": "Alimentação",
        "tipo": "Fixo"
    },
    {
        "id": 3,
        "descricao": "Conta de Luz",
        "valor": 250.00,
        "data": f"{mes_atual}-15",
        "categoria": "Moradia",
        "tipo": "Fixo"
    },
    {
        "id": 4,
        "descricao": "Internet e TV",
        "valor": 180.00,
        "data": f"{mes_atual}-15",
        "categoria": "Serviços",
        "tipo": "Fixo"
    },
    {
        "id": 5,
        "descricao": "Academia",
        "valor": 120.00,
        "data": f"{mes_atual}-05",
        "categoria": "Saúde",
        "tipo": "Fixo"
    },
    {
        "id": 6,
        "descricao": "Jantar fora",
        "valor": 150.00,
        "data": f"{mes_atual}-18",
        "categoria": "Lazer",
        "tipo": "Variável"
    },
    {
        "id": 7,
        "descricao": "Uber",
        "valor": 80.00,
        "data": f"{mes_atual}-20",
        "categoria": "Transporte",
        "tipo": "Variável"
    },
    {
        "id": 8,
        "descricao": "Roupas",
        "valor": 350.00,
        "data": f"{mes_atual}-22",
        "categoria": "Vestuário",
        "tipo": "Variável"
    },
    
    # Gastos do mês anterior
    {
        "id": 9,
        "descricao": "Aluguel",
        "valor": 2000.00,
        "data": f"{mes_anterior}-05",
        "categoria": "Moradia",
        "tipo": "Fixo"
    },
    {
        "id": 10,
        "descricao": "Supermercado",
        "valor": 1150.00,
        "data": f"{mes_anterior}-10",
        "categoria": "Alimentação",
        "tipo": "Fixo"
    },
    {
        "id": 11,
        "descricao": "Conta de Luz",
        "valor": 230.00,
        "data": f"{mes_anterior}-15",
        "categoria": "Moradia",
        "tipo": "Fixo"
    },
    {
        "id": 12,
        "descricao": "Internet e TV",
        "valor": 180.00,
        "data": f"{mes_anterior}-15",
        "categoria": "Serviços",
        "tipo": "Fixo"
    },
    {
        "id": 13,
        "descricao": "Jantar fora",
        "valor": 200.00,
        "data": f"{mes_anterior}-18",
        "categoria": "Lazer",
        "tipo": "Variável"
    },
    {
        "id": 14,
        "descricao": "Manutenção do carro",
        "valor": 300.00,
        "data": f"{mes_anterior}-20",
        "categoria": "Transporte",
        "tipo": "Variável"
    }
]

# Gerar IDs fixos para objetivos para permitir vinculação com investimentos
objetivo_apartamento_id = str(uuid.uuid4())
objetivo_aposentadoria_id = str(uuid.uuid4())
objetivo_viagem_id = str(uuid.uuid4())

# Objetivos financeiros
SAMPLE_OBJETIVOS = [
    {
        "id": objetivo_apartamento_id,
        "nome": "Comprar um Apartamento",
        "descricao": "Juntar dinheiro para a entrada de um apartamento",
        "valor_total": 500000.00,
        "valor_atual": 120000.00,
        "data_inicio": "2022-01-01",
        "data_alvo": "2028-12-31",
        "categoria": "imovel",
        "prioridade": "alta",
        "taxa_retorno": 0.07,
        "investimentos_vinculados": []
    },
    {
        "id": objetivo_aposentadoria_id,
        "nome": "Aposentadoria",
        "descricao": "Fundo para aposentadoria",
        "valor_total": 2000000.00,
        "valor_atual": 150000.00,
        "data_inicio": "2019-06-01",
        "data_alvo": "2045-12-31",
        "categoria": "aposentadoria",
        "prioridade": "media",
        "taxa_retorno": 0.08,
        "investimentos_vinculados": []
    },
    {
        "id": objetivo_viagem_id,
        "nome": "Viagem à Europa",
        "descricao": "Viagem para conhecer países da Europa",
        "valor_total": 30000.00,
        "valor_atual": 15000.00,
        "data_inicio": "2023-01-01",
        "data_alvo": "2024-06-30",
        "categoria": "viagem",
        "prioridade": "baixa",
        "taxa_retorno": 0.04,
        "investimentos_vinculados": []
    }
]

# Gerar IDs fixos para investimentos
inv_tesouro_id = str(uuid.uuid4())
inv_cdb_id = str(uuid.uuid4())
inv_acoes_id = str(uuid.uuid4())
inv_fii_id = str(uuid.uuid4())
inv_poupanca_id = str(uuid.uuid4())
inv_etf_id = str(uuid.uuid4())

# Investimentos
SAMPLE_INVESTIMENTOS = [
    {
        "id": inv_tesouro_id,
        "descricao": "Tesouro Direto IPCA+",
        "categoria": "renda_fixa",
        "instituicao": "Tesouro Nacional",
        "valor_inicial": 80000.00,
        "valor_atual": 100000.00,
        "data_inicio": "2020-01-15",
        "rentabilidade_anual": 6.5,
        "risco": "baixo"
    },
    {
        "id": inv_cdb_id,
        "descricao": "CDB Banco XYZ",
        "categoria": "renda_fixa",
        "instituicao": "Banco XYZ",
        "valor_inicial": 45000.00,
        "valor_atual": 50000.00,
        "data_inicio": "2021-05-20",
        "rentabilidade_anual": 7.0,
        "risco": "baixo"
    },
    {
        "id": inv_acoes_id,
        "descricao": "Ações PETR4",
        "categoria": "acoes",
        "instituicao": "Corretora ABC",
        "valor_inicial": 28000.00,
        "valor_atual": 30000.00,
        "data_inicio": "2022-03-10",
        "rentabilidade_anual": 12.0,
        "risco": "alto"
    },
    {
        "id": inv_fii_id,
        "descricao": "Fundo Imobiliário XPLG11",
        "categoria": "fii",
        "instituicao": "Corretora ABC",
        "valor_inicial": 35000.00,
        "valor_atual": 40000.00,
        "data_inicio": "2021-09-15",
        "rentabilidade_anual": 8.5,
        "risco": "medio"
    },
    {
        "id": inv_poupanca_id,
        "descricao": "Poupança",
        "categoria": "renda_fixa",
        "instituicao": "Banco XYZ",
        "valor_inicial": 14000.00,
        "valor_atual": 15000.00,
        "data_inicio": "2023-01-05",
        "rentabilidade_anual": 5.0,
        "risco": "baixo"
    },
    {
        "id": inv_etf_id,
        "descricao": "ETF BOVA11",
        "categoria": "acoes",
        "instituicao": "Corretora ABC",
        "valor_inicial": 22000.00,
        "valor_atual": 25000.00,
        "data_inicio": "2022-06-10",
        "rentabilidade_anual": 9.0,
        "risco": "alto"
    }
]

# Vincular investimentos aos objetivos
for objetivo in SAMPLE_OBJETIVOS:
    if objetivo["id"] == objetivo_apartamento_id:
        objetivo["investimentos_vinculados"] = [inv_fii_id]
    elif objetivo["id"] == objetivo_aposentadoria_id:
        objetivo["investimentos_vinculados"] = [inv_tesouro_id, inv_etf_id]
    elif objetivo["id"] == objetivo_viagem_id:
        objetivo["investimentos_vinculados"] = [inv_poupanca_id]

# Dívidas
SAMPLE_DIVIDAS = [
    {
        "id": 1,
        "nome": "Financiamento do Carro",
        "valor_total": 60000.00,
        "valor_restante": 40000.00,
        "parcelas_total": 60,
        "parcelas_pagas": 20,
        "parcela_mensal": 1200.00,
        "taxa_juros": 0.12,  # 12% ao ano
        "data_inicio": "2022-03-15",
        "data_fim": "2027-03-15"
    },
    {
        "id": 2,
        "nome": "Empréstimo Pessoal",
        "valor_total": 15000.00,
        "valor_restante": 9000.00,
        "parcelas_total": 24,
        "parcelas_pagas": 10,
        "parcela_mensal": 750.00,
        "taxa_juros": 0.15,  # 15% ao ano
        "data_inicio": "2023-01-10",
        "data_fim": "2024-12-10"
    },
    {
        "id": 3,
        "nome": "Financiamento de Curso",
        "valor_total": 20000.00,
        "valor_restante": 12000.00,
        "parcelas_total": 36,
        "parcelas_pagas": 15,
        "parcela_mensal": 650.00,
        "taxa_juros": 0.08,  # 8% ao ano
        "data_inicio": "2022-08-05",
        "data_fim": "2025-07-05"
    }
]

# Seguros
SAMPLE_SEGUROS = [
    {
        "id": 1,
        "tipo": "Seguro de Vida",
        "seguradora": "Seguradora ABC",
        "valor_cobertura": 500000.00,
        "premio_mensal": 120.00,
        "data_contratacao": "2021-05-10",
        "data_renovacao": "2024-05-10",
        "beneficiarios": "Família"
    },
    {
        "id": 2,
        "tipo": "Seguro Auto",
        "seguradora": "Seguradora XYZ",
        "valor_cobertura": 80000.00,
        "premio_mensal": 250.00,
        "data_contratacao": "2023-02-15",
        "data_renovacao": "2024-02-15",
        "bem_segurado": "Veículo - Modelo SUV"
    },
    {
        "id": 3,
        "tipo": "Plano de Saúde",
        "seguradora": "Plano Saúde Total",
        "valor_cobertura": None,  # Cobertura variável por procedimento
        "premio_mensal": 450.00,
        "data_contratacao": "2020-06-20",
        "data_renovacao": "2024-06-20",
        "tipo_plano": "Apartamento"
    }
] 