from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class Goal(BaseModel):
    """Modelo para objetivos financeiros."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    target_amount: float
    current_amount: float = 0.0
    start_date: datetime = Field(default_factory=datetime.now)
    deadline: datetime
    priority: int = 2  # 1 (alta), 2 (média), 3 (baixa)
    expected_return_rate: float = 0.05  # Taxa anual esperada (padrão: 5%)
    category: str = "outros"  # reserva, aposentadoria, imóvel, educação, etc.
    
    @property
    def months_remaining(self) -> int:
        """Calcula a quantidade de meses restantes até o prazo final."""
        today = datetime.now()
        if today >= self.deadline:
            return 0
        
        delta = self.deadline - today
        return max(0, int(delta.days / 30))
    
    @property
    def progress_percentage(self) -> float:
        """Calcula a porcentagem de progresso para atingir o objetivo."""
        if self.target_amount <= 0:
            return 100.0
        
        percentage = (self.current_amount / self.target_amount) * 100
        return min(100.0, percentage)
    
    def monthly_contribution_needed(self) -> float:
        """
        Calcula a contribuição mensal necessária para atingir o objetivo
        considerando juros compostos mensais.
        """
        if self.months_remaining <= 0 or self.current_amount >= self.target_amount:
            return 0.0
        
        # Converter taxa anual para mensal
        monthly_rate = self.expected_return_rate / 12
        months = self.months_remaining
        
        # Valor futuro desejado
        future_value = self.target_amount
        
        # Valor presente já acumulado
        present_value = self.current_amount
        
        # Calcular valor futuro do montante atual
        future_value_of_present = present_value * ((1 + monthly_rate) ** months)
        
        # Valor ainda necessário
        remaining_amount = future_value - future_value_of_present
        
        if remaining_amount <= 0:
            return 0.0
        
        # Se a taxa for próxima de zero, usar cálculo simplificado
        if abs(monthly_rate) < 0.0001:
            return remaining_amount / months
        
        # Fórmula para calcular PMT (valor do pagamento periódico)
        # PMT = FV * r / ((1 + r)^n - 1)
        pmt = remaining_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)
        
        return max(0.0, pmt)
    
    def expected_final_amount(self, monthly_contribution: float) -> float:
        """
        Calcula o valor final esperado baseado na contribuição mensal
        e taxa de retorno esperada.
        """
        if self.months_remaining <= 0:
            return self.current_amount
        
        # Converter taxa anual para mensal
        monthly_rate = self.expected_return_rate / 12
        months = self.months_remaining
        
        # Valor futuro do montante atual
        future_value_of_present = self.current_amount * ((1 + monthly_rate) ** months)
        
        # Valor futuro das contribuições mensais
        if abs(monthly_rate) < 0.0001:
            future_value_of_contributions = monthly_contribution * months
        else:
            future_value_of_contributions = monthly_contribution * ((1 + monthly_rate) ** months - 1) / monthly_rate
        
        return future_value_of_present + future_value_of_contributions 