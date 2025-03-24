"""
Módulo para a página de Investimentos do aplicativo de Controle Financeiro Pessoal.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

# Importar funções de manipulação de dados
from app.data.data_handler import (
    load_user_data,
    load_investimentos,
    save_investimentos,
    add_investimento,
    calcular_progresso_objetivos
)

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    """
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def render_investimentos_page():
    """
    Renderiza a página de Gestão de Investimentos.
    """
    # Cabeçalho moderno
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-right: 0.8rem;">📈</div>
        <div>
            <h1 style="margin: 0; padding: 0;">Gestão de Investimentos</h1>
            <p style="margin: 0; padding: 0; color: var(--gray);">Acompanhe e gerencie seus investimentos</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar investimentos
    investimentos = load_investimentos()
    
    # Botão em destaque para adicionar novo investimento
    col_btn, col_empty = st.columns([1, 3])
    with col_btn:
        if st.button("➕ Adicionar Investimento", type="primary", use_container_width=True, key="btn_add_investimento"):
            st.session_state.mostrar_form_investimento = True
            
    # Se o botão foi clicado, mostrar o formulário
    if st.session_state.get("mostrar_form_investimento", False):
        with st.expander("Novo Investimento", expanded=True):
            with st.form("form_novo_investimento"):
                st.markdown("### Registre seu investimento")
                
                descricao = st.text_input("Qual investimento você fez?", 
                                        help="Ex: Tesouro Direto, Ações, Fundos Imobiliários, etc.")
                
                col1, col2 = st.columns(2)
                with col1:
                    valor_inicial = st.number_input(
                        "Valor investido (R$)", 
                        min_value=0.01, 
                        step=100.0,
                        format="%.2f"
                    )
                
                with col2:
                    valor_atual = st.number_input(
                        "Valor atual (R$)", 
                        min_value=0.01, 
                        step=100.0,
                        format="%.2f"
                    )
                
                col3, col4 = st.columns(2)
                with col3:
                    data_inicio = st.date_input("Data do investimento", value=datetime.now())
                
                with col4:
                    rentabilidade_anual = st.number_input(
                        "Rentabilidade anual (%)", 
                        min_value=0.0, 
                        value=0.0,
                        step=0.1,
                        format="%.2f"
                    )
                
                st.markdown("### Categoria")
                categoria = st.selectbox(
                    "Tipo de investimento:",
                    options=[
                        "Renda Fixa", "Renda Variável", "Fundos", 
                        "Imóveis", "Criptomoedas", "Outros"
                    ]
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("💾 Salvar investimento", use_container_width=True)
                with col_btn2:
                    cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if submitted:
                    # Criar novo investimento
                    novo_investimento = {
                        "descricao": descricao,
                        "valor_inicial": valor_inicial,
                        "valor_atual": valor_atual,
                        "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                        "rentabilidade_anual": rentabilidade_anual,
                        "categoria": categoria
                    }
                    
                    # Adicionar à lista
                    if add_investimento(novo_investimento):
                        # Recalcular progresso dos objetivos
                        # Comentado temporariamente: calcular_progresso_objetivos()
                        st.success("Investimento adicionado com sucesso!")
                        st.session_state.mostrar_form_investimento = False
                        st.rerun()
                    else:
                        st.error("Erro ao adicionar investimento.")
                
                if cancel:
                    st.session_state.mostrar_form_investimento = False
                    st.rerun()
    
    # Separar investimentos em categorias para exibição em tabs
    categorias = {
        "Renda Fixa": [],
        "Renda Variável": [],
        "Fundos": [],
        "Imóveis": [],
        "Criptomoedas": [],
        "Outros": []
    }
    
    # Total investido
    total_investido = sum(inv.get("valor_inicial", 0) for inv in investimentos)
    total_atual = sum(inv.get("valor_atual", 0) for inv in investimentos)
    rentabilidade_total = ((total_atual / total_investido) - 1) * 100 if total_investido > 0 else 0
    
    # Preencher categorias
    for inv in investimentos:
        categoria = inv.get("categoria", "Outros")
        if categoria in categorias:
            categorias[categoria].append(inv)
    
    # Exibir resumo em cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Total Investido</div>
            <div class="metric-value">{formatar_moeda(total_investido)}</div>
            <div>Valor inicial aplicado</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Valor Atual</div>
            <div class="metric-value">{formatar_moeda(total_atual)}</div>
            <div>Patrimônio investido atual</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Escolher classe de cor com base na rentabilidade
        card_class = "success" if rentabilidade_total > 0 else "danger" if rentabilidade_total < 0 else ""
        
        st.markdown(f"""
        <div class="card {card_class}">
            <div class="metric-label">Rentabilidade</div>
            <div class="metric-value">{rentabilidade_total:.2f}%</div>
            <div>Rendimento total</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de distribuição por categoria
    if investimentos:
        st.subheader("Distribuição por Categoria")
        
        # Preparar dados para o gráfico
        valores_por_categoria = {}
        for categoria, invs in categorias.items():
            if invs:  # Se tem investimentos na categoria
                valores_por_categoria[categoria] = sum(inv.get("valor_atual", 0) for inv in invs)
        
        # Criar Dataframe
        df_categorias = pd.DataFrame({
            "Categoria": valores_por_categoria.keys(),
            "Valor": valores_por_categoria.values()
        })
        
        # Criar gráfico de pizza
        cores = ['#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#0099C6']
        
        fig = px.pie(
            df_categorias, 
            values="Valor", 
            names="Categoria",
            color_discrete_sequence=cores,
            hole=0.4
        )
        
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            annotations=[dict(
                text=f"Total<br>{formatar_moeda(total_atual)}",
                x=0.5, y=0.5,
                font_size=14,
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Exibir investimentos por categoria
    categoria_tabs = st.tabs(list(categorias.keys()))
    
    for i, (categoria, tab) in enumerate(zip(categorias.keys(), categoria_tabs)):
        with tab:
            if categorias[categoria]:
                # Criar cards para cada investimento
                for inv in categorias[categoria]:
                    # Calcular rentabilidade de cada investimento
                    valor_inicial = inv.get("valor_inicial", 0)
                    valor_atual = inv.get("valor_atual", 0)
                    
                    if valor_inicial > 0:
                        rentabilidade = ((valor_atual / valor_inicial) - 1) * 100
                    else:
                        rentabilidade = 0
                    
                    # Determinar classe de cor com base na rentabilidade
                    card_class = "success" if rentabilidade > 0 else "danger" if rentabilidade < 0 else ""
                    
                    # Data formatada
                    data_inicio = datetime.strptime(inv.get("data_inicio", "2023-01-01"), "%Y-%m-%d")
                    data_formatada = data_inicio.strftime("%d/%m/%Y")
                    
                    # Calcular tempo decorrido
                    dias_decorridos = (datetime.now() - data_inicio).days
                    
                    if dias_decorridos < 30:
                        tempo_decorrido = f"{dias_decorridos} dias"
                    elif dias_decorridos < 365:
                        meses = dias_decorridos // 30
                        tempo_decorrido = f"{meses} {'mês' if meses == 1 else 'meses'}"
                    else:
                        anos = dias_decorridos // 365
                        tempo_decorrido = f"{anos} {'ano' if anos == 1 else 'anos'}"
                    
                    # Criar card
                    st.markdown(f"""
                    <div class="card {card_class}" style="margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 1.1rem; font-weight: 500;">{inv.get('descricao', 'Investimento')}</div>
                            <div style="font-size: 1.2rem; font-weight: 600;">{formatar_moeda(valor_atual)}</div>
                        </div>
                        <div style="margin: 10px 0; display: flex; justify-content: space-between;">
                            <div>Valor inicial: {formatar_moeda(valor_inicial)}</div>
                            <div>Rentabilidade: {rentabilidade:.2f}%</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: var(--gray);">
                            <div>Desde {data_formatada} ({tempo_decorrido})</div>
                            <div>Anual: {float(inv.get('rentabilidade_anual', 0) or 0):.2f}%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(f"Você ainda não possui investimentos na categoria {categoria}.")
    
    # Criar abas para a página de investimentos
    tab1, tab2, tab3 = st.tabs(["Resumo", "Carteira", "Análise"])
    
    # Aba de Resumo
    with tab1:
        st.subheader("Resumo de Investimentos")
        
        if not investimentos:
            st.info("Você ainda não tem investimentos cadastrados. Adicione seu primeiro investimento!")
        else:
            # Mostrar cards com resumo
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Investido",
                    formatar_moeda(total_investido),
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Valor Atual",
                    formatar_moeda(total_atual),
                    delta=formatar_moeda(total_atual - total_investido)
                )
            
            with col3:
                # Escolher classe de cor com base na rentabilidade
                arrow = "↑" if rentabilidade_total > 0 else "↓" if rentabilidade_total < 0 else ""
                st.metric(
                    "Rentabilidade Total",
                    f"{rentabilidade_total:.2f}%",
                    delta=arrow,
                    delta_color="normal" if rentabilidade_total == 0 else "normal" if rentabilidade_total > 0 else "inverse"
                )
            
            # Mostrar gráfico de distribuição por categoria
            st.subheader("Distribuição por Categoria")
            
            # Agrupar investimentos por categoria
            df_categorias = pd.DataFrame({
                "Categoria": [inv.get("categoria", "Outros") for inv in investimentos],
                "Valor": [(inv.get("valor_atual", 0) or 0) for inv in investimentos]
            })
            
            df_categorias = df_categorias.groupby("Categoria").sum().reset_index()
            
            cores = ['#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#0099C6']
            
            fig = px.pie(
                df_categorias,
                values="Valor",
                names="Categoria",
                color_discrete_sequence=cores,
                hole=0.4
            )
            
            fig.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                annotations=[dict(
                    text=f"Total<br>{formatar_moeda(total_atual)}",
                    x=0.5, y=0.5,
                    font_size=14,
                    showarrow=False
                )]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    # Aba de Carteira
    with tab2:
        st.subheader("Gerenciar Investimentos")
        
        if not investimentos:
            st.info("Adicione seu primeiro investimento usando o botão acima.")
        else:
            # Mostrar tabela de investimentos
            df = pd.DataFrame(investimentos)
            
            # Verifica se as colunas existem antes de tentar acessá-las
            colunas_exibicao = ["descricao", "categoria", "valor_inicial", "valor_atual", "data_inicio", "rentabilidade_anual"]
            colunas_disponiveis = [col for col in colunas_exibicao if col in df.columns]
            
            if colunas_disponiveis:
                # Preparar dados para exibição
                df_exibicao = df[colunas_disponiveis].copy()
                
                # Renomear colunas
                mapeamento_colunas = {
                    "descricao": "Descrição",
                    "categoria": "Categoria",
                    "valor_inicial": "Valor Inicial",
                    "valor_atual": "Valor Atual",
                    "data_inicio": "Data de Início",
                    "rentabilidade_anual": "Rendimento Anual (%)"
                }
                
                df_exibicao = df_exibicao.rename(columns={
                    col: mapeamento_colunas.get(col, col)
                    for col in colunas_disponiveis
                })
                
                # Formatar valores monetários
                if "Valor Inicial" in df_exibicao.columns:
                    df_exibicao["Valor Inicial"] = df_exibicao["Valor Inicial"].apply(
                        lambda x: formatar_moeda(x) if pd.notna(x) else "R$ 0,00"
                    )
                
                if "Valor Atual" in df_exibicao.columns:
                    df_exibicao["Valor Atual"] = df_exibicao["Valor Atual"].apply(
                        lambda x: formatar_moeda(x) if pd.notna(x) else "R$ 0,00"
                    )
                
                st.dataframe(df_exibicao, use_container_width=True)
            
            # Opção para excluir investimento
            st.subheader("Excluir Investimento")
            
            # Criar lista de opções para exclusão
            opcoes_exclusao = [f"{inv.get('descricao', 'Investimento')} - {formatar_moeda(inv.get('valor_atual', 0))}" for inv in investimentos]
            opcoes_dict = {opcao: i for i, opcao in enumerate(opcoes_exclusao)}
            
            if opcoes_exclusao:
                inv_selecionado = st.selectbox(
                    "Selecione o investimento para excluir:",
                    options=list(opcoes_dict.keys())
                )
                
                if st.button("🗑️ Excluir Investimento", type="primary", key="btn_excluir_investimento_2"):
                    indice = opcoes_dict[inv_selecionado]
                    inv_para_excluir = investimentos[indice]
                    
                    for i, inv in enumerate(investimentos):
                        if all(inv[k] == inv_para_excluir[k] for k in inv_para_excluir.keys()):
                            investimentos.pop(i)
                            if save_investimentos(investimentos):
                                # Recalcular progresso dos objetivos após excluir um investimento
                                # Comentado temporariamente: calcular_progresso_objetivos()
                                st.success(f"Investimento '{inv_para_excluir.get('descricao', 'Investimento sem nome')}' excluído com sucesso!")
                                st.rerun()
                            break
    
    # Aba de Análise
    with tab3:
        st.subheader("Análise de Investimentos")
        
        if not investimentos:
            st.info("Adicione investimentos para visualizar análises.")
        else:
            # Calcular rentabilidade média ponderada
            valor_total = sum((inv.get("valor_atual", 0) or 0) for inv in investimentos)
            rentabilidade_media = 0  # Inicializar valor padrão
            
            if valor_total > 0:
                rentabilidade_media = sum(
                    (inv.get("rentabilidade_anual", 0) or 0) * (inv.get("valor_atual", 0) or 0) / valor_total 
                    for inv in investimentos
                )
                
                # Mostrar rentabilidade média
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Rentabilidade Média Anual", 
                        f"{rentabilidade_media:.2f}%",
                        help="Média ponderada pelo valor atual de cada investimento"
                    )
                
                with col2:
                    # Calcular projeção para 1 ano
                    projecao_1_ano = valor_total * (1 + rentabilidade_media/100)
                    ganho_1_ano = projecao_1_ano - valor_total
                    
                    st.metric(
                        "Ganho Projetado (1 ano)", 
                        formatar_moeda(ganho_1_ano),
                        f"+{ganho_1_ano/valor_total*100:.2f}%",
                        help="Projeção baseada na rentabilidade média atual"
                    )
            
            # Criar gráfico de rentabilidade por categoria
            categorias_rent = {}
            categorias_valor = {}
            
            for inv in investimentos:
                categoria = inv.get("categoria", "Outros")
                rent = inv.get("rentabilidade_anual", 0) or 0  # Garantir que não seja None
                valor = inv.get("valor_atual", 0) or 0  # Garantir que não seja None
                
                if categoria not in categorias_rent:
                    categorias_rent[categoria] = 0
                    categorias_valor[categoria] = 0
                
                categorias_rent[categoria] += rent * valor
                categorias_valor[categoria] += valor
            
            # Calcular média ponderada por categoria
            for categoria in categorias_rent:
                if categorias_valor[categoria] > 0:
                    categorias_rent[categoria] /= categorias_valor[categoria]
            
            # Criar DataFrame para o gráfico
            df_rent = pd.DataFrame({
                'Categoria': list(categorias_rent.keys()),
                'Rentabilidade': list(categorias_rent.values())
            })
            
            # Ordenar por rentabilidade
            df_rent = df_rent.sort_values('Rentabilidade', ascending=False)
            
            # Criar gráfico
            fig_rent = px.bar(
                df_rent,
                x='Categoria',
                y='Rentabilidade',
                title='Rentabilidade Anual por Categoria (%)',
                color='Rentabilidade',
                color_continuous_scale=['#F44336', '#FFEB3B', '#4CAF50'],
                text='Rentabilidade'
            )
            
            fig_rent.update_traces(
                texttemplate='%{text:.2f}%', 
                textposition='outside'
            )
            
            fig_rent.update_layout(
                xaxis_title="",
                yaxis_title="Rentabilidade Anual (%)",
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig_rent, use_container_width=True)
            
            # Opções de previsão
            st.subheader("Simulador de Crescimento")
            
            col_sim1, col_sim2 = st.columns(2)
            
            with col_sim1:
                aporte_mensal = st.number_input(
                    "Aporte Mensal (R$):", 
                    min_value=0.0, 
                    value=200.0, 
                    step=100.0
                )
            
            with col_sim2:
                anos_projecao = st.slider(
                    "Período de Projeção (anos):", 
                    min_value=1, 
                    max_value=30, 
                    value=10
                )
            
            # Calcular projeção
            valor_final = valor_total
            valores_projecao = [valor_final]
            
            for i in range(anos_projecao * 12):
                # Adicionar aporte mensal
                valor_final += aporte_mensal
                
                # Aplicar rentabilidade mensal (rentabilidade anual / 12)
                valor_final *= (1 + rentabilidade_media / 100 / 12)
                
                # Guardar valor a cada 12 meses para o gráfico
                if (i + 1) % 12 == 0:
                    valores_projecao.append(valor_final)
            
            # Garantir que temos o número correto de valores
            while len(valores_projecao) < anos_projecao + 1:
                valores_projecao.append(valor_final)
            
            # Criar DataFrame para o gráfico
            df_projecao = pd.DataFrame({
                'Ano': list(range(anos_projecao + 1)),
                'Valor': valores_projecao[:anos_projecao + 1]  # Limitar ao número correto de anos
            })
            
            # Mostrar resultados
            st.markdown(f"### Resultado da Simulação")
            st.markdown(f"""
            <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:20px; border-radius:10px; margin-bottom:20px;">
                <h4>Valor Final Projetado:</h4>
                <h2 style="color: #4CAF50; margin:10px 0 0 0;">{formatar_moeda(valor_final)}</h2>
                <p>Aportes: {formatar_moeda(aporte_mensal * anos_projecao * 12)}</p>
                <p>Rendimentos: {formatar_moeda(valor_final - valor_total - (aporte_mensal * anos_projecao * 12))}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Criar gráfico
            fig_projecao = px.line(
                df_projecao,
                x='Ano',
                y='Valor',
                title=f"Projeção de Crescimento para {anos_projecao} anos",
                markers=True
            )
            
            fig_projecao.update_traces(
                line=dict(width=3, color='#4CAF50'),
                marker=dict(size=8, color='#1E88E5')
            )
            
            fig_projecao.update_layout(
                xaxis_title="Ano",
                yaxis_title="Valor Projetado (R$)",
                hovermode="x unified"
            )
            
            # Formatar valores no hover
            fig_projecao.update_traces(
                hovertemplate="Ano %{x}<br>Valor: " + 
                            f"{formatar_moeda(0).replace('0', '%{y:,.2f}')}"
            )
            
            st.plotly_chart(fig_projecao, use_container_width=True) 