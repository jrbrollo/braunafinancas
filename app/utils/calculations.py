from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta


def compound_interest(principal: float, rate: float, time: float, 
                     monthly_contribution: float = 0) -> float:
    """
    Calcula juros compostos com contribuições mensais.
    
    Args:
        principal (float): Valor inicial
        rate (float): Taxa de juros anual (decimal)
        time (float): Tempo em anos
        monthly_contribution (float): Contribuição mensal
        
    Returns:
        float: Valor futuro
    """
    monthly_rate = rate / 12
    n_months = int(time * 12)
    
    # Valor futuro do principal inicial
    future_principal = principal * (1 + monthly_rate) ** n_months
    
    # Valor futuro das contribuições mensais
    if monthly_contribution > 0 and abs(monthly_rate) > 0.0001:
        future_contributions = monthly_contribution * ((1 + monthly_rate) ** n_months - 1) / monthly_rate
    else:
        future_contributions = monthly_contribution * n_months
    
    return future_principal + future_contributions


def calculate_monthly_payment(present_value: float, future_value: float, 
                             rate: float, time: float) -> float:
    """
    Calcula o pagamento mensal necessário para atingir um valor futuro.
    
    Args:
        present_value (float): Valor presente
        future_value (float): Valor futuro desejado
        rate (float): Taxa de juros anual (decimal)
        time (float): Tempo em anos
        
    Returns:
        float: Pagamento mensal necessário
    """
    monthly_rate = rate / 12
    n_months = int(time * 12)
    
    # Calcular valor futuro do montante atual
    future_present_value = present_value * ((1 + monthly_rate) ** n_months)
    
    # Valor adicional necessário
    additional_needed = future_value - future_present_value
    
    if additional_needed <= 0:
        return 0.0
    
    # Se a taxa for próxima de zero, usar cálculo simplificado
    if abs(monthly_rate) < 0.0001:
        return additional_needed / n_months
    
    # Fórmula PMT para calcular o pagamento mensal necessário
    # PMT = FV * r / ((1 + r)^n - 1)
    pmt = additional_needed * monthly_rate / ((1 + monthly_rate) ** n_months - 1)
    
    return max(0.0, pmt)


def calculate_time_to_goal(present_value: float, future_value: float,
                          rate: float, monthly_contribution: float) -> float:
    """
    Calcula o tempo necessário para atingir um objetivo financeiro.
    
    Args:
        present_value (float): Valor presente
        future_value (float): Valor futuro desejado
        rate (float): Taxa de juros anual (decimal)
        monthly_contribution (float): Contribuição mensal
        
    Returns:
        float: Tempo em anos
    """
    if present_value >= future_value:
        return 0.0
    
    if monthly_contribution <= 0 and rate <= 0:
        return float('inf')
    
    monthly_rate = rate / 12
    
    # Se a taxa for próxima de zero, usar cálculo simplificado
    if abs(monthly_rate) < 0.0001:
        if monthly_contribution > 0:
            return (future_value - present_value) / monthly_contribution / 12
        else:
            return float('inf')
    
    # Fórmula para calcular o tempo (n)
    # FV = PV*(1+r)^n + PMT*((1+r)^n - 1)/r
    # Resolver para n: n = log((FV*r + PMT)/(PV*r + PMT)) / log(1+r)
    if monthly_contribution > 0:
        numerator = future_value * monthly_rate + monthly_contribution
        denominator = present_value * monthly_rate + monthly_contribution
        
        if denominator <= 0:
            return float('inf')
        
        n_months = np.log(numerator / denominator) / np.log(1 + monthly_rate)
        return max(0.0, n_months / 12)
    else:
        # Sem contribuição mensal, apenas juros compostos no valor atual
        if present_value <= 0 or rate <= 0:
            return float('inf')
        
        n_months = np.log(future_value / present_value) / np.log(1 + monthly_rate)
        return max(0.0, n_months / 12)


def allocate_resources(available_amount: float, goals: List[Dict]) -> Dict[str, float]:
    """
    Distribui recursos disponíveis entre objetivos financeiros.
    
    Args:
        available_amount (float): Valor mensal disponível para investimento
        goals (List[Dict]): Lista de objetivos com atributos:
                           - id: Identificador único
                           - name: Nome do objetivo
                           - target_amount: Valor alvo
                           - current_amount: Valor atual
                           - deadline: Data limite
                           - priority: Prioridade (1=alta, 2=média, 3=baixa)
                           - expected_return_rate: Taxa de retorno esperada anual
    
    Returns:
        Dict[str, float]: Alocação recomendada para cada objetivo
    """
    allocations = {}
    remaining = available_amount
    
    # Calcular pontuação para cada objetivo
    scored_goals = []
    for goal in goals:
        if goal.get('current_amount', 0) >= goal.get('target_amount', 0):
            continue  # Pular objetivos já alcançados
        
        deadline = goal.get('deadline')
        if not isinstance(deadline, datetime):
            continue
            
        # Calcular meses restantes
        now = datetime.now()
        if deadline <= now:
            months_left = 0
        else:
            months_left = max(1, (deadline - now).days / 30)
        
        # Calcular quanto ainda falta
        amount_needed = goal.get('target_amount', 0) - goal.get('current_amount', 0)
        
        # Calcular valor mensal necessário considerando retorno esperado
        rate = goal.get('expected_return_rate', 0.05)  # Taxa padrão de 5% a.a.
        
        monthly_needed = calculate_monthly_payment(
            goal.get('current_amount', 0),
            goal.get('target_amount', 0),
            rate,
            months_left / 12
        )
        
        # Fator de prioridade (maior prioridade = maior pontuação)
        priority = goal.get('priority', 2)
        priority_factor = 4 - priority  # Converte 1,2,3 para 3,2,1
        
        # Fator de urgência (menos tempo = mais urgente)
        urgency_factor = 1 / max(1, months_left)
        
        # Pontuação combinada
        score = priority_factor * urgency_factor * amount_needed / 10000  # Normalização
        
        scored_goals.append((goal.get('id'), goal.get('name', ''), monthly_needed, score))
    
    # Ordenar por pontuação (decrescente)
    scored_goals.sort(key=lambda x: x[3], reverse=True)
    
    # Primeira passagem: alocar o mínimo necessário para objetivos de alta prioridade
    for goal_id, goal_name, needed, _ in scored_goals:
        if remaining <= 0:
            break
            
        # Alocar ou o que for necessário ou o que restar, o que for menor
        allocation = min(needed, remaining)
        allocations[goal_id] = allocation
        remaining -= allocation
    
    # Segunda passagem: distribuir o restante proporcionalmente às pontuações
    if remaining > 0 and scored_goals:
        total_score = sum(score for _, _, _, score in scored_goals)
        
        if total_score > 0:
            for goal_id, _, _, score in scored_goals:
                extra_allocation = (score / total_score) * remaining
                if goal_id in allocations:
                    allocations[goal_id] += extra_allocation
                else:
                    allocations[goal_id] = extra_allocation
    
    return allocations


def inflation_adjust(value: float, inflation_rate: float, years: float) -> float:
    """
    Ajusta um valor futuro considerando a inflação.
    
    Args:
        value (float): Valor nominal futuro
        inflation_rate (float): Taxa de inflação anual (decimal)
        years (float): Número de anos
        
    Returns:
        float: Valor futuro ajustado pela inflação (poder de compra atual)
    """
    return value / ((1 + inflation_rate) ** years)


def real_return_rate(nominal_rate: float, inflation_rate: float) -> float:
    """
    Calcula a taxa real de retorno considerando a inflação.
    
    Args:
        nominal_rate (float): Taxa nominal de retorno anual (decimal)
        inflation_rate (float): Taxa de inflação anual (decimal)
        
    Returns:
        float: Taxa real de retorno anual
    """
    return (1 + nominal_rate) / (1 + inflation_rate) - 1 