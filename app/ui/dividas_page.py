"""
Módulo para a página de Dívidas do aplicativo de Controle Financeiro Pessoal.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import uuid

# Importar funções de manipulação de dados
from app.data.data_handler import (
    load_user_data,
    load_dividas,
    save_dividas,
    add_divida,
    delete_divida
)

def formatar_moeda(valor):
    """
    Formata um valor numérico como moeda brasileira (R$).
    """
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_dias_para_vencimento(data_vencimento):
    """
    Calcula quantos dias faltam para o vencimento da dívida.
    
    Args:
        data_vencimento (str): Data de vencimento no formato "YYYY-MM-DD"
        
    Returns:
        int: Número de dias até o vencimento, negativo se já venceu
    """
    if not data_vencimento:
        return None
    
    try:
        data_venc = datetime.strptime(data_vencimento, "%Y-%m-%d")
        hoje = datetime.now()
        return (data_venc - hoje).days
    except (ValueError, TypeError):
        return None

def render_dividas_page():
    """
    Renderiza a página de Controle de Dívidas.
    """
    # Cabeçalho moderno
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-right: 0.8rem;">💰</div>
        <div>
            <h1 style="margin: 0; padding: 0;">Controle de Dívidas</h1>
            <p style="margin: 0; padding: 0; color: var(--gray);">Gerencie suas dívidas e planeje a quitação</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dívidas
    dividas = load_dividas()
    
    # Mostrar resumo das dívidas
    mostrar_resumo_dividas(dividas)
    
    # Botão em destaque para adicionar nova dívida
    col_btn, col_empty = st.columns([1, 3])
    with col_btn:
        if st.button("➕ Adicionar Dívida", type="primary", use_container_width=True):
            st.session_state.mostrar_form_divida = True
            
    # Se o botão foi clicado, mostrar o formulário
    if st.session_state.get("mostrar_form_divida", False):
        with st.form("form_nova_divida"):
            st.markdown("### Registre sua dívida")
            
            # Campos principais em colunas
            col1, col2 = st.columns(2)
            
            with col1:
                descricao = st.text_input("Nome da dívida", 
                                         placeholder="Ex: Cartão Nubank, Financiamento Carro",
                                         help="Um nome para identificar facilmente esta dívida")
                
                # Tipo de dívida com ícones
                tipo_divida = st.selectbox(
                    "Tipo da dívida",
                    options=[
                        "💳 Cartão de Crédito",
                        "🏦 Empréstimo",
                        "🏠 Financiamento",
                        "🧾 Conta a Pagar",
                        "👤 Dívida Pessoal",
                        "📦 Outra"
                    ],
                    help="Categoria da dívida"
                )
                
                # Remover emoji para armazenar apenas o texto
                tipo_divida_valor = tipo_divida.split(" ", 1)[1]
                
                credor = st.text_input(
                    "Credor/Instituição",
                    placeholder="Ex: Banco Itaú, Loja X, João",
                    help="Nome do banco, loja ou pessoa para quem deve"
                )
            
            with col2:
                valor_atual = st.number_input(
                    "Saldo restante a ser pago (R$)",
                    min_value=0.01,
                    step=100.0,
                    format="%.2f",
                    help="Valor atual que resta para ser pago"
                )
                
                valor_parcela = st.number_input(
                    "Valor da parcela (R$)",
                    min_value=0.01,
                    step=50.0,
                    format="%.2f",
                    help="Quanto você paga em cada parcela"
                )
                
                taxa_juros = st.number_input(
                    "Taxa de juros (% ao mês)",
                    min_value=0.0,
                    step=0.1,
                    format="%.2f",
                    help="Taxa de juros mensal aplicada a esta dívida"
                )
            
            # Segunda linha de campos
            col3, col4 = st.columns(2)
            
            with col3:
                parcelas_total = st.number_input(
                    "Número de parcelas",
                    min_value=1,
                    max_value=500,
                    value=1,
                    step=1,
                    help="Quantidade total de parcelas"
                )
                
                parcela_atual = st.number_input(
                    "Parcela atual",
                    min_value=1,
                    max_value=int(parcelas_total),
                    value=1,
                    step=1,
                    help="Qual parcela você está pagando agora"
                )
                
                valor_inicial = valor_atual + (valor_parcela * (parcela_atual - 1))
            
            with col4:
                data_inicio = st.date_input(
                    "Data de início", 
                    value=datetime.now(),
                    help="Quando a dívida foi contraída"
                )
                
                data_vencimento = st.date_input(
                    "Data de vencimento", 
                    value=datetime.now() + timedelta(days=30),
                    help="Próxima data de vencimento"
                )
                
                # Calcular parcelas pagas
                parcelas_pagas = parcela_atual - 1
            
            # Observações
            detalhes = st.text_area(
                "Observações",
                placeholder="Informações adicionais sobre essa dívida...",
                help="Detalhes que você queira lembrar sobre esta dívida"
            )
            
            # Opção para registrar automaticamente no controle de gastos
            st.markdown("### Controle de gastos")
            
            registrar_gasto = st.checkbox(
                "Registrar parcela automaticamente no controle de gastos",
                value=True,
                help="A parcela será adicionada automaticamente no controle de gastos"
            )
            
            if registrar_gasto:
                col_ga, col_gb = st.columns(2)
                
                with col_ga:
                    gasto_categoria = st.selectbox(
                        "Categoria do gasto",
                        options=["Moradia", "Educação", "Saúde", "Transporte", "Serviços", "Outra"],
                        help="Como este gasto será categorizado"
                    )
                
                with col_gb:
                    gasto_tipo = st.radio(
                        "Tipo de gasto",
                        options=["fixo", "variavel"],
                        horizontal=True,
                        format_func=lambda x: "Fixo" if x == "fixo" else "Variável",
                        help="Se é um gasto fixo (ocorre todo mês) ou variável"
                    )
            
            # Botões de ação
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("💾 Salvar dívida", use_container_width=True)
            with col_btn2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                # Verificar se o nome foi preenchido
                if not descricao:
                    st.error("Por favor, informe um nome para a dívida.")
                elif valor_atual <= 0:
                    st.error("O valor restante deve ser maior que zero.")
                elif valor_parcela <= 0:
                    st.error("O valor da parcela deve ser maior que zero.")
                else:
                    # Criar nova dívida
                    nova_divida = {
                        "id": str(uuid.uuid4()),
                        "descricao": descricao,
                        "tipo": tipo_divida_valor,
                        "valor_inicial": valor_inicial,
                        "valor_atual": valor_atual,
                        "valor_parcela": valor_parcela,
                        "data_inicio": data_inicio.strftime("%Y-%m-%d"),
                        "data_vencimento": data_vencimento.strftime("%Y-%m-%d"),
                        "taxa_juros": taxa_juros,
                        "parcelas_total": int(parcelas_total),
                        "parcela_atual": int(parcela_atual),
                        "parcelas_pagas": int(parcelas_pagas),
                        "credor": credor,
                        "detalhes": detalhes,
                        "registrar_gasto": registrar_gasto
                    }
                    
                    # Adicionar informações de registro de gasto, se selecionado
                    if registrar_gasto:
                        nova_divida["gasto_categoria"] = gasto_categoria
                        nova_divida["gasto_tipo"] = gasto_tipo
                    
                    # Adicionar à lista de dívidas
                    if add_divida(nova_divida):
                        # Se configurado para registrar no controle de gastos
                        if registrar_gasto:
                            from app.data.data_handler import add_gasto
                            
                            novo_gasto = {
                                "descricao": f"Parcela {parcela_atual}/{parcelas_total} - {descricao}",
                                "valor": valor_parcela,
                                "data": data_vencimento.strftime("%Y-%m-%d"),
                                "categoria": gasto_categoria,
                                "tipo": gasto_tipo,
                                "observacao": f"Gerado automaticamente do controle de dívidas - {credor}"
                            }
                            
                            # Adicionar gasto
                            add_gasto(novo_gasto)
                            
                            st.success("✅ Dívida adicionada com sucesso e parcela registrada no controle de gastos!")
                        else:
                            st.success("✅ Dívida adicionada com sucesso!")
                            
                        st.session_state.mostrar_form_divida = False
                        st.rerun()
                    else:
                        st.error("Erro ao adicionar dívida.")
                
            if cancel:
                st.session_state.mostrar_form_divida = False
                st.rerun()
    
    # Lista de dívidas existentes
    if dividas:
        st.subheader("Suas Dívidas")
        mostrar_lista_dividas(dividas)
    else:
        st.info("Você ainda não tem dívidas cadastradas.")

def mostrar_resumo_dividas(dividas):
    # Calcular totais
    total_inicial = sum(d.get("valor_inicial", d.get("valor_total", 0)) for d in dividas)
    total_atual = sum(d.get("valor_atual", d.get("valor_restante", 0)) for d in dividas)
    total_pago = total_inicial - total_atual
    
    # Mostrar resumo em cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card danger">
            <div class="metric-label">Total de Dívidas</div>
            <div class="metric-value">{formatar_moeda(total_atual)}</div>
            <div>Valor atual pendente</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Valor Original</div>
            <div class="metric-value">{formatar_moeda(total_inicial)}</div>
            <div>Total contratado</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Verificar se há algum pagamento
        card_class = "success" if total_pago > 0 else ""
        
        st.markdown(f"""
        <div class="card {card_class}">
            <div class="metric-label">Já Pago</div>
            <div class="metric-value">{formatar_moeda(total_pago)}</div>
            <div style="margin-top: 0.5rem; font-size: 0.9rem; color: var(--text-color-secondary);">
                <div>Valor original: {formatar_moeda(total_inicial)}</div>
                <div>Valor pago: {formatar_moeda(total_pago)}</div>
                <div>{((total_pago / total_inicial) * 100 if total_inicial > 0 else 0):.1f}% do total</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Criar barra de progresso
    st.subheader("Progresso de pagamento")
    progresso = total_pago / total_inicial if total_inicial > 0 else 0
    st.progress(progresso)

def mostrar_lista_dividas(dividas):
    # Criar abas para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["Todas as Dívidas", "Próximos Vencimentos", "Análise"])
    
    with tab1:
        if dividas:
            # Listagem de dívidas em forma de cards
            st.subheader("Lista de Dívidas")
            
            # Ordenar dívidas por valor atual (maior para menor)
            dividas_ordenadas = sorted(dividas, key=lambda x: x.get("valor_atual", x.get("valor_restante", 0)), reverse=True)
            
            for divida in dividas_ordenadas:
                # Calcular dados
                valor_atual = divida.get("valor_atual", divida.get("valor_restante", 0))
                valor_inicial = divida.get("valor_inicial", divida.get("valor_total", 0))
                
                # Calcular progresso de pagamento e data de vencimento
                progresso_pagamento = ((valor_inicial - valor_atual) / valor_inicial) * 100 if valor_inicial > 0 else 0
                
                # Verificar se tem data de vencimento
                data_vencimento = divida.get("data_vencimento", "")
                dias_para_vencimento = calcular_dias_para_vencimento(data_vencimento) if data_vencimento else None
                
                # Definir classe de status com base no vencimento
                status_class = ""
                status_text = "Sem data de vencimento"
                
                if dias_para_vencimento is not None:
                    if dias_para_vencimento < 0:
                        status_class = "danger"
                        status_text = f"Vencida há {abs(dias_para_vencimento)} dias"
                    elif dias_para_vencimento == 0:
                        status_class = "danger"
                        status_text = "Vence hoje!"
                    elif dias_para_vencimento <= 7:
                        status_class = "warning"
                        status_text = f"Vence em {dias_para_vencimento} dias"
                    else:
                        status_class = "success"
                        status_text = f"Vence em {dias_para_vencimento} dias"
                
                # Criar card para cada dívida
                st.markdown(f"""
                <div class="card" style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-size: 1.1rem; font-weight: 500;">{divida.get('descricao', 'Dívida')}</div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: var(--red);">
                            {formatar_moeda(valor_atual)}
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                        <div style="color: var(--gray);">Tipo: {divida.get('tipo', divida.get('credor', 'Não especificado'))}</div>
                        <div class="badge {status_class}">{status_text}</div>
                    </div>
                    <div style="margin: 10px 0;">
                        <div style="font-size: 0.85rem; margin-bottom: 5px;">
                            Progresso de pagamento: {progresso_pagamento:.1f}%
                        </div>
                        <div style="background-color: var(--gray-lighter); height: 8px; border-radius: 4px;">
                            <div style="background-color: var(--green); width: {progresso_pagamento}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: var(--gray); font-size: 0.9rem;">
                        <div>Valor inicial: {formatar_moeda(valor_inicial)}</div>
                        <div>{divida.get('parcelas_pagas', 0)}/{divida.get('parcelas', divida.get('parcelas_total', 1))} parcelas</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Você ainda não possui dívidas registradas.")
    
    with tab2:
        st.subheader("Próximos Vencimentos")
        
        if dividas:
            # Filtrar dívidas com data de vencimento
            dividas_com_vencimento = [d for d in dividas if d.get("data_vencimento", "")]
            
            if dividas_com_vencimento:
                # Calcular dias para vencimento e adicionar à dívida
                for divida in dividas_com_vencimento:
                    divida["dias_para_vencimento"] = calcular_dias_para_vencimento(divida.get("data_vencimento", ""))
                
                # Ordenar por data de vencimento (mais próxima primeiro)
                dividas_ordenadas = sorted(dividas_com_vencimento, key=lambda x: x.get("dias_para_vencimento", 999999))
                
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
                .valor-coluna {
                    text-align: right;
                    font-weight: 500;
                }
                .data-coluna {
                    text-align: center;
                }
                .badge-vencimento {
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-size: 0.8rem;
                    text-align: center;
                }
                .vencido {
                    background-color: var(--red-light);
                    color: var(--red);
                }
                .proximo {
                    background-color: var(--yellow-light);
                    color: var(--yellow-dark);
                }
                .futuro {
                    background-color: var(--green-light);
                    color: var(--green);
                }
                </style>
                
                <table class="vencimento-tabela">
                    <thead>
                        <tr>
                            <th>Descrição</th>
                            <th>Valor</th>
                            <th>Vencimento</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                
                for divida in dividas_ordenadas:
                    valor_atual = divida.get("valor_atual", divida.get("valor_restante", 0))
                    dias = divida.get("dias_para_vencimento", 0)
                    
                    # Formatar data de vencimento
                    data_vencimento = datetime.strptime(divida.get("data_vencimento", "2023-01-01"), "%Y-%m-%d")
                    data_formatada = data_vencimento.strftime("%d/%m/%Y")
                    
                    # Definir status com base nos dias para vencimento
                    status_class = ""
                    status_text = ""
                    
                    if dias < 0:
                        status_class = "vencido"
                        status_text = f"Vencida há {abs(dias)} dias"
                    elif dias == 0:
                        status_class = "vencido"
                        status_text = "Vence hoje!"
                    elif dias <= 7:
                        status_class = "proximo"
                        status_text = f"Vence em {dias} dias"
                    else:
                        status_class = "futuro"
                        status_text = f"Vence em {dias} dias"
                    
                    st.markdown(f"""
                    <tr>
                        <td>{divida.get('descricao', 'Dívida')}</td>
                        <td class="valor-coluna">{formatar_moeda(valor_atual)}</td>
                        <td class="data-coluna">{data_formatada}</td>
                        <td><div class="badge-vencimento {status_class}">{status_text}</div></td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            else:
                st.info("Não há dívidas com data de vencimento definida.")
        else:
            st.info("Você ainda não possui dívidas registradas.")
            
    with tab3:
        st.subheader("Análise de Dívidas")
        
        if dividas:
            # Criar gráfico de distribuição por tipo de dívida
            tipos_divida = {}
            for divida in dividas:
                tipo = divida.get("tipo", divida.get("credor", "Outro"))
                valor = divida.get("valor_atual", divida.get("valor_restante", 0))
                
                if tipo not in tipos_divida:
                    tipos_divida[tipo] = 0
                tipos_divida[tipo] += valor
            
            # Criar DataFrame para o gráfico
            df_tipos = pd.DataFrame({
                "Tipo": tipos_divida.keys(),
                "Valor": tipos_divida.values()
            })
            
            # Adicionar coluna de porcentagem
            df_tipos["Porcentagem"] = df_tipos["Valor"] / df_tipos["Valor"].sum() * 100
            
            # Ordenar por valor (maior para menor)
            df_tipos = df_tipos.sort_values(by="Valor", ascending=False)
            
            # Definir cores para o gráfico
            cores = ['#DC3912', '#FF9900', '#990099', '#3366CC', '#109618', '#0099C6']
            
            # Criar gráfico de pizza
            fig = px.pie(
                df_tipos,
                values="Valor",
                names="Tipo",
                color_discrete_sequence=cores,
                hole=0.4
            )
            
            # Personalizar layout
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
                    text=f"Total<br>{formatar_moeda(sum(tipos_divida.values()))}",
                    x=0.5, y=0.5,
                    font_size=14,
                    showarrow=False
                )]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Mostrar detalhamento em tabela
            st.markdown("### Detalhamento por Tipo")
            
            # Formatar valores para exibição
            df_tipos["Valor Formatado"] = df_tipos["Valor"].apply(lambda x: formatar_moeda(x))
            df_tipos["Porcentagem Formatada"] = df_tipos["Porcentagem"].apply(lambda x: f"{x:.1f}%")
            
            # Criar tabela estilizada
            st.markdown("""
            <style>
            .tipo-tabela {
                width: 100%;
                border-collapse: collapse;
            }
            .tipo-tabela th {
                text-align: left;
                padding: 8px;
                border-bottom: 2px solid var(--gray-light);
            }
            .tipo-tabela td {
                text-align: left;
                padding: 8px;
                border-bottom: 1px solid var(--gray-lighter);
            }
            .tipo-tabela .valor-coluna {
                text-align: right;
            }
            .tipo-tabela .percent-coluna {
                text-align: right;
            }
            </style>
            
            <table class="tipo-tabela">
                <thead>
                    <tr>
                        <th>Tipo de Dívida</th>
                        <th class="valor-coluna">Valor Total</th>
                        <th class="percent-coluna">Percentual</th>
                    </tr>
                </thead>
                <tbody>
            """, unsafe_allow_html=True)
            
            for _, row in df_tipos.iterrows():
                st.markdown(f"""
                <tr>
                    <td>{row['Tipo']}</td>
                    <td class="valor-coluna">{row['Valor Formatado']}</td>
                    <td class="percent-coluna">{row['Porcentagem Formatada']}</td>
                </tr>
                """, unsafe_allow_html=True)
            
            st.markdown("</tbody></table>", unsafe_allow_html=True)
        else:
            st.info("Você ainda não possui dívidas registradas.")
    
    # Opção para excluir dívidas
    if dividas:
        st.markdown("### Gerenciar Dívidas")
        
        opcoes_exclusao = [f"{d.get('descricao', 'Dívida sem nome')} - {formatar_moeda(d.get('valor_atual', d.get('valor_restante', 0)))}" for d in dividas]
        opcoes_dict = {opcao: i for i, opcao in enumerate(opcoes_exclusao)}
        
        divida_selecionada = st.selectbox(
            "Selecione uma dívida para excluir:",
            options=list(opcoes_dict.keys())
        )
        
        if st.button("🗑️ Excluir Dívida", type="primary"):
            indice = opcoes_dict[divida_selecionada]
            divida_para_excluir = dividas[indice]
            
            # Usar função delete_divida se existir, senão fazer manualmente
            try:
                if delete_divida(divida_para_excluir["id"]):
                    st.success(f"Dívida '{divida_para_excluir.get('descricao', 'Dívida sem nome')}' excluída com sucesso!")
                    st.rerun()
            except:
                # Fallback manual
                for i, divida in enumerate(dividas):
                    if all(divida.get(k) == divida_para_excluir.get(k) for k in divida_para_excluir.keys()):
                        dividas.pop(i)
                        save_dividas(dividas)
                        st.success(f"Dívida '{divida_para_excluir.get('descricao', 'Dívida sem nome')}' excluída com sucesso!")
                        st.rerun()
                        break 