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
    'descricao': 'nome',
    'rendimento_anual': 'rentabilidade_anual',
    'data_inicial': 'data_inicio',
    'vencimento': 'data_vencimento'
}

MAPEAMENTO_GASTOS = {
    'data_gasto': 'data',
}

MAPEAMENTO_SEGUROS = {
    'valor': 'valor_premio',
    'cobertura': 'valor_cobertura',
}

# Mapeamentos de campos
FIELD_MAPPINGS = {
    'objetivos': {
        'nome': 'nome',
        'valor_total': 'valor_total',
        'valor_atual': 'valor_atual',
        'data_inicio': 'data_inicio',
        'data_fim': 'data_fim'
    },
    'dividas': {
        'descricao': 'descricao',
        'valor_total': 'valor_total',
        'valor_restante': 'valor_restante',
        'valor_inicial': 'valor_inicial',
        'valor_atual': 'valor_atual',
        'data_inicio': 'data_inicio',
        'data_vencimento': 'data_vencimento'
    },
    'investimentos': {
        'descricao': 'nome',
        'rendimento_anual': 'rentabilidade_anual',
        'data_inicial': 'data_inicio',
        'vencimento': 'data_vencimento'
    },
    'gastos': {
        'descricao': 'descricao',
        'valor': 'valor',
        'data': 'data',
        'data_gasto': 'data_gasto',
        'tipo': 'tipo',
        'categoria': 'categoria'
    },
    'seguros': {
        'tipo': 'tipo',
        'descricao': 'descricao',
        'valor_premio': 'valor_premio',
        'valor_cobertura': 'valor_cobertura',
        'data_inicio': 'data_inicio',
        'data_vencimento': 'data_vencimento',
        'seguradora': 'seguradora',
        'notas': 'notas'
    }
}

# Campos obrigatórios por entidade
REQUIRED_FIELDS = {
    'objetivos': ['nome', 'valor_total'],
    'dividas': ['descricao', 'valor_total'],
    'investimentos': ['descricao', 'valor_inicial', 'categoria'],
    'gastos': ['descricao', 'valor'],
    'seguros': ['tipo', 'descricao', 'valor_premio']
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
    if entidade not in REQUIRED_FIELDS:
        return True
        
    for campo in REQUIRED_FIELDS[entidade]:
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
    try:
        inv_normalizado = investimento.copy()
        
        # Garantir ID
        if 'id' not in inv_normalizado:
            inv_normalizado['id'] = gerar_id()
        
        # Garantir que nome está presente
        if 'descricao' in inv_normalizado and 'nome' not in inv_normalizado:
            inv_normalizado['nome'] = inv_normalizado.pop('descricao')
        
        # Garantir que rendimento_anual e rentabilidade_anual existam
        if 'rendimento_anual' in inv_normalizado:
            inv_normalizado['rentabilidade_anual'] = float(inv_normalizado.pop('rendimento_anual'))
        
        # Garantir campos de data
        if 'data_inicial' in inv_normalizado and 'data_inicio' not in inv_normalizado:
            inv_normalizado['data_inicio'] = inv_normalizado.pop('data_inicial')
        elif 'data_inicio' not in inv_normalizado:
            inv_normalizado['data_inicio'] = datetime.now().strftime("%Y-%m-%d")
        
        if 'vencimento' in inv_normalizado and 'data_vencimento' not in inv_normalizado:
            inv_normalizado['data_vencimento'] = inv_normalizado.pop('vencimento')
        
        # Formatar datas
        for campo_data in ['data_inicio', 'data_vencimento']:
            if campo_data in inv_normalizado:
                inv_normalizado[campo_data] = formatar_data(inv_normalizado[campo_data])
        
        # Garantir valores numéricos
        if 'valor_inicial' in inv_normalizado:
            inv_normalizado['valor_inicial'] = float(inv_normalizado['valor_inicial'])
        
        if 'valor_atual' in inv_normalizado:
            inv_normalizado['valor_atual'] = float(inv_normalizado['valor_atual'])
        elif 'valor_inicial' in inv_normalizado:
            inv_normalizado['valor_atual'] = float(inv_normalizado['valor_inicial'])
        
        # Garantir categoria e tipo
        if 'categoria' not in inv_normalizado and 'tipo' in inv_normalizado:
            inv_normalizado['categoria'] = inv_normalizado['tipo'].lower().replace(' ', '_')
        elif 'categoria' not in inv_normalizado:
            inv_normalizado['categoria'] = "outros"
        
        if 'tipo' not in inv_normalizado and 'categoria' in inv_normalizado:
            inv_normalizado['tipo'] = inv_normalizado['categoria'].replace('_', ' ').title()
        elif 'tipo' not in inv_normalizado:
            inv_normalizado['tipo'] = "Outros"
        
        # Garantir campos vazios como strings vazias em vez de None
        for campo in ['instituicao', 'notas']:
            if campo not in inv_normalizado or inv_normalizado[campo] is None:
                inv_normalizado[campo] = ""
        
        # Remover campos que não existem na tabela
        campos_validos = [
            'id', 'user_id', 'nome', 'tipo', 'categoria', 
            'valor_inicial', 'valor_atual', 'data_inicio', 
            'data_vencimento', 'rentabilidade_anual', 
            'instituicao', 'notas'
        ]
        return {k: v for k, v in inv_normalizado.items() if k in campos_validos}
        
    except Exception as e:
        print(f"Erro ao normalizar investimento: {e}")
        print(f"Dados do investimento: {investimento}")
        raise

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
    seg_normalizado = seguro.copy()
    
    # Garantir ID
    if 'id' not in seg_normalizado:
        seg_normalizado['id'] = gerar_id()
    
    # Mapear campos para equivalentes
    if 'premio_anual' in seg_normalizado and 'valor_premio' not in seg_normalizado:
        seg_normalizado['valor_premio'] = seg_normalizado['premio_anual']
        del seg_normalizado['premio_anual']
    
    if 'data_contratacao' in seg_normalizado and 'data_inicio' not in seg_normalizado:
        seg_normalizado['data_inicio'] = seg_normalizado['data_contratacao']
        del seg_normalizado['data_contratacao']
    
    # Formatar datas
    for campo_data in ['data_inicio', 'data_vencimento']:
        if campo_data in seg_normalizado:
            seg_normalizado[campo_data] = formatar_data(seg_normalizado[campo_data])
    
    # Valores padrão
    if 'valor_cobertura' not in seg_normalizado:
        seg_normalizado['valor_cobertura'] = 0.0
    
    if 'notas' not in seg_normalizado:
        seg_normalizado['notas'] = ''
    
    return seg_normalizado

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