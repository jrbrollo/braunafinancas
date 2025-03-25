"""
Módulo para a página de Objetivos Financeiros do aplicativo de Controle Financeiro Pessoal.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import math

# Importar funções de manipulação de dados
from app.data.data_handler import (
    load_user_data,
    load_objetivos,
    save_objetivos,
    add_objetivo,
    load_investimentos,
    atualizar_progresso_objetivo,
    vincular_investimento_objetivo,
    desvincular_investimento_objetivo,
    calcular_progresso_objetivos
)

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    """
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_contribuicao_mensal_necessaria(valor_total, valor_atual, meses_restantes, taxa_mensal):
    """
    Calcula a contribuição mensal necessária para atingir o objetivo dentro do prazo.
    
    Args:
        valor_total (float): Valor total do objetivo
        valor_atual (float): Valor atual acumulado
        meses_restantes (int): Número de meses até a data alvo
        taxa_mensal (float): Taxa de retorno mensal (decimal)
        
    Returns:
        float: Valor mensal necessário
    """
    if meses_restantes <= 0:
        return 0
    
    # Valor a atingir
    valor_a_atingir = valor_total - valor_atual
    
    # Se não há rendimento, é uma divisão simples
    if taxa_mensal == 0:
        return valor_a_atingir / meses_restantes
    
    # Para cálculo com rendimento, usamos a fórmula de contribuição periódica
    # PMT = FV * r / ((1 + r)^n - 1)
    # Onde: PMT = pagamento mensal, FV = valor futuro, r = taxa, n = número de períodos
    return valor_a_atingir * taxa_mensal / ((1 + taxa_mensal) ** meses_restantes - 1)

def calcular_meses_entre_datas(data_inicio, data_alvo):
    """
    Calcula o número de meses entre duas datas.
    
    Args:
        data_inicio (datetime): Data inicial
        data_alvo (datetime): Data alvo
        
    Returns:
        int: Número de meses entre as datas
    """
    return (data_alvo.year - data_inicio.year) * 12 + (data_alvo.month - data_inicio.month)

def render_objetivos_page():
    """
    Renderiza a página de Objetivos Financeiros.
    """
    # Cabeçalho moderno
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-right: 0.8rem;">🎯</div>
        <div>
            <h1 style="margin: 0; padding: 0;">Objetivos Financeiros</h1>
            <p style="margin: 0; padding: 0; color: var(--gray);">Planeje e acompanhe suas metas financeiras</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    objetivos = load_objetivos()
    investimentos = load_investimentos()
    
    # Criar um dicionário de investimentos para acesso rápido
    investimentos_dict = {inv.get("id", ""): inv for inv in investimentos}
    
    # Botão em destaque para adicionar novo objetivo
    col_btn, col_empty = st.columns([1, 3])
    with col_btn:
        if st.button("➕ Adicionar Objetivo", type="primary", use_container_width=True):
            st.session_state.mostrar_form_objetivo = True
    
    # Formulário para adicionar novo objetivo
    if st.session_state.get("mostrar_form_objetivo", False):
        with st.expander("Novo Objetivo", expanded=True):
            with st.form("form_novo_objetivo"):
                st.markdown("### Registre seu objetivo financeiro")
                
                nome = st.text_input("Nome do objetivo", 
                                   help="Ex: Comprar casa, Fazer intercâmbio, etc.")
                
                descricao = st.text_area("Descrição (opcional)", 
                                       help="Detalhes sobre o objetivo")
                
                col1, col2 = st.columns(2)
                with col1:
                    valor_total = st.number_input(
                        "Valor total (R$)", 
                        min_value=1.0, 
                        step=1000.0,
                        format="%.2f",
                        help="Quanto custa realizar este objetivo"
                    )
                
                with col2:
                    valor_atual = st.number_input(
                        "Valor atual (R$)", 
                        min_value=0.0, 
                        max_value=valor_total,
                        step=100.0,
                        format="%.2f",
                        help="Quanto você já tem guardado para este objetivo"
                    )
                
                col3, col4 = st.columns(2)
                with col3:
                    categoria = st.selectbox(
                        "Categoria",
                        options=[
                            "imovel", "veiculo", "educacao", 
                            "viagem", "aposentadoria", "emergencia", "outros"
                        ],
                        format_func=lambda x: {
                            "imovel": "🏠 Imóvel",
                            "veiculo": "🚗 Veículo",
                            "educacao": "🎓 Educação",
                            "viagem": "✈️ Viagem",
                            "aposentadoria": "👵 Aposentadoria",
                            "emergencia": "🚨 Fundo de Emergência",
                            "outros": "📋 Outros"
                        }.get(x, x)
                    )
                
                with col4:
                    prioridade = st.selectbox(
                        "Prioridade",
                        options=["alta", "media", "baixa"],
                        format_func=lambda x: {
                            "alta": "🔴 Alta",
                            "media": "🟠 Média",
                            "baixa": "🟢 Baixa"
                        }.get(x, x)
                    )
                
                # Datas
                col5, col6 = st.columns(2)
                with col5:
                    data_inicio = st.date_input(
                        "Data de início", 
                        value=datetime.now(),
                        help="Quando você começou a poupar para este objetivo"
                    )
                
                with col6:
                    anos_para_alvo = st.slider(
                        "Anos para alcançar", 
                        min_value=1, 
                        max_value=30, 
                        value=5,
                        help="Em quantos anos você pretende atingir este objetivo"
                    )
                    data_alvo = data_inicio + timedelta(days=365 * anos_para_alvo)
                    st.write(f"Data alvo: {data_alvo.strftime('%d/%m/%Y')}")
                
                # Taxa de retorno estimada
                st.markdown("""
                <div style="padding: 10px; background-color: var(--blue-light); border-radius: 5px; margin-bottom: 10px;">
                    <p style="margin: 0; color: var(--blue);">
                        <strong>💡 Dica:</strong> Quando você vincular investimentos a este objetivo, 
                        a rentabilidade será calculada automaticamente com base nesses investimentos.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                taxa_retorno = st.slider(
                    "Taxa de retorno anual estimada (%) - opcional", 
                    min_value=0.0, 
                    max_value=20.0, 
                    value=5.0,
                    step=0.5,
                    help="Estimativa inicial de rendimento. Será substituída pelos rendimentos reais dos investimentos vinculados."
                )
                
                # Botões de ação
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("💾 Salvar objetivo", use_container_width=True)
                with col_btn2:
                    cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if submitted:
                    if not nome:
                        st.error("O nome do objetivo é obrigatório.")
                    elif valor_total <= 0:
                        st.error("O valor total deve ser maior que zero.")
                    else:
                        # Criar novo objetivo
                        novo_objetivo = {
                            "nome": nome,
                            "descricao": descricao,
                            "valor_total": valor_total,
                            "valor_atual": valor_atual,
                            "categoria": categoria,
                            "prioridade": 1 if prioridade == "alta" else 2 if prioridade == "media" else 3,  # Converter para inteiro
                            "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                            "data_alvo": data_alvo.strftime("%Y-%m-%d"),
                            "taxa_retorno": taxa_retorno / 100,  # Converter para decimal
                            "investimentos_vinculados": []
                        }
                        
                        # Adicionar à lista
                        if add_objetivo(novo_objetivo):
                            st.success("Objetivo adicionado com sucesso!")
                            st.session_state.mostrar_form_objetivo = False
                            st.rerun()
                        else:
                            st.error("Erro ao adicionar objetivo.")
                
                if cancel:
                    st.session_state.mostrar_form_objetivo = False
                    st.rerun()
    
    # Criar tabs para diferentes visualizações
    tab1, tab2 = st.tabs(["Meus Objetivos", "Vinculação com Investimentos"])
    
    with tab1:
        if objetivos:
            # Adicionar resumo dos objetivos em cards
            total_objetivos = len(objetivos)
            total_valor = sum(obj.get("valor_total", 0) for obj in objetivos)
            total_acumulado = sum(obj.get("valor_atual", 0) for obj in objetivos)
            percentual_geral = (total_acumulado / total_valor * 100) if total_valor > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="card">
                    <div class="metric-label">Total de Objetivos</div>
                    <div class="metric-value">{total_objetivos}</div>
                    <div>Metas financeiras ativas</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="card">
                    <div class="metric-label">Valor Total</div>
                    <div class="metric-value">{formatar_moeda(total_valor)}</div>
                    <div>Soma de todos os objetivos</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                card_class = "success" if percentual_geral >= 50 else "warning" if percentual_geral >= 25 else ""
                st.markdown(f"""
                <div class="card {card_class}">
                    <div class="metric-label">Progresso Geral</div>
                    <div class="metric-value">{percentual_geral:.1f}%</div>
                    <div>{formatar_moeda(total_acumulado)} acumulados</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Listar objetivos ordenados por prioridade
            st.subheader("Metas em andamento")
            
            # Ordenar objetivos por prioridade
            objetivos_ordenados = sorted(objetivos, key=lambda x: (
                x.get("prioridade", 3),  # Ordenar por prioridade numérica (1=alta, 2=média, 3=baixa)
                datetime.strptime(x.get("data_alvo", "2100-01-01"), "%Y-%m-%d")
            ))
            
            for obj in objetivos_ordenados:
                # Calcular progresso
                valor_total = obj.get("valor_total", 1)
                valor_atual = obj.get("valor_atual", 0)
                percentual = (valor_atual / valor_total) * 100 if valor_total > 0 else 0
                
                # Converter datas para objetos datetime
                data_inicio = datetime.strptime(obj.get("data_inicio", "2023-01-01"), "%Y-%m-%d")
                data_alvo = datetime.strptime(obj.get("data_alvo", "2024-01-01"), "%Y-%m-%d")
                
                # Calcular tempo restante
                hoje = datetime.now()
                dias_totais = (data_alvo - data_inicio).days
                dias_passados = (hoje - data_inicio).days
                dias_restantes = (data_alvo - hoje).days
                
                # Tempo total e restante em formato legível
                tempo_restante = ""
                if dias_restantes <= 0:
                    tempo_restante = "Prazo vencido"
                elif dias_restantes < 30:
                    tempo_restante = f"{dias_restantes} dias restantes"
                elif dias_restantes < 365:
                    meses = dias_restantes // 30
                    tempo_restante = f"{meses} {'mês restante' if meses == 1 else 'meses restantes'}"
                else:
                    anos = dias_restantes // 365
                    meses = (dias_restantes % 365) // 30
                    tempo_restante = f"{anos} {'ano' if anos == 1 else 'anos'}"
                    if meses > 0:
                        tempo_restante += f" e {meses} {'mês' if meses == 1 else 'meses'}"
                    tempo_restante += " restantes"
                
                # Calcular a contribuição mensal necessária
                meses_restantes = calcular_meses_entre_datas(hoje, data_alvo)
                taxa_mensal = (1 + obj.get("taxa_retorno", 0)) ** (1/12) - 1
                
                if meses_restantes > 0 and percentual < 100:
                    contribuicao_mensal = calcular_contribuicao_mensal_necessaria(
                        valor_total, valor_atual, meses_restantes, taxa_mensal
                    )
                else:
                    contribuicao_mensal = 0
                
                # Definir classe de cor baseada na prioridade
                prioridade_classe = {
                    "alta": "danger",
                    "media": "warning",
                    "baixa": "success"
                }.get(obj.get("prioridade", "baixa"), "")
                
                # Mostrar card com objetivo
                with st.expander(f"{obj.get('nome', 'Objetivo')} - {percentual:.1f}% concluído"):
                    # Exibir detalhes do objetivo
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Categoria:** {obj.get('categoria', 'Não categorizado').title()}")
                        st.markdown(f"**Descrição:** {obj.get('descricao', 'Sem descrição')}")
                        st.markdown(f"**Prioridade:** {'Alta' if obj.get('prioridade') == 1 else 'Média' if obj.get('prioridade') == 2 else 'Baixa'}")
                        st.markdown(f"**Taxa de retorno estimada:** {obj.get('taxa_retorno', 0) * 100:.1f}% ao ano")
                    
                    with col2:
                        st.markdown(f"**Valor atual:** {formatar_moeda(valor_atual)}")
                        st.markdown(f"**Valor total:** {formatar_moeda(valor_total)}")
                        st.markdown(f"**Faltam:** {formatar_moeda(valor_total - valor_atual)}")
                        st.markdown(f"**Prazo:** {data_alvo.strftime('%d/%m/%Y')} ({tempo_restante})")
                    
                    # Barra de progresso
                    st.progress(percentual / 100)
                    
                    # Contribuição mensal necessária
                    if meses_restantes > 0 and percentual < 100:
                        st.markdown(f"**Contribuição mensal necessária:** {formatar_moeda(contribuicao_mensal)}")
                    
                    # Investimentos vinculados
                    if "investimentos_vinculados" in obj and obj["investimentos_vinculados"]:
                        st.markdown("**Investimentos vinculados:**")
                        for inv_id in obj["investimentos_vinculados"]:
                            if inv_id in investimentos_dict:
                                inv = investimentos_dict[inv_id]
                                st.markdown(f"- {inv.get('descricao', 'Investimento')} ({formatar_moeda(inv.get('valor_atual', 0))})")
                    
                    # Opções para editar, excluir, etc.
                    col_acoes1, col_acoes2, col_acoes3 = st.columns(3)
                    
                    with col_acoes1:
                        if st.button("✏️ Editar", key=f"edit_{obj.get('id')}"):
                            st.session_state.objetivo_para_editar = obj.get("id")
                            st.session_state.mostrar_form_edicao = True
                            st.rerun()
                    
                    with col_acoes2:
                        if st.button("💰 Atualizar valor", key=f"update_{obj.get('id')}"):
                            st.session_state.objetivo_para_atualizar = obj.get("id")
                            st.session_state.mostrar_form_atualizacao = True
                    
                    with col_acoes3:
                        if st.button("🗑️ Excluir", key=f"delete_{obj.get('id')}"):
                            st.session_state.objetivo_para_excluir = obj.get("id")
                            st.session_state.confirmar_exclusao = True
            
            # Formulário para edição de objetivo
            if "mostrar_form_edicao" in st.session_state and st.session_state.mostrar_form_edicao:
                objetivo_id = st.session_state.objetivo_para_editar
                objetivo = next((obj for obj in objetivos if obj.get("id") == objetivo_id), None)
                
                if objetivo:
                    st.subheader(f"Editar objetivo: '{objetivo.get('nome')}'")
                    
                    with st.form("form_editar_objetivo"):
                        nome = st.text_input(
                            "Nome do objetivo", 
                            value=objetivo.get("nome", ""),
                            help="Ex: Comprar casa, Fazer intercâmbio, etc."
                        )
                        
                        descricao = st.text_area(
                            "Descrição (opcional)", 
                            value=objetivo.get("descricao", ""),
                            help="Detalhes sobre o objetivo"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            valor_total = st.number_input(
                                "Valor total (R$)", 
                                min_value=1.0, 
                                value=float(objetivo.get("valor_total", 1000.0)),
                                step=1000.0,
                                format="%.2f",
                                help="Quanto custa realizar este objetivo"
                            )
                        
                        with col2:
                            valor_atual = st.number_input(
                                "Valor atual (R$)", 
                                min_value=0.0, 
                                max_value=valor_total,
                                value=float(objetivo.get("valor_atual", 0.0)),
                                step=100.0,
                                format="%.2f",
                                help="Quanto você já tem guardado para este objetivo"
                            )
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            categoria = st.selectbox(
                                "Categoria",
                                options=[
                                    "imovel", "veiculo", "educacao", 
                                    "viagem", "aposentadoria", "emergencia", "outros"
                                ],
                                index=["imovel", "veiculo", "educacao", "viagem", "aposentadoria", "emergencia", "outros"].index(
                                    objetivo.get("categoria", "outros")
                                ),
                                format_func=lambda x: {
                                    "imovel": "🏠 Imóvel",
                                    "veiculo": "🚗 Veículo",
                                    "educacao": "🎓 Educação",
                                    "viagem": "✈️ Viagem",
                                    "aposentadoria": "👵 Aposentadoria",
                                    "emergencia": "🚨 Fundo de Emergência",
                                    "outros": "📋 Outros"
                                }.get(x, x)
                            )
                        
                        with col4:
                            prioridade_atual = objetivo.get("prioridade", 2)
                            if isinstance(prioridade_atual, int):
                                prioridade_str = "alta" if prioridade_atual == 1 else "media" if prioridade_atual == 2 else "baixa"
                            else:
                                prioridade_str = prioridade_atual
                                
                            prioridade = st.selectbox(
                                "Prioridade",
                                options=["alta", "media", "baixa"],
                                index=["alta", "media", "baixa"].index(prioridade_str),
                                format_func=lambda x: {
                                    "alta": "🔴 Alta",
                                    "media": "🟠 Média",
                                    "baixa": "🟢 Baixa"
                                }.get(x, x)
                            )
                        
                        # Datas
                        col5, col6 = st.columns(2)
                        with col5:
                            data_inicio = st.date_input(
                                "Data de início", 
                                value=datetime.strptime(objetivo.get("data_inicio", datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d"),
                                help="Quando você começou a poupar para este objetivo"
                            )
                        
                        with col6:
                            # Calcular a diferença entre as datas em anos
                            data_alvo_atual = datetime.strptime(objetivo.get("data_alvo", ""), "%Y-%m-%d")
                            data_inicio_atual = datetime.strptime(objetivo.get("data_inicio", ""), "%Y-%m-%d")
                            anos_atuais = max(1, round((data_alvo_atual - data_inicio_atual).days / 365))
                            
                            anos_para_alvo = st.slider(
                                "Anos para alcançar", 
                                min_value=1, 
                                max_value=30, 
                                value=int(anos_atuais),
                                help="Em quantos anos você pretende atingir este objetivo"
                            )
                            data_alvo = data_inicio + timedelta(days=365 * anos_para_alvo)
                            st.write(f"Data alvo: {data_alvo.strftime('%d/%m/%Y')}")
                        
                        # Taxa de retorno estimada
                        taxa_atual = objetivo.get("taxa_retorno", 0.05) * 100  # Converter de decimal para percentual
                        taxa_retorno = st.slider(
                            "Taxa de retorno anual estimada (%) - opcional", 
                            min_value=0.0, 
                            max_value=20.0, 
                            value=float(taxa_atual),
                            step=0.5,
                            help="Estimativa inicial de rendimento. Será substituída pelos rendimentos reais dos investimentos vinculados."
                        )
                        
                        # Manter os investimentos vinculados
                        investimentos_vinculados = objetivo.get("investimentos_vinculados", [])
                        
                        # Botões de ação
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            atualizar = st.form_submit_button("💾 Salvar alterações", use_container_width=True)
                        with col_btn2:
                            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
                        
                        if atualizar:
                            if not nome:
                                st.error("O nome do objetivo é obrigatório.")
                            elif valor_total <= 0:
                                st.error("O valor total deve ser maior que zero.")
                            else:
                                # Atualizar objetivo
                                objetivo_atualizado = {
                                    "id": objetivo_id,
                                    "nome": nome,
                                    "descricao": descricao,
                                    "valor_total": valor_total,
                                    "valor_atual": valor_atual,
                                    "categoria": categoria,
                                    "prioridade": 1 if prioridade == "alta" else 2 if prioridade == "media" else 3,
                                    "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                                    "data_alvo": data_alvo.strftime("%Y-%m-%d"),
                                    "taxa_retorno": taxa_retorno / 100,  # Converter para decimal
                                    "investimentos_vinculados": investimentos_vinculados
                                }
                                
                                # Atualizar na lista
                                objetivos = [objetivo_atualizado if obj.get("id") == objetivo_id else obj for obj in objetivos]
                                
                                if save_objetivos(objetivos):
                                    st.success("Objetivo atualizado com sucesso!")
                                    st.session_state.mostrar_form_edicao = False
                                    st.rerun()
                                else:
                                    st.error("Erro ao atualizar objetivo.")
                        
                        if cancelar:
                            st.session_state.mostrar_form_edicao = False
                            st.rerun()
            
            # Formulário para atualização de valor
            if "mostrar_form_atualizacao" in st.session_state and st.session_state.mostrar_form_atualizacao:
                objetivo_id = st.session_state.objetivo_para_atualizar
                objetivo = next((obj for obj in objetivos if obj.get("id") == objetivo_id), None)
                
                if objetivo:
                    st.subheader(f"Atualizar valor de '{objetivo.get('nome')}'")
                    
                    with st.form("form_atualizar_valor"):
                        valor_atual = st.number_input(
                            "Novo valor atual (R$)", 
                            min_value=0.0, 
                            max_value=objetivo.get("valor_total", 1000000),
                            value=float(objetivo.get("valor_atual", 0)),
                            step=100.0,
                            format="%.2f"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            atualizar = st.form_submit_button("✅ Atualizar", use_container_width=True)
                        with col2:
                            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)
                        
                        if atualizar:
                            if atualizar_progresso_objetivo(objetivo_id, valor_atual):
                                st.success("Valor atualizado com sucesso!")
                                st.session_state.mostrar_form_atualizacao = False
                                st.rerun()
                            else:
                                st.error("Erro ao atualizar valor.")
                        
                        if cancelar:
                            st.session_state.mostrar_form_atualizacao = False
                            st.rerun()
            
            # Confirmação de exclusão
            if "confirmar_exclusao" in st.session_state and st.session_state.confirmar_exclusao:
                objetivo_id = st.session_state.objetivo_para_excluir
                objetivo = next((obj for obj in objetivos if obj.get("id") == objetivo_id), None)
                
                if objetivo:
                    st.subheader("Confirmação de Exclusão")
                    st.warning(f"Tem certeza que deseja excluir o objetivo '{objetivo.get('nome')}'?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Sim, excluir", key="confirm_delete"):
                            # Remover o objetivo da lista
                            objetivos = [obj for obj in objetivos if obj.get("id") != objetivo_id]
                            if save_objetivos(objetivos):
                                st.success("Objetivo excluído com sucesso!")
                                st.session_state.confirmar_exclusao = False
                                st.rerun()
                            else:
                                st.error("Erro ao excluir objetivo.")
                    
                    with col2:
                        if st.button("❌ Cancelar", key="cancel_delete"):
                            st.session_state.confirmar_exclusao = False
                            st.rerun()
        else:
            st.info("Você ainda não possui objetivos financeiros. Clique no botão 'Adicionar Objetivo' para começar.")
    
    with tab2:
        st.subheader("Vincular Investimentos aos Objetivos")
        
        if not objetivos:
            st.info("Você precisa cadastrar objetivos financeiros primeiro.")
        elif not investimentos:
            st.info("Você precisa cadastrar investimentos primeiro.")
        else:
            # Formulário para vincular investimentos a objetivos
            col1, col2 = st.columns(2)
            
            with col1:
                # Selecionar objetivo
                opcoes_objetivos = {obj.get("nome", f"Objetivo {i}"): obj.get("id") 
                                   for i, obj in enumerate(objetivos)}
                
                objetivo_selecionado = st.selectbox(
                    "Selecione um objetivo:",
                    options=list(opcoes_objetivos.keys()),
                    key="vinculo_objetivo"
                )
                
                objetivo_id = opcoes_objetivos[objetivo_selecionado]
                objetivo = next((obj for obj in objetivos if obj.get("id") == objetivo_id), None)
            
            with col2:
                # Selecionar investimento
                # Filtrar investimentos que já estão vinculados a este objetivo
                investimentos_vinculados = objetivo.get("investimentos_vinculados", []) if objetivo else []
                
                # Criar opções apenas com investimentos não vinculados
                investimentos_disponiveis = [inv for inv in investimentos 
                                            if inv.get("id") not in investimentos_vinculados]
                
                if investimentos_disponiveis:
                    opcoes_investimentos = {
                        f"{inv.get('descricao', 'Investimento')} - {formatar_moeda(inv.get('valor_atual', 0))}": inv.get("id")
                        for inv in investimentos_disponiveis
                    }
                    
                    investimento_selecionado = st.selectbox(
                        "Selecione um investimento para vincular:",
                        options=list(opcoes_investimentos.keys()),
                        key="vinculo_investimento"
                    )
                    
                    investimento_id = opcoes_investimentos[investimento_selecionado]
                    
                    if st.button("🔗 Vincular Investimento", type="primary"):
                        if vincular_investimento_objetivo(objetivo_id, investimento_id):
                            # Recalcular progresso dos objetivos
                            calcular_progresso_objetivos()
                            st.success("Investimento vinculado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro ao vincular investimento.")
                else:
                    st.info("Não há investimentos disponíveis para vincular a este objetivo.")
            
            # Mostrar investimentos vinculados e permitir desvincular
            if objetivo and "investimentos_vinculados" in objetivo and objetivo["investimentos_vinculados"]:
                st.subheader("Investimentos vinculados a este objetivo")
                
                for inv_id in objetivo["investimentos_vinculados"]:
                    if inv_id in investimentos_dict:
                        inv = investimentos_dict[inv_id]
                        
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{inv.get('descricao', 'Investimento')}** - {formatar_moeda(inv.get('valor_atual', 0))}")
                        
                        with col3:
                            if st.button("❌ Desvincular", key=f"unlink_{inv_id}"):
                                if desvincular_investimento_objetivo(objetivo_id, inv_id):
                                    # Recalcular progresso dos objetivos
                                    calcular_progresso_objetivos()
                                    st.success("Investimento desvinculado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao desvincular investimento.")
            
            # Mostrar visualização gráfica dos objetivos
            if objetivos:
                st.subheader("Visão Geral dos Objetivos")
                
                # Preparar dados para o gráfico
                dados_grafico = []
                for obj in objetivos:
                    valor_total = obj.get("valor_total", 0)
                    valor_atual = obj.get("valor_atual", 0)
                    percentual = (valor_atual / valor_total) * 100 if valor_total > 0 else 0
                    
                    dados_grafico.append({
                        "Objetivo": obj.get("nome", "Objetivo"),
                        "Percentual": percentual,
                        "Valor Atual": valor_atual,
                        "Valor Total": valor_total,
                        "Categoria": obj.get("categoria", "outros").title()
                    })
                
                # Criar DataFrame
                df = pd.DataFrame(dados_grafico)
                
                # Ordenar por percentual de conclusão
                df = df.sort_values("Percentual", ascending=False)
                
                # Criar gráfico de barras horizontais
                fig = px.bar(
                    df,
                    y="Objetivo",
                    x="Percentual",
                    title="Progresso dos Objetivos (%)",
                    color="Categoria",
                    hover_data=["Valor Atual", "Valor Total"],
                    text="Percentual",
                    orientation="h"
                )
                
                fig.update_traces(
                    texttemplate="%{text:.1f}%", 
                    textposition="outside"
                )
                
                fig.update_layout(
                    xaxis_title="Progresso (%)",
                    yaxis_title="",
                    xaxis=dict(range=[0, 100])
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Dicas para alcançar os objetivos
        with st.expander("Dicas para alcançar seus objetivos financeiros"):
            st.markdown("""
            ### Como alcançar seus objetivos financeiros
            
            1. **Seja realista**: Estabeleça metas que sejam desafiadoras, mas alcançáveis
            2. **Automatize suas finanças**: Configure transferências automáticas para suas contas de investimento
            3. **Revise regularmente**: Acompanhe seu progresso mensalmente e ajuste conforme necessário
            4. **Diversifique investimentos**: Diferentes objetivos podem exigir diferentes estratégias de investimento
            5. **Priorize seus objetivos**: Foque nos objetivos mais importantes ou nos que têm prazos mais curtos
            6. **Celebre as conquistas**: Comemore quando atingir marcos importantes rumo aos seus objetivos
            
            ### Estratégias por tipo de objetivo:
            
            - **Curto prazo** (até 2 anos): Priorize liquidez e segurança (CDB, Tesouro Selic)
            - **Médio prazo** (2-5 anos): Equilibre risco e retorno (Tesouro IPCA+, fundos multimercado)
            - **Longo prazo** (mais de 5 anos): Foque no crescimento (ações, fundos imobiliários)
            """)

def modificar_investimentos_page():
    """
    Modifica a página de investimentos para atualizar o progresso dos objetivos
    quando um investimento é atualizado.
    """
    # Esta função será chamada para modificar a função add_investimento
    # no arquivo de funções de dados para que recalcule o progresso dos objetivos
    pass 