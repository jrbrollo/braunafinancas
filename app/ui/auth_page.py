"""
Módulo para a página de autenticação do aplicativo.
"""
import streamlit as st
import re
from app.database.supabase_client import (
    login_user,
    signup_user,
    logout_user,
    get_current_user
)

def is_valid_email(email):
    """Verifica se o e-mail é válido."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def is_valid_password(password):
    """Verifica se a senha atende aos requisitos mínimos."""
    return len(password) >= 6

def is_valid_name(name):
    """Verifica se o nome é válido."""
    return len(name) >= 3

def render_login_form():
    """
    Renderiza o formulário de login.
    """
    with st.form("login_form"):
        st.markdown("### Entre na sua conta")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button("Entrar", use_container_width=True)
        with col2:
            st.form_submit_button("Esqueci minha senha", use_container_width=True, 
                                  on_click=lambda: st.session_state.update({"auth_view": "reset_password"}))
        
        if login_button:
            if not email or not password:
                st.error("Preencha todos os campos")
                return
            
            if not is_valid_email(email):
                st.error("E-mail inválido")
                return
            
            success, result = login_user(email, password)
            
            if success:
                st.session_state.user = result
                st.session_state.authenticated = True
                st.session_state.pop("auth_view", None)
                st.rerun()
            else:
                st.error(f"Erro ao fazer login: {result}")

def render_signup_form():
    """
    Renderiza o formulário de cadastro.
    """
    with st.form("signup_form"):
        st.markdown("### Crie sua conta")
        
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password", 
                                help="A senha deve ter pelo menos 6 caracteres")
        password_confirm = st.text_input("Confirme a senha", type="password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            signup_button = st.form_submit_button("Cadastrar", use_container_width=True)
        with col2:
            st.form_submit_button("Voltar para login", use_container_width=True, 
                                 on_click=lambda: st.session_state.update({"auth_view": "login"}))
        
        if signup_button:
            if not nome or not email or not password or not password_confirm:
                st.error("Preencha todos os campos")
                return
            
            if not is_valid_name(nome):
                st.error("Nome muito curto")
                return
            
            if not is_valid_email(email):
                st.error("E-mail inválido")
                return
            
            if not is_valid_password(password):
                st.error("A senha deve ter pelo menos 6 caracteres")
                return
            
            if password != password_confirm:
                st.error("As senhas não coincidem")
                return
            
            success, result = signup_user(email, password, nome)
            
            if success:
                st.success("Cadastro realizado com sucesso! Agora você pode fazer login.")
                st.session_state.auth_view = "login"
                st.rerun()
            else:
                st.error(f"Erro ao criar conta: {result}")

def render_reset_password_form():
    """
    Renderiza o formulário de recuperação de senha.
    """
    with st.form("reset_password_form"):
        st.markdown("### Recuperar senha")
        
        email = st.text_input("Digite seu e-mail")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            reset_button = st.form_submit_button("Enviar link de recuperação", use_container_width=True)
        with col2:
            st.form_submit_button("Voltar para login", use_container_width=True, 
                                 on_click=lambda: st.session_state.update({"auth_view": "login"}))
        
        if reset_button:
            if not email:
                st.error("Digite seu e-mail")
                return
            
            if not is_valid_email(email):
                st.error("E-mail inválido")
                return
            
            # Aqui você implementaria a lógica de recuperação de senha
            st.success("Se o e-mail estiver cadastrado, você receberá instruções para redefinir sua senha.")
            st.session_state.auth_view = "login"

def render_auth_page():
    """
    Renderiza a página de autenticação.
    """
    # Verificar se o usuário já está autenticado
    if "authenticated" in st.session_state and st.session_state.authenticated:
        user = get_current_user()
        if user:
            st.session_state.user = user
            return True
        else:
            st.session_state.pop("authenticated", None)
            st.session_state.pop("user", None)
    
    # Centralizar o conteúdo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo e título
        st.image("app/static/brauna_logo.png", width=150)
        st.title("Brauna Finanças")
        st.markdown("Controle suas finanças com simplicidade e segurança.")
        
        # Separador
        st.markdown("---")
        
        # Mostrar formulário apropriado com base no estado
        auth_view = st.session_state.get("auth_view", "login")
        
        if auth_view == "login":
            render_login_form()
            
            # Botão para alternar para o formulário de cadastro
            st.markdown("---")
            st.markdown("Ainda não tem uma conta?")
            if st.button("Criar uma conta", use_container_width=True):
                st.session_state.auth_view = "signup"
                st.rerun()
                
        elif auth_view == "signup":
            render_signup_form()
            
        elif auth_view == "reset_password":
            render_reset_password_form()
    
    return False

def logout():
    """
    Realiza o logout do usuário.
    """
    if logout_user():
        # Limpar o estado da sessão
        st.session_state.pop("authenticated", None)
        st.session_state.pop("user", None)
        st.rerun() 