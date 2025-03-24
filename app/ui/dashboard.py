"""
Módulo para a página de Dashboard do aplicativo de Controle Financeiro Pessoal.
Exibe uma visão geral das finanças com gráficos e indicadores.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Adicionar diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user import User
from models.goals import Goal
from models.investments import Portfolio, Investment
from utils.data_processor import load_user_data, load_goals, load_investments
from utils.calculations import compound_interest, inflation_adjust

# Importar funções de manipulação de dados
from data.data_handler import (
    load_gastos,
    load_investimentos,
    load_dividas,
    load_seguros
)

def calcular_estatisticas():
    """
    Calcula as estatísticas financeiras para exibição no dashboard.
    """
    # Carregar dados
    gastos = load_gastos()
    investimentos = load_investimentos()
    dividas = load_dividas()
    user_data = load_user_data() or {"renda_mensal": 0.0}
    
    # Calcular valores
    receita_total = user_data.get("renda_mensal", 0)
    
    # Filtramos apenas gastos do mês atual
    mes_atual = datetime.now().strftime("%Y-%m")
    gastos_mes = [g for g in gastos if g.get("data", "").startswith(mes_atual)]
    gastos_total = sum(g.get("valor", 0) for g in gastos_mes)
    
    # Mês anterior para comparação
    mes_anterior = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    gastos_mes_anterior = [g for g in gastos if g.get("data", "").startswith(mes_anterior)]
    gastos_anterior = sum(g.get("valor", 0) for g in gastos_mes_anterior)
    
    # Calcular tendências
    variacao_gastos = ((gastos_total - gastos_anterior) / max(gastos_anterior, 1)) * 100 if gastos_anterior else 0
    
    # Total de investimentos
    investimentos_total = sum(i.get("valor", 0) for i in investimentos)
    
    # Total de dívidas
    dividas_total = sum(d.get("valor_restante", 0) for d in dividas)
    
    # Gastos fixos e variáveis
    gastos_fixos = sum(g.get("valor", 0) for g in gastos_mes if g.get("tipo") == "Fixo")
    gastos_variaveis = sum(g.get("valor", 0) for g in gastos_mes if g.get("tipo") == "Variável")
    
    return {
        "receita_total": receita_total,
        "gastos_total": gastos_total,
        "variacao_gastos": variacao_gastos,
        "investimentos_total": investimentos_total,
        "dividas_total": dividas_total,
        "gastos_fixos": gastos_fixos,
        "gastos_variaveis": gastos_variaveis,
        "saldo": receita_total - gastos_total
    }

def criar_grafico_pizza(gastos_fixos, gastos_variaveis):
    """
    Cria um gráfico de pizza mostrando a distribuição entre gastos fixos e variáveis.
    """
    labels = ['Gastos Fixos', 'Gastos Variáveis']
    values = [gastos_fixos, gastos_variaveis]
    
    # Criar figura com plotly
    fig = px.pie(
        values=values, 
        names=labels,
        color_discrete_sequence=['#1E88E5', '#FFC107'],
        hole=0.4,
    )
    
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=300,
    )
    
    return fig

def criar_grafico_barras_comparativo():
    """
    Cria um gráfico de barras comparando receitas e despesas por mês.
    """
    # Carregar dados
    gastos = load_gastos()
    user_data = load_user_data() or {"renda_mensal": 0.0}
    receita_mensal = user_data.get("renda_mensal", 0)
    
    # Preparar dados para os últimos 6 meses
    meses = []
    receitas = []
    despesas = []
    
    for i in range(5, -1, -1):
        data = (datetime.now().replace(day=1) - timedelta(days=i*30)).strftime("%Y-%m")
        mes_nome = (datetime.now().replace(day=1) - timedelta(days=i*30)).strftime("%b")
        
        gastos_mes = [g for g in gastos if g.get("data", "").startswith(data)]
        total_gastos = sum(g.get("valor", 0) for g in gastos_mes)
        
        meses.append(mes_nome)
        receitas.append(receita_mensal)
        despesas.append(total_gastos)
    
    # Criar dataframe
    df = pd.DataFrame({
        'Mês': meses,
        'Receitas': receitas,
        'Despesas': despesas
    })
    
    # Criar figura com plotly
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Mês'],
        y=df['Receitas'],
        name='Receitas',
        marker_color='#4CAF50'
    ))
    
    fig.add_trace(go.Bar(
        x=df['Mês'],
        y=df['Despesas'],
        name='Despesas',
        marker_color='#F44336'
    ))
    
    fig.update_layout(
        barmode='group',
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300,
    )
    
    return fig

def criar_grafico_linha_tendencias():
    """
    Cria um gráfico de linha mostrando as tendências de gastos e investimentos.
    """
    # Carregar dados
    gastos = load_gastos()
    investimentos = load_investimentos()
    
    # Preparar dados para os últimos 12 meses
    meses = []
    gastos_mensais = []
    investimentos_mensais = []
    
    for i in range(11, -1, -1):
        data = (datetime.now().replace(day=1) - timedelta(days=i*30)).strftime("%Y-%m")
        mes_nome = (datetime.now().replace(day=1) - timedelta(days=i*30)).strftime("%b")
        
        gastos_mes = [g for g in gastos if g.get("data", "").startswith(data)]
        total_gastos = sum(g.get("valor", 0) for g in gastos_mes)
        
        investimentos_mes = [inv for inv in investimentos if inv.get("data_inicio", "").startswith(data)]
        total_investimentos = sum(inv.get("valor", 0) for inv in investimentos_mes)
        
        meses.append(mes_nome)
        gastos_mensais.append(total_gastos)
        investimentos_mensais.append(total_investimentos)
    
    # Criar figura com plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses,
        y=gastos_mensais,
        name='Gastos',
        line=dict(color='#F44336', width=2),
        mode='lines+markers'
    ))
    
    fig.add_trace(go.Scatter(
        x=meses,
        y=investimentos_mensais,
        name='Investimentos',
        line=dict(color='#4CAF50', width=2),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300,
    )
    
    return fig

def criar_grafico_area_fluxo():
    """
    Cria um gráfico de área mostrando o fluxo de caixa.
    """
    # Carregar dados
    gastos = load_gastos()
    user_data = load_user_data() or {"renda_mensal": 0.0}
    receita_mensal = user_data.get("renda_mensal", 0)
    
    # Preparar dados para os últimos 6 meses
    meses = []
    receitas = []
    despesas = []
    saldos = []
    
    for i in range(5, -1, -1):
        data = (datetime.now().replace(day=1) - timedelta(days=i*30)).strftime("%Y-%m")
        mes_nome = (datetime.now().replace(day=1) - timedelta(days=i*30)).strftime("%b")
        
        gastos_mes = [g for g in gastos if g.get("data", "").startswith(data)]
        total_gastos = sum(g.get("valor", 0) for g in gastos_mes)
        saldo = receita_mensal - total_gastos
        
        meses.append(mes_nome)
        receitas.append(receita_mensal)
        despesas.append(total_gastos)
        saldos.append(saldo)
    
    # Criar figura com plotly
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=meses,
        y=saldos,
        fill='tozeroy',
        name='Saldo',
        line=dict(color='#2196F3'),
        fillcolor='rgba(33, 150, 243, 0.3)'
    ))
    
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300,
    )
    
    return fig

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_variacao_badge(variacao):
    """
    Retorna HTML para exibir um badge de variação (positiva/negativa).
    """
    if variacao > 0:
        return f'<span class="positive">▲ {abs(variacao):.1f}%</span>'
    elif variacao < 0:
        return f'<span class="negative">▼ {abs(variacao):.1f}%</span>'
    else:
        return f'<span class="info">• {abs(variacao):.1f}%</span>'

def render_dashboard():
    """
    Renderiza a página de Dashboard com gráficos e indicadores financeiros.
    """
    st.header("Dashboard")
    
    # Obter estatísticas calculadas
    stats = calcular_estatisticas()
    
    # Criar quatro cards de estatísticas em uma linha
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### Receita Mensal")
        st.markdown(f"""
        <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:10px; border-radius:5px;">
            <h2 class="currency">{formatar_moeda(stats['receita_total'])}</h2>
            <p>A receber este mês</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Gastos Mensais")
        variacao_html = get_variacao_badge(stats['variacao_gastos'])
        st.markdown(f"""
        <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:10px; border-radius:5px;">
            <h2 class="currency">{formatar_moeda(stats['gastos_total'])}</h2>
            <p>Variação mensal: {variacao_html}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### Investimentos")
        st.markdown(f"""
        <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:10px; border-radius:5px;">
            <h2 class="currency">{formatar_moeda(stats['investimentos_total'])}</h2>
            <p>Total investido</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("### Dívidas")
        st.markdown(f"""
        <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:10px; border-radius:5px;">
            <h2 class="currency">{formatar_moeda(stats['dividas_total'])}</h2>
            <p>Saldo devedor total</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Badge do período
    col_periodo = st.columns([6, 2])
    with col_periodo[1]:
        mes_atual = datetime.now().strftime("%B %Y").capitalize()
        st.markdown(f"""
        <div style="background-color:{'#1E88E5'}; color:white; padding:5px 10px; border-radius:15px; text-align:center; margin-top:20px;">
            <p style="margin:0;">{mes_atual}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Abas para alternar entre visões
    tab1, tab2 = st.tabs(["Visão Geral", "Tendências"])
    
    with tab1:
        # Primeira linha de gráficos
        col_esq, col_dir = st.columns(2)
        
        with col_esq:
            st.subheader("Distribuição de Gastos")
            fig_pizza = criar_grafico_pizza(stats['gastos_fixos'], stats['gastos_variaveis'])
            st.plotly_chart(fig_pizza, use_container_width=True)
        
        with col_dir:
            st.subheader("Comparativo Mensal")
            fig_barras = criar_grafico_barras_comparativo()
            st.plotly_chart(fig_barras, use_container_width=True)
    
    with tab2:
        # Gráficos de tendências
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Tendências de Gastos e Investimentos")
            fig_linha = criar_grafico_linha_tendencias()
            st.plotly_chart(fig_linha, use_container_width=True)
        
        with col2:
            st.subheader("Fluxo de Caixa")
            fig_area = criar_grafico_area_fluxo()
            st.plotly_chart(fig_area, use_container_width=True)
    
    # Resumo do saldo mensal
    st.markdown("---")
    st.subheader("Resumo do Mês Atual")
    
    col_resumo1, col_resumo2, col_resumo3 = st.columns(3)
    
    with col_resumo1:
        st.metric("Receita", formatar_moeda(stats['receita_total']))
    
    with col_resumo2:
        st.metric("Despesas", formatar_moeda(stats['gastos_total']))
    
    with col_resumo3:
        saldo_label = "Saldo Positivo" if stats['saldo'] >= 0 else "Saldo Negativo"
        saldo_delta = f"{stats['saldo'] / stats['receita_total'] * 100:.1f}% da receita" if stats['receita_total'] > 0 else None
        st.metric(saldo_label, formatar_moeda(stats['saldo']), saldo_delta)


def render_financial_summary(user: User, portfolio: Portfolio):
    """Renderiza o resumo financeiro do usuário."""
    st.header("Resumo Financeiro")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Renda Mensal", 
            value=f"R$ {user.total_monthly_income():.2f}".replace('.', ',')
        )
    
    with col2:
        st.metric(
            label="Despesas Mensais", 
            value=f"R$ {user.total_monthly_expenses():.2f}".replace('.', ',')
        )
    
    with col3:
        st.metric(
            label="Disponível para Investir", 
            value=f"R$ {user.available_for_investment():.2f}".replace('.', ',')
        )
    
    # Gráfico de distribuição de despesas
    expense_dict = user.expenses_by_category()
    if expense_dict:
        st.subheader("Distribuição de Despesas")
        
        # Criar DataFrame para o gráfico
        expense_df = pd.DataFrame({
            'Categoria': list(expense_dict.keys()),
            'Valor': list(expense_dict.values())
        })
        
        # Criar gráfico de pizza
        fig = px.pie(
            expense_df, 
            values='Valor', 
            names='Categoria',
            title='Distribuição de Despesas por Categoria',
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Patrimônio atual
    st.subheader("Patrimônio Atual")
    
    current_assets = portfolio.total_value()
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Patrimônio Total", 
            value=f"R$ {current_assets:.2f}".replace('.', ',')
        )
    
    with col2:
        monthly_return = portfolio.expected_monthly_return()
        annual_return = monthly_return * 12
        
        st.metric(
            label="Rendimento Anual Estimado", 
            value=f"R$ {annual_return:.2f}".replace('.', ',')
        )


def render_goals_summary(goals: list):
    """Renderiza o resumo dos objetivos financeiros."""
    st.header("Objetivos Financeiros")
    
    # Filtrar objetivos não concluídos e ordenar por prazo mais próximo
    active_goals = [g for g in goals if g.progress_percentage < 100]
    active_goals.sort(key=lambda x: x.deadline)
    
    if not active_goals:
        st.info("Nenhum objetivo financeiro configurado. Adicione objetivos na página de Objetivos.")
        return
    
    # Mostrar os próximos objetivos
    st.subheader("Próximos Objetivos")
    
    col1, col2, col3 = st.columns(3)
    
    for i, goal in enumerate(active_goals[:3]):
        col = [col1, col2, col3][i % 3]
        
        with col:
            st.metric(
                label=goal.name,
                value=f"R$ {goal.current_amount:.2f}".replace('.', ','),
                delta=f"{goal.progress_percentage:.1f}%"
            )
            
            # Barra de progresso
            st.progress(goal.progress_percentage / 100)
            
            # Data limite
            remaining_months = goal.months_remaining
            if remaining_months == 0:
                st.caption("🔥 **Prazo vencido!**")
            elif remaining_months < 3:
                st.caption(f"⚠️ **{remaining_months} meses restantes**")
            else:
                st.caption(f"🕒 {remaining_months} meses restantes")
    
    # Gráfico de progresso dos objetivos
    st.subheader("Progresso dos Objetivos")
    
    # Criar DataFrame para o gráfico
    goals_df = pd.DataFrame({
        'Objetivo': [goal.name for goal in active_goals],
        'Atual': [goal.current_amount for goal in active_goals],
        'Alvo': [goal.target_amount for goal in active_goals],
        'Progresso (%)': [goal.progress_percentage for goal in active_goals]
    })
    
    fig = px.bar(
        goals_df, 
        x='Objetivo', 
        y=['Atual', 'Alvo'],
        title='Progresso dos Objetivos',
        barmode='group',
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar projetos de conclusão
    st.subheader("Projeção de Conclusão")
    
    # Tabela de projeções
    projection_data = []
    
    for goal in active_goals:
        monthly_contribution = goal.monthly_contribution_needed()
        
        projection_data.append({
            "Objetivo": goal.name,
            "Valor Atual": f"R$ {goal.current_amount:.2f}".replace('.', ','),
            "Valor Alvo": f"R$ {goal.target_amount:.2f}".replace('.', ','),
            "Contribuição Mensal": f"R$ {monthly_contribution:.2f}".replace('.', ','),
            "Data Estimada": (datetime.now() + timedelta(days=30 * goal.months_remaining)).strftime("%d/%m/%Y") if goal.months_remaining > 0 else "Atrasado"
        })
    
    st.dataframe(pd.DataFrame(projection_data), hide_index=True)


def render_investment_summary(portfolio: Portfolio):
    """Renderiza o resumo dos investimentos."""
    st.header("Investimentos")
    
    if not portfolio.investments:
        st.info("Nenhum investimento registrado. Adicione investimentos na página de Investimentos.")
        return
    
    # Distribuição por tipo de investimento
    st.subheader("Distribuição por Tipo")
    
    type_dist = portfolio.type_distribution()
    
    if type_dist:
        # Criar DataFrame para o gráfico
        type_df = pd.DataFrame({
            'Tipo': list(type_dist.keys()),
            'Percentual': list(type_dist.values())
        })
        
        fig = px.pie(
            type_df, 
            values='Percentual', 
            names='Tipo',
            title='Distribuição por Tipo de Investimento',
            color_discrete_sequence=px.colors.sequential.Greens
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Distribuição por risco
    st.subheader("Distribuição por Risco")
    
    risk_dist = portfolio.risk_distribution()
    
    # Criar DataFrame para o gráfico
    risk_df = pd.DataFrame({
        'Nível de Risco': ["Baixo", "Médio", "Alto"],
        'Percentual': [risk_dist["baixo"], risk_dist["médio"], risk_dist["alto"]]
    })
    
    fig = px.bar(
        risk_df, 
        x='Nível de Risco', 
        y='Percentual',
        title='Distribuição por Nível de Risco',
        color='Nível de Risco',
        color_discrete_map={
            "Baixo": "#2ca02c",  # Verde
            "Médio": "#1f77b4",  # Azul
            "Alto": "#d62728"    # Vermelho
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Projeção de crescimento
    st.subheader("Projeção de Crescimento")
    
    # Elementos interativos para simulação
    col1, col2 = st.columns(2)
    
    with col1:
        simulation_years = st.slider(
            "Anos para projeção", 
            min_value=1, 
            max_value=30, 
            value=10
        )
    
    with col2:
        monthly_contribution = st.number_input(
            "Contribuição mensal (R$)",
            min_value=0.0,
            value=500.0,
            step=100.0
        )
    
    # Criar projeção
    months = simulation_years * 12
    projection = portfolio.project_growth(months, monthly_contribution)
    
    # Ajustar para inflação
    inflation_rate = 0.04  # 4% ao ano (média brasileira de longo prazo)
    projection_adjusted = [
        inflation_adjust(value, inflation_rate, i/12) 
        for i, value in enumerate(projection)
    ]
    
    # Criar DataFrame para o gráfico
    time_points = [i for i in range(0, months + 1, max(1, months // 10))]
    time_labels = [f"Ano {i//12}" for i in time_points]
    
    projection_df = pd.DataFrame({
        'Mês': range(len(projection)),
        'Valor Nominal': projection,
        'Valor Ajustado pela Inflação': projection_adjusted
    })
    
    fig = px.line(
        projection_df, 
        x='Mês', 
        y=['Valor Nominal', 'Valor Ajustado pela Inflação'],
        title=f'Projeção de Crescimento para {simulation_years} Anos',
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    
    # Configurar eixo X para mostrar anos
    fig.update_xaxes(
        tickvals=time_points,
        ticktext=time_labels
    )
    
    # Formatar eixo Y para mostrar valores em R$
    fig.update_layout(
        yaxis_title="Valor (R$)",
        xaxis_title="Tempo",
        legend_title="Cenário"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Valores finais projetados
    final_value = projection[-1]
    final_value_adjusted = projection_adjusted[-1]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label=f"Valor Estimado em {simulation_years} Anos", 
            value=f"R$ {final_value:.2f}".replace('.', ',')
        )
    
    with col2:
        st.metric(
            label=f"Valor Ajustado pela Inflação", 
            value=f"R$ {final_value_adjusted:.2f}".replace('.', ',')
        ) 