"""
Módulo para a página de Seguros do aplicativo de Controle Financeiro Pessoal.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Importar funções de manipulação de dados
from data.data_handler import (
    load_user_data,
    load_seguros,
    save_seguros
)

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    """
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_dias_para_vencimento(seguro):
    """
    Calcula quantos dias faltam para o vencimento do seguro.
    
    Args:
        seguro (dict): Objeto seguro contendo data de vencimento ou renovação
        
    Returns:
        int: Número de dias até o vencimento, negativo se já venceu, None se não houver data
    """
    # Verificar campos de data comuns para compatibilidade
    data_vencimento = None
    
    # Tentar obter a data do campo de vencimento ou renovação, caso um deles esteja definido
    if "data_vencimento" in seguro:
        data_vencimento = seguro["data_vencimento"]
    elif "data_renovacao" in seguro:
        data_vencimento = seguro["data_renovacao"]
    
    if not data_vencimento:
        return -1  # Valor padrão se não houver data
    
    try:
        data_venc = datetime.strptime(data_vencimento, "%Y-%m-%d")
        hoje = datetime.now()
        return (data_venc - hoje).days
    except (ValueError, TypeError):
        return -1

def render_seguros_page():
    """
    Renderiza a página de Controle de Seguros.
    """
    # Cabeçalho moderno
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-right: 0.8rem;">🛡️</div>
        <div>
            <h1 style="margin: 0; padding: 0;">Gestão de Seguros</h1>
            <p style="margin: 0; padding: 0; color: var(--gray);">Acompanhe e gerencie suas apólices de seguros</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados de seguros
    seguros = load_seguros()
    
    # Botão em destaque para adicionar novo seguro
    col_btn, col_empty = st.columns([1, 3])
    with col_btn:
        if st.button("➕ Adicionar Seguro", type="primary", use_container_width=True):
            st.session_state.mostrar_form_seguro = True
            
    # Se o botão foi clicado, mostrar o formulário
    if st.session_state.get("mostrar_form_seguro", False):
        with st.expander("Novo Seguro", expanded=True):
            with st.form("form_novo_seguro"):
                st.markdown("### Registre seu seguro")
                
                # Informações básicas
                descricao = st.text_input("Descrição do seguro", help="Ex: Seguro Auto, Seguro Residencial, etc.")
                
                # Tipo de seguro
                st.markdown("### Tipo de seguro")
                categoria = st.radio(
                    "Selecione o tipo:",
                    options=[
                        "🚗 Automóvel",
                        "🏠 Residencial",
                        "💊 Saúde",
                        "⚰️ Vida",
                        "🔒 Garantia",
                        "📱 Eletrônicos",
                        "🧳 Viagem",
                        "📦 Outros"
                    ],
                    horizontal=True,
                    format_func=lambda x: x.split(" ", 1)[1]  # Remove o emoji
                )
                
                # Remover emoji para armazenar
                categoria = categoria.split(" ", 1)[1]
                
                # Seguradora
                seguradora = st.text_input("Seguradora", help="Nome da empresa que oferece o seguro")
                
                # Valores
                col1, col2 = st.columns(2)
                with col1:
                    premio_anual = st.number_input(
                        "Prêmio anual (R$)",
                        min_value=0.01,
                        step=100.0,
                        format="%.2f",
                        help="Valor pago anualmente pelo seguro"
                    )
                
                with col2:
                    valor_cobertura = st.number_input(
                        "Valor da cobertura (R$)",
                        min_value=0.0,
                        step=1000.0,
                        format="%.2f",
                        help="Valor máximo coberto pelo seguro (opcional)"
                    )
                
                # Datas
                col3, col4 = st.columns(2)
                with col3:
                    data_contratacao = st.date_input(
                        "Data de contratação",
                        value=datetime.now(),
                        help="Quando o seguro foi contratado"
                    )
                
                with col4:
                    data_vencimento = st.date_input(
                        "Data de vencimento",
                        value=datetime.now() + timedelta(days=365),
                        help="Quando o seguro expira/precisa ser renovado"
                    )
                
                # Observações (opcional)
                observacoes = st.text_area(
                    "Observações",
                    placeholder="Detalhes adicionais sobre o seguro...",
                    help="Informações importantes sobre o seguro (opcional)"
                )
                
                # Botões de ação
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("💾 Salvar seguro", use_container_width=True)
                with col_btn2:
                    cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if submitted:
                    # Criar novo seguro
                    novo_seguro = {
                        "descricao": descricao,
                        "categoria": categoria,
                        "seguradora": seguradora,
                        "premio_anual": premio_anual,
                        "valor_cobertura": valor_cobertura,
                        "data_contratacao": data_contratacao.strftime("%Y-%m-%d"),
                        "data_vencimento": data_vencimento.strftime("%Y-%m-%d"),
                        "observacoes": observacoes
                    }
                    
                    # Adicionar à lista
                    if add_seguro(novo_seguro):
                        st.success("Seguro adicionado com sucesso!")
                        st.session_state.mostrar_form_seguro = False
                        st.rerun()
                    else:
                        st.error("Erro ao adicionar seguro.")
                
                if cancel:
                    st.session_state.mostrar_form_seguro = False
                    st.rerun()
    
    # Calcular totais
    total_premio_anual = sum(float(s.get("premio_anual", 0) or 0) for s in seguros)
    total_premio_mensal = total_premio_anual / 12 if total_premio_anual else 0
    total_cobertura = sum(float(s.get("valor_cobertura", 0) or 0) for s in seguros)
    
    # Mostrar resumo em cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Total de Seguros</div>
            <div class="metric-value">{len(seguros)}</div>
            <div>Apólices ativas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card danger">
            <div class="metric-label">Custo Anual</div>
            <div class="metric-value">{formatar_moeda(total_premio_anual)}</div>
            <div>Valor pago por ano</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card warning">
            <div class="metric-label">Custo Mensal</div>
            <div class="metric-value">{formatar_moeda(total_premio_mensal)}</div>
            <div>Valor médio mensal</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="card success">
            <div class="metric-label">Capital Segurado</div>
            <div class="metric-value">{formatar_moeda(total_cobertura)}</div>
            <div>Valor total coberto</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Criar abas para diferentes visualizações
    tab1, tab2 = st.tabs(["Todos os Seguros", "Próximos Vencimentos"])
    
    with tab1:
        if seguros:
            # Listagem de seguros em forma de cards
            st.subheader("Lista de Seguros")
            
            # Ordenar seguros por data de vencimento ou renovação
            def obter_data_vencimento(seguro):
                if "data_vencimento" in seguro:
                    return seguro["data_vencimento"]
                elif "data_renovacao" in seguro:
                    return seguro["data_renovacao"]
                return "2099-12-31"  # Data distante para itens sem vencimento
            
            seguros_ordenados = sorted(
                seguros,
                key=lambda x: datetime.strptime(obter_data_vencimento(x), "%Y-%m-%d")
            )
            
            for seguro in seguros_ordenados:
                # Calcular dias para vencimento
                dias_para_vencimento = calcular_dias_para_vencimento(seguro)
                
                # Definir classe de status com base no vencimento
                status_class = ""
                status_text = ""
                
                if dias_para_vencimento < 0:
                    status_class = "danger"
                    status_text = f"Vencido há {abs(dias_para_vencimento)} dias"
                elif dias_para_vencimento == 0:
                    status_class = "danger"
                    status_text = "Vence hoje!"
                elif dias_para_vencimento <= 30:
                    status_class = "warning"
                    status_text = f"Vence em {dias_para_vencimento} dias"
                else:
                    status_class = "success"
                    status_text = f"Vence em {dias_para_vencimento} dias"
                
                # Formatar datas
                data_contratacao = datetime.strptime(seguro.get("data_contratacao", "2023-01-01"), "%Y-%m-%d")
                data_contratacao_formatada = data_contratacao.strftime("%d/%m/%Y")
                
                data_vencimento = datetime.strptime(seguro.get("data_vencimento", "2099-12-31"), "%Y-%m-%d")
                data_vencimento_formatada = data_vencimento.strftime("%d/%m/%Y")
                
                # Criar card para cada seguro
                st.markdown(f"""
                <div class="card" style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 1.1rem; font-weight: 500;">{seguro.get('descricao', 'Seguro')}</div>
                        <div class="badge {status_class}">{status_text}</div>
                    </div>
                    <div style="margin: 10px 0;">
                        <div>Seguradora: <strong>{seguro.get('seguradora', 'Não informada')}</strong></div>
                        <div>Categoria: {seguro.get('categoria', 'Não categorizado')}</div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <div>Prêmio anual: <strong>{formatar_moeda(seguro.get('premio_anual', 0))}</strong></div>
                        <div>Cobertura: <strong>{formatar_moeda(seguro.get('valor_cobertura', 0))}</strong></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: var(--gray); font-size: 0.9rem;">
                        <div>Contratado em: {data_contratacao_formatada}</div>
                        <div>Válido até: {data_vencimento_formatada}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Você ainda não possui seguros registrados.")
    
    with tab2:
        st.subheader("Próximos Vencimentos")
        
        if seguros:
            # Calcular dias para vencimento e adicionar à lista
            seguros_com_vencimento = []
            for seguro in seguros:
                dias = calcular_dias_para_vencimento(seguro)
                if dias is not None:
                    seguro_temp = seguro.copy()
                    seguro_temp["dias_para_vencimento"] = dias
                    seguros_com_vencimento.append(seguro_temp)
            
            # Ordenar por data de vencimento (mais próxima primeiro)
            seguros_vencimento = sorted(seguros_com_vencimento, key=lambda x: x.get("dias_para_vencimento", 999999))
            
            # Criar tabela de próximos vencimentos
            st.markdown("""
            <style>
            .vencimento-tabela {
                width: 100%;
                border-collapse: collapse;
            }
            .vencimento-tabela th {
                text-align: left;
                padding: 8px;
                border-bottom: 2px solid var(--gray-light);
            }
            .vencimento-tabela td {
                text-align: left;
                padding: 12px 8px;
                border-bottom: 1px solid var(--gray-lighter);
            }
            .premio-coluna {
                text-align: right;
                font-weight: 500;
            }
            .data-coluna {
                text-align: center;
            }
            </style>
            
            <table class="vencimento-tabela">
                <thead>
                    <tr>
                        <th>Descrição</th>
                        <th>Seguradora</th>
                        <th class="premio-coluna">Prêmio Anual</th>
                        <th class="data-coluna">Vencimento</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
            """, unsafe_allow_html=True)
            
            for seguro in seguros_vencimento:
                dias = seguro.get("dias_para_vencimento", 0)
                
                # Formatar data de vencimento
                data_vencimento = datetime.strptime(seguro.get("data_vencimento", "2099-12-31"), "%Y-%m-%d")
                data_formatada = data_vencimento.strftime("%d/%m/%Y")
                
                # Definir status com base nos dias para vencimento
                status_class = ""
                status_text = ""
                
                if dias < 0:
                    status_class = "vencido"
                    status_text = f"Vencido há {abs(dias)} dias"
                elif dias == 0:
                    status_class = "vencido"
                    status_text = "Vence hoje!"
                elif dias <= 30:
                    status_class = "proximo"
                    status_text = f"Vence em {dias} dias"
                else:
                    status_class = "futuro"
                    status_text = f"Vence em {dias} dias"
                
                st.markdown(f"""
                <tr>
                    <td>{seguro.get('descricao', 'Seguro')}</td>
                    <td>{seguro.get('seguradora', 'Não informada')}</td>
                    <td class="premio-coluna">{formatar_moeda(seguro.get('premio_anual', 0))}</td>
                    <td class="data-coluna">{data_formatada}</td>
                    <td><div class="badge-vencimento {status_class}">{status_text}</div></td>
                </tr>
                """, unsafe_allow_html=True)
            
            st.markdown("</tbody></table>", unsafe_allow_html=True)
        else:
            st.info("Você ainda não possui seguros registrados.")
    
    # Opção para excluir ou renovar seguros
    if seguros:
        st.markdown("### Gerenciar Seguros")
        
        col_excluir, col_renovar = st.columns(2)
        
        with col_excluir:
            st.subheader("Excluir Seguro")
            
            opcoes_exclusao = [f"{s.get('descricao', 'Seguro sem nome')} - {formatar_moeda(s.get('premio_anual', 0))}" for s in seguros]
            opcoes_dict = {opcao: i for i, opcao in enumerate(opcoes_exclusao)}
            
            seguro_para_excluir = st.selectbox(
                "Selecione um seguro para excluir:",
                options=list(opcoes_dict.keys()),
                key="excluir_seguro"
            )
            
            if st.button("🗑️ Excluir Seguro", type="primary"):
                indice = opcoes_dict[seguro_para_excluir]
                seguro_excluir = seguros[indice]
                
                # Encontrar e remover o seguro
                for i, seguro in enumerate(seguros):
                    if all(seguro.get(k) == seguro_excluir.get(k) for k in seguro_excluir.keys()):
                        seguros.pop(i)
                        save_seguros(seguros)
                        st.success(f"Seguro '{seguro_excluir.get('descricao', 'Seguro sem nome')}' excluído com sucesso!")
                        st.rerun()
                        break
        
        with col_renovar:
            st.subheader("Renovar Seguro")
            
            # Filtrar seguros próximos do vencimento
            seguros_para_renovar = []
            for seguro in seguros:
                dias = calcular_dias_para_vencimento(seguro)
                if dias is not None and dias <= 60:  # Mostrar apenas seguros a vencer em até 60 dias
                    seguros_para_renovar.append(seguro)
            
            if seguros_para_renovar:
                opcoes_renovacao = [f"{s.get('descricao', 'Seguro sem nome')} - Vence em {calcular_dias_para_vencimento(s)} dias" for s in seguros_para_renovar]
                opcoes_dict_renovacao = {opcao: i for i, opcao in enumerate(opcoes_renovacao)}
                
                seguro_para_renovar = st.selectbox(
                    "Selecione um seguro para renovar:",
                    options=list(opcoes_dict_renovacao.keys()),
                    key="renovar_seguro"
                )
                
                # Pegar o índice nos seguros para renovar
                indice_renovar = opcoes_dict_renovacao[seguro_para_renovar]
                seguro_selecionado = seguros_para_renovar[indice_renovar]
                
                # Encontrar o índice na lista completa de seguros
                indice_original = next((i for i, s in enumerate(seguros) if all(s.get(k) == seguro_selecionado.get(k) for k in seguro_selecionado.keys())), None)
                
                if indice_original is not None:
                    # Opções de renovação
                    col_data, col_premio = st.columns(2)
                    
                    with col_data:
                        data_vencimento_atual = datetime.strptime(seguro_selecionado.get("data_vencimento", "2099-12-31"), "%Y-%m-%d")
                        nova_data_vencimento = st.date_input(
                            "Nova data de vencimento:",
                            value=data_vencimento_atual + timedelta(days=365),
                            min_value=datetime.now()
                        )
                    
                    with col_premio:
                        premio_atual = seguro_selecionado.get("premio_anual", 0)
                        novo_premio = st.number_input(
                            "Novo prêmio anual (R$):",
                            min_value=0.0,
                            value=float(premio_atual),
                            step=100.0,
                            format="%.2f"
                        )
                    
                    if st.button("♻️ Renovar Seguro", type="primary"):
                        # Atualizar o seguro com as novas informações
                        seguros[indice_original]["data_renovacao"] = datetime.now().strftime("%Y-%m-%d")
                        seguros[indice_original]["data_vencimento"] = nova_data_vencimento.strftime("%Y-%m-%d")
                        seguros[indice_original]["premio_anual"] = novo_premio
                        
                        # Salvar as alterações
                        save_seguros(seguros)
                        st.success(f"Seguro '{seguro_selecionado.get('descricao', 'Seguro sem nome')}' renovado com sucesso!")
                        st.rerun()
            else:
                st.info("Não há seguros próximos do vencimento para renovar.")
    
    # Informação educativa sobre seguros
    with st.expander("Saiba mais sobre seguros"):
        st.markdown("""
        ### A importância dos seguros
        
        Seguros são uma parte essencial de um plano financeiro sólido. Eles protegem você e sua família contra riscos e perdas financeiras significativas.
        
        #### Dicas para escolher seguros:
        
        1. **Priorize os seguros essenciais**: Saúde, vida (se você tem dependentes), residencial e automóvel são geralmente os mais importantes
        2. **Compare ofertas**: Obtenha cotações de várias seguradoras antes de decidir
        3. **Revise anualmente**: Suas necessidades mudam com o tempo, então avalie seus seguros regularmente
        4. **Não pague por coberturas desnecessárias**: Escolha apenas os complementos que realmente fazem sentido para sua situação
        5. **Leia a apólice com atenção**: Entenda exatamente o que está coberto e o que não está
        
        #### Seguros comuns e suas funções:
        
        - **Seguro de Vida**: Protege seus dependentes financeiramente em caso de falecimento
        - **Seguro Saúde**: Cobre despesas médicas e hospitalares
        - **Seguro Residencial**: Protege sua casa contra incêndios, roubos e outros danos
        - **Seguro Auto**: Cobre danos ao seu veículo e responsabilidade civil contra terceiros
        - **Seguro de Garantia Estendida**: Prolonga a garantia de produtos eletrônicos e eletrodomésticos
        """)

def add_seguro(seguro):
    """
    Adiciona um novo seguro à lista.
    
    Args:
        seguro (dict): Dados do seguro para adicionar
        
    Returns:
        bool: True se adicionado com sucesso, False caso contrário
    """
    try:
        # Garantir compatibilidade com os nomes dos campos nos dados de exemplo
        if "data_inicio" in seguro and "data_contratacao" not in seguro:
            seguro["data_contratacao"] = seguro["data_inicio"]
            del seguro["data_inicio"]
            
        if "data_vencimento" in seguro and "data_renovacao" not in seguro:
            seguro["data_renovacao"] = seguro["data_vencimento"]
            del seguro["data_vencimento"]
            
        # Importar a função add_seguro do data_handler
        from data.data_handler import add_seguro as dh_add_seguro
        return dh_add_seguro(seguro)
    except Exception as e:
        st.error(f"Erro ao adicionar seguro: {str(e)}")
        return False 