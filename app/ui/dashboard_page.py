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
    Renderiza a página principal do dashboard.
    """
    st.header("Dashboard Financeiro")
    
    # Carregar dados
    user_data = load_user_data() or {"nome": "Usuário", "renda_mensal": 0.0}
    gastos = load_gastos()
    investimentos = load_investimentos()
    dividas = load_dividas()
    seguros = load_seguros()
    objetivos = load_objetivos()
    
    # Obter valores
    renda_mensal = user_data.get("renda_mensal", 0)
    mes_atual = datetime.now().strftime("%Y-%m")
    gastos_mes_atual = calcular_gastos_periodo(gastos, mes_atual)
    
    # Calcular saldo do mês
    saldo_mes = renda_mensal - gastos_mes_atual
    percentual_gasto = (gastos_mes_atual / renda_mensal * 100) if renda_mensal > 0 else 0
    
    # Mostrar cartões com valores principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:20px; border-radius:10px; text-align:center;">
            <h4 style="margin:0;">Receita Mensal</h4>
            <h2 style="color: #1E88E5; margin:10px 0 0 0;">{formatar_moeda(renda_mensal)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:20px; border-radius:10px; text-align:center;">
            <h4 style="margin:0;">Gastos do Mês</h4>
            <h2 style="color: {'#F44336' if percentual_gasto > 80 else '#FF9800' if percentual_gasto > 50 else '#4CAF50'}; margin:10px 0 0 0;">{formatar_moeda(gastos_mes_atual)}</h2>
            <p>({percentual_gasto:.1f}% da receita)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:20px; border-radius:10px; text-align:center;">
            <h4 style="margin:0;">Saldo do Mês</h4>
            <h2 style="color: {'#4CAF50' if saldo_mes >= 0 else '#F44336'}; margin:10px 0 0 0;">{formatar_moeda(saldo_mes)}</h2>
            <p>({(saldo_mes / renda_mensal * 100) if renda_mensal > 0 else 0:.1f}% da receita)</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Adicionar progresso mensal
    st.markdown("### Progresso Mensal")
    
    # Criar barra de progresso personalizada
    dias_no_mes = calendar.monthrange(datetime.now().year, datetime.now().month)[1]
    dia_atual = datetime.now().day
    progresso_mes = min(dia_atual / dias_no_mes * 100, 100)
    
    st.markdown(f"""
    <div style="margin-top:10px; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span>Dia 1</span>
            <span>Dia {dia_atual} de {dias_no_mes}</span>
            <span>Dia {dias_no_mes}</span>
        </div>
        <div style="background-color: #E0E0E0; height: 10px; border-radius: 5px;">
            <div style="background-color: #1E88E5; width: {progresso_mes}%; height: 100%; border-radius: 5px;"></div>
        </div>
        <div style="text-align:right; margin-top:5px;">
            <span>Progresso: {progresso_mes:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Dividir em duas colunas para gráficos
    col_esq, col_dir = st.columns([3, 2])
    
    with col_esq:
        # Mostrar gráfico de gastos por categoria para o mês atual
        st.subheader(f"Gastos por Categoria ({datetime.now().strftime('%B/%Y')})")
        
        # Agrupar gastos por categoria para o mês atual
        gastos_por_categoria = {}
        for gasto in gastos:
            if gasto["data"].startswith(mes_atual):
                categoria = gasto.get("categoria", "Outros")
                if categoria not in gastos_por_categoria:
                    gastos_por_categoria[categoria] = 0
                gastos_por_categoria[categoria] += gasto["valor"]
        
        if gastos_por_categoria:
            # Criar DataFrame para o gráfico
            df_categorias = pd.DataFrame({
                'Categoria': list(gastos_por_categoria.keys()),
                'Valor': list(gastos_por_categoria.values())
            })
            
            # Ordenar por valor
            df_categorias = df_categorias.sort_values('Valor', ascending=False)
            
            # Criar gráfico de barras
            fig = px.bar(
                df_categorias,
                x='Categoria',
                y='Valor',
                color='Categoria',
                title=f"Gastos por Categoria - {datetime.now().strftime('%B/%Y')}",
                text_auto=True
            )
            
            fig.update_layout(
                xaxis_title="",
                yaxis_title="Valor (R$)",
                showlegend=False
            )
            
            # Formatar valores no hover
            fig.update_traces(
                hovertemplate="<b>%{x}</b><br>Valor: " + 
                             f"{formatar_moeda(0).replace('0', '%{y:,.2f}')}<br>"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"Nenhum gasto registrado para {datetime.now().strftime('%B/%Y')}.")
        
        # Mostrar tendência de gastos dos últimos meses
        st.subheader("Tendência de Gastos (Últimos 6 Meses)")
        
        # Obter meses anteriores
        meses_anteriores = obter_meses_anteriores(6)
        
        # Verificar se há gastos nos meses anteriores
        tem_gastos_anteriores = any(
            any(gasto["data"].startswith(mes["formato_numerico"]) for gasto in gastos)
            for mes in meses_anteriores
        )
        
        if tem_gastos_anteriores:
            # Criar gráfico de tendência
            fig_tendencia = criar_grafico_tendencia_gastos(gastos, meses_anteriores)
            st.plotly_chart(fig_tendencia, use_container_width=True)
        else:
            st.info("Não há dados suficientes para mostrar a tendência de gastos.")
    
    with col_dir:
        # Mostrar resumo do patrimônio
        st.subheader("Resumo do Patrimônio")
        
        # Calcular valores
        patrimonio_bruto, total_dividas, patrimonio_liquido = calcular_patrimonios(investimentos, dividas)
        
        # Mostrar valores em cards modernos usando a classe 'card' definida no CSS
        st.markdown("""
        <div class="card success">
            <div class="metric-label">Patrimônio Bruto</div>
            <div class="metric-value">{}</div>
            <div>Total de todos seus investimentos</div>
        </div>
        """.format(formatar_moeda(patrimonio_bruto)), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card danger">
            <div class="metric-label">Total de Dívidas</div>
            <div class="metric-value">{}</div>
            <div>Soma de todas suas dívidas</div>
        </div>
        """.format(formatar_moeda(total_dividas)), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
            <div class="metric-label">Patrimônio Líquido</div>
            <div class="metric-value">{}</div>
            <div>Patrimônio bruto menos dívidas</div>
        </div>
        """.format(formatar_moeda(patrimonio_liquido)), unsafe_allow_html=True)

        # Informações adicionais
        if investimentos:
            # Encontrar o investimento com maior rentabilidade
            # Certifique-se de que None seja convertido para 0 antes da comparação
            rentabilidades = [float(i.get("rentabilidade_anual", 0) or 0) for i in investimentos]
            maior_rentabilidade = max(rentabilidades, default=0)
            melhor_investimento = next((i for i in investimentos if i.get("rentabilidade_anual", 0) == maior_rentabilidade), None)
            
            if melhor_investimento and maior_rentabilidade > 0:
                st.markdown("""
                <div class="card success" style="background-color: rgba(76, 175, 80, 0.1);">
                    <div class="metric-label">Melhor Investimento</div>
                    <div class="metric-value" style="font-size: 1.5rem;">{}</div>
                    <div>Rentabilidade de {}% ao ano</div>
                </div>
                """.format(
                    melhor_investimento.get("descricao", ""),
                    maior_rentabilidade
                ), unsafe_allow_html=True)
        
        # Próximas dívidas ou seguros a vencer
        st.markdown("### Próximos Vencimentos")
        
        # Combinar dívidas e seguros em uma única lista
        vencimentos = []
        
        for divida in dividas:
            if "data_vencimento" in divida and "descricao" in divida:
                try:
                    data_venc = datetime.strptime(divida["data_vencimento"], "%Y-%m-%d")
                    vencimentos.append({
                        "tipo": "Dívida",
                        "descricao": divida["descricao"],
                        "data": data_venc,
                        "valor": divida.get("valor_atual", 0)
                    })
                except:
                    pass
        
        for seguro in seguros:
            if "data_renovacao" in seguro and "descricao" in seguro:
                try:
                    data_venc = datetime.strptime(seguro["data_renovacao"], "%Y-%m-%d")
                    vencimentos.append({
                        "tipo": "Seguro",
                        "descricao": seguro["descricao"],
                        "data": data_venc,
                        "valor": seguro.get("premio_anual", 0)
                    })
                except:
                    pass
        
        # Ordenar por data de vencimento
        vencimentos.sort(key=lambda x: x["data"])
        
        # Mostrar os próximos 3 vencimentos
        proximos = vencimentos[:3]
        
        if proximos:
            for item in proximos:
                dias_faltantes = (item["data"] - datetime.now()).days
                cor = "success"
                if dias_faltantes <= 7: cor = "danger"
                elif dias_faltantes <= 30: cor = "warning"
                
                st.markdown(f"""
                <div class="card {cor}" style="margin-bottom: 10px; padding: 10px;">
                    <div style="display:flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{item["descricao"]}</strong> ({item["tipo"]})
                            <div>{item["data"].strftime("%d/%m/%Y")}</div>
                        </div>
                        <div style="text-align: right;">
                            <div>{formatar_moeda(item["valor"])}</div>
                            <div>{dias_faltantes} dias</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Não há vencimentos próximos.")
        
        # Mostrar objetivos próximos de conclusão
        st.markdown("### Objetivos Próximos")
        
        if objetivos:
            # Calcular percentual de conclusão para cada objetivo
            objetivos_com_progresso = []
            for obj in objetivos:
                valor_total = obj.get("valor_total", 1)
                valor_atual = obj.get("valor_atual", 0)
                percentual = (valor_atual / valor_total) * 100 if valor_total > 0 else 0
                
                # Adicionar à lista com percentual calculado
                obj_temp = obj.copy()
                obj_temp["percentual"] = percentual
                objetivos_com_progresso.append(obj_temp)
            
            # Ordenar objetivos pelo percentual de conclusão (descendente)
            objetivos_ordenados = sorted(objetivos_com_progresso, key=lambda x: x["percentual"], reverse=True)
            
            # Mostrar os 3 objetivos mais próximos de conclusão
            objetivos_proximos = objetivos_ordenados[:3]
            
            for obj in objetivos_proximos:
                percentual = obj["percentual"]
                cor = "success" if percentual >= 75 else "warning" if percentual >= 50 else "danger"
                
                st.markdown(f"""
                <div class="card {cor}" style="margin-bottom: 10px; padding: 10px;">
                    <div style="display:flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{obj.get("nome", "Objetivo")}</strong>
                            <div>{formatar_moeda(obj.get("valor_atual", 0))} de {formatar_moeda(obj.get("valor_total", 0))}</div>
                        </div>
                        <div style="text-align: right;">
                            <div>{percentual:.1f}%</div>
                            <div>concluído</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhum objetivo financeiro cadastrado.")
    
    # Mostrar ações recomendadas
    st.markdown("---")
    st.subheader("Ações Recomendadas")
    
    acoes = []
    
    # Verificar se a pessoa está gastando mais do que ganha
    if saldo_mes < 0:
        acoes.append(("Alerta de saldo negativo", "Seus gastos estão superando sua receita mensal. Considere revisar despesas.", "#F44336"))
    
    # Verificar se há gastos cadastrados
    if not gastos:
        acoes.append(("Cadastre seus gastos", "Registre seus gastos para ter um melhor controle financeiro.", "#FF9800"))
    
    # Verificar se há investimentos cadastrados
    if not investimentos:
        acoes.append(("Comece a investir", "Cadastre seus investimentos ou inicie uma estratégia de investimentos.", "#1E88E5"))
    
    # Verificar se há patrimônio líquido negativo
    if patrimonio_liquido < 0:
        acoes.append(("Patrimônio líquido negativo", "Suas dívidas superam seus ativos. Priorize a quitação de dívidas.", "#F44336"))
    
    # Verificar proporção de gastos (se está gastando mais de 80% da renda)
    if renda_mensal > 0 and percentual_gasto > 80:
        acoes.append(("Despesas elevadas", f"Seus gastos representam {percentual_gasto:.1f}% da sua receita. Considere reduzir despesas.", "#FF9800"))
    
    # Verificar se há objetivos cadastrados
    if not objetivos:
        acoes.append(("Defina seus objetivos", "Cadastre seus objetivos financeiros para acompanhar seu progresso.", "#1E88E5"))
    
    # Verificar se há objetivos sem investimentos vinculados
    objetivos_sem_investimentos = [obj for obj in objetivos if not obj.get("investimentos_vinculados")]
    if objetivos_sem_investimentos:
        acoes.append(("Vincule investimentos aos objetivos", "Associe seus investimentos aos seus objetivos financeiros.", "#FF9800"))
    
    # Exibir ações recomendadas
    if acoes:
        for titulo, descricao, cor in acoes:
            st.markdown(f"""
            <div style="background-color:{'#263238' if st.session_state.tema == 'escuro' else '#F5F5F5'}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:5px solid {cor};">
                <h4 style="margin:0; color:{cor};">{titulo}</h4>
                <p style="margin:10px 0 0 0;">{descricao}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("Parabéns! Suas finanças parecem estar em ordem. Continue acompanhando regularmente.") 