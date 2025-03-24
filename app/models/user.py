from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Income(BaseModel):
    """Modelo para receitas do usuário."""
    name: str
    amount: float
    frequency: str = "mensal"  # mensal, quinzenal, semanal, etc.


class Expense(BaseModel):
    """Modelo para despesas do usuário."""
    name: str
    amount: float
    category: str
    is_fixed: bool = True
    frequency: str = "mensal"  # mensal, quinzenal, semanal, etc.


class User(BaseModel):
    """Modelo para o perfil financeiro do usuário."""
    name: str
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    incomes: List[Income] = []
    expenses: List[Expense] = []
    risk_profile: str = "moderado"  # conservador, moderado, agressivo
    
    def total_monthly_income(self) -> float:
        """Calcula a renda mensal total do usuário."""
        total = 0.0
        for income in self.incomes:
            if income.frequency == "mensal":
                total += income.amount
            elif income.frequency == "quinzenal":
                total += income.amount * 2
            elif income.frequency == "semanal":
                total += income.amount * 4.33  # Aproximação de semanas em um mês
            elif income.frequency == "anual":
                total += income.amount / 12
        return total
    
    def total_monthly_expenses(self) -> float:
        """Calcula as despesas mensais totais do usuário."""
        total = 0.0
        for expense in self.expenses:
            if expense.frequency == "mensal":
                total += expense.amount
            elif expense.frequency == "quinzenal":
                total += expense.amount * 2
            elif expense.frequency == "semanal":
                total += expense.amount * 4.33  # Aproximação de semanas em um mês
            elif expense.frequency == "anual":
                total += expense.amount / 12
        return total
    
    def available_for_investment(self) -> float:
        """Calcula o valor disponível para investimentos."""
        return max(0, self.total_monthly_income() - self.total_monthly_expenses())
    
    def expenses_by_category(self) -> Dict[str, float]:
        """Retorna um dicionário com o total de despesas por categoria."""
        result = {}
        for expense in self.expenses:
            if expense.category in result:
                result[expense.category] += expense.amount
            else:
                result[expense.category] = expense.amount
        return result 