from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Investment(BaseModel):
    """Modelo para investimentos."""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    type: str  # "renda fixa", "renda variável", "imobiliário", etc.
    amount: float = 0.0
    expected_return_rate: float  # Taxa anual esperada
    risk_level: int = 2  # 1 (baixo), 2 (médio), 3 (alto)
    liquidity: str = "média"  # "alta", "média", "baixa"
    start_date: datetime = Field(default_factory=datetime.now)
    goal_id: Optional[int] = None  # ID do objetivo associado, se houver
    
    def calculate_growth(self, months: int) -> float:
        """
        Calcula o crescimento esperado do investimento após um período.
        
        Args:
            months (int): Número de meses para projeção
            
        Returns:
            float: Valor futuro estimado
        """
        # Converter taxa anual para mensal
        monthly_rate = self.expected_return_rate / 12
        
        # Calcular valor futuro com juros compostos
        future_value = self.amount * ((1 + monthly_rate) ** months)
        
        return future_value
    
    def calculate_with_contributions(self, months: int, monthly_contribution: float) -> float:
        """
        Calcula o crescimento esperado do investimento com contribuições mensais.
        
        Args:
            months (int): Número de meses para projeção
            monthly_contribution (float): Valor da contribuição mensal
            
        Returns:
            float: Valor futuro estimado
        """
        # Converter taxa anual para mensal
        monthly_rate = self.expected_return_rate / 12
        
        # Valor futuro do montante atual
        future_value_of_present = self.amount * ((1 + monthly_rate) ** months)
        
        # Valor futuro das contribuições mensais
        if abs(monthly_rate) < 0.0001:
            # Para taxas muito próximas de zero
            future_value_of_contributions = monthly_contribution * months
        else:
            future_value_of_contributions = monthly_contribution * ((1 + monthly_rate) ** months - 1) / monthly_rate
        
        return future_value_of_present + future_value_of_contributions
    
    def monthly_return(self) -> float:
        """
        Calcula o retorno mensal estimado do investimento atual.
        
        Returns:
            float: Retorno mensal estimado
        """
        monthly_rate = self.expected_return_rate / 12
        return self.amount * monthly_rate


class Portfolio(BaseModel):
    """Modelo para portfólio de investimentos."""
    investments: List[Investment] = []
    
    def total_value(self) -> float:
        """
        Calcula o valor total do portfólio.
        
        Returns:
            float: Soma dos valores de todos os investimentos
        """
        return sum(investment.amount for investment in self.investments)
    
    def expected_monthly_return(self) -> float:
        """
        Calcula o retorno mensal esperado do portfólio.
        
        Returns:
            float: Soma dos retornos mensais esperados de todos os investimentos
        """
        return sum(investment.monthly_return() for investment in self.investments)
    
    def risk_distribution(self) -> dict:
        """
        Calcula a distribuição de risco do portfólio.
        
        Returns:
            dict: Dicionário com percentuais por nível de risco
        """
        total = self.total_value()
        if total <= 0:
            return {"baixo": 0, "médio": 0, "alto": 0}
        
        risk_amounts = {1: 0, 2: 0, 3: 0}
        
        for investment in self.investments:
            risk_amounts[investment.risk_level] += investment.amount
        
        return {
            "baixo": (risk_amounts[1] / total) * 100 if total > 0 else 0,
            "médio": (risk_amounts[2] / total) * 100 if total > 0 else 0,
            "alto": (risk_amounts[3] / total) * 100 if total > 0 else 0
        }
    
    def type_distribution(self) -> dict:
        """
        Calcula a distribuição por tipo de investimento.
        
        Returns:
            dict: Dicionário com percentuais por tipo de investimento
        """
        total = self.total_value()
        if total <= 0:
            return {}
        
        type_amounts = {}
        
        for investment in self.investments:
            if investment.type in type_amounts:
                type_amounts[investment.type] += investment.amount
            else:
                type_amounts[investment.type] = investment.amount
        
        return {k: (v / total) * 100 for k, v in type_amounts.items()}
    
    def project_growth(self, months: int, monthly_contribution: float = 0) -> List[float]:
        """
        Projeta o crescimento do portfólio ao longo do tempo.
        
        Args:
            months (int): Número de meses para projeção
            monthly_contribution (float): Contribuição mensal total
            
        Returns:
            List[float]: Lista com valores projetados para cada mês
        """
        # Começar com o valor atual
        projection = [self.total_value()]
        
        # Distribuição da contribuição mensal proporcional ao valor de cada investimento
        total = self.total_value()
        
        for month in range(1, months + 1):
            monthly_value = projection[-1]
            
            # Contribuição mensal dividida proporcionalmente
            for investment in self.investments:
                if total > 0:
                    investment_weight = investment.amount / total
                    contribution_share = monthly_contribution * investment_weight
                    
                    # Crescimento no mês atual
                    monthly_rate = investment.expected_return_rate / 12
                    investment_growth = investment.amount * monthly_rate
                    
                    # Atualizar valor do investimento
                    investment.amount += investment_growth + contribution_share
                    
                    # Atualizar valor mensal
                    monthly_value += investment_growth + contribution_share
            
            projection.append(monthly_value)
            
        return projection 