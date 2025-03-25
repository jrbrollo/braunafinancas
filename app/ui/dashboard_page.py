"""
Módulo para a página de Dashboard principal do aplicativo de Controle Financeiro Pessoal.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar

# Importar funções de manipulação de dados
from data.data_handler import (
    load_user_data,
    load_gastos,
    load_investimentos,
    load_dividas,
    load_seguros,
    load_objetivos
)

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_gastos_periodo(gastos, mes_ano):
    """
    Calcula o total de gastos para um período específico.
    
    Args:
        gastos (list): Lista de gastos
        mes_ano (str): Mês e ano no formato "YYYY-MM"
        
    Returns:
        float: Total de gastos no período
    """
    return sum(gasto["valor"] for gasto in gastos if gasto["data"].startswith(mes_ano))

def obter_meses_anteriores(n=6):
    """
    Obtém uma lista dos N meses anteriores ao mês atual.
    
    Args:
        n (int): Número de meses anteriores a retornar
        
    Returns:
        list: Lista de dicionários contendo informações sobre os meses
    """
    meses = []
    data_atual = datetime.now()
    
    for i in range(n):
        # Calcular o mês anterior
        data_anterior = data_atual - timedelta(days=data_atual.day)
        data_atual = data_anterior
        
        # Obter o primeiro dia do mês anterior
        primeiro_dia = data_anterior.replace(day=1)
        
        # Obter o nome do mês
        nome_mes = calendar.month_name[primeiro_dia.month]
        
        # Formatar o mês no formato "YYYY-MM"
        mes_formatado = primeiro_dia.strftime("%Y-%m")
        
        # Adicionar à lista
        meses.append({
            "nome": nome_mes,
            "ano": primeiro_dia.year,
            "formato_numerico": mes_formatado,
            "abreviacao": primeiro_dia.strftime("%b/%Y")
        })
    
    # Inverter a lista para ficar em ordem cronológica
    return list(reversed(meses))

def criar_grafico_tendencia_gastos(gastos, meses_anteriores):
    """
    Cria um gráfico de linha mostrando a tendência de gastos nos últimos meses.
    
    Args:
        gastos (list): Lista de gastos
        meses_anteriores (list): Lista de meses anteriores
        
    Returns:
        figura: Objeto de figura do Plotly
    """
    # Preparar dados para o gráfico
    dados_grafico = []
    
    categorias = set()
    for gasto in gastos:
        categorias.add(gasto.get("categoria", "Outros"))
    
    for mes in meses_anteriores:
        mes_formatado = mes["formato_numerico"]
        
        # Calcular total por categoria para este mês
        totais_categoria = {categoria: 0 for categoria in categorias}
        
        for gasto in gastos:
            if gasto["data"].startswith(mes_formatado):
                categoria = gasto.get("categoria", "Outros")
                totais_categoria[categoria] += gasto["valor"]
        
        # Adicionar ao gráfico
        for categoria, valor in totais_categoria.items():
            dados_grafico.append({
                "Mês": mes["abreviacao"],
                "Categoria": categoria,
                "Valor": valor
            })
    
    # Criar DataFrame para o gráfico
    df = pd.DataFrame(dados_grafico)
    
    # Ordenar o DataFrame por mês
    df["ordem_mes"] = df["Mês"].apply(lambda x: meses_anteriores.index(next(m for m in meses_anteriores if m["abreviacao"] == x)))
    df = df.sort_values("ordem_mes")
    
    # Criar gráfico
    fig = px.line(
        df,
        x="Mês",
        y="Valor",
        color="Categoria",
        title="Tendência de Gastos por Categoria",
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Valor (R$)",
        legend_title="Categoria",
        hovermode="x unified"
    )
    
    # Formatar valores no hover
    fig.update_traces(
        hovertemplate="%{y:,.2f}"
    )
    
    return fig

def calcular_patrimonios(investimentos, dividas):
    """
    Calcula o patrimônio líquido com base nos investimentos e dívidas.
    
    Args:
        investimentos (list): Lista de investimentos
        dividas (list): Lista de dívidas
        
    Returns:
        tuple: (patrimônio bruto, total de dívidas, patrimônio líquido)
    """
    # Calcular patrimônio bruto (total dos investimentos)
    patrimonio_bruto = sum(inv.get("valor_atual", 0) for inv in investimentos)
    
    # Calcular total de dívidas
    total_dividas = sum(div.get("valor_atual", 0) for div in dividas)
    
    # Calcular patrimônio líquido
    patrimonio_liquido = patrimonio_bruto - total_dividas
    
    return patrimonio_bruto, total_dividas, patrimonio_liquido

def render_dashboard_page():
    """
    Renderiza a página de dashboard principal
    """
    st.title("Dashboard")
    
    # Buscar dados para o dashboard
    objetivos = load_objetivos()
    investimentos = load_investimentos()
    dividas = load_dividas()
    gastos = load_gastos()
    seguros = load_seguros()
    
    # Seção de resumo financeiro
    st.markdown("""
    <h2 class="card-title">Resumo Financeiro</h2>
    """, unsafe_allow_html=True)
    
    # Calcular totais
    total_objetivos = sum(float(o.get("valor_total", 0) or 0) for o in objetivos)
    total_atingido = sum(float(o.get("valor_atual", 0) or 0) for o in objetivos)
    
    total_investimentos = sum(float(i.get("valor_atual", 0) or i.get("valor_inicial", 0) or 0) for i in investimentos)
    total_dividas = sum(float(d.get("valor_restante", 0) or d.get("valor_atual", 0) or 0) for d in dividas)
    
    total_seguros_anual = sum(float(s.get("valor_premio", 0) or 0) for s in seguros)
    total_seguros_mensal = total_seguros_anual / 12 if total_seguros_anual else 0
    
    # Gastos do mês atual
    mes_atual = datetime.now().month
    ano_atual = datetime.now().year
    gastos_mes = [g for g in gastos if (
        datetime.strptime(g.get("data", "2023-01-01"), "%Y-%m-%d").month == mes_atual and
        datetime.strptime(g.get("data", "2023-01-01"), "%Y-%m-%d").year == ano_atual
    )]
    total_gastos_mes = sum(float(g.get("valor", 0) or 0) for g in gastos_mes)
    
    # Patrimônio líquido
    patrimonio_liquido = total_investimentos - total_dividas
    
    # Cards de resumo financeiro
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Patrimônio Líquido</div>
            <div class="metric-value{'positive' if patrimonio_liquido >= 0 else ' negative'}">{formatar_moeda(patrimonio_liquido)}</div>
            <div>Investimentos - Dívidas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Investimentos</div>
            <div class="metric-value positive">{formatar_moeda(total_investimentos)}</div>
            <div>{len(investimentos)} ativos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Dívidas</div>
            <div class="metric-value negative">{formatar_moeda(total_dividas)}</div>
            <div>{len(dividas)} pendentes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">Gastos do Mês</div>
            <div class="metric-value">{formatar_moeda(total_gastos_mes)}</div>
            <div>{len(gastos_mes)} transações</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos e visualizações
    st.markdown("""
    <h2 class="card-title">Visualizações</h2>
    """, unsafe_allow_html=True)
    
    # Linha 1 de visualizações
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <div class="card-title">Distribuição de Investimentos</div>
        """, unsafe_allow_html=True)
        
        # Preparar dados para o gráfico de pizza de investimentos
        if investimentos:
            categorias_inv = {}
            for inv in investimentos:
                categoria = inv.get("categoria", "Outros")
                valor = float(inv.get("valor_atual", 0) or inv.get("valor_inicial", 0) or 0)
                if categoria in categorias_inv:
                    categorias_inv[categoria] += valor
                else:
                    categorias_inv[categoria] = valor
            
            # Criar DataFrame para o gráfico
            df_inv = pd.DataFrame({
                'Categoria': list(categorias_inv.keys()),
                'Valor': list(categorias_inv.values())
            })
            
            # Gráfico de pizza para investimentos
            fig = px.pie(
                df_inv, 
                values='Valor', 
                names='Categoria',
                color_discrete_sequence=px.colors.sequential.Blues,
                hole=0.4
            )
            
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Valor: %{value:,.2f}<br>Percentual: %{percent}'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Adicione investimentos para visualizar a distribuição.")
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <div class="card-title">Progresso dos Objetivos</div>
        """, unsafe_allow_html=True)
        
        if objetivos:
            # Preparar dados para o gráfico de barras de objetivos
            nomes_obj = [o.get("nome", f"Objetivo {i+1}") for i, o in enumerate(objetivos)]
            valores_total = [float(o.get("valor_total", 0) or 0) for o in objetivos]
            valores_atual = [float(o.get("valor_atual", 0) or 0) for o in objetivos]
            
            # Calcular percentuais para mostrar no hover
            percentuais = [
                round(atual / total * 100 if total > 0 else 0, 2)
                for atual, total in zip(valores_atual, valores_total)
            ]
            
            # Gráfico de barras para objetivos
            df_obj = pd.DataFrame({
                'Objetivo': nomes_obj,
                'Atual': valores_atual,
                'Total': valores_total,
                'Percentual': percentuais
            })
            
            # Ordenar por percentual de conclusão (do menor para o maior)
            df_obj = df_obj.sort_values('Percentual', ascending=True)
            
            # Gráfico de barras para objetivos
            fig = go.Figure()
            
            # Adicionar barra do valor total (fundo)
            fig.add_trace(go.Bar(
                x=df_obj['Total'],
                y=df_obj['Objetivo'],
                orientation='h',
                marker=dict(color='rgba(0, 0, 0, 0.1)'),
                hoverinfo='none',
                showlegend=False
            ))
            
            # Adicionar barra do valor atual (progresso)
            fig.add_trace(go.Bar(
                x=df_obj['Atual'],
                y=df_obj['Objetivo'],
                orientation='h',
                marker=dict(color='#2A5CAA'),
                text=df_obj['Percentual'].apply(lambda x: f"{x:.1f}%"),
                textposition='auto',
                name='Progresso',
                hovertemplate='<b>%{y}</b><br>Atual: R$ %{x:,.2f}<br>Percentual: %{text}'
            ))
            
            fig.update_layout(
                barmode='overlay',
                yaxis=dict(
                    title='',
                    tickfont=dict(size=12)
                ),
                xaxis=dict(
                    title='Valor (R$)',
                    tickformat=',.0f'
                ),
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Adicione objetivos para visualizar o progresso.")
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    # Linha 2 de visualizações
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <div class="card-title">Gastos por Categoria</div>
        """, unsafe_allow_html=True)
        
        if gastos_mes:
            # Preparar dados para o gráfico de gastos por categoria
            categorias_gastos = {}
            for gasto in gastos_mes:
                categoria = gasto.get("categoria", "Outros")
                valor = float(gasto.get("valor", 0) or 0)
                if categoria in categorias_gastos:
                    categorias_gastos[categoria] += valor
                else:
                    categorias_gastos[categoria] = valor
            
            # Criar DataFrame para o gráfico
            df_gastos = pd.DataFrame({
                'Categoria': list(categorias_gastos.keys()),
                'Valor': list(categorias_gastos.values())
            })
            
            # Ordenar por valor (do maior para o menor)
            df_gastos = df_gastos.sort_values('Valor', ascending=False)
            
            # Gráfico de barras para gastos
            fig = px.bar(
                df_gastos, 
                x='Categoria', 
                y='Valor',
                color='Valor',
                color_continuous_scale=px.colors.sequential.Reds,
                text='Valor'
            )
            
            fig.update_traces(
                texttemplate='R$ %{text:.2f}',
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}'
            )
            
            fig.update_layout(
                yaxis_title="Valor (R$)",
                xaxis_title="",
                coloraxis_showscale=False,
                margin=dict(t=20, b=20, l=20, r=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Adicione gastos no mês atual para visualizar a distribuição por categoria.")
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <div class="card-title">Vencimentos Próximos</div>
        """, unsafe_allow_html=True)
        
        # Combinar dívidas e seguros para mostrar próximos vencimentos
        vencimentos = []
        hoje = datetime.now().date()
        
        # Adicionar vencimentos de dívidas
        for divida in dividas:
            if "data_vencimento" in divida and divida["data_vencimento"]:
                try:
                    data_venc = datetime.strptime(divida["data_vencimento"], "%Y-%m-%d").date()
                    dias_restantes = (data_venc - hoje).days
                    if 0 <= dias_restantes <= 30:  # Mostrar vencimentos nos próximos 30 dias
                        vencimentos.append({
                            "tipo": "Dívida",
                            "descricao": divida.get("descricao", "Sem descrição"),
                            "data": data_venc,
                            "dias_restantes": dias_restantes,
                            "valor": float(divida.get("valor_restante", 0) or divida.get("valor_atual", 0) or 0)
                        })
                except (ValueError, TypeError):
                    continue
        
        # Adicionar vencimentos de seguros
        for seguro in seguros:
            if "data_vencimento" in seguro and seguro["data_vencimento"]:
                try:
                    data_venc = datetime.strptime(seguro["data_vencimento"], "%Y-%m-%d").date()
                    dias_restantes = (data_venc - hoje).days
                    if 0 <= dias_restantes <= 30:  # Mostrar vencimentos nos próximos 30 dias
                        vencimentos.append({
                            "tipo": "Seguro",
                            "descricao": seguro.get("descricao", "Sem descrição"),
                            "data": data_venc,
                            "dias_restantes": dias_restantes,
                            "valor": float(seguro.get("valor_premio", 0) or 0)
                        })
                except (ValueError, TypeError):
                    continue
        
        # Ordenar por dias restantes (do menor para o maior)
        vencimentos.sort(key=lambda x: x["dias_restantes"])
        
        if vencimentos:
            # Mostrar lista de vencimentos próximos
            st.markdown("""
            <div class="styled-table-container" style="max-height: 300px; overflow-y: auto;">
                <table class="styled-table">
                    <thead>
                        <tr>
                            <th>Tipo</th>
                            <th>Descrição</th>
                            <th>Vencimento</th>
                            <th>Dias</th>
                            <th>Valor</th>
                        </tr>
                    </thead>
                    <tbody>
            """, unsafe_allow_html=True)
            
            for venc in vencimentos:
                # Determinar classe de status com base nos dias restantes
                if venc["dias_restantes"] <= 3:
                    status_class = "badge-danger"
                    status_text = "Urgente"
                elif venc["dias_restantes"] <= 7:
                    status_class = "badge-warning"
                    status_text = "Próximo"
                else:
                    status_class = "badge-success"
                    status_text = "OK"
                
                st.markdown(f"""
                    <tr>
                        <td>{venc["tipo"]}</td>
                        <td>{venc["descricao"]}</td>
                        <td>{venc["data"].strftime("%d/%m/%Y")}</td>
                        <td><span class="badge {status_class}">{venc["dias_restantes"]} dias</span></td>
                        <td>{formatar_moeda(venc["valor"])}</td>
                    </tr>
                """, unsafe_allow_html=True)
            
            st.markdown("""
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Não há vencimentos nos próximos 30 dias.")
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    # Seção de ações rápidas
    st.markdown("""
    <h2 class="card-title">Ações Rápidas</h2>
    <div class="card">
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px;">
    """, unsafe_allow_html=True)
    
    # Usar colunas para criar botões de ação rápida
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("➕ Novo Gasto", use_container_width=True):
            st.session_state.pagina_atual = "gastos"
            st.session_state.mostrar_form_gasto = True
            st.rerun()
    
    with col2:
        if st.button("💰 Novo Investimento", use_container_width=True):
            st.session_state.pagina_atual = "investimentos"
            st.session_state.mostrar_form_investimento = True
            st.rerun()
    
    with col3:
        if st.button("🎯 Novo Objetivo", use_container_width=True):
            st.session_state.pagina_atual = "objetivos"
            st.session_state.mostrar_form_objetivo = True
            st.rerun()
    
    with col4:
        if st.button("💳 Nova Dívida", use_container_width=True):
            st.session_state.pagina_atual = "dividas"
            st.session_state.mostrar_form_divida = True
            st.rerun()
    
    with col5:
        if st.button("🔒 Novo Seguro", use_container_width=True):
            st.session_state.pagina_atual = "seguros"
            st.session_state.mostrar_form_seguro = True
            st.rerun()
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True) 