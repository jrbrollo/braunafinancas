import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from app.data.data_handler import load_data, save_data
from app.ui.custom_style import load_custom_styles

def render_planejamento_page():
    """
    Renderiza a página de planejamento orçamentário
    """
    st.title("📊 Meu Planejamento")
    
    # Carregar dados
    renda = load_data("renda")
    gastos = load_data("gastos")
    planejamento = load_data("planejamento")
    
    # Se não houver renda cadastrada, mostrar mensagem
    if renda.empty:
        st.warning("⚠️ Para criar seu planejamento, primeiro cadastre sua renda mensal na página de configurações.")
        return
    
    # Obter renda mensal
    renda_mensal = renda['valor'].sum()
    
    # Criar duas colunas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Formulário para cadastro/atualização do planejamento
        st.subheader("🎯 Definir Metas de Orçamento")
        
        # Se já existir planejamento, mostrar valores atuais
        if not planejamento.empty:
            st.info("💡 Você já tem um planejamento definido. Ajuste os valores conforme necessário.")
            gastos_fixos_atual = planejamento['gastos_fixos'].iloc[0]
            gastos_variaveis_atual = planejamento['gastos_variaveis'].iloc[0]
            objetivos_atual = planejamento['objetivos'].iloc[0]
        else:
            gastos_fixos_atual = renda_mensal * 0.5
            gastos_variaveis_atual = renda_mensal * 0.3
            objetivos_atual = renda_mensal * 0.2
        
        # Campos do formulário
        gastos_fixos = st.number_input(
            "Gastos Fixos (50% recomendado)",
            min_value=0.0,
            max_value=renda_mensal,
            value=float(gastos_fixos_atual),
            format="R$ %.2f"
        )
        
        gastos_variaveis = st.number_input(
            "Gastos Variáveis (30% recomendado)",
            min_value=0.0,
            max_value=renda_mensal,
            value=float(gastos_variaveis_atual),
            format="R$ %.2f"
        )
        
        objetivos = st.number_input(
            "Objetivos/Poupança (20% recomendado)",
            min_value=0.0,
            max_value=renda_mensal,
            value=float(objetivos_atual),
            format="R$ %.2f"
        )
        
        # Validar soma dos valores
        soma = gastos_fixos + gastos_variaveis + objetivos
        if abs(soma - renda_mensal) > 0.01:  # Permitir pequena diferença por arredondamento
            st.error(f"⚠️ A soma dos valores (R$ {soma:.2f}) deve ser igual à sua renda mensal (R$ {renda_mensal:.2f})")
        else:
            if st.button("💾 Salvar Planejamento", type="primary"):
                # Criar ou atualizar planejamento
                novo_planejamento = pd.DataFrame({
                    'data': [datetime.now()],
                    'renda_mensal': [renda_mensal],
                    'gastos_fixos': [gastos_fixos],
                    'gastos_variaveis': [gastos_variaveis],
                    'objetivos': [objetivos]
                })
                
                save_data("planejamento", novo_planejamento)
                st.success("✅ Planejamento salvo com sucesso!")
                st.rerun()
    
    with col2:
        # Mostrar resumo do planejamento
        st.subheader("📈 Resumo do Planejamento")
        
        if not planejamento.empty:
            # Calcular gastos reais do mês atual
            hoje = datetime.now()
            gastos_mes = gastos[gastos['data'].dt.month == hoje.month]
            
            gastos_fixos_reais = gastos_mes[gastos_mes['tipo'] == 'fixo']['valor'].sum()
            gastos_variaveis_reais = gastos_mes[gastos_mes['tipo'] == 'variavel']['valor'].sum()
            
            # Criar gráfico de pizza para planejamento
            fig_planejamento = go.Figure(data=[go.Pie(
                labels=['Gastos Fixos', 'Gastos Variáveis', 'Objetivos'],
                values=[gastos_fixos, gastos_variaveis, objetivos],
                hole=.3,
                marker=dict(colors=['#2A5CAA', '#4CAF50', '#FFD700'])
            )])
            
            fig_planejamento.update_layout(
                title="Distribuição Planejada",
                showlegend=True,
                height=300
            )
            
            st.plotly_chart(fig_planejamento, use_container_width=True)
            
            # Mostrar progresso
            st.subheader("🎯 Progresso do Mês")
            
            # Calcular percentuais
            progresso_fixos = (gastos_fixos_reais / gastos_fixos) * 100
            progresso_variaveis = (gastos_variaveis_reais / gastos_variaveis) * 100
            
            # Barras de progresso
            st.markdown("**Gastos Fixos**")
            st.progress(min(progresso_fixos, 100) / 100)
            st.markdown(f"R$ {gastos_fixos_reais:.2f} / R$ {gastos_fixos:.2f}")
            
            st.markdown("**Gastos Variáveis**")
            st.progress(min(progresso_variaveis, 100) / 100)
            st.markdown(f"R$ {gastos_variaveis_reais:.2f} / R$ {gastos_variaveis:.2f}")
            
            # Alertas
            if progresso_fixos > 100:
                st.error("⚠️ Você ultrapassou o limite planejado para gastos fixos!")
            if progresso_variaveis > 100:
                st.error("⚠️ Você ultrapassou o limite planejado para gastos variáveis!")
            
            # Sugestões
            if progresso_fixos > 80:
                st.warning("💡 Você está próximo do limite de gastos fixos. Considere revisar seus gastos.")
            if progresso_variaveis > 80:
                st.warning("💡 Você está próximo do limite de gastos variáveis. Considere revisar seus gastos.")
        else:
            st.info("ℹ️ Crie seu planejamento usando o formulário ao lado.")
    
    # Seção de histórico
    st.subheader("📊 Histórico de Planejamento")
    
    if not planejamento.empty:
        # Criar gráfico de linha para histórico
        fig_historico = go.Figure()
        
        fig_historico.add_trace(go.Scatter(
            x=planejamento['data'],
            y=planejamento['gastos_fixos'],
            name='Gastos Fixos',
            line=dict(color='#2A5CAA')
        ))
        
        fig_historico.add_trace(go.Scatter(
            x=planejamento['data'],
            y=planejamento['gastos_variaveis'],
            name='Gastos Variáveis',
            line=dict(color='#4CAF50')
        ))
        
        fig_historico.add_trace(go.Scatter(
            x=planejamento['data'],
            y=planejamento['objetivos'],
            name='Objetivos',
            line=dict(color='#FFD700')
        ))
        
        fig_historico.update_layout(
            title="Evolução do Planejamento",
            xaxis_title="Data",
            yaxis_title="Valor (R$)",
            height=400
        )
        
        st.plotly_chart(fig_historico, use_container_width=True)
        
        # Tabela com histórico
        st.markdown("**Histórico Detalhado**")
        historico_display = planejamento.copy()
        historico_display['data'] = historico_display['data'].dt.strftime('%d/%m/%Y')
        historico_display.columns = ['Data', 'Renda Mensal', 'Gastos Fixos', 'Gastos Variáveis', 'Objetivos']
        st.dataframe(historico_display, use_container_width=True)
    else:
        st.info("ℹ️ Nenhum histórico de planejamento disponível.") 