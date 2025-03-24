import os
import json
import pandas as pd
import csv
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Constantes para diretórios e arquivos
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USER_FILE = os.path.join(DATA_DIR, "user.json")
GOALS_FILE = os.path.join(DATA_DIR, "goals.csv")
INVESTMENTS_FILE = os.path.join(DATA_DIR, "investments.csv")


def ensure_data_dir():
    """Garante que o diretório de dados existe."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def save_user_data(user_data: Dict[str, Any]) -> bool:
    """
    Salva os dados do usuário em um arquivo JSON.
    
    Args:
        user_data (Dict[str, Any]): Dados do usuário
        
    Returns:
        bool: True se o salvamento foi bem-sucedido
    """
    ensure_data_dir()
    try:
        # Formatar datas para ISO antes de salvar
        if "created_at" in user_data and isinstance(user_data["created_at"], datetime):
            user_data["created_at"] = user_data["created_at"].isoformat()
        if "last_updated" in user_data and isinstance(user_data["last_updated"], datetime):
            user_data["last_updated"] = user_data["last_updated"].isoformat()
        
        with open(USER_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados do usuário: {e}")
        return False


def load_user_data() -> Dict[str, Any]:
    """
    Carrega os dados do usuário a partir do arquivo JSON.
    
    Returns:
        Dict[str, Any]: Dados do usuário ou um dicionário vazio se o arquivo não existir
    """
    ensure_data_dir()
    try:
        if os.path.exists(USER_FILE):
            with open(USER_FILE, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
                
                # Converter strings ISO para objetos datetime
                if "created_at" in user_data and isinstance(user_data["created_at"], str):
                    user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                if "last_updated" in user_data and isinstance(user_data["last_updated"], str):
                    user_data["last_updated"] = datetime.fromisoformat(user_data["last_updated"])
                
                return user_data
        return {}
    except Exception as e:
        print(f"Erro ao carregar dados do usuário: {e}")
        return {}


def save_goals(goals: List[Dict[str, Any]]) -> bool:
    """
    Salva a lista de objetivos em um arquivo CSV.
    
    Args:
        goals (List[Dict[str, Any]]): Lista de objetivos
        
    Returns:
        bool: True se o salvamento foi bem-sucedido
    """
    ensure_data_dir()
    try:
        # Definir campos do CSV
        fields = [
            'id', 'name', 'description', 'target_amount', 'current_amount',
            'start_date', 'deadline', 'priority', 'expected_return_rate', 'category'
        ]
        
        # Converter para DataFrame para facilitar o salvamento
        goals_data = []
        for goal in goals:
            goal_dict = {field: goal.get(field, None) for field in fields}
            
            # Formatação de datas para ISO
            if "start_date" in goal_dict and isinstance(goal_dict["start_date"], datetime):
                goal_dict["start_date"] = goal_dict["start_date"].isoformat()
            if "deadline" in goal_dict and isinstance(goal_dict["deadline"], datetime):
                goal_dict["deadline"] = goal_dict["deadline"].isoformat()
            
            goals_data.append(goal_dict)
        
        # Salvar em CSV
        df = pd.DataFrame(goals_data)
        df.to_csv(GOALS_FILE, index=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar objetivos: {e}")
        return False


def load_goals() -> List[Dict[str, Any]]:
    """
    Carrega a lista de objetivos a partir do arquivo CSV.
    
    Returns:
        List[Dict[str, Any]]: Lista de objetivos ou uma lista vazia se o arquivo não existir
    """
    ensure_data_dir()
    try:
        if os.path.exists(GOALS_FILE):
            df = pd.read_csv(GOALS_FILE)
            
            # Converter para lista de dicionários
            goals = df.to_dict('records')
            
            # Converter strings ISO para objetos datetime
            for goal in goals:
                if "start_date" in goal and isinstance(goal["start_date"], str):
                    goal["start_date"] = datetime.fromisoformat(goal["start_date"])
                if "deadline" in goal and isinstance(goal["deadline"], str):
                    goal["deadline"] = datetime.fromisoformat(goal["deadline"])
            
            return goals
        return []
    except Exception as e:
        print(f"Erro ao carregar objetivos: {e}")
        return []


def save_investments(investments: List[Dict[str, Any]]) -> bool:
    """
    Salva a lista de investimentos em um arquivo CSV.
    
    Args:
        investments (List[Dict[str, Any]]): Lista de investimentos
        
    Returns:
        bool: True se o salvamento foi bem-sucedido
    """
    ensure_data_dir()
    try:
        # Definir campos do CSV
        fields = [
            'id', 'name', 'description', 'type', 'amount', 'expected_return_rate',
            'risk_level', 'liquidity', 'start_date', 'goal_id'
        ]
        
        # Converter para DataFrame para facilitar o salvamento
        investments_data = []
        for investment in investments:
            inv_dict = {field: investment.get(field, None) for field in fields}
            
            # Formatação de datas para ISO
            if "start_date" in inv_dict and isinstance(inv_dict["start_date"], datetime):
                inv_dict["start_date"] = inv_dict["start_date"].isoformat()
            
            investments_data.append(inv_dict)
        
        # Salvar em CSV
        df = pd.DataFrame(investments_data)
        df.to_csv(INVESTMENTS_FILE, index=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar investimentos: {e}")
        return False


def load_investments() -> List[Dict[str, Any]]:
    """
    Carrega a lista de investimentos a partir do arquivo CSV.
    
    Returns:
        List[Dict[str, Any]]: Lista de investimentos ou uma lista vazia se o arquivo não existir
    """
    ensure_data_dir()
    try:
        if os.path.exists(INVESTMENTS_FILE):
            df = pd.read_csv(INVESTMENTS_FILE)
            
            # Converter para lista de dicionários
            investments = df.to_dict('records')
            
            # Converter strings ISO para objetos datetime
            for investment in investments:
                if "start_date" in investment and isinstance(investment["start_date"], str):
                    investment["start_date"] = datetime.fromisoformat(investment["start_date"])
            
            return investments
        return []
    except Exception as e:
        print(f"Erro ao carregar investimentos: {e}")
        return []


def get_next_id(items: List[Dict[str, Any]]) -> int:
    """
    Gera o próximo ID disponível para uma lista de itens.
    
    Args:
        items (List[Dict[str, Any]]): Lista de itens
        
    Returns:
        int: Próximo ID disponível
    """
    if not items:
        return 1
    
    max_id = 0
    for item in items:
        if 'id' in item and isinstance(item['id'], (int, float)) and item['id'] > max_id:
            max_id = item['id']
    
    return max_id + 1


def export_data_to_csv(data: Union[List[Dict[str, Any]], pd.DataFrame], 
                      filename: str) -> bool:
    """
    Exporta dados para um arquivo CSV.
    
    Args:
        data (Union[List[Dict[str, Any]], pd.DataFrame]): Dados a serem exportados
        filename (str): Nome do arquivo (caminho completo)
        
    Returns:
        bool: True se a exportação foi bem-sucedida
    """
    try:
        # Verificar se o diretório existe
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Converter para DataFrame se for uma lista de dicionários
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data
        
        # Salvar em CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Erro ao exportar dados para CSV: {e}")
        return False


def import_data_from_csv(filename: str) -> Optional[pd.DataFrame]:
    """
    Importa dados de um arquivo CSV.
    
    Args:
        filename (str): Nome do arquivo (caminho completo)
        
    Returns:
        Optional[pd.DataFrame]: DataFrame com os dados ou None se a importação falhar
    """
    try:
        if os.path.exists(filename):
            return pd.read_csv(filename, encoding='utf-8')
        return None
    except Exception as e:
        print(f"Erro ao importar dados do CSV: {e}")
        return None 