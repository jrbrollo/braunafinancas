"""
Módulo para mapear e normalizar dados entre o front-end e o banco de dados.
Garante compatibilidade entre diferentes nomes de campos e validação de dados.
"""
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Mapeamentos de campos para cada entidade
# Formato: {'nome_frontend': 'nome_banco_dados'}
MAPEAMENTO_OBJETIVOS = {
    'nome': 'titulo',
    'valor_total': 'valor_meta',
    'data_alvo': 'data_meta',
    'prioridade': 'nivel_prioridade'
}

MAPEAMENTO_DIVIDAS = {
    'valor_atual': 'valor_restante',
    'valor_inicial': 'valor_total',
    'parcelas': 'parcelas_total',
    'detalhes': 'notas',
}

MAPEAMENTO_INVESTIMENTOS = {
    'rendimento': 'rendimento_mensal',
    'taxa_retorno': 'rendimento_anual',
}

MAPEAMENTO_GASTOS = {
    'data_gasto': 'data',
}

MAPEAMENTO_SEGUROS = {
    'valor': 'valor_premio',
    'cobertura': 'valor_cobertura',
}

# Campos obrigatórios para cada entidade
CAMPOS_OBRIGATORIOS = {
    'objetivos': ['nome', 'valor_total'],
    'dividas': ['descricao', 'valor_total'],
    'investimentos': ['descricao', 'valor_inicial', 'categoria'],
    'gastos': ['descricao', 'valor'],
    'seguros': ['tipo', 'descricao', 'valor_premio'],
}

def gerar_id() -> str:
    """Gera um ID único."""
    return str(uuid.uuid4())

def formatar_data(data: Union[str, datetime, None]) -> Optional[str]:
    """
    Formata uma data para o formato YYYY-MM-DD ou retorna None se for inválida.
    """
    if not data:
        return None
    
    try:
        if isinstance(data, str):
            # Tenta converter a string em objeto datetime
            formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]
            for formato in formatos:
                try:
                    data_obj = datetime.strptime(data, formato)
                    return data_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return None
        elif isinstance(data, datetime):
            return data.strftime("%Y-%m-%d")
        else:
            return None
    except Exception:
        return None

def validar_campos_obrigatorios(dados: Dict[str, Any], entidade: str) -> bool:
    """
    Verifica se todos os campos obrigatórios estão presentes e válidos.
    
    Args:
        dados: Dicionário com os dados a validar
        entidade: Nome da entidade (objetivos, dividas, etc.)
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if entidade not in CAMPOS_OBRIGATORIOS:
        return True
        
    for campo in CAMPOS_OBRIGATORIOS[entidade]:
        if campo not in dados or dados[campo] is None:
            return False
            
        # Validação específica para valores numéricos
        if 'valor' in campo and not isinstance(dados[campo], (int, float)):
            try:
                float(dados[campo])
            except (ValueError, TypeError):
                return False
    
    return True

def normalizar_objetivo(objetivo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza os dados de um objetivo para garantir compatibilidade.
    
    Args:
        objetivo: Dados do objetivo a normalizar
    
    Returns:
        Dict: Objetivo com campos normalizados
    """
    obj_normalizado = objetivo.copy()
    
    # Garantir ID
    if 'id' not in obj_normalizado:
        obj_normalizado['id'] = gerar_id()
    
    # Mapear campos para equivalentes
    if 'nome' in obj_normalizado and 'titulo' not in obj_normalizado:
        obj_normalizado['titulo'] = obj_normalizado['nome']
    
    if 'titulo' in obj_normalizado and 'nome' not in obj_normalizado:
        obj_normalizado['nome'] = obj_normalizado['titulo']
    
    if 'valor_total' in obj_normalizado and 'valor_meta' not in obj_normalizado:
        obj_normalizado['valor_meta'] = obj_normalizado['valor_total']
    
    if 'valor_meta' in obj_normalizado and 'valor_total' not in obj_normalizado:
        obj_normalizado['valor_total'] = obj_normalizado['valor_meta']
    
    if 'data_alvo' in obj_normalizado and 'data_meta' not in obj_normalizado:
        obj_normalizado['data_meta'] = obj_normalizado['data_alvo']
    
    if 'data_meta' in obj_normalizado and 'data_alvo' not in obj_normalizado:
        obj_normalizado['data_alvo'] = obj_normalizado['data_meta']
    
    # Formatar datas
    for campo_data in ['data_inicio', 'data_alvo', 'data_meta']:
        if campo_data in obj_normalizado:
            obj_normalizado[campo_data] = formatar_data(obj_normalizado[campo_data])
    
    # Valores padrão
    if 'investimentos_vinculados' not in obj_normalizado:
        obj_normalizado['investimentos_vinculados'] = []
    
    if 'valor_atual' not in obj_normalizado:
        obj_normalizado['valor_atual'] = 0
    
    return obj_normalizado

def normalizar_divida(divida: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza os dados de uma dívida para garantir compatibilidade.
    
    Args:
        divida: Dados da dívida a normalizar
    
    Returns:
        Dict: Dívida com campos normalizados
    """
    div_normalizada = divida.copy()
    
    # Garantir ID
    if 'id' not in div_normalizada:
        div_normalizada['id'] = gerar_id()
    
    # Mapear campos para equivalentes
    if 'valor_atual' in div_normalizada and 'valor_restante' not in div_normalizada:
        div_normalizada['valor_restante'] = div_normalizada['valor_atual']
    
    if 'valor_restante' in div_normalizada and 'valor_atual' not in div_normalizada:
        div_normalizada['valor_atual'] = div_normalizada['valor_restante']
    
    if 'valor_inicial' in div_normalizada and 'valor_total' not in div_normalizada:
        div_normalizada['valor_total'] = div_normalizada['valor_inicial']
    
    if 'valor_total' in div_normalizada and 'valor_inicial' not in div_normalizada:
        div_normalizada['valor_inicial'] = div_normalizada['valor_total']
    
    if 'parcelas' in div_normalizada and 'parcelas_total' not in div_normalizada:
        div_normalizada['parcelas_total'] = div_normalizada['parcelas']
    
    if 'parcelas_total' in div_normalizada and 'parcelas' not in div_normalizada:
        div_normalizada['parcelas'] = div_normalizada['parcelas_total']
    
    # Formatar datas
    for campo_data in ['data_inicio', 'data_vencimento']:
        if campo_data in div_normalizada:
            div_normalizada[campo_data] = formatar_data(div_normalizada[campo_data])
    
    # Valores padrão
    if 'parcelas_pagas' not in div_normalizada:
        div_normalizada['parcelas_pagas'] = 0
    
    if 'tipo' not in div_normalizada:
        div_normalizada['tipo'] = 'outros'
    
    if 'taxa_juros' not in div_normalizada:
        div_normalizada['taxa_juros'] = 0.0
    
    return div_normalizada

def normalizar_investimento(investimento: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza os dados de um investimento para garantir compatibilidade.
    
    Args:
        investimento: Dados do investimento a normalizar
    
    Returns:
        Dict: Investimento com campos normalizados
    """
    inv_normalizado = investimento.copy()
    
    # Garantir ID
    if 'id' not in inv_normalizado:
        inv_normalizado['id'] = gerar_id()
    
    # Mapear campos para equivalentes
    if 'rendimento' in inv_normalizado and 'rendimento_mensal' not in inv_normalizado:
        inv_normalizado['rendimento_mensal'] = inv_normalizado['rendimento']
    
    if 'taxa_retorno' in inv_normalizado and 'rendimento_anual' not in inv_normalizado:
        inv_normalizado['rendimento_anual'] = inv_normalizado['taxa_retorno']
    
    # Formatar datas
    for campo_data in ['data_inicio', 'data_vencimento', 'data_resgate']:
        if campo_data in inv_normalizado:
            inv_normalizado[campo_data] = formatar_data(inv_normalizado[campo_data])
    
    # Valores padrão
    if 'valor_atual' not in inv_normalizado and 'valor_inicial' in inv_normalizado:
        inv_normalizado['valor_atual'] = inv_normalizado['valor_inicial']
    
    # Garantir categoria
    if 'categoria' not in inv_normalizado:
        inv_normalizado['categoria'] = "outros"
    
    return inv_normalizado

def normalizar_gasto(gasto: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza os dados de um gasto para garantir compatibilidade.
    
    Args:
        gasto: Dados do gasto a normalizar
    
    Returns:
        Dict: Gasto com campos normalizados
    """
    gasto_normalizado = gasto.copy()
    
    # Garantir ID
    if 'id' not in gasto_normalizado:
        gasto_normalizado['id'] = gerar_id()
    
    # Mapear campos para equivalentes
    if 'data_gasto' in gasto_normalizado and 'data' not in gasto_normalizado:
        gasto_normalizado['data'] = gasto_normalizado['data_gasto']
    
    # Formatar datas
    if 'data' in gasto_normalizado:
        gasto_normalizado['data'] = formatar_data(gasto_normalizado['data'])
    
    # Garantir tipo e categoria
    if 'tipo' not in gasto_normalizado:
        gasto_normalizado['tipo'] = "outros"
    
    if 'categoria' not in gasto_normalizado:
        gasto_normalizado['categoria'] = "outros"
    
    return gasto_normalizado

def normalizar_seguro(seguro: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza os dados de um seguro para garantir compatibilidade.
    
    Args:
        seguro: Dados do seguro a normalizar
    
    Returns:
        Dict: Seguro com campos normalizados
    """
    seguro_normalizado = seguro.copy()
    
    # Garantir ID
    if 'id' not in seguro_normalizado:
        seguro_normalizado['id'] = gerar_id()
    
    # Mapear campos para equivalentes
    if 'valor' in seguro_normalizado and 'valor_premio' not in seguro_normalizado:
        seguro_normalizado['valor_premio'] = seguro_normalizado['valor']
    
    if 'cobertura' in seguro_normalizado and 'valor_cobertura' not in seguro_normalizado:
        seguro_normalizado['valor_cobertura'] = seguro_normalizado['cobertura']
    
    # Formatar datas
    for campo_data in ['data_inicio', 'data_vencimento']:
        if campo_data in seguro_normalizado:
            seguro_normalizado[campo_data] = formatar_data(seguro_normalizado[campo_data])
    
    return seguro_normalizado

def normalizar_dados(dados: Dict[str, Any], tipo_entidade: str) -> Dict[str, Any]:
    """
    Normaliza os dados de acordo com o tipo de entidade.
    
    Args:
        dados: Dados a normalizar
        tipo_entidade: Tipo de entidade (objetivos, dividas, investimentos, gastos, seguros)
    
    Returns:
        Dict: Dados normalizados
    """
    normalizadores = {
        'objetivos': normalizar_objetivo,
        'dividas': normalizar_divida,
        'investimentos': normalizar_investimento,
        'gastos': normalizar_gasto,
        'seguros': normalizar_seguro,
    }
    
    if tipo_entidade in normalizadores:
        return normalizadores[tipo_entidade](dados)
    
    return dados.copy()  # Retorna uma cópia se não houver normalizador específico 