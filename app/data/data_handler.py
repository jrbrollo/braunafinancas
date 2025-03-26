"""
Módulo para gerenciar a persistência e carregamento de dados do aplicativo.
Inclui funções para salvar e carregar dados do usuário, gastos, investimentos, dívidas e seguros.
"""
import os
import json
import yaml
from datetime import datetime
from pathlib import Path
import uuid
import streamlit as st

# Tente importar as funções do Supabase
try:
    from app.database.supabase_client import (
        get_current_user,
        get_supabase_client,
        load_gastos as supabase_load_gastos,
        save_gastos as supabase_save_gastos,
        add_gasto as supabase_add_gasto,
        delete_gasto as supabase_delete_gasto,
        load_investimentos as supabase_load_investimentos,
        save_investimentos as supabase_save_investimentos,
        add_investimento as supabase_add_investimento,
        delete_investimento as supabase_delete_investimento,
        load_dividas as supabase_load_dividas,
        save_dividas as supabase_save_dividas,
        add_divida as supabase_add_divida,
        delete_divida as supabase_delete_divida,
        load_objetivos as supabase_load_objetivos,
        save_objetivos as supabase_save_objetivos,
        add_objetivo as supabase_add_objetivo,
        delete_objetivo as supabase_delete_objetivo,
        load_user_data as supabase_load_user_data,
        save_user_data as supabase_save_user_data,
    )
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Importar o módulo de mapeamento de dados
try:
    from app.database.data_mapper import (
        normalizar_dados,
        validar_campos_obrigatorios,
        normalizar_objetivo,
        normalizar_divida,
        normalizar_investimento,
        normalizar_gasto,
        normalizar_seguro
    )
    DATA_MAPPER_AVAILABLE = True
except ImportError:
    DATA_MAPPER_AVAILABLE = False

# Definir diretório de dados - adaptado para funcionar no Streamlit Cloud
# No Streamlit Cloud, os dados serão armazenados na sessão
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Arquivos locais
USER_FILE = DATA_DIR / "user.json"
GASTOS_FILE = DATA_DIR / "gastos.json"
INVESTIMENTOS_FILE = DATA_DIR / "investimentos.json"
DIVIDAS_FILE = DATA_DIR / "dividas.json"
SEGUROS_FILE = DATA_DIR / "seguros.json"
CONFIG_FILE = DATA_DIR / "config.yaml"
OBJETIVOS_FILE = DATA_DIR / "objetivos.json"

# Verificar se estamos em ambiente de produção (Streamlit Cloud)
def is_prod():
    """
    Verifica se estamos em ambiente de produção (Streamlit Cloud)
    """
    return os.environ.get('STREAMLIT_SHARING', '') != ''

# Verificar se o usuário está autenticado no Supabase
def is_authenticated():
    """
    Verifica se o usuário está autenticado no Supabase
    """
    if not SUPABASE_AVAILABLE:
        return False
    
    user = get_current_user()
    return user is not None

# Funções para carregar dados

def load_user_data():
    """
    Carrega os dados do usuário (perfil).
    
    Returns:
        dict: Dicionário com os dados do usuário ou None se não encontrado
    """
    # Obter usuário atual
    user = get_current_user()
    if not user:
        return None
    
    try:
        # Tenta carregar o perfil do usuário
        perfis = supabase_load_user_data("perfis", user["id"])
        if perfis and len(perfis) > 0:
            return perfis[0]
        return None
    except Exception as e:
        st.error(f"Erro ao carregar dados do usuário: {e}")
        return None

def load_gastos():
    """
    Carrega os gastos. Se o arquivo não existir, retorna uma lista vazia.
    """
    # Se o Supabase estiver disponível e o usuário estiver autenticado, carregar do Supabase
    if SUPABASE_AVAILABLE and is_authenticated():
        return supabase_load_gastos()
    
    if is_prod():
        return st.session_state.get("gastos", [])
    
    if not os.path.exists(GASTOS_FILE):
        return []
    
    try:
        with open(GASTOS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar gastos: {e}")
        return []

def load_investimentos():
    """
    Carrega os investimentos. Se o arquivo não existir, retorna uma lista vazia.
    """
    # Se o Supabase estiver disponível e o usuário estiver autenticado, carregar do Supabase
    if SUPABASE_AVAILABLE and is_authenticated():
        return supabase_load_investimentos()
    
    if is_prod():
        return st.session_state.get("investimentos", [])
    
    if not os.path.exists(INVESTIMENTOS_FILE):
        return []
    
    try:
        with open(INVESTIMENTOS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar investimentos: {e}")
        return []

def load_dividas():
    """
    Carrega a lista de dívidas do usuário.
    
    Returns:
        list: Lista de dívidas do usuário atual.
    """
    try:
        # Tentar carregar do session state primeiro
        if "dividas" in st.session_state:
            return st.session_state.dividas
        
        # Tentar carregar do Supabase
        user = get_current_user()
        if user:
            cliente = get_supabase_client()
            if cliente:
                response = cliente.table('dividas').select('*').eq('user_id', user['id']).execute()
                if response.data:
                    st.session_state.dividas = response.data
                    return response.data
        
        # Carregar do arquivo local como fallback
        user_id = st.session_state.get("user_id", "default")
        arquivo = f"data/dividas_{user_id}.json"
        
        if os.path.exists(arquivo):
            with open(arquivo, "r", encoding="utf-8") as f:
                dividas = json.load(f)
                st.session_state.dividas = dividas
                return dividas
    except Exception as e:
        print(f"Erro ao carregar dívidas: {e}")
    
    # Caso não tenha dados, inicializa lista vazia
    st.session_state.dividas = []
    return []

def load_seguros():
    """
    Carrega os seguros. Se o arquivo não existir, retorna uma lista vazia.
    """
    if is_prod():
        return st.session_state.get("seguros", [])
    
    if not os.path.exists(SEGUROS_FILE):
        return []
    
    try:
        with open(SEGUROS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar seguros: {e}")
        return []

def load_config():
    """
    Carrega a configuração do aplicativo. Se o arquivo não existir, retorna um dicionário padrão.
    """
    default_config = {
        "inflacao_anual": 0.045,
        "primeiro_uso": True,
        "tema": "claro"
    }
    
    if is_prod():
        return st.session_state.get("config", default_config)
    
    if not os.path.exists(CONFIG_FILE):
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        return default_config

def load_objetivos():
    """
    Carrega os objetivos financeiros. Se o arquivo não existir, retorna uma lista vazia.
    """
    # Se o Supabase estiver disponível e o usuário estiver autenticado, carregar do Supabase
    if SUPABASE_AVAILABLE and is_authenticated():
        return supabase_load_objetivos()
    
    if is_prod():
        return st.session_state.get("objetivos", [])
    
    if not os.path.exists(OBJETIVOS_FILE):
        return []
    
    try:
        with open(OBJETIVOS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar objetivos: {e}")
        return []

# Funções para salvar dados

def save_user_data(user_data):
    """
    Salva os dados do usuário.
    """
    # Se o Supabase estiver disponível e o usuário estiver autenticado, salvar no Supabase
    if SUPABASE_AVAILABLE and is_authenticated():
        return supabase_save_user_data("perfis", user_data)
    
    if is_prod():
        st.session_state["user_data"] = user_data
        return True
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
        
        with open(USER_FILE, 'w', encoding='utf-8') as file:
            json.dump(user_data, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados do usuário: {e}")
        return False

def save_gastos(gastos):
    """
    Salva a lista de gastos.
    """
    # Se o Supabase estiver disponível e o usuário estiver autenticado, salvar no Supabase
    if SUPABASE_AVAILABLE and is_authenticated():
        return supabase_save_gastos(gastos)
    
    if is_prod():
        st.session_state["gastos"] = gastos
        return True
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(GASTOS_FILE), exist_ok=True)
        
        with open(GASTOS_FILE, 'w', encoding='utf-8') as file:
            json.dump(gastos, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar gastos: {e}")
        return False

def save_investimentos(investimentos):
    """
    Salva a lista de investimentos.
    """
    # Se o Supabase estiver disponível e o usuário estiver autenticado, salvar no Supabase
    if SUPABASE_AVAILABLE and is_authenticated():
        return supabase_save_investimentos(investimentos)
    
    if is_prod():
        st.session_state["investimentos"] = investimentos
        return True
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(INVESTIMENTOS_FILE), exist_ok=True)
        
        with open(INVESTIMENTOS_FILE, 'w', encoding='utf-8') as file:
            json.dump(investimentos, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar investimentos: {e}")
        return False

def save_dividas(dividas):
    """
    Salva a lista de dívidas do usuário.
    
    Args:
        dividas (list): Lista de dívidas a ser salva.
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário.
    """
    try:
        print(f"Tentando salvar {len(dividas)} dívidas")
        
        # Verificar se estamos em ambiente de produção (Streamlit Cloud)
        if is_prod():
            # Salvar no session state do Streamlit
            st.session_state.dividas = dividas
            print("Dívidas salvas no session_state")
            return True
        
        # Verificar se há dados de autenticação
        user = get_current_user() if SUPABASE_AVAILABLE else None
        
        if user and SUPABASE_AVAILABLE:
            # Salvar no Supabase
            try:
                cliente = get_supabase_client()
                if not cliente:
                    print("Cliente Supabase não disponível")
                    return False
                
                # Adicionar user_id a cada dívida
                for divida in dividas:
                    divida["user_id"] = user["id"]
                
                # Primeiro excluir todas as dívidas existentes do usuário
                response = cliente.table('dividas').delete().eq('user_id', user['id']).execute()
                
                # Depois inserir as novas
                if dividas:  # Verificar se a lista não está vazia
                    response = cliente.table('dividas').insert(dividas).execute()
                    if hasattr(response, 'error') and response.error:
                        print(f"Erro ao salvar dívidas no Supabase: {response.error}")
                        return False
                
                # Atualizar cache local
                st.session_state.dividas = dividas
                print("Dívidas salvas no Supabase")
                return True
            except Exception as e:
                print(f"Erro ao salvar dívidas no Supabase: {e}")
                import traceback
                print(traceback.format_exc())
                return False
        else:
            # Salvar em arquivo local
            try:
                # Definir o caminho do arquivo baseado no ID do usuário
                user_id = st.session_state.get("user_id", "default")
                arquivo = f"data/dividas_{user_id}.json"
                
                # Garantir que o diretório exista
                os.makedirs(os.path.dirname(arquivo), exist_ok=True)
                
                # Salvar o arquivo
                with open(arquivo, "w", encoding="utf-8") as f:
                    json.dump(dividas, f, ensure_ascii=False, indent=2)
                
                # Atualizar cache local
                st.session_state.dividas = dividas
                print(f"Dívidas salvas no arquivo: {arquivo}")
                return True
            except Exception as e:
                print(f"Erro ao salvar dívidas em arquivo: {e}")
                import traceback
                print(traceback.format_exc())
                return False
    except Exception as e:
        print(f"Erro geral ao salvar dívidas: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def save_seguros(seguros):
    """
    Salva a lista de seguros.
    """
    try:
        # Salvar no session state
        st.session_state["seguros"] = seguros
        
        # Tentar salvar no Supabase
        user = get_current_user()
        if user:
            cliente = get_supabase_client()
            if cliente:
                # Remover dados existentes
                cliente.table('seguros').delete().eq('user_id', user['id']).execute()
                
                # Inserir novos dados
                if seguros:
                    for seguro in seguros:
                        seguro_supabase = seguro.copy()
                        seguro_supabase['user_id'] = user['id']
                        cliente.table('seguros').insert(seguro_supabase).execute()
                
                return True
        
        # Salvar no arquivo local como fallback
        user_id = st.session_state.get("user_id", "default")
        arquivo = f"data/seguros_{user_id}.json"
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(arquivo), exist_ok=True)
        
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(seguros, f, ensure_ascii=False, indent=4)
        
        return True
    except Exception as e:
        print(f"Erro ao salvar seguros: {e}")
        return False

def save_config(config):
    """
    Salva a configuração do aplicativo.
    """
    if is_prod():
        st.session_state["config"] = config
        return True
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"Erro ao salvar configuração: {e}")
        return False

def save_objetivos(objetivos):
    """
    Salva a lista de objetivos financeiros.
    """
    # Se o Supabase estiver disponível e o usuário estiver autenticado, salvar no Supabase
    if SUPABASE_AVAILABLE and is_authenticated():
        return supabase_save_objetivos(objetivos)
    
    if is_prod():
        st.session_state["objetivos"] = objetivos
        return True
    
    try:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(OBJETIVOS_FILE), exist_ok=True)
        
        with open(OBJETIVOS_FILE, 'w', encoding='utf-8') as file:
            json.dump(objetivos, file, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar objetivos: {e}")
        return False

# Funções para adicionar itens

def add_gasto(gasto):
    """
    Adiciona um novo gasto à lista de gastos do usuário.
    
    Args:
        gasto (dict): Dados do gasto a ser adicionado.
        
    Returns:
        bool: True se adicionou com sucesso, False caso contrário.
    """
    try:
        # Validar campos obrigatórios
        if DATA_MAPPER_AVAILABLE and not validar_campos_obrigatorios(gasto, 'gastos'):
            print("Erro: campos obrigatórios ausentes no gasto")
            return False
            
        # Normalizar dados para garantir compatibilidade
        if DATA_MAPPER_AVAILABLE:
            gasto = normalizar_gasto(gasto)
        else:
            # Adicionar ID único se não foi fornecido
            if "id" not in gasto:
                gasto["id"] = str(uuid.uuid4())
                
            # Garantir tipo e categoria
            if 'tipo' not in gasto:
                gasto['tipo'] = "variavel"  # Valor padrão em minúsculas
            else:
                # Converter para minúsculas para garantir consistência
                gasto['tipo'] = gasto['tipo'].lower()
                
                # Normalizar "Fixo"/"Variável" para "fixo"/"variavel"
                if gasto['tipo'] == "fixo" or gasto['tipo'] == "fíxo" or gasto['tipo'] == "fixado":
                    gasto['tipo'] = "fixo"
                elif gasto['tipo'] == "variável" or gasto['tipo'] == "variavel" or gasto['tipo'] == "variable":
                    gasto['tipo'] = "variavel"
                
            if 'categoria' not in gasto:
                gasto['categoria'] = "outros"
        
        # Carregar gastos existentes
        gastos = load_gastos()
        
        # Adicionar novo gasto
        gastos.append(gasto)
        
        # Salvar lista atualizada
        return save_gastos(gastos)
    except Exception as e:
        print(f"Erro ao adicionar gasto: {e}")
        return False

def add_investimento(investimento):
    """
    Adiciona um novo investimento à lista de investimentos do usuário.
    
    Args:
        investimento (dict): Dados do investimento a ser adicionado.
        
    Returns:
        bool: True se adicionou com sucesso, False caso contrário.
    """
    try:
        # Validar campos obrigatórios
        campos_obrigatorios = ['nome', 'valor_inicial', 'valor_atual', 'data_inicio']
        campos_faltantes = [campo for campo in campos_obrigatorios if campo not in investimento]
        
        if campos_faltantes:
            print(f"Erro: campos obrigatórios ausentes no investimento: {campos_faltantes}")
            return False
            
        # Normalizar dados para garantir compatibilidade
        if DATA_MAPPER_AVAILABLE:
            try:
                investimento = normalizar_investimento(investimento)
            except Exception as e:
                print(f"Erro ao normalizar investimento: {e}")
                return False
        else:
            # Adicionar ID único se não foi fornecido
            if "id" not in investimento:
                investimento["id"] = str(uuid.uuid4())
                
            # Garantir categoria
            if 'categoria' not in investimento:
                investimento['categoria'] = "outros"
        
        # Carregar investimentos existentes
        investimentos = load_investimentos()
        
        # Adicionar novo investimento
        investimentos.append(investimento)
        
        # Salvar lista atualizada
        if save_investimentos(investimentos):
            return True
        else:
            print("Erro ao salvar lista de investimentos")
            return False
            
    except Exception as e:
        print(f"Erro ao adicionar investimento: {e}")
        print(f"Dados do investimento: {investimento}")
        return False

def add_divida(divida):
    """
    Adiciona uma nova dívida à lista de dívidas do usuário.
    
    Args:
        divida (dict): Dados da dívida a ser adicionada.
        
    Returns:
        bool: True se adicionou com sucesso, False caso contrário.
    """
    try:
        print(f"DEBUG: Iniciando adição de dívida: {divida}")
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['descricao', 'valor_atual', 'tipo']
        campos_faltantes = [campo for campo in campos_obrigatorios if campo not in divida]
        
        if campos_faltantes:
            print(f"ERRO: campos obrigatórios ausentes na dívida: {campos_faltantes}")
            st.error(f"Campos obrigatórios ausentes: {', '.join(campos_faltantes)}")
            return False
            
        # Normalizar dados para garantir compatibilidade
        if "id" not in divida:
            divida["id"] = str(uuid.uuid4())
            
        # Garantir compatibilidade entre campos
        if 'valor_atual' in divida and 'valor_restante' not in divida:
            divida['valor_restante'] = divida['valor_atual']
            
        if 'valor_inicial' in divida and 'valor_total' not in divida:
            divida['valor_total'] = divida['valor_inicial']
        
        # Simplificar o acesso às dívidas - usar diretamente session_state quando possível
        if "dividas" in st.session_state:
            dividas = st.session_state.dividas
        else:
            # Carregar dívidas ou criar lista vazia
            dividas = load_dividas() or []
            
        # Adicionar nova dívida
        dividas.append(divida)
        
        # Salvar diretamente no session_state primeiro
        st.session_state.dividas = dividas
        
        # Salvar no armazenamento persistente
        print(f"DEBUG: Tentando salvar lista de {len(dividas)} dívidas")
        
        # Método simplificado de persistência - evitar problemas com Supabase
        try:
            # Utilizar método mais simples para produção
            if is_prod():
                print("DEBUG: Salvando em ambiente de produção (session_state)")
                return True  # Já salvamos no session_state anteriormente
                
            # Salvamento local
            user_id = st.session_state.get("user_id", "default")
            arquivo = f"data/dividas_{user_id}.json"
            
            # Garantir que o diretório exista
            os.makedirs(os.path.dirname(arquivo), exist_ok=True)
            
            # Salvar o arquivo
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dividas, f, ensure_ascii=False, indent=2)
                
            print(f"DEBUG: Dívidas salvas com sucesso no arquivo: {arquivo}")
            return True
        except Exception as e:
            print(f"ERRO: Falha ao persistir dívidas: {e}")
            import traceback
            print(traceback.format_exc())
            
            # Retornar verdadeiro mesmo assim, já que os dados estão no session_state
            # Pelo menos o usuário não perderá seus dados durante a sessão atual
            return True
            
    except Exception as e:
        import traceback
        print(f"ERRO: Erro ao adicionar dívida: {e}")
        print(traceback.format_exc())
        return False

def add_objetivo(objetivo):
    """
    Adiciona um novo objetivo à lista de objetivos do usuário.
    
    Args:
        objetivo (dict): Dados do objetivo a ser adicionado.
        
    Returns:
        bool: True se adicionou com sucesso, False caso contrário.
    """
    try:
        # Validar campos obrigatórios
        if DATA_MAPPER_AVAILABLE and not validar_campos_obrigatorios(objetivo, 'objetivos'):
            print("Erro: campos obrigatórios ausentes no objetivo")
            return False
            
        # Normalizar dados para garantir compatibilidade
        if DATA_MAPPER_AVAILABLE:
            objetivo = normalizar_objetivo(objetivo)
        else:
            # Adicionar compatibilidade para o Supabase:
            if 'nome' in objetivo and 'titulo' not in objetivo:
                objetivo['titulo'] = objetivo['nome']
                
            if 'valor_total' in objetivo and 'valor_meta' not in objetivo:
                objetivo['valor_meta'] = objetivo['valor_total']
                
            # Adicionar ID único se não foi fornecido
            if "id" not in objetivo:
                objetivo["id"] = str(uuid.uuid4())
        
        # Carregar objetivos existentes
        objetivos = load_objetivos()
        
        # Adicionar novo objetivo
        objetivos.append(objetivo)
        
        # Salvar lista atualizada
        return save_objetivos(objetivos)
    except Exception as e:
        print(f"Erro ao adicionar objetivo: {e}")
        return False

def create_backup():
    """
    Cria um backup dos dados atuais.
    """
    backup_dir = DATA_DIR / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Copiar arquivos existentes
    for file_path in [USER_FILE, GASTOS_FILE, INVESTIMENTOS_FILE, DIVIDAS_FILE, SEGUROS_FILE, CONFIG_FILE, OBJETIVOS_FILE]:
        if os.path.exists(file_path):
            backup_file = backup_dir / file_path.name
            try:
                with open(file_path, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            except Exception as e:
                print(f"Erro ao fazer backup de {file_path.name}: {e}")
    
    return backup_dir

def initialize_data():
    """
    Inicializa os dados do aplicativo se for o primeiro uso.
    Carrega dados de exemplo para demonstração.
    
    Returns:
        bool: True se os dados foram inicializados, False caso contrário
    """
    config = load_config()
    
    # Verificar se é o primeiro uso
    if not config.get("primeiro_uso", True):
        return False
    
    try:
        # Criar diretórios se não existirem
        ensure_data_dirs()
        
        # Carregar e salvar dados de exemplo
        # ... existing code ...
        
        # Adicionar objetivos de exemplo se não existirem
        if not os.path.exists(OBJETIVOS_FILE):
            exemplo_objetivos = [
                {
                    "id": str(uuid.uuid4()),
                    "nome": "Comprar Apartamento",
                    "descricao": "Juntar dinheiro para a entrada de um apartamento",
                    "valor_total": 500000.0,
                    "valor_atual": 120000.0,
                    "data_inicio": "2023-01-01",
                    "data_alvo": "2027-12-31",
                    "categoria": "imovel",
                    "prioridade": "alta",
                    "taxa_retorno": 0.07,
                    "investimentos_vinculados": []
                },
                {
                    "id": str(uuid.uuid4()),
                    "nome": "Aposentadoria",
                    "descricao": "Fundo para aposentadoria",
                    "valor_total": 2000000.0,
                    "valor_atual": 150000.0,
                    "data_inicio": "2022-06-01",
                    "data_alvo": "2045-12-31",
                    "categoria": "aposentadoria",
                    "prioridade": "media",
                    "taxa_retorno": 0.08,
                    "investimentos_vinculados": []
                },
                {
                    "id": str(uuid.uuid4()),
                    "nome": "Viagem Europa",
                    "descricao": "Viagem para conhecer países da Europa",
                    "valor_total": 30000.0,
                    "valor_atual": 8000.0,
                    "data_inicio": "2023-03-15",
                    "data_alvo": "2024-07-01",
                    "categoria": "viagem",
                    "prioridade": "baixa",
                    "taxa_retorno": 0.04,
                    "investimentos_vinculados": []
                }
            ]
            save_objetivos(exemplo_objetivos)
        
        # Marcar que não é mais o primeiro uso
        config["primeiro_uso"] = False
        save_config(config)
        
        return True
    except Exception as e:
        print(f"Erro ao inicializar dados: {e}")
        return False

# Funções de utilidade
def ensure_data_dirs():
    """Garante que os diretórios de dados existam."""
    os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(GASTOS_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(INVESTIMENTOS_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(DIVIDAS_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(SEGUROS_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OBJETIVOS_FILE), exist_ok=True)

def atualizar_progresso_objetivo(objetivo_id, novo_valor):
    """
    Atualiza o valor atual de um objetivo específico.
    
    Args:
        objetivo_id (str): ID do objetivo a ser atualizado
        novo_valor (float): Novo valor atual do objetivo
        
    Returns:
        bool: True se atualizado com sucesso, False caso contrário
    """
    objetivos = load_objetivos()
    
    for objetivo in objetivos:
        if objetivo.get("id") == objetivo_id:
            objetivo["valor_atual"] = novo_valor
            return save_objetivos(objetivos)
    
    return False

def vincular_investimento_objetivo(objetivo_id, investimento_id):
    """
    Vincula um investimento a um objetivo financeiro.
    
    Args:
        objetivo_id (str): ID do objetivo
        investimento_id (str): ID do investimento
        
    Returns:
        bool: True se vinculado com sucesso, False caso contrário
    """
    objetivos = load_objetivos()
    
    for objetivo in objetivos:
        if objetivo.get("id") == objetivo_id:
            if "investimentos_vinculados" not in objetivo:
                objetivo["investimentos_vinculados"] = []
            
            # Verificar se o investimento já está vinculado
            if investimento_id not in objetivo["investimentos_vinculados"]:
                objetivo["investimentos_vinculados"].append(investimento_id)
                return save_objetivos(objetivos)
            return True  # Já está vinculado
    
    return False

def desvincular_investimento_objetivo(objetivo_id, investimento_id):
    """
    Remove o vínculo entre um investimento e um objetivo.
    
    Args:
        objetivo_id (str): ID do objetivo
        investimento_id (str): ID do investimento
        
    Returns:
        bool: True se desvinculado com sucesso, False caso contrário
    """
    objetivos = load_objetivos()
    
    for objetivo in objetivos:
        if objetivo.get("id") == objetivo_id and "investimentos_vinculados" in objetivo:
            if investimento_id in objetivo["investimentos_vinculados"]:
                objetivo["investimentos_vinculados"].remove(investimento_id)
                return save_objetivos(objetivos)
    
    return False

def calcular_progresso_objetivos():
    """
    Recalcula o progresso de todos os objetivos com base nos investimentos vinculados.
    Usado quando um investimento é atualizado ou removido.
    
    Returns:
        bool: True se atualizado com sucesso, False caso contrário
    """
    objetivos = load_objetivos()
    investimentos = load_investimentos()
    
    # Criar um dicionário de investimentos para acesso rápido
    investimentos_dict = {inv.get("id", ""): inv for inv in investimentos if "id" in inv}
    
    for objetivo in objetivos:
        if "investimentos_vinculados" in objetivo and objetivo["investimentos_vinculados"]:
            # Calcular a soma dos valores atuais dos investimentos vinculados
            valor_atual = 0
            for inv_id in objetivo["investimentos_vinculados"]:
                if inv_id in investimentos_dict:
                    investimento = investimentos_dict[inv_id]
                    valor_atual += investimento.get("valor_atual", 0)
            
            # Atualizar o valor atual do objetivo
            objetivo["valor_atual"] = valor_atual
    
    # Salvar os objetivos atualizados
    return save_objetivos(objetivos)

# Funções para seguros

def add_seguro(seguro):
    """
    Adiciona um novo seguro à lista de seguros do usuário.
    
    Args:
        seguro (dict): Dados do seguro a ser adicionado.
        
    Returns:
        bool: True se adicionou com sucesso, False caso contrário.
    """
    try:
        # Validar campos obrigatórios
        if DATA_MAPPER_AVAILABLE and not validar_campos_obrigatorios(seguro, 'seguros'):
            print("Erro: campos obrigatórios ausentes no seguro")
            return False
            
        # Normalizar dados para garantir compatibilidade
        if DATA_MAPPER_AVAILABLE:
            seguro = normalizar_seguro(seguro)
        else:
            # Adicionar ID único se não foi fornecido
            if "id" not in seguro:
                seguro["id"] = str(uuid.uuid4())
        
        # Carregar seguros existentes
        seguros = load_seguros()
        
        # Adicionar novo seguro
        seguros.append(seguro)
        
        # Salvar lista atualizada
        return save_seguros(seguros)
    except Exception as e:
        print(f"Erro ao adicionar seguro: {e}")
        return False

def delete_seguro(seguro_id):
    """
    Remove um seguro da lista.
    
    Args:
        seguro_id (str): ID do seguro a ser removido.
        
    Returns:
        bool: True se o seguro foi removido com sucesso, False caso contrário.
    """
    seguros = load_seguros()
    
    # Encontrar o seguro pelo ID
    for i, seguro in enumerate(seguros):
        if seguro.get("id") == seguro_id:
            seguros.pop(i)
            return save_seguros(seguros)
    
    return False

def delete_divida(divida_id):
    """
    Remove uma dívida da lista de dívidas do usuário.
    
    Args:
        divida_id (str): ID da dívida a ser removida.
        
    Returns:
        bool: True se removeu com sucesso, False caso contrário.
    """
    try:
        # Carregar dívidas existentes
        dividas = load_dividas()
        
        # Encontrar e remover a dívida com o ID especificado
        for i, divida in enumerate(dividas):
            if divida.get("id") == divida_id:
                dividas.pop(i)
                break
        else:
            # Dívida não encontrada
            return False
        
        # Salvar lista atualizada
        return save_dividas(dividas)
    except Exception as e:
        print(f"Erro ao remover dívida: {e}")
        return False

def load_data(data_type):
    """
    Carrega dados de um tipo específico.
    
    Args:
        data_type (str): Tipo de dados a carregar (ex: 'gastos', 'investimentos', etc.)
        
    Returns:
        list: Lista de dados carregados ou lista vazia se não houver dados
    """
    if is_prod():
        return st.session_state.get(data_type, [])
    
    file_path = DATA_DIR / f"{data_type}.json"
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar {data_type}: {e}")
        return []

def save_data(data_type, data):
    """
    Salva dados de um tipo específico.
    
    Args:
        data_type (str): Tipo de dados a salvar (ex: 'gastos', 'investimentos', etc.)
        data (list): Lista de dados a salvar
    """
    # Normalizar os tipos dos gastos se for tipo 'gastos'
    if data_type == 'gastos':
        # Garantir que os tipos estejam em minúsculas
        for item in data:
            if 'tipo' in item:
                item['tipo'] = item['tipo'].lower()
                # Padronizar valores
                if item['tipo'] in ['fixo', 'fíxo', 'fixado']:
                    item['tipo'] = 'fixo'
                elif item['tipo'] in ['variável', 'variavel', 'variable']:
                    item['tipo'] = 'variavel'
    
    if is_prod():
        st.session_state[data_type] = data
        return
    
    file_path = DATA_DIR / f"{data_type}.json"
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar {data_type}: {e}") 