import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Adicionar diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.goals import Goal
from utils.data_processor import load_goals, save_goals, get_next_id
from utils.calculations import calculate_monthly_payment, calculate_time_to_goal


def render_goals_page():
    """Renderiza a página de gestão de objetivos financeiros."""
    st.title("Objetivos Financeiros")
    
    # Carregar objetivos existentes
    goals_data = load_goals()
    
    # Tabs para diferentes seções
    tab1, tab2, tab3 = st.tabs(["Meus Objetivos", "Adicionar Objetivo", "Simulador"])
    
    # Tab 1: Lista de objetivos
    with tab1:
        render_goals_list(goals_data)
    
    # Tab 2: Adicionar novo objetivo
    with tab2:
        render_add_goal_form(goals_data)
    
    # Tab 3: Simulador de objetivos
    with tab3:
        render_goal_simulator()


def render_goals_list(goals_data):
    """Renderiza a lista de objetivos existentes."""
    if not goals_data:
        st.info("Você ainda não possui objetivos financeiros cadastrados. Use a aba 'Adicionar Objetivo' para criar seu primeiro objetivo.")
        return
    
    st.header("Meus Objetivos")
    
    # Convertemos para objetos Goal para usar os métodos
    goals = [Goal(**goal) for goal in goals_data]
    
    # Ordenar por prioridade e depois por prazo
    goals.sort(key=lambda x: (x.priority, x.deadline))
    
    # Mostrar cada objetivo com detalhes
    for i, goal in enumerate(goals):
        with st.expander(f"{goal.name} - {goal.progress_percentage:.1f}% concluído"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Categoria:** {goal.category}")
                st.markdown(f"**Valor Atual:** R$ {goal.current_amount:.2f}".replace('.', ','))
                st.markdown(f"**Valor Alvo:** R$ {goal.target_amount:.2f}".replace('.', ','))
                st.markdown(f"**Prioridade:** {'Alta' if goal.priority == 1 else 'Média' if goal.priority == 2 else 'Baixa'}")
            
            with col2:
                st.markdown(f"**Data de Início:** {goal.start_date.strftime('%d/%m/%Y')}")
                st.markdown(f"**Prazo Final:** {goal.deadline.strftime('%d/%m/%Y')}")
                st.markdown(f"**Meses Restantes:** {goal.months_remaining}")
                st.markdown(f"**Taxa de Retorno Esperada:** {goal.expected_return_rate*100:.2f}% a.a.")
            
            # Barra de progresso
            st.markdown(f"**Progresso: {goal.progress_percentage:.1f}%**")
            st.progress(goal.progress_percentage / 100)
            
            # Contribuição mensal necessária
            monthly_contribution = goal.monthly_contribution_needed()
            st.markdown(f"**Contribuição mensal necessária:** R$ {monthly_contribution:.2f}".replace('.', ','))
            
            # Botões de ação
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Editar", key=f"edit_{goal.id}"):
                    st.session_state.edit_goal_id = goal.id
                    st.session_state.show_edit_form = True
            
            with col2:
                if st.button("Atualizar Valor", key=f"update_{goal.id}"):
                    st.session_state.update_goal_id = goal.id
                    st.session_state.show_update_form = True
            
            with col3:
                if st.button("Excluir", key=f"delete_{goal.id}"):
                    st.session_state.delete_goal_id = goal.id
                    st.session_state.confirm_delete = True
        
        # Pequeno espaço entre os expanders
        st.write("")
    
    # Formulário de edição
    if 'show_edit_form' in st.session_state and st.session_state.show_edit_form:
        render_edit_goal_form(goals_data, st.session_state.edit_goal_id)
    
    # Formulário de atualização de valor
    if 'show_update_form' in st.session_state and st.session_state.show_update_form:
        render_update_goal_value_form(goals_data, st.session_state.update_goal_id)
    
    # Confirmação de exclusão
    if 'confirm_delete' in st.session_state and st.session_state.confirm_delete:
        confirm_delete_goal(goals_data, st.session_state.delete_goal_id)


def render_add_goal_form(goals_data):
    """Renderiza o formulário para adicionar um novo objetivo."""
    st.header("Adicionar Novo Objetivo")
    
    with st.form("add_goal_form"):
        name = st.text_input("Nome do Objetivo")
        description = st.text_area("Descrição (opcional)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_amount = st.number_input("Valor Alvo (R$)", min_value=0.01, step=100.0)
            current_amount = st.number_input("Valor Atual (R$)", min_value=0.0, step=100.0)
            
            # Categoria do objetivo
            category_options = [
                "reserva_emergencial", "aposentadoria", "imóvel", 
                "veículo", "educação", "viagem", "outros"
            ]
            category = st.selectbox(
                "Categoria",
                options=category_options,
                format_func=lambda x: x.replace("_", " ").title()
            )
        
        with col2:
            # Data de prazo
            years_to_deadline = st.slider("Anos para atingir", 1, 30, 5)
            deadline = datetime.now() + timedelta(days=365 * years_to_deadline)
            st.write(f"Data limite: {deadline.strftime('%d/%m/%Y')}")
            
            # Prioridade
            priority_options = {"Alta": 1, "Média": 2, "Baixa": 3}
            priority = st.selectbox(
                "Prioridade",
                options=list(priority_options.keys()),
                index=1
            )
            
            # Taxa de retorno esperada
            expected_return_rate = st.slider(
                "Taxa de Retorno Esperada (% a.a.)",
                min_value=0.0,
                max_value=15.0,
                value=5.0,
                step=0.5
            ) / 100
        
        submitted = st.form_submit_button("Adicionar Objetivo")
        
        if submitted:
            if not name:
                st.error("O nome do objetivo é obrigatório!")
                return
            
            if target_amount <= 0:
                st.error("O valor alvo deve ser maior que zero!")
                return
            
            # Criar novo objetivo
            new_goal = {
                "id": get_next_id(goals_data),
                "name": name,
                "description": description,
                "target_amount": target_amount,
                "current_amount": current_amount,
                "start_date": datetime.now(),
                "deadline": deadline,
                "priority": priority_options[priority],
                "expected_return_rate": expected_return_rate,
                "category": category
            }
            
            # Adicionar à lista e salvar
            goals_data.append(new_goal)
            if save_goals(goals_data):
                st.success(f"Objetivo '{name}' adicionado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Erro ao salvar o objetivo. Tente novamente.")


def render_edit_goal_form(goals_data, goal_id):
    """Renderiza o formulário para editar um objetivo existente."""
    st.subheader("Editar Objetivo")
    
    # Encontrar o objetivo pelo ID
    goal_to_edit = next((g for g in goals_data if g["id"] == goal_id), None)
    
    if not goal_to_edit:
        st.error("Objetivo não encontrado!")
        return
    
    with st.form("edit_goal_form"):
        name = st.text_input("Nome do Objetivo", value=goal_to_edit["name"])
        description = st.text_area("Descrição (opcional)", value=goal_to_edit.get("description", ""))
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_amount = st.number_input(
                "Valor Alvo (R$)", 
                min_value=0.01, 
                value=float(goal_to_edit["target_amount"]), 
                step=100.0
            )
            
            current_amount = st.number_input(
                "Valor Atual (R$)", 
                min_value=0.0, 
                value=float(goal_to_edit["current_amount"]), 
                step=100.0
            )
            
            # Categoria do objetivo
            category_options = [
                "reserva_emergencial", "aposentadoria", "imóvel", 
                "veículo", "educação", "viagem", "outros"
            ]
            
            category_index = 0
            for i, option in enumerate(category_options):
                if option == goal_to_edit.get("category", "outros"):
                    category_index = i
                    break
            
            category = st.selectbox(
                "Categoria",
                options=category_options,
                index=category_index,
                format_func=lambda x: x.replace("_", " ").title()
            )
        
        with col2:
            # Data de prazo
            deadline = goal_to_edit["deadline"]
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline)
            
            years_to_deadline = max(1, (deadline - datetime.now()).days // 365)
            new_years = st.slider("Anos para atingir", 1, 30, years_to_deadline)
            new_deadline = datetime.now() + timedelta(days=365 * new_years)
            st.write(f"Nova data limite: {new_deadline.strftime('%d/%m/%Y')}")
            
            # Prioridade
            priority_options = {"Alta": 1, "Média": 2, "Baixa": 3}
            priority_names = list(priority_options.keys())
            current_priority = goal_to_edit.get("priority", 2)
            
            priority_index = 1  # Default to "Média"
            for i, (name, value) in enumerate(priority_options.items()):
                if value == current_priority:
                    priority_index = i
                    break
            
            priority = st.selectbox(
                "Prioridade",
                options=priority_names,
                index=priority_index
            )
            
            # Taxa de retorno esperada
            expected_return_rate = st.slider(
                "Taxa de Retorno Esperada (% a.a.)",
                min_value=0.0,
                max_value=15.0,
                value=float(goal_to_edit.get("expected_return_rate", 0.05) * 100),
                step=0.5
            ) / 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("Salvar Alterações")
        
        with col2:
            canceled = st.form_submit_button("Cancelar")
        
        if submitted:
            if not name:
                st.error("O nome do objetivo é obrigatório!")
                return
            
            if target_amount <= 0:
                st.error("O valor alvo deve ser maior que zero!")
                return
            
            # Atualizar o objetivo
            goal_to_edit.update({
                "name": name,
                "description": description,
                "target_amount": target_amount,
                "current_amount": current_amount,
                "deadline": new_deadline,
                "priority": priority_options[priority],
                "expected_return_rate": expected_return_rate,
                "category": category
            })
            
            # Salvar a lista atualizada
            if save_goals(goals_data):
                st.success(f"Objetivo '{name}' atualizado com sucesso!")
                st.session_state.show_edit_form = False
                st.experimental_rerun()
            else:
                st.error("Erro ao atualizar o objetivo. Tente novamente.")
        
        if canceled:
            st.session_state.show_edit_form = False
            st.experimental_rerun()


def render_update_goal_value_form(goals_data, goal_id):
    """Renderiza o formulário para atualizar o valor atual de um objetivo."""
    st.subheader("Atualizar Valor do Objetivo")
    
    # Encontrar o objetivo pelo ID
    goal_to_update = next((g for g in goals_data if g["id"] == goal_id), None)
    
    if not goal_to_update:
        st.error("Objetivo não encontrado!")
        return
    
    with st.form("update_value_form"):
        st.write(f"Objetivo: **{goal_to_update['name']}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"Valor Atual: R$ {float(goal_to_update['current_amount']):.2f}".replace('.', ','))
            st.write(f"Valor Alvo: R$ {float(goal_to_update['target_amount']):.2f}".replace('.', ','))
        
        with col2:
            update_type = st.radio(
                "Tipo de Atualização",
                options=["Novo Valor Total", "Adicionar Valor"],
                index=1
            )
        
        if update_type == "Novo Valor Total":
            new_value = st.number_input(
                "Novo Valor Total (R$)", 
                min_value=0.0, 
                value=float(goal_to_update["current_amount"]),
                step=100.0
            )
            value_to_add = new_value - float(goal_to_update["current_amount"])
        else:  # "Adicionar Valor"
            value_to_add = st.number_input(
                "Valor a Adicionar (R$)", 
                min_value=0.0,
                step=100.0
            )
            new_value = float(goal_to_update["current_amount"]) + value_to_add
        
        st.write(f"Novo Valor Total: R$ {new_value:.2f}".replace('.', ','))
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("Atualizar Valor")
        
        with col2:
            canceled = st.form_submit_button("Cancelar")
        
        if submitted:
            # Atualizar o valor
            goal_to_update["current_amount"] = new_value
            
            # Salvar a lista atualizada
            if save_goals(goals_data):
                st.success(f"Valor do objetivo '{goal_to_update['name']}' atualizado com sucesso!")
                st.session_state.show_update_form = False
                st.experimental_rerun()
            else:
                st.error("Erro ao atualizar o valor. Tente novamente.")
        
        if canceled:
            st.session_state.show_update_form = False
            st.experimental_rerun()


def confirm_delete_goal(goals_data, goal_id):
    """Exibe a confirmação de exclusão de um objetivo."""
    st.subheader("Excluir Objetivo")
    
    # Encontrar o objetivo pelo ID
    goal_to_delete = next((g for g in goals_data if g["id"] == goal_id), None)
    
    if not goal_to_delete:
        st.error("Objetivo não encontrado!")
        st.session_state.confirm_delete = False
        return
    
    st.warning(f"Você está prestes a excluir o objetivo '{goal_to_delete['name']}'. Esta ação não pode ser desfeita.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Confirmar Exclusão"):
            # Remover o objetivo da lista
            goals_data.remove(goal_to_delete)
            
            # Salvar a lista atualizada
            if save_goals(goals_data):
                st.success(f"Objetivo '{goal_to_delete['name']}' excluído com sucesso!")
                st.session_state.confirm_delete = False
                st.experimental_rerun()
            else:
                st.error("Erro ao excluir o objetivo. Tente novamente.")
    
    with col2:
        if st.button("Cancelar"):
            st.session_state.confirm_delete = False
            st.experimental_rerun()


def render_goal_simulator():
    """Renderiza o simulador de objetivos financeiros."""
    st.header("Simulador de Objetivos")
    st.write("Use este simulador para calcular quanto você precisa investir mensalmente para atingir um objetivo financeiro.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_amount = st.number_input("Valor Desejado (R$)", min_value=1000.0, value=50000.0, step=1000.0)
        current_savings = st.number_input("Quanto já tem guardado? (R$)", min_value=0.0, value=0.0, step=1000.0)
    
    with col2:
        return_rate = st.slider("Taxa de Retorno Anual (%)", min_value=0.0, max_value=15.0, value=5.0, step=0.5) / 100
        years = st.slider("Prazo (anos)", min_value=1, max_value=30, value=5)
    
    # Calcular a contribuição mensal necessária
    monthly_payment = calculate_monthly_payment(
        present_value=current_savings,
        future_value=target_amount,
        rate=return_rate,
        time=years
    )
    
    # Exibir resultado
    st.subheader("Resultado")
    
    result_col1, result_col2 = st.columns(2)
    
    with result_col1:
        st.metric(
            label="Contribuição Mensal Necessária", 
            value=f"R$ {monthly_payment:.2f}".replace('.', ',')
        )
    
    # Calcular também o tempo necessário para diferentes valores de contribuição
    with result_col2:
        contribution_options = [
            monthly_payment * 0.5,
            monthly_payment * 0.75,
            monthly_payment,
            monthly_payment * 1.25,
            monthly_payment * 1.5
        ]
        
        selected_contribution = st.selectbox(
            "Ou simule com outra contribuição mensal:",
            options=contribution_options,
            format_func=lambda x: f"R$ {x:.2f}".replace('.', ','),
            index=2
        )
    
    # Se selecionou um valor diferente, calcular o tempo necessário
    if selected_contribution != monthly_payment:
        time_needed = calculate_time_to_goal(
            present_value=current_savings,
            future_value=target_amount,
            rate=return_rate,
            monthly_contribution=selected_contribution
        )
        
        years_needed = int(time_needed)
        months_needed = int((time_needed - years_needed) * 12)
        
        st.metric(
            label="Tempo Necessário", 
            value=f"{years_needed} anos e {months_needed} meses"
        )
    
    # Gráfico de projeção
    st.subheader("Projeção de Crescimento")
    
    # Gerar dados para o gráfico
    months = years * 12
    data = []
    
    balance = current_savings
    monthly_rate = return_rate / 12
    
    for month in range(months + 1):
        if month > 0:
            # Adicionar juros e contribuição
            interest = balance * monthly_rate
            balance += interest + monthly_payment
        
        # Adicionar ao dataframe
        data.append({
            "Mês": month,
            "Saldo": balance,
            "Contribuições Acumuladas": min(month * monthly_payment, target_amount - current_savings),
            "Rendimentos": balance - current_savings - (month * monthly_payment)
        })
    
    df = pd.DataFrame(data)
    
    # Criar gráfico de área empilhada
    fig = px.area(
        df, 
        x="Mês", 
        y=["Contribuições Acumuladas", "Rendimentos"],
        title=f"Projeção para {years} Anos com Contribuição Mensal de R$ {monthly_payment:.2f}".replace('.', ','),
        color_discrete_sequence=['#1f77b4', '#2ca02c']
    )
    
    # Adicionar linha para o objetivo
    fig.add_hline(
        y=target_amount, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Objetivo", 
        annotation_position="top right"
    )
    
    # Configurar eixo X para mostrar anos
    time_points = [i * 12 for i in range(years + 1)]
    time_labels = [f"Ano {i}" for i in range(years + 1)]
    
    fig.update_xaxes(
        tickvals=time_points,
        ticktext=time_labels
    )
    
    # Formatar eixo Y para mostrar valores em R$
    fig.update_layout(
        yaxis_title="Valor (R$)",
        xaxis_title="Tempo",
        legend_title="Componentes"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas finais
    final_balance = df.iloc[-1]["Saldo"]
    total_contributions = months * monthly_payment
    total_returns = final_balance - current_savings - total_contributions
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"Saldo Final em {years} Anos", 
            value=f"R$ {final_balance:.2f}".replace('.', ',')
        )
    
    with col2:
        st.metric(
            label="Total de Contribuições", 
            value=f"R$ {total_contributions:.2f}".replace('.', ',')
        )
    
    with col3:
        st.metric(
            label="Total de Rendimentos", 
            value=f"R$ {total_returns:.2f}".replace('.', ','),
            delta=f"{(total_returns / total_contributions * 100):.1f}% do investido"
        ) 