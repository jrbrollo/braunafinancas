"""
Script para inicializar o aplicativo com dados de exemplo.
Este arquivo pode ser executado diretamente para gerar dados iniciais na aplicação.
"""
import os
import json
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path
import streamlit as st

import app.data.data_handler as data_handler
from app.data.data_handler import ensure_data_dirs

def is_prod():
    """
    Verifica se o app está rodando em ambiente de produção (Streamlit Cloud).
    """
    # No Streamlit Cloud, podemos identificar pela existência de variáveis de ambiente específicas
    # ou pela ausência de acesso a certos diretórios
    return os.environ.get("STREAMLIT_SHARING", "") == "true" or os.environ.get("STREAMLIT_CLOUD", "") == "true"

def reset_and_initialize_data():
    """
    Função que inicializa o banco de dados com dados de exemplo APENAS quando necessário.
    Esta função foi aprimorada para NUNCA substituir dados reais de usuários existentes.
    Em produção (Streamlit Cloud), utiliza o session_state para armazenar os dados.
    """
    print("INFO: Verificando necessidade de inicialização de dados")
    
    # Primeira camada de proteção: verificar se já inicializamos na sessão atual
    if is_prod():
        # Verificar se os dados já foram inicializados na sessão
        if 'data_initialized' in st.session_state and st.session_state['data_initialized']:
            print("INFO: Dados já inicializados na sessão atual, pulando inicialização")
            return
    
    # Segunda camada de proteção: verificar se o usuário já existe e tem dados
    # Verificar se há gastos existentes
    has_existing_data = False
    
    # Verificar os gastos nas possíveis fontes
    try:
        # Verificar no arquivo
        if os.path.exists(data_handler.GASTOS_FILE):
            try:
                with open(data_handler.GASTOS_FILE, 'r', encoding='utf-8') as file:
                    gastos = json.load(file)
                    if gastos and len(gastos) > 0:
                        print(f"INFO: Detectados {len(gastos)} gastos existentes no arquivo, pulando inicialização")
                        has_existing_data = True
            except Exception as e:
                print(f"AVISO: Erro ao verificar arquivo de gastos: {e}")
        
        # Verificar no Supabase se disponível
        if not has_existing_data and data_handler.SUPABASE_AVAILABLE and data_handler.is_authenticated():
            try:
                gastos_supabase = data_handler.supabase_load_gastos()
                if gastos_supabase and len(gastos_supabase) > 0:
                    print(f"INFO: Detectados {len(gastos_supabase)} gastos existentes no Supabase, pulando inicialização")
                    has_existing_data = True
            except Exception as e:
                print(f"AVISO: Erro ao verificar gastos no Supabase: {e}")
        
        # Verificar na sessão
        if not has_existing_data and "gastos" in st.session_state:
            gastos_sessao = st.session_state.get("gastos", [])
            if gastos_sessao and len(gastos_sessao) > 0:
                print(f"INFO: Detectados {len(gastos_sessao)} gastos existentes na sessão, pulando inicialização")
                has_existing_data = True
    except Exception as e:
        print(f"AVISO: Erro ao verificar existência de dados: {e}")
    
    # Se já tem dados, não sobrescrever
    if has_existing_data:
        # Marcar que a inicialização já foi verificada mas não executada
        if is_prod():
            st.session_state['data_initialized'] = True
            st.session_state['data_initialization_skipped'] = True
        return
    
    print("INFO: Iniciando criação de dados de exemplo")
    
    # Garantir que os diretórios de dados existam
    ensure_data_dirs()
    
    # Dados do usuário
    user_data = {
        "nome": "Usuário de Exemplo",
        "email": "usuario@exemplo.com",
        "renda_mensal": 5000.0,
        "data_registro": datetime.now().strftime("%Y-%m-%d"),
        "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Gerar dados de exemplo
    gastos = gerar_dados_gastos()
    investimentos = gerar_dados_investimentos()
    dividas = gerar_dados_dividas()
    seguros = gerar_dados_seguros()
    objetivos = gerar_dados_objetivos()
    
    # Configurações
    config = {
        "inflacao_anual": 0.045,  # 4.5% ao ano
        "tema": "light",
        "moeda": "BRL",
        "formato_data": "DD/MM/YYYY",
        "notificacoes": True,
        "dados_exemplo": True  # Marcar que são dados de exemplo
    }
    
    # Salvar dados com log detalhado
    print("INFO: Salvando dados de usuário de exemplo")
    data_handler.save_user_data(user_data)
    
    print(f"INFO: Salvando {len(gastos)} gastos de exemplo")
    data_handler.save_gastos(gastos)
    
    print(f"INFO: Salvando {len(investimentos)} investimentos de exemplo")
    data_handler.save_investimentos(investimentos)
    
    print(f"INFO: Salvando {len(dividas)} dívidas de exemplo")
    data_handler.save_dividas(dividas)
    
    print(f"INFO: Salvando {len(seguros)} seguros de exemplo")
    data_handler.save_seguros(seguros)
    
    print(f"INFO: Salvando {len(objetivos)} objetivos de exemplo")
    data_handler.save_objetivos(objetivos)
    
    print("INFO: Salvando configuração")
    data_handler.save_config(config)
    
    # Marcar que os dados foram inicializados
    if is_prod():
        st.session_state['data_initialized'] = True
        st.session_state['data_initialization_date'] = datetime.now().isoformat()
        print("INFO: Dados de exemplo inicializados com sucesso na sessão")
    else:
        print("INFO: Dados de exemplo inicializados com sucesso em arquivos locais")

def gerar_dados_gastos():
    """
    Gera dados de exemplo de gastos para os últimos 3 meses.
    """
    gastos = []
    categorias = [
        "Moradia", "Alimentação", "Transporte", "Saúde", 
        "Educação", "Lazer", "Vestuário", "Serviços", "Outros"
    ]
    
    # Dados fixos para consistência
    gastos_fixos = [
        {
            "descricao": "Aluguel",
            "valor": 1200.0,
            "categoria": "Moradia",
            "tipo": "Fixo"
        },
        {
            "descricao": "Internet",
            "valor": 120.0,
            "categoria": "Serviços",
            "tipo": "Fixo"
        },
        {
            "descricao": "Energia",
            "valor": 150.0,
            "categoria": "Moradia",
            "tipo": "Fixo"
        },
        {
            "descricao": "Celular",
            "valor": 70.0,
            "categoria": "Serviços",
            "tipo": "Fixo"
        },
        {
            "descricao": "Assinatura de Streaming",
            "valor": 40.0,
            "categoria": "Lazer",
            "tipo": "Fixo"
        }
    ]
    
    # Gerar dados para os últimos 3 meses
    hoje = datetime.now()
    for i in range(3):
        # Calcular o mês
        mes_atual = hoje - timedelta(days=30*i)
        
        # Adicionar os gastos fixos para cada mês
        for gasto_fixo in gastos_fixos:
            gasto = gasto_fixo.copy()
            gasto["data"] = mes_atual.replace(day=5).strftime("%Y-%m-%d")
            gasto["id"] = str(uuid.uuid4())
            gastos.append(gasto)
        
        # Adicionar alguns gastos variáveis
        for _ in range(15):
            dia = random.randint(1, 28)
            categoria = random.choice(categorias)
            
            # Valores típicos por categoria
            if categoria == "Alimentação":
                valor = random.uniform(20, 200)
                descricao = random.choice(["Supermercado", "Restaurante", "Delivery", "Lanche"])
            elif categoria == "Transporte":
                valor = random.uniform(10, 150)
                descricao = random.choice(["Combustível", "Uber", "Ônibus", "Estacionamento"])
            elif categoria == "Lazer":
                valor = random.uniform(30, 300)
                descricao = random.choice(["Cinema", "Show", "Bar", "Viagem"])
            else:
                valor = random.uniform(50, 500)
                descricao = f"Gasto com {categoria.lower()}"
            
            gasto = {
                "id": str(uuid.uuid4()),
                "descricao": descricao,
                "valor": round(valor, 2),
                "data": mes_atual.replace(day=dia).strftime("%Y-%m-%d"),
                "categoria": categoria,
                "tipo": "Variável"
            }
            gastos.append(gasto)
    
    return gastos

def gerar_dados_investimentos():
    """
    Gera dados de exemplo de investimentos.
    """
    investimentos = [
        {
            "id": str(uuid.uuid4()),
            "descricao": "Tesouro Direto",
            "tipo": "Renda Fixa",
            "valor_inicial": 5000.0,
            "data_inicial": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "rendimento_anual": 0.085,
            "valor_atual": 5425.0,
            "vencimento": (datetime.now() + timedelta(days=365*2)).strftime("%Y-%m-%d"),
            "instituicao": "Banco do Brasil"
        },
        {
            "id": str(uuid.uuid4()),
            "descricao": "Fundo de Ações",
            "tipo": "Renda Variável",
            "valor_inicial": 3000.0,
            "data_inicial": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
            "rendimento_anual": 0.12,
            "valor_atual": 3250.0,
            "vencimento": "",
            "instituicao": "XP Investimentos"
        },
        {
            "id": str(uuid.uuid4()),
            "descricao": "CDB",
            "tipo": "Renda Fixa",
            "valor_inicial": 2000.0,
            "data_inicial": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
            "rendimento_anual": 0.095,
            "valor_atual": 2047.5,
            "vencimento": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "instituicao": "Nubank"
        },
        {
            "id": str(uuid.uuid4()),
            "descricao": "Fundo Imobiliário",
            "tipo": "Renda Variável",
            "valor_inicial": 4000.0,
            "data_inicial": (datetime.now() - timedelta(days=240)).strftime("%Y-%m-%d"),
            "rendimento_anual": 0.065,
            "valor_atual": 4130.0,
            "vencimento": "",
            "instituicao": "BTG Pactual"
        }
    ]
    return investimentos

def gerar_dados_dividas():
    """
    Gera dados de exemplo de dívidas.
    """
    dividas = [
        {
            "id": str(uuid.uuid4()),
            "descricao": "Financiamento do Carro",
            "valor_inicial": 30000.0,
            "valor_atual": 25000.0,
            "data_inicial": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "taxa_juros": 0.0125,  # 1.25% ao mês
            "parcelas_total": 48,
            "parcelas_pagas": 12,
            "valor_parcela": 750.0,
            "dia_vencimento": 10,
            "instituicao": "Banco do Brasil"
        },
        {
            "id": str(uuid.uuid4()),
            "descricao": "Cartão de Crédito",
            "valor_inicial": 2500.0,
            "valor_atual": 2500.0,
            "data_inicial": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
            "taxa_juros": 0.15,  # 15% ao mês
            "parcelas_total": 1,
            "parcelas_pagas": 0,
            "valor_parcela": 2500.0,
            "dia_vencimento": 5,
            "instituicao": "Nubank"
        }
    ]
    return dividas

def gerar_dados_seguros():
    """
    Gera dados de exemplo de seguros.
    """
    seguros = [
        {
            "id": str(uuid.uuid4()),
            "descricao": "Seguro do Carro",
            "tipo": "Automóvel",
            "valor_anual": 1800.0,
            "cobertura": 50000.0,
            "data_inicio": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
            "data_fim": (datetime.now() + timedelta(days=305)).strftime("%Y-%m-%d"),
            "forma_pagamento": "Anual",
            "seguradora": "Porto Seguro"
        },
        {
            "id": str(uuid.uuid4()),
            "descricao": "Seguro de Vida",
            "tipo": "Vida",
            "valor_anual": 600.0,
            "cobertura": 100000.0,
            "data_inicio": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
            "data_fim": (datetime.now() + timedelta(days=275)).strftime("%Y-%m-%d"),
            "forma_pagamento": "Mensal",
            "seguradora": "Bradesco Seguros"
        }
    ]
    return seguros

def gerar_dados_objetivos():
    """
    Gera dados de exemplo de objetivos financeiros.
    """
    objetivos = [
        {
            "id": str(uuid.uuid4()),
            "descricao": "Viagem para Europa",
            "valor_total": 15000.0,
            "valor_acumulado": 6000.0,
            "data_inicio": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
            "data_objetivo": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "aporte_mensal": 750.0,
            "prioridade": "Alta",
            "categoria": "Lazer"
        },
        {
            "id": str(uuid.uuid4()),
            "descricao": "Entrada para Apartamento",
            "valor_total": 50000.0,
            "valor_acumulado": 15000.0,
            "data_inicio": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "data_objetivo": (datetime.now() + timedelta(days=365*2)).strftime("%Y-%m-%d"),
            "aporte_mensal": 1500.0,
            "prioridade": "Alta",
            "categoria": "Moradia"
        },
        {
            "id": str(uuid.uuid4()),
            "descricao": "Fundo de Emergência",
            "valor_total": 20000.0,
            "valor_acumulado": 8000.0,
            "data_inicio": (datetime.now() - timedelta(days=240)).strftime("%Y-%m-%d"),
            "data_objetivo": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "aporte_mensal": 1000.0,
            "prioridade": "Média",
            "categoria": "Segurança"
        }
    ]
    return objetivos

if __name__ == "__main__":
    # Se executado diretamente, reinicializar os dados
    print("Inicializando dados de exemplo...")
    reset_and_initialize_data()
    print("Dados inicializados com sucesso!") 