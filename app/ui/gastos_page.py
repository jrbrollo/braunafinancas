"""
Módulo para a página de Controle de Gastos do aplicativo de Controle Financeiro Pessoal.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Importar funções de manipulação de dados
from data.data_handler import (
    load_user_data,
    load_gastos,
    save_gastos,
    add_gasto,
    load_data,
    save_data
)

def calcular_total_gastos_por_semana(gastos, mes):
    """
    Calcula o total de gastos por semana do mês.
    """
    # Filtrar gastos do mês
    gastos_mes = [g for g in gastos if g["data"].startswith(mes)]
    
    # Inicializar variáveis para acumular os totais por semana
    semanas = {
        "Semana 1 (1-7)": {"fixo": 0, "variavel": 0},
        "Semana 2 (8-14)": {"fixo": 0, "variavel": 0},
        "Semana 3 (15-21)": {"fixo": 0, "variavel": 0},
        "Semana 4 (22-31)": {"fixo": 0, "variavel": 0}
    }
    
    # Somar gastos por semana e tipo
    for gasto in gastos_mes:
        dia = int(gasto["data"].split("-")[-1])
        
        if 1 <= dia <= 7:
            semana = "Semana 1 (1-7)"
        elif 8 <= dia <= 14:
            semana = "Semana 2 (8-14)"
        elif 15 <= dia <= 21:
            semana = "Semana 3 (15-21)"
        else:
            semana = "Semana 4 (22-31)"
        
        # Verificar o tipo (fixo ou variável)
        tipo_lower = gasto["tipo"].lower()
        if tipo_lower == "fixo":
            semanas[semana]["fixo"] += gasto["valor"]
        else:
            semanas[semana]["variavel"] += gasto["valor"]
    
    return semanas

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def criar_grafico_barras_semanal(dados_semanas):
    """
    Cria um gráfico de barras mostrando os gastos por semana.
    """
    semanas = list(dados_semanas.keys())
    gastos_fixos = [dados_semanas[s]["fixo"] for s in semanas]
    gastos_variaveis = [dados_semanas[s]["variavel"] for s in semanas]
    
    # Criar figura
    fig = go.Figure()
    
    # Adicionar barras para gastos fixos
    fig.add_trace(go.Bar(
        x=semanas,
        y=gastos_fixos,
        name='Gastos Fixos',
        marker_color='#1E88E5'
    ))
    
    # Adicionar barras para gastos variáveis
    fig.add_trace(go.Bar(
        x=semanas,
        y=gastos_variaveis,
        name='Gastos Variáveis',
        marker_color='#FFC107'
    ))
    
    # Configurar layout
    fig.update_layout(
        barmode='group',
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300,
    )
    
    return fig

def render_gastos_page():
    """
    Renderiza a página de Controle de Gastos.
    """
    # Cabeçalho moderno
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-right: 0.8rem;">💸</div>
        <div>
            <h1 style="margin: 0; padding: 0;">Controle de Gastos</h1>
            <p style="margin: 0; padding: 0; color: var(--gray);">Gerencie e acompanhe seus gastos mensais</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados necessários
    gastos = load_gastos()
    user_data = load_user_data() or {"renda_mensal": 0.0}
    renda_mensal = user_data.get("renda_mensal", 0)
    
    # Botão em destaque para adicionar novo gasto
    col_btn, col_empty = st.columns([1, 3])
    with col_btn:
        if st.button("➕ Adicionar Novo Gasto", type="primary", use_container_width=True):
            st.session_state.mostrar_form_gasto = True
            
    # Se o botão foi clicado, mostrar o formulário
    if st.session_state.get("mostrar_form_gasto", False):
        with st.expander("Adicionar Novo Gasto", expanded=True):
            with st.form("form_novo_gasto"):
                # Cabeçalho com explicação simples
                st.markdown("### Registre seu gasto")
                
                # Perguntas diretas e simples
                descricao = st.text_input("O que você comprou ou pagou?")
                
                # Usar número para valor - mais simples
                valor = st.number_input(
                    "Quanto custou?", 
                    min_value=0.01, 
                    step=1.0, 
                    format="%.2f"
                )
                
                # Data com linguagem simples
                data = st.date_input("Quando foi?", value=datetime.now())
                
                # Simplificar categorias com imagens mais intuitivas
                st.markdown("### Categoria")
                categorias_com_icones = {
                    "🏠 Moradia": "Moradia", # Aluguel, contas de casa
                    "🍔 Alimentação": "Alimentação", # Mercado, restaurantes
                    "🚗 Transporte": "Transporte", # Combustível, ônibus, apps
                    "💊 Saúde": "Saúde", # Remédios, consultas
                    "📚 Educação": "Educação", # Cursos, mensalidades
                    "🎬 Lazer": "Lazer", # Cinema, viagens, festas
                    "👕 Compras": "Vestuário", # Roupas, acessórios
                    "💼 Serviços": "Serviços", # Internet, celular
                    "📦 Outros": "Outros" # Outros gastos
                }
                
                # Usar radio buttons em grade para selecionar categoria
                categoria_selecionada = st.radio(
                    "Escolha uma categoria:",
                    options=list(categorias_com_icones.keys()),
                    index=0,
                    horizontal=True
                )
                
                # Converter a categoria com ícone para o valor armazenado
                categoria = categorias_com_icones[categoria_selecionada]
                
                # Dica baseada na categoria selecionada
                dicas_categorias = {
                    "🏠 Moradia": "Aluguel, condomínio, IPTU, luz, água, gás, etc.",
                    "🍔 Alimentação": "Mercado, restaurantes, delivery, lanches.",
                    "🚗 Transporte": "Combustível, ônibus, táxi, aplicativos, estacionamento.",
                    "💊 Saúde": "Remédios, consultas médicas, plano de saúde.",
                    "📚 Educação": "Mensalidades, material escolar, cursos, livros.",
                    "🎬 Lazer": "Cinema, streaming, viagens, festas, esportes.",
                    "👕 Compras": "Roupas, acessórios, eletrônicos, presentes.",
                    "💼 Serviços": "Internet, celular, assinaturas, serviços domésticos.",
                    "📦 Outros": "Qualquer gasto que não se encaixe nas categorias acima."
                }
                
                st.caption(dicas_categorias.get(categoria_selecionada, ""))
                
                # É um gasto fixo?
                tipo = st.toggle("Este é um gasto que se repete todo mês?", value=False)
                # Converter toggle para "Fixo" ou "Variável"
                tipo = "Fixo" if tipo else "Variável"
                
                # Botões de ação
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("💾 Salvar gasto", use_container_width=True)
                with col_btn2:
                    cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
                
                if submitted:
                    # Criar novo gasto
                    novo_gasto = {
                        "descricao": descricao,
                        "valor": valor,
                        "data": data.strftime("%Y-%m-%d"),
                        "categoria": categoria,
                        "tipo": tipo
                    }
                    
                    # Adicionar à lista
                    if add_gasto(novo_gasto):
                        st.success("Gasto adicionado com sucesso!")
                        st.session_state.mostrar_form_gasto = False
                        st.rerun()
                    else:
                        st.error("Erro ao adicionar gasto.")
                
                if cancel:
                    st.session_state.mostrar_form_gasto = False
                    st.rerun()
    
    # Definir mês atual para filtragem (default) e permitir seleção
    mes_atual = datetime.now().strftime("%Y-%m")
    
    # Criar seletor de mês
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Resumo de Gastos")
    
    with col2:
        # Criar uma lista de meses para seleção (últimos 12 meses)
        meses = []
        for i in range(11, -1, -1):
            data = (datetime.now().replace(day=1) - timedelta(days=i*30))
            meses.append(data.strftime("%Y-%m"))
        
        mes_selecionado = st.selectbox(
            "Selecione o mês:",
            options=meses,
            format_func=lambda x: f"{x[5:7]}/{x[0:4]}",
            index=meses.index(mes_atual) if mes_atual in meses else 0
        )
    
    # Filtrar gastos do mês selecionado
    gastos_mes = [g for g in gastos if g["data"].startswith(mes_selecionado)]
    
    # Calcular totais
    total_gastos = sum(g["valor"] for g in gastos_mes)
    gasto_categoria = {}
    
    for g in gastos_mes:
        categoria = g["categoria"]
        if categoria not in gasto_categoria:
            gasto_categoria[categoria] = 0
        gasto_categoria[categoria] += g["valor"]
    
    # Cards de resumo
    col_total, col_perc = st.columns(2)
    
    # Estilo melhorado para os cards
    st.markdown("""
    <style>
    .resumo-card {
        background: linear-gradient(135deg, var(--background-secondary, #f8f9fa) 0%, var(--background-primary, #ffffff) 100%);
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: transform 0.2s;
    }
    .resumo-card:hover {
        transform: translateY(-5px);
    }
    .metric-label {
        font-size: 14px;
        color: var(--text-color-secondary, #6c757d);
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .metric-context {
        font-size: 13px;
        color: var(--text-color-secondary, #6c757d);
    }
    .card-icon {
        font-size: 24px;
        margin-bottom: 10px;
    }
    .card-success {
        border-left: 4px solid var(--success, #4CAF50);
    }
    .card-warning {
        border-left: 4px solid var(--warning, #FF9800);
    }
    .card-danger {
        border-left: 4px solid var(--danger, #F44336);
    }
    .text-success {
        color: var(--success, #4CAF50);
    }
    .text-warning {
        color: var(--warning, #FF9800);
    }
    .text-danger {
        color: var(--danger, #F44336);
    }
    .barra-progresso-container {
        margin-top: 20px;
        padding: 16px;
        background-color: var(--background-secondary, #f8f9fa);
        border-radius: 10px;
    }
    .barra-progresso-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .barra-progresso-label {
        font-size: 14px;
        font-weight: 500;
    }
    .barra-progresso-valor {
        font-size: 14px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with col_total:
        # Card de gasto total modernizado
        st.markdown(f"""
        <div class="resumo-card">
            <div class="card-icon">💰</div>
            <div class="metric-label">Total Gasto no Mês</div>
            <div class="metric-value">{formatar_moeda(total_gastos)}</div>
            <div class="metric-context">Período: {mes_selecionado[5:7]}/{mes_selecionado[0:4]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_perc:
        # Percentual da renda com visual melhorado
        if renda_mensal > 0:
            percentual = (total_gastos / renda_mensal) * 100
            
            # Definir cor e ícone com base no percentual
            cor_classe = ""
            texto_classe = ""
            icon = ""
            mensagem = ""
            
            if percentual > 80:
                cor_classe = "card-danger"
                texto_classe = "text-danger"
                icon = "⚠️"
                mensagem = "Cuidado! Gastos acima de 80% da sua renda."
            elif percentual > 50:
                cor_classe = "card-warning"
                texto_classe = "text-warning"
                icon = "⚡"
                mensagem = "Atenção! Você já gastou mais da metade da sua renda."
            else:
                cor_classe = "card-success"
                texto_classe = "text-success"
                icon = "✅"
                mensagem = "Ótimo! Seus gastos estão abaixo de 50% da sua renda."
            
            st.markdown(f"""
            <div class="resumo-card {cor_classe}">
                <div class="card-icon">{icon}</div>
                <div class="metric-label">Percentual da Renda</div>
                <div class="metric-value {texto_classe}">{percentual:.1f}%</div>
                <div class="metric-context">Da sua renda mensal de {formatar_moeda(renda_mensal)}</div>
                <div class="metric-context" style="margin-top: 8px;">{mensagem}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="resumo-card">
                <div class="card-icon">ℹ️</div>
                <div class="metric-label">Percentual da Renda</div>
                <div class="metric-value">-</div>
                <div class="metric-context">Configure sua renda mensal nas configurações para ver esta informação.</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Barra de progresso modernizada
    if renda_mensal > 0:
        progresso = min(total_gastos / renda_mensal, 1.0)
        
        # Determinar cor da barra de progresso
        cor_barra = "#4CAF50"  # Verde por padrão
        if progresso >= 0.8:
            cor_barra = "#F44336"  # Vermelho
        elif progresso >= 0.5:
            cor_barra = "#FF9800"  # Laranja
        
        # Barra de progresso customizada
        st.markdown(f"""
        <div class="barra-progresso-container">
            <div class="barra-progresso-info">
                <div class="barra-progresso-label">Limite de gastos</div>
                <div class="barra-progresso-valor">{formatar_moeda(total_gastos)} de {formatar_moeda(renda_mensal)}</div>
            </div>
            <div style="width: 100%; background-color: rgba(0,0,0,0.1); border-radius: 5px; height: 12px; overflow: hidden;">
                <div style="width: {progresso * 100}%; background-color: {cor_barra}; height: 100%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                <div style="font-size: 12px; color: var(--text-color-secondary);">0%</div>
                <div style="font-size: 12px; color: var(--text-color-secondary);">50%</div>
                <div style="font-size: 12px; color: var(--text-color-secondary);">100%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Criar abas para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["Gastos por Categoria", "Gastos por Semana", "Lista de Gastos"])
    
    with tab1:
        # Mostrar resumo de gastos por categoria
        st.subheader("Gastos por Categoria")
        
        # Converter para DataFrame para criar o gráfico
        if gasto_categoria:
            df_categorias = pd.DataFrame({
                'Categoria': list(gasto_categoria.keys()),
                'Valor': list(gasto_categoria.values())
            })
            
            # Ordenar por valor (maior para menor)
            df_categorias = df_categorias.sort_values(by='Valor', ascending=False)
            
            # Adicionar coluna de porcentagem
            df_categorias['Porcentagem'] = df_categorias['Valor'] / df_categorias['Valor'].sum() * 100
            
            # Criar figura com cores personalizadas baseadas no tema
            cores = ['#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395']
            
            # Criar gráfico de pizza
            fig = px.pie(
                df_categorias, 
                values='Valor', 
                names='Categoria',
                color_discrete_sequence=cores,
                hole=0.4  # Doughnut chart
            )
            
            # Personalizar layout
            fig.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                legend_title_text='',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                annotations=[dict(
                    text=f"Total<br>{formatar_moeda(total_gastos)}",
                    x=0.5, y=0.5,
                    font_size=14,
                    showarrow=False
                )]
            )
            
            # Mostrar o gráfico no Streamlit
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar detalhamento em cards modernos com barras de progresso
            st.markdown("### Detalhamento")
            
            # Estilo para os cards e barras de progresso
            st.markdown("""
            <style>
            .categoria-card {
                display: flex;
                flex-direction: column;
                background-color: var(--background-secondary, #f8f9fa);
                border-radius: 10px;
                padding: 16px;
                margin-bottom: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .categoria-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .categoria-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }
            .categoria-nome {
                font-size: 16px;
                font-weight: 600;
                color: var(--text-color);
            }
            .categoria-valor {
                font-size: 16px;
                font-weight: 700;
                color: var(--primary);
            }
            .progress-container {
                width: 100%;
                background-color: var(--gray-lighter, #e9ecef);
                border-radius: 10px;
                height: 10px;
                overflow: hidden;
                margin-bottom: 8px;
            }
            .progress-bar {
                height: 100%;
                border-radius: 10px;
            }
            .categoria-footer {
                display: flex;
                justify-content: space-between;
                font-size: 13px;
                color: var(--text-color-secondary, #6c757d);
            }
            .coluna-categorias {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 16px;
                margin-top: 16px;
            }
            @media (max-width: 768px) {
                .coluna-categorias {
                    grid-template-columns: 1fr;
                }
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Criar cores para cada categoria (mapeamento consistente)
            cores_categorias = {
                'Moradia': '#3366CC',
                'Alimentação': '#DC3912', 
                'Vestuário': '#FF9900',
                'Serviços': '#109618',
                'Lazer': '#990099',
                'Saúde': '#0099C6',
                'Transporte': '#DD4477',
                'Educação': '#66AA00',
                'Outros': '#B82E2E'
            }
            
            # Início do grid de cards
            st.markdown('<div class="coluna-categorias">', unsafe_allow_html=True)
            
            # Criar cards para cada categoria
            for index, row in df_categorias.sort_values(by='Valor', ascending=False).iterrows():
                categoria = row['Categoria']
                valor = row['Valor']
                percentual = row['Porcentagem']
                
                # Obter cor para a categoria (ou usar uma padrão se não existir)
                cor = cores_categorias.get(categoria, '#3366CC')
                
                # Criar card para a categoria
                st.markdown(f"""
                <div class="categoria-card">
                    <div class="categoria-header">
                        <div class="categoria-nome">{categoria}</div>
                        <div class="categoria-valor">{formatar_moeda(valor)}</div>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {percentual}%; background-color: {cor};"></div>
                    </div>
                    <div class="categoria-footer">
                        <div>{percentual:.1f}% do total</div>
                        <div>{len([g for g in gastos_mes if g["categoria"] == categoria])} gastos</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Fechar o grid
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Adicionar resumo detalhado expansível
            with st.expander("Ver detalhes em tabela"):
                # Criar uma tabela com todas as categorias
                detalhes = []
                for categoria, valor in gasto_categoria.items():
                    detalhes.append({
                        "Categoria": categoria,
                        "Valor": formatar_moeda(valor),
                        "Percentual": f"{(valor / total_gastos * 100):.1f}%",
                        "Qtd. Gastos": len([g for g in gastos_mes if g["categoria"] == categoria])
                    })
                
                # Converter para DataFrame e exibir
                df_detalhes = pd.DataFrame(detalhes)
                st.dataframe(df_detalhes, use_container_width=True)
        else:
            st.info("Nenhum gasto registrado neste mês.")
    
    with tab2:
        st.subheader("Gastos por Semana")
        
        # Agrupar gastos por semana
        if gastos_mes:
            # Converter string de data para datetime
            for g in gastos_mes:
                g["data_dt"] = datetime.strptime(g["data"], "%Y-%m-%d")
            
            # Obter o primeiro e último dia do mês
            primeiro_dia = datetime.strptime(f"{mes_selecionado}-01", "%Y-%m-%d")
            if primeiro_dia.month == 12:
                ultimo_dia = datetime(primeiro_dia.year + 1, 1, 1) - timedelta(days=1)
            else:
                ultimo_dia = datetime(primeiro_dia.year, primeiro_dia.month + 1, 1) - timedelta(days=1)
            
            # Criar um DataFrame com todos os dias do mês
            dias = pd.date_range(start=primeiro_dia, end=ultimo_dia)
            df_dias = pd.DataFrame({"data": dias})
            
            # Adicionar número da semana
            df_dias["semana"] = df_dias["data"].dt.isocalendar().week
            
            # Criar um DataFrame com os gastos
            df_gastos = pd.DataFrame(gastos_mes)
            df_gastos["data_dt"] = pd.to_datetime(df_gastos["data"])
            df_gastos["dia"] = df_gastos["data_dt"].dt.day
            df_gastos["semana"] = df_gastos["data_dt"].dt.isocalendar().week
            
            # Pegar as semanas únicas do mês
            semanas_do_mes = df_dias["semana"].unique()
            
            # Filtrar apenas as semanas do mês
            gastos_semana = df_gastos.groupby("semana")["valor"].sum().reset_index()
            
            # Criar nomes legíveis para as semanas
            nomes_semanas = {}
            for semana in semanas_do_mes:
                dias_semana = df_dias[df_dias["semana"] == semana]["data"]
                primeiro = dias_semana.min().day
                ultimo = dias_semana.max().day
                nomes_semanas[semana] = f"Semana {primeiro} a {ultimo}"
            
            # Substituir número da semana pelo nome
            gastos_semana["nome_semana"] = gastos_semana["semana"].map(nomes_semanas)
            
            # Criar gráfico de barras com cores agradáveis
            fig = px.bar(
                gastos_semana,
                x="nome_semana",
                y="valor",
                labels={"nome_semana": "Semana", "valor": "Valor Total"},
                color_discrete_sequence=["#3366CC"]
            )
            
            # Adicionar rótulos com valor formatado
            fig.update_traces(
                text=[formatar_moeda(valor) for valor in gastos_semana["valor"]],
                textposition="outside"
            )
            
            # Remover título do eixo y
            fig.update_layout(
                yaxis_title="",
                xaxis_title="",
                margin=dict(t=0, b=0, l=0, r=0)
            )
            
            # Mostrar o gráfico
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar resumo de cada semana - versão moderna
            st.markdown("### Detalhamento por Semana")

            # Estilo para os cards de semana
            st.markdown("""
            <style>
            .semana-card {
                background-color: var(--background-secondary, #f8f9fa);
                border-radius: 12px;
                margin-bottom: 16px;
                overflow: hidden;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            }
            .semana-header {
                padding: 16px;
                border-bottom: 1px solid var(--gray-lighter, #e9ecef);
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: var(--primary-light, #e3f2fd);
                cursor: pointer;
            }
            .semana-header:hover {
                background-color: var(--primary-lighter, #bbdefb);
            }
            .semana-titulo {
                font-size: 16px;
                font-weight: 600;
                color: var(--primary-dark, #1976d2);
            }
            .semana-valor {
                font-size: 18px;
                font-weight: 700;
                color: var(--primary, #2196f3);
            }
            .semana-content {
                padding: 0 16px 16px 16px;
            }
            .categoria-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid var(--gray-lightest, #f7f7f7);
            }
            .mini-bar {
                height: 6px;
                background-color: var(--gray-lighter, #e9ecef);
                border-radius: 3px;
                overflow: hidden;
                flex-grow: 1;
                margin: 0 12px;
            }
            .mini-bar-fill {
                height: 100%;
                border-radius: 3px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Script para controlar a expansão/colapso dos cards
            st.markdown("""
            <script>
            function toggleSemana(semanaId) {
                const content = document.getElementById('semana-content-' + semanaId);
                if (content.style.display === 'none') {
                    content.style.display = 'block';
                } else {
                    content.style.display = 'none';
                }
            }
            </script>
            """, unsafe_allow_html=True)
            
            # Agrupar por semana e categoria para o detalhamento
            gastos_semana_categoria = df_gastos.groupby(["semana", "categoria"])["valor"].sum().reset_index()
            
            # Adicionar coluna de nome da semana
            gastos_semana_categoria["nome_semana"] = gastos_semana_categoria["semana"].map(nomes_semanas)
            
            # Para cada semana, criar um card interativo
            for i, semana in enumerate(semanas_do_mes):
                # Filtrar gastos desta semana
                gastos_da_semana = gastos_semana[gastos_semana["semana"] == semana]
                gastos_categorias_semana = gastos_semana_categoria[gastos_semana_categoria["semana"] == semana]
                
                if not gastos_da_semana.empty:
                    total_semana = gastos_da_semana["valor"].sum()
                    nome_semana = nomes_semanas[semana]
                    
                    # Calcular percentual da semana em relação ao total do mês
                    percentual_do_mes = (total_semana / total_gastos) * 100 if total_gastos > 0 else 0
                    
                    # Cabeçalho do card com toggle
                    st.markdown(f"""
                    <div class="semana-card">
                        <div class="semana-header" onclick="toggleSemana({i})">
                            <div class="semana-titulo">{nome_semana}</div>
                            <div class="semana-valor">{formatar_moeda(total_semana)} ({percentual_do_mes:.1f}%)</div>
                        </div>
                        <div id="semana-content-{i}" class="semana-content">
                    """, unsafe_allow_html=True)
                    
                    # Criar mini gráfico de barras para as categorias da semana
                    top_categorias = gastos_categorias_semana.sort_values("valor", ascending=False)
                    
                    for _, row in top_categorias.iterrows():
                        categoria = row["categoria"]
                        valor_categoria = row["valor"]
                        percentual = (valor_categoria / total_semana) * 100
                        
                        # Obter cor para a categoria
                        cor = cores_categorias.get(categoria, '#3366CC')
                        
                        # Criar linha com mini-barra de progresso
                        st.markdown(f"""
                        <div class="categoria-row">
                            <div style="min-width: 120px;">{categoria}</div>
                            <div class="mini-bar">
                                <div class="mini-bar-fill" style="width: {percentual}%; background-color: {cor};"></div>
                            </div>
                            <div style="min-width: 100px; text-align: right;">{formatar_moeda(valor_categoria)}</div>
                            <div style="min-width: 60px; text-align: right;">{percentual:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Fechar o container
                    st.markdown("</div></div>", unsafe_allow_html=True)
                
            # Adicionar JavaScript para expandir/colapsar os cards
            st.markdown("""
            <script>
                // Inicialmente mostrar apenas o conteúdo do primeiro card
                document.addEventListener('DOMContentLoaded', function() {
                    const contents = document.querySelectorAll('[id^="semana-content-"]');
                    contents.forEach((content, index) => {
                        if (index === 0) {
                            content.style.display = 'block';
                        } else {
                            content.style.display = 'none';
                        }
                    });
                });
            </script>
            """, unsafe_allow_html=True)
        else:
            st.info("Nenhum gasto registrado neste mês.")
    
    with tab3:
        st.subheader("Lista de Gastos")
        
        # Filtrar e ordenar gastos do mês
        if gastos_mes:
            # Converter para DataFrame
            df_gastos = pd.DataFrame(gastos_mes)
            df_gastos['data'] = pd.to_datetime(df_gastos['data'])
            
            # Ordenar por data (mais recente primeiro)
            df_gastos = df_gastos.sort_values('data', ascending=False)
            
            # Formatar os dados para exibição
            df_display = df_gastos.copy()
            df_display['data_formatada'] = df_display['data'].dt.strftime('%d/%m/%Y')
            df_display['valor_formatado'] = df_display['valor'].apply(formatar_moeda)
            
            # Interface de filtro moderna
            st.markdown("""
            <style>
            .filtro-container {
                display: flex;
                align-items: center;
                gap: 10px;
                background-color: var(--background-secondary, #f8f9fa);
                border-radius: 10px;
                padding: 12px 16px;
                margin-bottom: 16px;
            }
            .filtro-icon {
                font-size: 20px;
                color: var(--primary);
            }
            .card-gasto {
                background-color: var(--background-secondary, #f8f9fa);
                border-radius: 12px;
                margin-bottom: 12px;
                overflow: hidden;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .card-gasto:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .card-header {
                background-color: var(--bg-header, #f0f2f5);
                padding: 12px 16px;
                border-bottom: 1px solid var(--gray-lighter, #e9ecef);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .card-titulo {
                font-size: 16px;
                font-weight: 600;
                color: var(--text-color);
            }
            .card-valor {
                font-weight: 700;
                color: var(--negative, #e53935);
                font-size: 16px;
            }
            .card-content {
                padding: 12px 16px;
            }
            .card-info {
                display: flex;
                flex-wrap: wrap;
                gap: 16px;
                align-items: center;
                margin-top: 4px;
                color: var(--text-color-secondary, #6c757d);
            }
            .info-item {
                display: flex;
                align-items: center;
                gap: 4px;
                font-size: 13px;
            }
            .badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
            }
            .badge-fixo {
                background-color: #e8f5e9;
                color: #43a047;
            }
            .badge-variavel {
                background-color: #fff8e1;
                color: #ffa000;
            }
            .gasto-acoes {
                display: flex;
                justify-content: flex-end;
                gap: 8px;
                margin-top: 10px;
            }
            .gasto-acao {
                cursor: pointer;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                color: var(--text-color-secondary, #6c757d);
                transition: background-color 0.2s;
            }
            .gasto-acao:hover {
                background-color: var(--gray-lighter, #e9ecef);
            }
            .lista-gastos {
                max-height: 600px;
                overflow-y: auto;
                padding-right: 8px;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Interface de filtro melhorada
            col_filtro1, col_filtro2 = st.columns([3, 1])
            
            with col_filtro1:
                # Filtrar por categoria com ícones coloridos
                categorias = sorted(df_display['categoria'].unique())
                categorias.insert(0, "Todas")
                categoria_filtro = st.selectbox("Filtrar por categoria:", options=categorias)
            
            with col_filtro2:
                # Adicionar filtro por tipo (Fixo/Variável)
                tipos = ["Todos", "Fixo", "Variável"]
                tipo_filtro = st.selectbox("Filtrar por tipo:", options=tipos)
            
            # Aplicar filtros
            df_filtrada = df_display.copy()
            if categoria_filtro != "Todas":
                df_filtrada = df_filtrada[df_filtrada['categoria'] == categoria_filtro]
            
            if tipo_filtro != "Todos":
                df_filtrada = df_filtrada[df_filtrada['tipo'] == tipo_filtro]
            
            # Mostrar estatísticas dos filtros
            st.markdown(f"**{len(df_filtrada)} gastos encontrados** • Total: **{formatar_moeda(df_filtrada['valor'].sum())}**")
            
            # Início da lista de gastos
            st.markdown('<div class="lista-gastos">', unsafe_allow_html=True)
            
            # Ícones para categorias
            icones_categorias = {
                'Moradia': '🏠',
                'Alimentação': '🍔',
                'Vestuário': '👕',
                'Serviços': '💼',
                'Lazer': '🎮',
                'Saúde': '💊',
                'Transporte': '🚗',
                'Educação': '📚',
                'Outros': '📦'
            }
            
            # Renderizar cards modernos para cada gasto
            for _, row in df_filtrada.iterrows():
                categoria = row.get('categoria', 'Outros')
                icone = icones_categorias.get(categoria, '📋')
                
                # Determinar a classe do badge baseado no tipo
                badge_class = "badge-fixo" if row['tipo'] == 'Fixo' else "badge-variavel"
                
                st.markdown(f"""
                <div class="card-gasto">
                    <div class="card-header">
                        <div class="card-titulo">{row.get('descricao', 'Gasto sem descrição')}</div>
                        <div class="card-valor">{row['valor_formatado']}</div>
                    </div>
                    <div class="card-content">
                        <div class="card-info">
                            <div class="info-item">
                                <span>📅</span> {row['data_formatada']}
                            </div>
                            <div class="info-item">
                                <span>{icone}</span> {row['categoria']}
                            </div>
                            <div class="badge {badge_class}">
                                {row['tipo']}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Fechar a lista
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Separador antes das opções de gestão
            st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
            
            # Seção de gerenciamento de gastos
            st.markdown("### Gerenciar Gastos")
            
            # Criar uma interface mais moderna para exclusão
            col_gerenciar1, col_gerenciar2 = st.columns([3, 1])
            
            with col_gerenciar1:
                # Criar lista de opções para excluir (mais legível)
                opcoes_exclusao = [{
                    "id": i,
                    "texto": f"{g.get('descricao', 'Gasto sem descrição')} - {datetime.strptime(g.get('data', '2023-01-01'), '%Y-%m-%d').strftime('%d/%m/%Y')} - {formatar_moeda(g.get('valor', 0))}"
                } for i, g in enumerate(gastos_mes)]
                
                # Melhorar a apresentação das opções
                selected = st.selectbox(
                    "Selecione um gasto para excluir:",
                    options=range(len(opcoes_exclusao)),
                    format_func=lambda x: opcoes_exclusao[x]["texto"]
                )
            
            with col_gerenciar2:
                # Botão de exclusão mais atraente
                if st.button("🗑️ Excluir Gasto", type="primary", use_container_width=True):
                    # Obter índice do gasto na lista original
                    indice = opcoes_exclusao[selected]["id"]
                    gasto_para_excluir = gastos_mes[indice]
                    
                    # Encontrar e remover o gasto da lista completa
                    for i, gasto in enumerate(gastos):
                        # Verificar se é o mesmo gasto comparando todos os campos
                        if all(gasto[k] == gasto_para_excluir[k] for k in gasto_para_excluir.keys()):
                            # Remover e salvar
                            gastos.pop(i)
                            save_gastos(gastos)
                            st.success(f"Gasto '{gasto_para_excluir.get('descricao', 'Gasto sem descrição')}' excluído com sucesso!")
                            st.rerun()
                            break
        else:
            # Mensagem vazia mais amigável
            st.markdown("""
            <div style="text-align: center; padding: 40px 20px; background-color: var(--background-secondary, #f8f9fa); border-radius: 10px;">
                <div style="font-size: 48px; margin-bottom: 10px;">💸</div>
                <h3>Nenhum gasto registrado neste mês</h3>
                <p>Clique no botão "Adicionar Novo Gasto" para começar a registrar seus gastos.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Mostrar resumo do orçamento na parte inferior
    st.markdown("---")
    st.subheader("Resumo do Orçamento Mensal")
    
    col_resumo1, col_resumo2, col_resumo3 = st.columns(3)
    
    with col_resumo1:
        st.metric("Receita", formatar_moeda(renda_mensal))
    
    with col_resumo2:
        st.metric("Despesas", formatar_moeda(total_gastos))
    
    with col_resumo3:
        saldo = renda_mensal - total_gastos
        saldo_label = "Saldo Positivo" if saldo >= 0 else "Saldo Negativo"
        saldo_delta = f"{saldo / renda_mensal * 100:.1f}% da receita" if renda_mensal > 0 else None
        st.metric(saldo_label, formatar_moeda(saldo), saldo_delta)

def cadastrar_gasto():
    """
    Cadastra um novo gasto
    """
    # Carregar dados existentes
    gastos = load_data("gastos")
    planejamento = load_data("planejamento")
    
    # Obter dados do formulário
    descricao = st.session_state.descricao_gasto
    valor = st.session_state.valor_gasto
    categoria = st.session_state.categoria_gasto
    data = st.session_state.data_gasto
    tipo = st.session_state.tipo_gasto
    
    # Validar se o valor não excede o planejamento
    if not planejamento.empty:
        if tipo == 'fixo' and valor > planejamento['gastos_fixos'].iloc[0]:
            st.error(f"⚠️ Este gasto fixo excede o limite planejado de R$ {planejamento['gastos_fixos'].iloc[0]:.2f}")
            return
        elif tipo == 'variavel' and valor > planejamento['gastos_variaveis'].iloc[0]:
            st.error(f"⚠️ Este gasto variável excede o limite planejado de R$ {planejamento['gastos_variaveis'].iloc[0]:.2f}")
            return
    
    # Criar novo gasto
    novo_gasto = pd.DataFrame({
        'data': [data],
        'descricao': [descricao],
        'valor': [valor],
        'categoria': [categoria],
        'tipo': [tipo]
    })
    
    # Adicionar ao DataFrame existente
    gastos = pd.concat([gastos, novo_gasto], ignore_index=True)
    
    # Salvar dados
    save_data("gastos", gastos)
    
    # Mostrar mensagem de sucesso
    st.success("✅ Gasto cadastrado com sucesso!")
    
    # Limpar formulário
    st.session_state.descricao_gasto = ""
    st.session_state.valor_gasto = 0.0
    st.session_state.categoria_gasto = "🏠 Moradia"
    st.session_state.data_gasto = datetime.now()
    st.session_state.tipo_gasto = "fixo"
    st.session_state.mostrar_form_gasto = False
    
    # Recarregar a página
    st.rerun() 