"""
Módulo para gerenciar a conexão com o Supabase e operações do banco de dados.
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Obter a URL e chave do Supabase das variáveis de ambiente ou do Streamlit secrets
def get_supabase_credentials():
    """
    Obtém as credenciais do Supabase do arquivo .env ou das secrets do Streamlit.
    """
    # Se estiver no Streamlit Cloud, usar as secrets
    if hasattr(st, "secrets") and "supabase" in st.secrets:
        supabase_url = st.secrets.supabase.url
        supabase_key = st.secrets.supabase.key
        supabase_service_key = st.secrets.supabase.service_key
    else:
        # Se não, usar as variáveis de ambiente
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        supabase_service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    return supabase_url, supabase_key, supabase_service_key

# Inicializar cliente Supabase
@st.cache_resource
def init_supabase_client():
    """
    Inicializa e retorna o cliente Supabase.
    """
    supabase_url, supabase_key, _ = get_supabase_credentials()
    
    if not supabase_url or not supabase_key:
        st.error("🚨 Credenciais do Supabase não configuradas. Verifique seu arquivo .env ou secrets do Streamlit.")
        return None
    
    try:
        # Usando forma compatível com supabase 1.0.3
        # Esta versão da biblioteca não tem o problema do proxy
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        st.error(f"🚨 Erro ao conectar ao Supabase: {e}")
        return None

# Função para obter o cliente Supabase
def get_supabase_client() -> Client:
    """
    Retorna o cliente Supabase inicializado.
    """
    if "supabase" not in st.session_state:
        st.session_state.supabase = init_supabase_client()
    
    return st.session_state.supabase

# === Funções de Autenticação ===

def signup_user(email, password, nome):
    """
    Registra um novo usuário no Supabase.
    
    Args:
        email (str): Email do usuário.
        password (str): Senha do usuário.
        nome (str): Nome do usuário.
        
    Returns:
        tuple: (success, data/error_message)
    """
    supabase = get_supabase_client()
    if not supabase:
        return False, "Cliente Supabase não está disponível"
    
    # Dados de cadastro em formato padrão para versão 2.x
    signup_data_v2 = {
        "email": email,
        "password": password,
        "options": {
            "data": {
                "nome": nome
            }
        }
    }
    
    # Dados de cadastro em formato padrão para versão 1.x
    signup_data_v1 = {
        "email": email,
        "password": password,
        "data": {
            "nome": nome
        }
    }
    
    # Tentar diferentes métodos de cadastro
    methods_to_try = [
        # Método para versão 2.x
        lambda: supabase.auth.sign_up(signup_data_v2),
        # Método alternativo para versão 2.x
        lambda: supabase.auth.sign_up(email=email, password=password, options={"data": {"nome": nome}}),
        # Método para versão 1.x
        lambda: supabase.auth.sign_up(signup_data_v1),
        # Método alternativo para versão 1.x
        lambda: supabase.auth.sign_up(email=email, password=password, data={"nome": nome})
    ]
    
    for method in methods_to_try:
        try:
            response = method()
            
            if response and hasattr(response, 'user') and response.user and response.user.id:
                try:
                    # Converter o datetime para string ISO format
                    created_at_str = response.user.created_at.isoformat() if hasattr(response.user, 'created_at') else None
                    
                    # Inserir dados adicionais do usuário na tabela 'perfis'
                    try:
                        supabase.table("perfis").insert({
                            "id": response.user.id,
                            "nome": nome,
                            "email": email,
                            "created_at": created_at_str
                        }).execute()
                    except Exception as perfil_error:
                        # Se falhar ao inserir no perfil, ainda podemos retornar sucesso no cadastro
                        st.warning(f"Usuário criado, mas falha ao criar perfil: {str(perfil_error)}")
                    
                    return True, response.user
                except Exception as perfil_error:
                    # Log do erro ao criar perfil, mas ainda retornamos sucesso no cadastro
                    st.warning(f"Erro ao salvar dados do perfil: {str(perfil_error)}")
                    return True, response.user
        except Exception as e:
            # Continuar tentando outros métodos se este falhar
            last_error = str(e)
            continue
    
    return False, f"Erro ao criar conta: {last_error}"

def login_user(email, password):
    """
    Autentica um usuário no Supabase.
    
    Args:
        email (str): Email do usuário.
        password (str): Senha do usuário.
        
    Returns:
        tuple: (success, user_data/error_message)
    """
    supabase = get_supabase_client()
    if not supabase:
        return False, "Cliente Supabase não está disponível"
    
    # Dados de autenticação em formato padrão
    auth_data = {
        "email": email,
        "password": password
    }
    
    # Tentar diferentes métodos de autenticação
    methods_to_try = [
        # Método para versão 2.x
        lambda: supabase.auth.sign_in_with_password(auth_data),
        # Método alternativo para versão 2.x
        lambda: supabase.auth.sign_in_with_password(email=email, password=password),
        # Método para versão 1.x
        lambda: supabase.auth.sign_in(auth_data),
        # Método alternativo para versão 1.x
        lambda: supabase.auth.sign_in(email=email, password=password)
    ]
    
    for method in methods_to_try:
        try:
            response = method()
            
            if response and hasattr(response, 'user') and response.user:
                user_data = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "nome": response.user.user_metadata.get("nome", "Usuário")
                }
                return True, user_data
        except Exception as e:
            # Continuar tentando outros métodos se este falhar
            last_error = str(e)
            continue
    
    return False, f"Erro de autenticação: {last_error}"

def logout_user():
    """
    Realiza logout do usuário atual.
    
    Returns:
        bool: True se o logout foi bem-sucedido, False caso contrário.
    """
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        supabase.auth.sign_out()
        return True
    except Exception:
        return False

def get_current_user():
    """
    Obtém informações do usuário atualmente autenticado.
    
    Returns:
        dict: Dados do usuário ou None se não houver usuário autenticado.
    """
    supabase = get_supabase_client()
    if not supabase:
        return None
    
    try:
        response = supabase.auth.get_user()
        if response and response.user:
            user = response.user
            return {
                "id": user.id,
                "email": user.email,
                "nome": user.user_metadata.get("nome", "Usuário")
            }
    except Exception:
        pass
    
    return None

# === Funções de Gerenciamento de Dados ===

def load_user_data(collection, user_id=None):
    """
    Carrega dados do usuário a partir do Supabase.
    
    Args:
        collection (str): Nome da coleção (tabela) a ser carregada.
        user_id (str, optional): ID do usuário. Se None, usa o usuário atual.
        
    Returns:
        list: Lista de dados carregados ou lista vazia em caso de erro.
    """
    if not user_id:
        user = get_current_user()
        if not user:
            return []
        user_id = user["id"]
    
    supabase = get_supabase_client()
    if not supabase:
        return []
    
    try:
        response = supabase.table(collection).select("*").eq("user_id", user_id).execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Erro ao carregar dados de {collection}: {e}")
        return []

def save_user_data(collection, data, user_id=None):
    """
    Salva dados do usuário no Supabase.
    
    Args:
        collection (str): Nome da coleção (tabela) a ser atualizada.
        data (dict): Dados a serem salvos.
        user_id (str, optional): ID do usuário. Se None, usa o usuário atual.
        
    Returns:
        bool: True se os dados foram salvos com sucesso, False caso contrário.
    """
    if not user_id:
        user = get_current_user()
        if not user:
            return False
        user_id = user["id"]
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Adicionar user_id aos dados se não estiver presente
        if isinstance(data, dict):
            # Fazer uma cópia dos dados para não modificar o original
            data_copy = data.copy()
            
            # Remover campos que não existem na tabela para evitar erros
            if collection == "perfis" and "data_registro" in data_copy:
                data_copy.pop("data_registro")
                # Usar created_at no lugar
                if "created_at" not in data_copy:
                    data_copy["created_at"] = datetime.now().isoformat()
            
            data_copy["user_id"] = user_id
            
            # Verificar se o registro já existe
            response = supabase.table(collection).select("*").eq("user_id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                # Se o registro já existe, atualizar
                record_id = response.data[0]["id"]
                supabase.table(collection).update(data_copy).eq("id", record_id).execute()
            else:
                # Se não existe, inserir novo
                supabase.table(collection).insert(data_copy).execute()
            
            return True
        elif isinstance(data, list):
            # Para listas de dados, remover dados existentes e inserir novos
            # Primeiro, apagar os dados existentes
            supabase.table(collection).delete().eq("user_id", user_id).execute()
            
            # Depois, inserir os novos dados
            if data:
                # Adicionar user_id a cada item
                for item in data:
                    if isinstance(item, dict):
                        item["user_id"] = user_id
                        
                        # Remover campos que causam erros específicos
                        if collection == "investimentos":
                            if "data_inicial" in item:
                                # Renomear para data_inicio se necessário
                                if "data_inicio" not in item:
                                    item["data_inicio"] = item.pop("data_inicial")
                                else:
                                    item.pop("data_inicial")
                
                supabase.table(collection).insert(data).execute()
            
            return True
        
        return False
    except Exception as e:
        st.error(f"Erro ao salvar dados em {collection}: {e}")
        return False

# === Funções Específicas para Gastos ===

def load_gastos():
    """
    Carrega os gastos do usuário atual.
    
    Returns:
        list: Lista de gastos ou lista vazia em caso de erro.
    """
    return load_user_data("gastos")

def save_gastos(gastos):
    """
    Salva a lista completa de gastos.
    
    Args:
        gastos (list): Lista de gastos a serem salvos.
        
    Returns:
        bool: True se os dados foram salvos com sucesso, False caso contrário.
    """
    user = get_current_user()
    if not user:
        return False
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Exclui gastos existentes do usuário
        supabase.table("gastos").delete().eq("user_id", user["id"]).execute()
        
        # Insere os novos gastos
        if gastos:
            for gasto in gastos:
                gasto["user_id"] = user["id"]
            
            supabase.table("gastos").insert(gastos).execute()
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar gastos: {e}")
        return False

def add_gasto(gasto):
    """
    Adiciona um novo gasto para o usuário atual.
    
    Args:
        gasto (dict): Dados do gasto a ser adicionado.
        
    Returns:
        bool: True se o gasto foi adicionado com sucesso, False caso contrário.
    """
    return save_user_data("gastos", gasto)

def delete_gasto(gasto_id):
    """
    Remove um gasto do usuário atual.
    
    Args:
        gasto_id (str): ID do gasto a ser removido.
        
    Returns:
        bool: True se o gasto foi removido com sucesso, False caso contrário.
    """
    user = get_current_user()
    if not user:
        return False
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        supabase.table("gastos").delete().eq("id", gasto_id).eq("user_id", user["id"]).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir gasto: {e}")
        return False

# === Funções Específicas para Investimentos ===

def load_investimentos():
    """
    Carrega os investimentos do usuário atual.
    
    Returns:
        list: Lista de investimentos ou lista vazia em caso de erro.
    """
    return load_user_data("investimentos")

def save_investimentos(investimentos):
    """
    Salva a lista completa de investimentos.
    
    Args:
        investimentos (list): Lista de investimentos a serem salvos.
        
    Returns:
        bool: True se os dados foram salvos com sucesso, False caso contrário.
    """
    user = get_current_user()
    if not user:
        return False
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Exclui investimentos existentes do usuário
        supabase.table("investimentos").delete().eq("user_id", user["id"]).execute()
        
        # Insere os novos investimentos
        if investimentos:
            for investimento in investimentos:
                investimento["user_id"] = user["id"]
            
            supabase.table("investimentos").insert(investimentos).execute()
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar investimentos: {e}")
        return False

def add_investimento(investimento):
    """
    Adiciona um novo investimento para o usuário atual.
    
    Args:
        investimento (dict): Dados do investimento a ser adicionado.
        
    Returns:
        bool: True se o investimento foi adicionado com sucesso, False caso contrário.
    """
    return save_user_data("investimentos", investimento)

def delete_investimento(investimento_id):
    """
    Remove um investimento do usuário atual.
    
    Args:
        investimento_id (str): ID do investimento a ser removido.
        
    Returns:
        bool: True se o investimento foi removido com sucesso, False caso contrário.
    """
    user = get_current_user()
    if not user:
        return False
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        supabase.table("investimentos").delete().eq("id", investimento_id).eq("user_id", user["id"]).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir investimento: {e}")
        return False

# === Funções Específicas para Dívidas ===

def load_dividas():
    """
    Carrega as dívidas do usuário atual.
    
    Returns:
        list: Lista de dívidas ou lista vazia em caso de erro.
    """
    return load_user_data("dividas")

def save_dividas(dividas):
    """
    Salva a lista completa de dívidas.
    
    Args:
        dividas (list): Lista de dívidas a serem salvas.
        
    Returns:
        bool: True se os dados foram salvos com sucesso, False caso contrário.
    """
    user = get_current_user()
    if not user:
        return False
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Exclui dívidas existentes do usuário
        supabase.table("dividas").delete().eq("user_id", user["id"]).execute()
        
        # Insere as novas dívidas
        if dividas:
            for divida in dividas:
                divida["user_id"] = user["id"]
            
            supabase.table("dividas").insert(dividas).execute()
        
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dívidas: {e}")
        return False

def add_divida(divida):
    """
    Adiciona uma nova dívida para o usuário atual.
    
    Args:
        divida (dict): Dados da dívida a ser adicionada.
        
    Returns:
        bool: True se a dívida foi adicionada com sucesso, False caso contrário.
    """
    return save_user_data("dividas", divida)

def delete_divida(divida_id):
    """
    Remove uma dívida do usuário atual.
    
    Args:
        divida_id (str): ID da dívida a ser removida.
        
    Returns:
        bool: True se a dívida foi removida com sucesso, False caso contrário.
    """
    user = get_current_user()
    if not user:
        return False
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        supabase.table("dividas").delete().eq("id", divida_id).eq("user_id", user["id"]).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir dívida: {e}")
        return False

# === Funções Específicas para Objetivos ===

def load_objetivos():
    """
    Carrega os objetivos financeiros do usuário atual.
    
    Returns:
        list: Lista de objetivos ou lista vazia em caso de erro.
    """
    return load_user_data("objetivos")

def save_objetivos(objetivos):
    """
    Salva a lista completa de objetivos.
    
    Args:
        objetivos (list): Lista de objetivos a serem salvos.
        
    Returns:
        bool: True se os dados foram salvos com sucesso, False caso contrário.
    """
    user = get_current_user()
    if not user:
        st.error("Erro ao salvar objetivos: usuário não autenticado")
        return False
    
    supabase = get_supabase_client()
    if not supabase:
        st.error("Erro ao salvar objetivos: cliente Supabase não disponível")
        return False
    
    try:
        # Verifica se há dados para salvar
        if not objetivos or len(objetivos) == 0:
            # Se a lista estiver vazia, apenas excluir todos
            supabase.table("objetivos").delete().eq("user_id", user["id"]).execute()
            return True
            
        # Lista de objetivos válidos para inserir
        objetivos_validos = []
        
        # Garantir que todos os campos obrigatórios estejam presentes
        for objetivo in objetivos:
            # Criar uma cópia para não modificar o original
            objetivo_valido = objetivo.copy()
            
            # Garantir que o título está presente (campo obrigatório)
            if "titulo" not in objetivo_valido and "nome" in objetivo_valido:
                objetivo_valido["titulo"] = objetivo_valido["nome"]
            elif "nome" not in objetivo_valido and "titulo" in objetivo_valido:
                objetivo_valido["nome"] = objetivo_valido["titulo"]
            elif "titulo" not in objetivo_valido and "nome" not in objetivo_valido:
                # Usar um título padrão em vez de retornar erro
                objetivo_valido["titulo"] = "Objetivo sem título"
                objetivo_valido["nome"] = "Objetivo sem título"
                print("Aviso: Objetivo sem título ou nome - usando título padrão")
                
            # Adicionar user_id em cada objetivo
            objetivo_valido["user_id"] = user["id"]
            
            # Adicionar à lista de objetivos válidos
            objetivos_validos.append(objetivo_valido)
        
        # Primeiro, fazer um backup dos objetivos existentes
        objetivos_existentes = []
        try:
            result = supabase.table("objetivos").select("*").eq("user_id", user["id"]).execute()
            if result.data:
                objetivos_existentes = result.data
        except Exception as e:
            print(f"Aviso: não foi possível fazer backup dos objetivos existentes: {e}")
        
        # Agora tenta excluir os objetivos existentes
        try:
            supabase.table("objetivos").delete().eq("user_id", user["id"]).execute()
        except Exception as e:
            st.error(f"Erro ao excluir objetivos existentes: {e}")
            return False
        
        # Finalmente, insere os novos objetivos (apenas os válidos)
        try:
            if objetivos_validos:
                supabase.table("objetivos").insert(objetivos_validos).execute()
            return True
        except Exception as e:
            # Se falhar ao inserir, tentar restaurar o backup
            st.error(f"Erro ao salvar objetivos: {e}")
            
            # Tenta restaurar os objetivos anteriores se houver backup
            if objetivos_existentes:
                try:
                    supabase.table("objetivos").insert(objetivos_existentes).execute()
                    st.warning("Os objetivos anteriores foram restaurados devido a um erro.")
                except Exception as restore_error:
                    st.error(f"Erro ao restaurar objetivos: {restore_error}")
                    
            return False
    except Exception as e:
        st.error(f"Erro ao salvar objetivos: {e}")
        return False

def add_objetivo(objetivo):
    """
    Adiciona um novo objetivo para o usuário atual.
    
    Args:
        objetivo (dict): Dados do objetivo a ser adicionado.
        
    Returns:
        bool: True se o objetivo foi adicionado com sucesso, False caso contrário.
    """
    return save_user_data("objetivos", objetivo)

def delete_objetivo(objetivo_id):
    """
    Remove um objetivo do usuário atual.
    
    Args:
        objetivo_id (str): ID do objetivo a ser removido.
        
    Returns:
        bool: True se o objetivo foi removido com sucesso, False caso contrário.
    """
    user = get_current_user()
    if not user:
        return False
    
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        supabase.table("objetivos").delete().eq("id", objetivo_id).eq("user_id", user["id"]).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir objetivo: {e}")
        return False 
