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
    
    # Adicionar estilos CSS diretos para a página
    st.markdown("""
    <style>
    /* Containers de gráficos - Estilos injetados diretamente */
    .grafico-container {
      background-color: white !important;
      border-radius: 10px !important; 
      box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
      margin-bottom: 20px !important;
      overflow: hidden !important;
    }
    
    .titulo-grafico {
      font-size: 1.1rem !important;
      font-weight: 600 !important;
      color: #2A5CAA !important;
      padding: 16px !important;
      background-color: #f8f9fa !important;
      border-bottom: 1px solid #e9ecef !important;
      margin: 0 !important;
    }
    
    .conteudo-grafico {
      padding: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Seção de ações rápidas no topo com título
    st.markdown("""
    <h3 class="card-title">Ações Rápidas</h3>
    """, unsafe_allow_html=True)
    
    # Usar colunas para criar botões de ação rápida
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("➕ Novo Gasto", key="btn_gasto", help="Adicionar novo gasto"):
            st.session_state.pagina_atual = "gastos"
            st.session_state.mostrar_form_gasto = True
            st.rerun()
    
    with col2:
        if st.button("💰 Investimento", key="btn_investimento", help="Adicionar novo investimento"):
            st.session_state.pagina_atual = "investimentos"
            st.session_state.mostrar_form_investimento = True
            st.rerun()
    
    with col3:
        if st.button("🎯 Objetivo", key="btn_objetivo", help="Adicionar novo objetivo"):
            st.session_state.pagina_atual = "objetivos"
            st.session_state.mostrar_form_objetivo = True
            st.rerun()
    
    with col4:
        if st.button("💳 Dívida", key="btn_divida", help="Adicionar nova dívida"):
            st.session_state.pagina_atual = "dividas"
            st.session_state.mostrar_form_divida = True
            st.rerun()
    
    with col5:
        if st.button("🔒 Seguro", key="btn_seguro", help="Adicionar novo seguro"):
            st.session_state.pagina_atual = "seguros"
            st.session_state.mostrar_form_seguro = True
            st.rerun()
    
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
        <div class="card dashboard-card">
            <div class="metric-label">Patrimônio Líquido</div>
            <div class="metric-value positive" style="color: {patrimonio_liquido >= 0 and 'var(--positive)' or 'var(--negative)'} !important;">{formatar_moeda(patrimonio_liquido)}</div>
            <div>{len(investimentos)} ativos - {len(dividas)} dívidas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card dashboard-card">
            <div class="metric-label">Investimentos</div>
            <div class="metric-value positive">{formatar_moeda(total_investimentos)}</div>
            <div>{len(investimentos)} ativos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card dashboard-card">
            <div class="metric-label">Dívidas</div>
            <div class="metric-value negative">{formatar_moeda(total_dividas)}</div>
            <div>{len(dividas)} pendentes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="card dashboard-card">
            <div class="metric-label">Gastos do Mês</div>
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
        # Novo método para renderizar os gráficos
        st.markdown("""
        <div class="grafico-container">
            <div class="titulo-grafico">Distribuição de Investimentos</div>
            <div class="conteudo-grafico">
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
                color_discrete_sequence=px.colors.qualitative.Pastel1,
                hole=0.6,
                template="plotly_white"
            )
            
            fig.update_layout(
                margin=dict(t=0, b=0, l=0, r=0),
                height=280,
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=-0.2, 
                    xanchor="center", 
                    x=0.5,
                    font=dict(size=11, family="Arial, sans-serif")
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                uniformtext_minsize=12,
                uniformtext_mode='hide'
            )
            
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                insidetextfont=dict(color='white', size=12, family="Arial, sans-serif"),
                hovertemplate='<b>%{label}</b><br>Valor: %{value:,.2f}<br>Percentual: %{percent}',
                marker=dict(
                    line=dict(color='white', width=2),
                    pattern=dict(shape="")
                ),
                rotation=45
            )
            
            # Adicionar título central no donut
            fig.add_annotation(
                text=f"R$ {sum(df_inv['Valor']):,.0f}",
                x=0.5, y=0.5,
                font=dict(size=14, color='#333', family="Arial, sans-serif"),
                showarrow=False
            )
            
            # Configurações adicionais para garantir a aparência correta
            config = {
                'displayModeBar': False,
                'responsive': True
            }
            
            st.plotly_chart(fig, use_container_width=True, config=config)
        else:
            st.info("Adicione investimentos para visualizar a distribuição.")
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card único contendo título e gráfico
        st.markdown("""
        <div class="grafico-container">
            <div class="titulo-grafico">Progresso dos Objetivos</div>
            <div class="conteudo-grafico">
        """, unsafe_allow_html=True)
        
        if objetivos:
            # Preparar dados para o gráfico de objetivos
            nomes_obj = [o.get("nome", f"Objetivo {i+1}") for i, o in enumerate(objetivos)]
            valores_total = [float(o.get("valor_total", 0) or 0) for o in objetivos]
            valores_atual = [float(o.get("valor_atual", 0) or 0) for o in objetivos]
            
            # Calcular percentuais para mostrar
            percentuais = [
                round(atual / total * 100 if total > 0 else 0, 0)
                for atual, total in zip(valores_atual, valores_total)
            ]
            
            # Usar componentes nativos do Streamlit em vez de HTML
            for i, (nome, atual, total, percentual) in enumerate(zip(nomes_obj, valores_atual, valores_total, percentuais)):
                # Definir cores baseadas no progresso
                cor_barra = "#1976D2"  # Azul padrão
                if percentual >= 75:
                    cor_barra = "#4CAF50"  # Verde para progresso alto
                elif percentual >= 25:
                    cor_barra = "#FFC107"  # Amarelo para progresso médio
                else:
                    cor_barra = "#F44336"  # Vermelho para progresso baixo
                
                # Definir ícone de conclusão baseado no progresso
                if percentual >= 100:
                    icone_status = "✨"  # Estrela para objetivo concluído
                elif percentual >= 75:
                    icone_status = "🔥"  # Fogo para progresso alto
                elif percentual >= 50:
                    icone_status = "💪"  # Braço forte para progresso médio
                elif percentual >= 25:
                    icone_status = "🚶"  # Pessoa andando para progresso baixo
                else:
                    icone_status = "🏁"  # Bandeira de início para progresso muito baixo
                
                # Criar linhas para cada objetivo
                st.markdown(f"### {nome} - {percentual:.0f}%", help=f"{formatar_moeda(atual)} de {formatar_moeda(total)}")
                
                # Linha superior com ícones
                col_start, col_prog, col_end = st.columns([1, 10, 1])
                
                with col_start:
                    st.markdown(f"<div style='text-align:center; font-size:24px;'>🏁</div>", unsafe_allow_html=True)
                
                with col_prog:
                    # Barra de progresso
                    progress_bar = st.progress(float(percentual) / 100)
                    
                    # Exibir ícone do status atual
                    current_pos = max(min(float(percentual) / 100, 0.95), 0.05)  # Limitar entre 5% e 95%
                    st.markdown(f"""
                    <div style='
                        position: relative;
                        height: 20px;
                        margin-top: -30px;
                    '>
                        <div style='
                            position: absolute;
                            left: {current_pos * 100}%;
                            transform: translateX(-50%);
                            font-size: 24px;
                        '>{icone_status}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_end:
                    st.markdown(f"<div style='text-align:center; font-size:24px;'>🏆</div>", unsafe_allow_html=True)
                
                # Mostrar valores
                col_zero, col_current, col_total = st.columns([1, 10, 1])
                with col_zero:
                    st.markdown("<div style='text-align:left; font-size:10px;'>R$ 0</div>", unsafe_allow_html=True)
                with col_current:
                    st.markdown(f"<div style='text-align:center; font-size:12px;'>{formatar_moeda(atual)} de {formatar_moeda(total)}</div>", unsafe_allow_html=True)
                with col_total:
                    st.markdown(f"<div style='text-align:right; font-size:10px;'>{formatar_moeda(total)}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
        else:
            st.info("Adicione objetivos para visualizar o progresso.")
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Linha 2 de visualizações
    col1, col2 = st.columns(2)
    
    with col1:
        # Card único contendo título e gráfico
        st.markdown("""
        <div class="grafico-container">
            <div class="titulo-grafico">Gastos por Categoria</div>
            <div class="conteudo-grafico">
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
            
            # Gráfico de barras para gastos com estilo moderno
            fig = px.bar(
                df_gastos, 
                x='Categoria', 
                y='Valor',
                color='Valor',
                color_continuous_scale=["#FFCDD2", "#E53935"],
                text='Valor',
                template="plotly_white"
            )
            
            fig.update_traces(
                texttemplate='R$ %{text:,.0f}',
                textposition='auto',
                textfont=dict(color="white", size=11, family="Arial, sans-serif"),
                marker=dict(
                    line=dict(width=1, color='#fff'),
                    pattern=dict(shape="")
                ),
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}'
            )
            
            fig.update_layout(
                yaxis_title="Valor (R$)",
                xaxis_title="",
                coloraxis_showscale=False,
                height=280,
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False,
                    tickangle=-45,
                    tickfont=dict(size=10, family="Arial, sans-serif")
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.05)',
                    zeroline=False,
                    tickformat='R$ %{y:,.0f}'
                ),
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Arial, sans-serif"
                )
            )
            
            # Configurações adicionais para garantir a aparência correta
            config = {
                'displayModeBar': False,
                'responsive': True
            }
            
            st.plotly_chart(fig, use_container_width=True, config=config)
        else:
            st.info("Adicione gastos no mês atual para visualizar a distribuição por categoria.")
        
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card único contendo título e vencimentos
        st.markdown("""
        <div class="grafico-container">
            <div class="titulo-grafico">Vencimentos Próximos</div>
            <div class="conteudo-grafico">
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
        
        # Ordenar por proximidade da data
        vencimentos.sort(key=lambda x: x["dias_restantes"])
        
        # Container para vencimentos
        st.markdown("""
        <div style="max-height: 280px; overflow-y: auto; border-radius: 4px; padding: 0; margin: 0;">
        """, unsafe_allow_html=True)
        
        if vencimentos:
            # Criar uma tabela de vencimentos
            vencimentos_html = ""
            for v in vencimentos:
                tipo_badge = "danger" if v["tipo"] == "Dívida" else "warning"
                dias_badge = "danger" if v["dias_restantes"] <= 7 else "warning" if v["dias_restantes"] <= 15 else "success"
                
                vencimentos_html += f"""
                <div style="
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                    padding: 12px;
                    background-color: rgba(0,0,0,0.02);
                    border-radius: 8px;
                    border-left: 4px solid {'#EF5350' if tipo_badge == 'danger' else '#FFD700'};
                    transition: all 0.2s ease;
                ">
                    <div style="flex: 0 0 auto; margin-right: 10px;">
                        <span style="
                            display: inline-block;
                            padding: 4px 8px;
                            border-radius: 30px;
                            font-size: 0.7rem;
                            font-weight: 600;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            background-color: {'#EF5350' if tipo_badge == 'danger' else '#FFD700'};
                            color: {'white' if tipo_badge == 'danger' else '#333'};
                            box-shadow: 0 1px 3px rgba({'239, 83, 80' if tipo_badge == 'danger' else '255, 215, 0'}, 0.3);
                        ">{v["tipo"]}</span>
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600;">{v["descricao"]}</div>
                        <div style="font-size: 0.85rem; color: #666;">{v["data"].strftime("%d/%m/%Y")} • {formatar_moeda(v["valor"])}</div>
                    </div>
                    <div style="flex: 0 0 auto;">
                        <span style="
                            display: inline-block;
                            padding: 4px 8px;
                            border-radius: 30px;
                            font-size: 0.7rem;
                            font-weight: 600;
                            text-transform: uppercase;
                            letter-spacing: 0.5px;
                            background-color: {'#EF5350' if dias_badge == 'danger' else '#FFD700' if dias_badge == 'warning' else '#4CAF50'};
                            color: {'#333' if dias_badge == 'warning' else 'white'};
                            box-shadow: 0 1px 3px rgba({'239, 83, 80' if dias_badge == 'danger' else '255, 215, 0' if dias_badge == 'warning' else '76, 175, 80'}, 0.3);
                        ">{v["dias_restantes"]} dias</span>
                    </div>
                </div>
                """
            
            st.markdown(f"{vencimentos_html}", unsafe_allow_html=True)
        else:
            st.info("Não há vencimentos nos próximos 30 dias.")
        
        st.markdown("""
            </div>
            </div>
        </div>
        """, unsafe_allow_html=True)