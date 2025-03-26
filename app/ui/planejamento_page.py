import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from app.data.data_handler import load_data, save_data, load_user_data, load_gastos
from app.ui.custom_style import load_custom_styles

def render_planejamento_page():
    """
    Renderiza a página de planejamento orçamentário
    """
    st.title("📊 Meu Planejamento")
    
    # Carregar dados
    dados_usuario = load_user_data()
    # Carregar gastos diretamente da função especializada
    gastos_lista = load_gastos()
    planejamento_lista = load_data("planejamento")
    
    # Debug para verificar os dados carregados
    if st.checkbox("Mostrar dados de debug", value=False):
        st.write("Dados do usuário:", dados_usuario)
        st.write("Lista de gastos:", gastos_lista[:5] if gastos_lista else "Sem gastos")
        st.write("Planejamento:", planejamento_lista)
        
        # Debug detalhado dos tipos dos gastos
        if gastos_lista:
            tipos_encontrados = [g.get('tipo', 'sem_tipo') for g in gastos_lista]
            contagem_tipos = {}
            for tipo in tipos_encontrados:
                if tipo in contagem_tipos:
                    contagem_tipos[tipo] += 1
                else:
                    contagem_tipos[tipo] = 1
            
            st.write("Tipos de gastos encontrados na lista:")
            for tipo, contagem in contagem_tipos.items():
                st.write(f"- '{tipo}': {contagem} gastos")
    
    # Converter listas para DataFrames
    gastos = pd.DataFrame(gastos_lista) if gastos_lista else pd.DataFrame()
    planejamento = pd.DataFrame(planejamento_lista) if planejamento_lista else pd.DataFrame()
    
    # Se não houver renda cadastrada, mostrar mensagem
    if not dados_usuario or "renda_mensal" not in dados_usuario:
        st.warning("⚠️ Para criar seu planejamento, primeiro cadastre sua renda mensal na página de configurações.")
        return
    
    # Obter renda mensal
    renda_mensal = dados_usuario["renda_mensal"]
    
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
        st.markdown("**Gastos Fixos (50% recomendado)**")
        gastos_fixos = st.number_input(
            "R$",
            min_value=0.0,
            max_value=renda_mensal,
            value=float(gastos_fixos_atual),
            format="%.2f",
            key="gastos_fixos"
        )
        
        st.markdown("**Gastos Variáveis (30% recomendado)**")
        gastos_variaveis = st.number_input(
            "R$",
            min_value=0.0,
            max_value=renda_mensal,
            value=float(gastos_variaveis_atual),
            format="%.2f",
            key="gastos_variaveis"
        )
        
        st.markdown("**Objetivos/Poupança (20% recomendado)**")
        objetivos = st.number_input(
            "R$",
            min_value=0.0,
            max_value=renda_mensal,
            value=float(objetivos_atual),
            format="%.2f",
            key="objetivos"
        )
        
        # Validar soma dos valores
        soma = gastos_fixos + gastos_variaveis + objetivos
        if abs(soma - renda_mensal) > 0.01:  # Permitir pequena diferença por arredondamento
            st.error(f"⚠️ A soma dos valores (R$ {soma:.2f}) deve ser igual à sua renda mensal (R$ {renda_mensal:.2f})")
        else:
            if st.button("💾 Salvar Planejamento", type="primary"):
                # Criar ou atualizar planejamento
                novo_planejamento = pd.DataFrame({
                    'data': [datetime.now().strftime("%Y-%m-%d")],
                    'renda_mensal': [renda_mensal],
                    'gastos_fixos': [gastos_fixos],
                    'gastos_variaveis': [gastos_variaveis],
                    'objetivos': [objetivos]
                })
                
                # Se já existe planejamento, concatenar com o novo
                if not planejamento.empty:
                    planejamento_atualizado = pd.concat([planejamento, novo_planejamento], ignore_index=True)
                else:
                    planejamento_atualizado = novo_planejamento
                
                save_data("planejamento", planejamento_atualizado.to_dict('records'))
                st.success("✅ Planejamento salvo com sucesso!")
                st.rerun()
    
    with col2:
        # Mostrar resumo do planejamento
        st.subheader("📈 Resumo do Planejamento")
        
        # Verificar se existem dados de planejamento
        if not planejamento.empty:
            # Converter string de data para objeto datetime nos gastos
            if not gastos.empty and 'data' in gastos.columns:
                if gastos['data'].dtype == 'object':
                    gastos['data'] = pd.to_datetime(gastos['data'])
            
            # Mostrar dados de debug sobre os gastos
            if st.checkbox("Mostrar detalhes dos gastos", value=False):
                st.write("Colunas nos gastos:", gastos.columns.tolist() if not gastos.empty else "DataFrame vazio")
                st.write("Primeiros gastos:", gastos.head() if not gastos.empty else "Sem dados")
                st.write("Tipos de dados:", gastos.dtypes if not gastos.empty else "Sem dados")
            
            # Calcular gastos reais do mês atual
            hoje = datetime.now()
            mes_atual = hoje.month
            ano_atual = hoje.year
            
            # Filtrar gastos do mês atual - com mais segurança
            if not gastos.empty and 'data' in gastos.columns:
                try:
                    # Tentar extrair mês e ano
                    if isinstance(gastos['data'].iloc[0], str):
                        # Converter string para datetime se necessário
                        st.info("Convertendo datas de string para datetime")
                        gastos['data'] = pd.to_datetime(gastos['data'])
                    
                    gastos_mes = gastos[
                        (gastos['data'].dt.month == mes_atual) & 
                        (gastos['data'].dt.year == ano_atual)
                    ]
                    
                    st.write(f"Gastos encontrados para o mês atual: {len(gastos_mes)}")
                except Exception as e:
                    st.error(f"Erro ao filtrar gastos: {e}")
                    st.write("Detalhes do erro:", gastos['data'].head() if not gastos.empty else "Sem dados")
                    gastos_mes = pd.DataFrame()
            else:
                st.warning("Nenhum gasto encontrado ou coluna 'data' não existe")
                if not gastos.empty:
                    st.write("Colunas disponíveis:", gastos.columns.tolist())
                gastos_mes = pd.DataFrame()
            
            # Se houver gastos para o mês atual
            if not gastos_mes.empty and 'tipo' in gastos_mes.columns and 'valor' in gastos_mes.columns:
                # Converter tipo para minúsculas para evitar problemas de case
                gastos_mes['tipo'] = gastos_mes['tipo'].str.lower() if hasattr(gastos_mes['tipo'], 'str') else gastos_mes['tipo'].astype(str).str.lower()
                
                # Gastos reais
                gastos_fixos_reais = gastos_mes[gastos_mes['tipo'] == 'fixo']['valor'].sum()
                gastos_variaveis_reais = gastos_mes[gastos_mes['tipo'] == 'variavel']['valor'].sum()
                
                st.write(f"Total de gastos fixos: R$ {gastos_fixos_reais:.2f}")
                st.write(f"Total de gastos variáveis: R$ {gastos_variaveis_reais:.2f}")
                
                # Adicionar debug para verificar os tipos de gastos encontrados
                if st.checkbox("Verificar tipos de gastos", value=False):
                    st.write("Tipos de gastos encontrados:", gastos_mes['tipo'].unique())
                    st.write("Número de gastos fixos:", len(gastos_mes[gastos_mes['tipo'] == 'fixo']))
                    st.write("Número de gastos variáveis:", len(gastos_mes[gastos_mes['tipo'] == 'variavel']))
            else:
                gastos_fixos_reais = 0
                gastos_variaveis_reais = 0
                if not gastos_mes.empty:
                    st.warning("Gastos encontrados mas sem colunas 'tipo' ou 'valor'")
                    st.write("Colunas disponíveis:", gastos_mes.columns.tolist())
            
            # Pegar último planejamento registrado
            ultimo_planejamento = planejamento.iloc[-1]
            gastos_fixos_plan = ultimo_planejamento['gastos_fixos']
            gastos_variaveis_plan = ultimo_planejamento['gastos_variaveis']
            objetivos_plan = ultimo_planejamento['objetivos']
            
            # Criar gráfico de pizza para planejamento
            fig_planejamento = go.Figure(data=[go.Pie(
                labels=['Gastos Fixos', 'Gastos Variáveis', 'Objetivos'],
                values=[gastos_fixos_plan, gastos_variaveis_plan, objetivos_plan],
                hole=.3,
                marker=dict(colors=['#2A5CAA', '#4CAF50', '#FFD700'])
            )])
            
            fig_planejamento.update_layout(
                title="Distribuição Planejada",
                showlegend=True,
                height=300
            )
            
            st.plotly_chart(fig_planejamento, use_container_width=True)
            
            # Mostrar progresso apenas se houver um planejamento definido
            st.subheader("🎯 Progresso do Mês")
            
            # Calcular percentuais
            if gastos_fixos_plan > 0:
                progresso_fixos = (gastos_fixos_reais / gastos_fixos_plan) * 100
            else:
                progresso_fixos = 0
                
            if gastos_variaveis_plan > 0:
                progresso_variaveis = (gastos_variaveis_reais / gastos_variaveis_plan) * 100
            else:
                progresso_variaveis = 0
            
            # Barras de progresso
            st.markdown("**Gastos Fixos**")
            st.progress(min(progresso_fixos / 100, 1.0))
            st.markdown(f"R$ {gastos_fixos_reais:.2f} / R$ {gastos_fixos_plan:.2f}")
            
            st.markdown("**Gastos Variáveis**")
            st.progress(min(progresso_variaveis / 100, 1.0))
            st.markdown(f"R$ {gastos_variaveis_reais:.2f} / R$ {gastos_variaveis_plan:.2f}")
            
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
        # Converter string de data para datetime
        if 'data' in planejamento.columns and planejamento['data'].dtype == 'object':
            planejamento['data'] = pd.to_datetime(planejamento['data'])
        
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
        
        if pd.api.types.is_datetime64_any_dtype(historico_display['data']):
            historico_display['data'] = historico_display['data'].dt.strftime('%d/%m/%Y')
        
        # Renomear colunas para exibição
        historico_display.columns = ['Data', 'Renda Mensal', 'Gastos Fixos', 'Gastos Variáveis', 'Objetivos']
        
        st.dataframe(historico_display, use_container_width=True)
    else:
        st.info("ℹ️ Nenhum histórico de planejamento disponível.") 