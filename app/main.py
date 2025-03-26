import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Configurar o path para funcionar tanto localmente quanto no Streamlit Cloud
current_dir = Path(__file__).parent
root_dir = current_dir.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# Importar os módulos de UI
from app.ui.dashboard_page import render_dashboard_page
from app.ui.gastos_page import render_gastos_page
from app.ui.investimentos_page import render_investimentos_page
from app.ui.dividas_page import render_dividas_page
from app.ui.seguros_page import render_seguros_page
# from app.ui.config_page import render_configuracoes_page  # Nome antigo
from app.ui.settings_page import render_settings_page
from app.ui.objetivos_page import render_objetivos_page
from app.ui.planejamento_page import render_planejamento_page
from app.ui.auth_page import render_auth_page, logout

# Importar manipulação de dados
from app.data.data_handler import (
    load_config, save_config, initialize_data, ensure_data_dirs, 
    load_gastos, save_gastos, normalizar_gastos_existentes
)
from app.data import init_data

# Importar cliente Supabase
from app.database.supabase_client import get_supabase_client, get_current_user

# Carregar estilos personalizados
def load_custom_styles():
    css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "custom_style.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"""
            <style>
            {f.read()}
            </style>
            """, unsafe_allow_html=True)
    else:
        st.error(f"Arquivo CSS não encontrado: {css_file}")
    
    # Garantir que os elementos padrão do Streamlit estejam ocultos
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden !important; display: none !important;}
        footer {visibility: hidden !important; display: none !important;}
        header {visibility: hidden !important; display: none !important;}
        div[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
        </style>
    """, unsafe_allow_html=True)
    
    # Aplicar atributo data-theme para o modo escuro
    if "tema" in st.session_state and st.session_state.tema == "escuro":
        # Adiciona um script para definir o atributo data-theme no elemento HTML
        st.markdown("""
            <script>
                // Aplicar tema escuro
                document.documentElement.setAttribute('data-theme', 'dark');
                document.body.classList.add('dark-theme');
                
                // Aplicar tema escuro aos elementos do Streamlit
                document.querySelectorAll('.stApp, .main, [data-testid="stAppViewContainer"]').forEach(el => {
                    el.classList.add('dark-theme');
                    el.setAttribute('data-theme', 'dark');
                });
                
                // Aplicar tema escuro à barra lateral
                document.querySelectorAll('[data-testid="stSidebar"]').forEach(el => {
                    el.classList.add('dark-theme');
                    el.setAttribute('data-theme', 'dark');
                });
                
                // Forçar atualização de estilos
                document.body.style.backgroundColor = '#121212';
                document.body.style.color = '#E0E0E0';
            </script>
            """, unsafe_allow_html=True)
    else:
        # Remove o atributo data-theme para o modo claro
        st.markdown("""
            <script>
                // Remover tema escuro
                document.documentElement.removeAttribute('data-theme');
                document.body.classList.remove('dark-theme');
                
                // Remover tema escuro dos elementos do Streamlit
                document.querySelectorAll('.stApp, .main, [data-testid="stAppViewContainer"]').forEach(el => {
                    el.classList.remove('dark-theme');
                    el.removeAttribute('data-theme');
                });
                
                // Remover tema escuro da barra lateral
                document.querySelectorAll('[data-testid="stSidebar"]').forEach(el => {
                    el.classList.remove('dark-theme');
                    el.removeAttribute('data-theme');
                });
                
                // Restaurar cores padrão
                document.body.style.backgroundColor = '#FFFFFF';
                document.body.style.color = '#333333';
            </script>
            """, unsafe_allow_html=True)

# Carregar as fontes do Google
def load_google_fonts():
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    """, unsafe_allow_html=True)

# Esconder o menu principal e o rodapé do Streamlit
def hide_streamlit_elements():
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Verificar se o cliente Supabase está disponível
def is_supabase_available():
    """
    Verifica se o cliente Supabase está disponível e conectado.
    """
    client = get_supabase_client()
    return client is not None

# Configuração da página
st.set_page_config(
    page_title="Brauna Finanças",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="auto"
)

# Renderizar o cabeçalho personalizado
def render_header():
    user = get_current_user()
    email = user.get('email', 'Usuário') if user else 'Usuário'
    nome = user.get('nome', email.split('@')[0]) if user else 'Usuário'
    
    st.markdown(f"""
    <div class="header">
        <div class="header-logo">💰 Brauna Finanças</div>
        <div class="header-user">
            <span class="user-icon">👤</span>
            <span class="user-name">{nome}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def apply_custom_style(tema="claro"):
    """
    Aplica estilos personalizados ao aplicativo
    
    Args:
        tema (str): O tema atual (claro ou escuro)
    """
    # Carregar o CSS personalizado do arquivo
    css_path = Path(__file__).parent / "static" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            custom_css = f.read()
            st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    else:
        # Fallback para o CSS incorporado se o arquivo não existir
        custom_css = """
        /* CSS básico de fallback */
        :root {
            --primary: #0066CC;
            --positive: #00A86B;
            --negative: #E53935;
        }
        """
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    
    # Aplicar tema escuro se necessário
    if tema == "escuro":
        st.markdown("""
        <style>
        :root {
            --primary: #4CAF50;
            --secondary: #2196F3;
            --accent: #FF9800;
            --background: #121212;
            --second-background: #1E1E1E;
            --text-color: #E0E0E0;
            --text-color-secondary: #9E9E9E;
            --card-background: #1E1E1E;
            --card-border: #333333;
            --success: #4CAF50;
            --warning: #FFC107;
            --error: #F44336;
            --gray-dark: #424242;
            --gray: #757575;
            --gray-light: #9E9E9E;
            --gray-lighter: #424242;
            --red: #F44336;
            --red-light: #331111;
            --green: #4CAF50;
            --green-light: #113311;
            --blue: #2196F3;
            --blue-light: #111133;
            --yellow: #FFC107;
            --yellow-light: #333311;
            --yellow-dark: #FF9800;
        }
        
        /* Aplicar tema escuro */
        body {
            background-color: var(--background);
            color: var(--text-color);
        }
        
        .stApp {
            background-color: var(--background);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--second-background);
        }
        
        .stTabs [data-baseweb="tab"] {
            color: var(--text-color);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: var(--primary);
            color: white;
        }
        
        /* Estilos para cards */
        .card {
            background-color: var(--card-background);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: box-shadow 0.3s;
        }
        
        .card:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }
        
        /* Estilos para badges */
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            text-align: center;
        }
        
        .badge.success {
            background-color: var(--green-light);
            color: var(--green);
        }
        
        .badge.warning {
            background-color: var(--yellow-light);
            color: var(--yellow);
        }
        
        .badge.danger {
            background-color: var(--red-light);
            color: var(--red);
        }
        
        /* Estilos para métricas */
        .metric-label {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        /* Cores para cartões específicos */
        .card.danger .metric-value {
            color: var(--red);
        }
        
        .card.success .metric-value {
            color: var(--green);
        }
        
        /* Estilos para input fields escuros */
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stDateInput>div>div>input {
            background-color: var(--second-background) !important;
            color: var(--text-color) !important;
            border-color: var(--gray-dark) !important;
        }
        
        .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stDateInput>div>div>input:focus {
            border-color: var(--primary) !important;
        }
        
        .stSelectbox>div>div>div, .stMultiselect>div>div>div {
            background-color: var(--second-background) !important;
            color: var(--text-color) !important;
            border-color: var(--gray-dark) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Tema claro (padrão)
        st.markdown("""
        <style>
        :root {
            --primary: #4CAF50;
            --secondary: #2196F3;
            --accent: #FF9800;
            --background: #FFFFFF;
            --second-background: #F5F5F5;
            --text-color: #212121;
            --text-color-secondary: #757575;
            --card-background: #FFFFFF;
            --card-border: #E0E0E0;
            --success: #4CAF50;
            --warning: #FFC107;
            --error: #F44336;
            --gray-dark: #424242;
            --gray: #757575;
            --gray-light: #9E9E9E;
            --gray-lighter: #E0E0E0;
            --red: #F44336;
            --red-light: #FFEBEE;
            --green: #4CAF50;
            --green-light: #E8F5E9;
            --blue: #2196F3;
            --blue-light: #E3F2FD;
            --yellow: #FFC107;
            --yellow-light: #FFF8E1;
            --yellow-dark: #FF9800;
        }
        
        /* Aplicar tema claro */
        body {
            background-color: var(--background);
            color: var(--text-color);
        }
        
        .stApp {
            background-color: var(--background);
        }
        
        /* Estilos para cards */
        .card {
            background-color: var(--card-background);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: box-shadow 0.3s;
        }
        
        .card:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Estilos para badges */
        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            text-align: center;
        }
        
        .badge.success {
            background-color: var(--green-light);
            color: var(--green);
        }
        
        .badge.warning {
            background-color: var(--yellow-light);
            color: var(--yellow-dark);
        }
        
        .badge.danger {
            background-color: var(--red-light);
            color: var(--red);
        }
        
        /* Estilos para métricas */
        .metric-label {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        /* Cores para cartões específicos */
        .card.danger .metric-value {
            color: var(--red);
        }
        
        .card.success .metric-value {
            color: var(--green);
        }
        </style>
        """, unsafe_allow_html=True)

def create_nav_item(icon, label, page_id, badge=None):
    """
    Cria um item de navegação estilizado para a barra lateral
    
    Args:
        icon (str): Ícone do item
        label (str): Texto do item
        page_id (str): ID da página para navegação
        badge (str, optional): Badge opcional para mostrar ao lado do item
    """
    is_active = st.session_state.pagina_atual == page_id
    active_class = "active" if is_active else ""
    
    badge_html = f'<span class="badge primary">{badge}</span>' if badge else ''
    
    nav_html = f"""
    <div class="nav-item {active_class}" id="nav-{page_id}" onclick="setPage('{page_id}')">
        <span class="nav-icon">{icon}</span>
        <span>{label}</span>
        {badge_html}
    </div>
    """
    
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # JavaScript para manipular a navegação
    js = f"""
    <script>
    function setPage(page) {{
        // Enviar uma mensagem para o Streamlit
        const data = {{
            page: page,
            timestamp: new Date().getTime()
        }};
        
        // Usar o armazenamento local para comunicação entre JavaScript e Streamlit
        localStorage.setItem('brauna_page', JSON.stringify(data));
        
        // Disparar um evento para notificar o Streamlit
        window.dispatchEvent(new Event('storage'));
        
        // Forçar um rerun
        setTimeout(() => {{
            window.location.reload();
        }}, 100);
    }}
    </script>
    """
    
    st.markdown(js, unsafe_allow_html=True)
    
    # Ler o localStorage para navegação
    if page_id == "dashboard":  # Só fazemos isso uma vez
        js_get_page = """
        <script>
        // Verificar se temos uma página salva
        const savedPage = localStorage.getItem('brauna_page');
        if (savedPage) {
            const pageData = JSON.parse(savedPage);
            // Enviar para Streamlit através do session state
            window.parent.postMessage({
                type: "streamlit:setComponentValue",
                value: pageData.page
            }, "*");
        }
        </script>
        """
        
        st.markdown(js_get_page, unsafe_allow_html=True)
        
        # Componente oculto para receber a navegação do JavaScript
        nav_value = st.text_input("", key="nav_input", label_visibility="collapsed")
        if nav_value and nav_value != st.session_state.pagina_atual:
            set_pagina(nav_value)
            st.rerun()

def load_svg(icon_name):
    """
    Carrega um ícone SVG a partir do arquivo.
    
    Args:
        icon_name (str): Nome do arquivo do ícone sem a extensão .svg
        
    Returns:
        str: Conteúdo do arquivo SVG ou emoji de fallback em caso de erro
    """
    icon_path = Path(__file__).parent / "static" / "icons" / f"{icon_name}.svg"
    fallback_icons = {
        "dashboard": "📊",
        "expenses": "💸",
        "investments": "📈",
        "goals": "🎯",
        "debts": "📉",
        "insurance": "🛡️",
        "settings": "⚙️",
        "theme": "🌙"
    }
    
    try:
        if icon_path.exists():
            with open(icon_path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return fallback_icons.get(icon_name, "📄")
    except Exception:
        return fallback_icons.get(icon_name, "📄")

def trend_indicator(value, prefix="", suffix="", positive_is_good=True):
    """
    Cria um indicador de tendência com seta para cima ou para baixo
    
    Args:
        value (float): Valor da tendência (positivo ou negativo)
        prefix (str): Prefixo para o valor (ex: "R$")
        suffix (str): Sufixo para o valor (ex: "%")
        positive_is_good (bool): Se True, valores positivos são bons (verde). Se False, valores negativos são bons (verde).
        
    Returns:
        str: HTML do indicador de tendência
    """
    if value == 0:
        return f'<span class="trend-neutral">{prefix}{value}{suffix}</span>'
    
    is_positive = value > 0
    is_good = (is_positive and positive_is_good) or (not is_positive and not positive_is_good)
    
    trend_class = "trend-up" if is_positive else "trend-down"
    color_class = "success" if is_good else "danger"
    
    value_abs = abs(value)
    sign = "+" if is_positive else "-"
    
    return f'<span class="{trend_class} {color_class}">{sign}{prefix}{value_abs}{suffix}</span>'

def configure_plotly_default_style(tema="claro"):
    """
    Configura o estilo padrão para gráficos Plotly com cores consistentes
    
    Args:
        tema (str): O tema atual (claro ou escuro)
    """
    import plotly.graph_objects as go
    import plotly.io as pio
    
    # Usar o esquema de cores do app
    colors = {
        'primary': '#0066CC',
        'primary_light': '#4D94FF',
        'positive': '#00A86B',
        'negative': '#E53935',
        'warning': '#F9A825',
        'text': '#333333',
        'gridline': '#E0E5E9',
        'background': '#FFFFFF'
    }
    
    # Tema escuro se necessário
    if tema == "escuro":
        colors['text'] = '#E0E0E0'
        colors['gridline'] = '#2A2A2A'
        colors['background'] = '#1E1E1E'
    
    # Template personalizado
    custom_template = go.layout.Template()
    
    # Configurações de layout padrão
    custom_template.layout = go.Layout(
        font=dict(family='Inter, sans-serif', color=colors['text']),
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        colorway=[
            colors['primary'], colors['positive'], colors['warning'], 
            colors['negative'], colors['primary_light']
        ],
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=colors['gridline'],
            zeroline=False,
            linecolor=colors['gridline']
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=colors['gridline'],
            zeroline=False,
            linecolor=colors['gridline']
        ),
        margin=dict(t=50, b=50, l=50, r=25),
        hoverlabel=dict(
            bgcolor=colors['background'],
            font_size=12,
            font_family='Inter, sans-serif'
        ),
        legend=dict(
            font=dict(size=12),
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)'
        )
    )
    
    # Definir como template padrão
    pio.templates['Brauna'] = custom_template
    pio.templates.default = 'Brauna'

def render_sidebar():
    """
    Renderiza a barra lateral com navegação
    """
    # Buscar as informações do usuário
    user = get_current_user()
    email = user.get('email', 'Usuário') if user else 'Usuário'
    nome = user.get('nome', email.split('@')[0]) if user else 'Usuário'
    
    # Sidebar para navegação
    with st.sidebar:
        # Logo e título do app
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 0.5rem 1rem; margin-bottom: 1rem; background-color: var(--card-background); border-radius: 0.5rem; box-shadow: var(--shadow-sm);">
            <div style="margin-right: 0.5rem;">
                <span style="font-size: 2rem;">💰</span>
            </div>
            <div>
                <h1 style="margin: 0; padding: 0; font-size: 1.8rem; color: var(--primary);">Brauna Finanças</h1>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações do usuário
        if user:
            st.markdown(f"""
            <div style="display: flex; align-items: center; padding: 0.5rem 1rem; margin-bottom: 0.5rem; background-color: var(--card-background); border-radius: 0.5rem; box-shadow: var(--shadow-sm);">
                <div style="margin-right: 0.5rem;">
                    <span style="font-size: 1.5rem;">👤</span>
                </div>
                <div>
                    <p style="margin: 0; padding: 0; font-size: 0.9rem;">Olá, <strong>{user.get('nome', 'Usuário')}</strong></p>
                    <p style="margin: 0; padding: 0; font-size: 0.8rem; color: var(--text-color-secondary);">{user.get('email', '')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Definição de botões de navegação
        nav_items = [
            {"icon": "📊", "label": "Dashboard", "id": "dashboard"},
            {"icon": "💸", "label": "Controle de Gastos", "id": "gastos"},
            {"icon": "📈", "label": "Investimentos", "id": "investimentos"},
            {"icon": "🎯", "label": "Objetivos", "id": "objetivos"},
            {"icon": "💳", "label": "Dívidas", "id": "dividas"},
            {"icon": "🔒", "label": "Seguros", "id": "seguros"},
            {"icon": "📋", "label": "Meu Planejamento", "id": "planejamento"},
            {"icon": "⚙️", "label": "Configurações", "id": "settings"}
        ]
        
        # Renderizar botões usando o Streamlit nativo
        pagina_atual = st.session_state.pagina_atual
        
        # Container para botões com espaçamento mínimo
        for item in nav_items:
            is_active = pagina_atual == item["id"]
            button_style = "primary" if is_active else "secondary"
            
            if st.button(
                f"{item['icon']} {item['label']}", 
                key=f"nav_{item['id']}",
                type=button_style,
                use_container_width=True
            ):
                set_pagina(item["id"])
        
        # Separador antes das configurações
        st.markdown('<div style="height: 1px; background: var(--border-color); margin: 8px 0;"></div>', unsafe_allow_html=True)
        
        # Botões para operações especiais
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Sair", use_container_width=True, type="secondary"):
                logout()
                st.rerun()
        
        with col2:
            tema_label = "🌙 Escuro" if st.session_state.tema == "claro" else "☀️ Claro"
            if st.button(tema_label, use_container_width=True, type="secondary"):
                toggle_tema()
                st.rerun()
        
        # Rodapé
        st.markdown("""
        <div style="position: relative; bottom: 1rem; left: 0; right: 0; text-align: center; padding: 0.5rem; font-size: 0.75rem; color: var(--text-color-secondary);">
            <p style="margin: 0;">Brauna Finanças v1.0.0</p>
            <p style="margin: 0;">© 2025 Brauna Finanças</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """
    Função principal que inicializa a aplicação
    """
    # Carregar estilos e fontes primeiro, antes de qualquer outro elemento da UI
    load_google_fonts()
    load_custom_styles()
    
    # Garantir que diretórios de dados existam
    ensure_data_dirs()
    
    # Carregar configuração
    config = load_config()
    
    # Inicializar dados e definir a variável de dados inicializados
    dados_inicializados = False
    try:
        # Função para inicializar os dados
        init_app_data()
        if not "initial_data_loaded" in st.session_state:
            dados_inicializados = True
    except Exception as e:
        print(f"Erro ao inicializar dados: {e}")
        dados_inicializados = False
    
    # Normalizar gastos para garantir consistência de tipos
    normalizar_gastos_existentes()
    
    # Configurar tema
    if "tema" not in st.session_state:
        st.session_state.tema = config.get("tema", "claro")
    
    # Inicializar session state para controle de navegação se não existir
    if "pagina_atual" not in st.session_state:
        st.session_state.pagina_atual = "dashboard"
    
    # Inicializar variáveis de estado para os formulários
    if "mostrar_form_gasto" not in st.session_state:
        st.session_state.mostrar_form_gasto = False
        
    if "mostrar_form_investimento" not in st.session_state:
        st.session_state.mostrar_form_investimento = False
        
    if "mostrar_form_divida" not in st.session_state:
        st.session_state.mostrar_form_divida = False
        
    if "mostrar_form_seguro" not in st.session_state:
        st.session_state.mostrar_form_seguro = False
        
    if "mostrar_form_objetivo" not in st.session_state:
        st.session_state.mostrar_form_objetivo = False
    
    # Inicializar variável para categoria selecionada nos gastos
    if "categoria_selecionada" not in st.session_state:
        st.session_state.categoria_selecionada = "🏠 Moradia"
    
    # Verificar autenticação
    is_authenticated = render_auth_page()
    
    # Só continua se o usuário estiver autenticado
    if not is_authenticated:
        return
        
    # Renderizar barra lateral
    render_sidebar()
    
    # Renderizar cabeçalho
    render_header()
    
    # Renderizar a página selecionada com transição suave
    pagina_atual = st.session_state.pagina_atual
    
    # Mostrar mensagem de dados inicializados após a inicialização do layout
    if dados_inicializados:
        st.markdown("""
        <div class="notification success">
            Dados de exemplo carregados com sucesso! Seu aplicativo está pronto para uso.
        </div>
        """, unsafe_allow_html=True)
    
    if pagina_atual == "dashboard":
        render_dashboard_page()
    elif pagina_atual == "gastos":
        render_gastos_page()
    elif pagina_atual == "investimentos":
        render_investimentos_page()
    elif pagina_atual == "objetivos":
        render_objetivos_page()
    elif pagina_atual == "dividas":
        render_dividas_page()
    elif pagina_atual == "seguros":
        render_seguros_page()
    elif pagina_atual == "planejamento":
        render_planejamento_page()
    elif pagina_atual == "settings":
        render_settings_page()
    else:
        # Página padrão (dashboard) se algum erro ocorrer
        render_dashboard_page()

# Função para definir a página atual
def set_pagina(pagina, rerun=True):
    st.session_state.pagina_atual = pagina
    if rerun:
        st.rerun()

# Função para alternar o tema
def toggle_tema(tema=None):
    config = load_config()
    
    if tema:
        st.session_state.tema = tema
        config["tema"] = tema
    else:
        if st.session_state.tema == "claro":
            st.session_state.tema = "escuro"
            config["tema"] = "escuro"
        else:
            st.session_state.tema = "claro"
            config["tema"] = "claro"
            
    save_config(config)
    
    # Força a atualização do atributo data-theme
    st.markdown(f"""
        <script>
            if ("{st.session_state.tema}" === "escuro") {{
                // Aplicar tema escuro
                document.documentElement.setAttribute('data-theme', 'dark');
                document.body.classList.add('dark-theme');
                
                // Aplicar tema escuro aos elementos do Streamlit
                document.querySelectorAll('.stApp, .main, [data-testid="stAppViewContainer"]').forEach(el => {{
                    el.classList.add('dark-theme');
                    el.setAttribute('data-theme', 'dark');
                }});
                
                // Aplicar tema escuro à barra lateral
                document.querySelectorAll('[data-testid="stSidebar"]').forEach(el => {{
                    el.classList.add('dark-theme');
                    el.setAttribute('data-theme', 'dark');
                }});
                
                // Forçar atualização de estilos
                document.body.style.backgroundColor = '#121212';
                document.body.style.color = '#E0E0E0';
            }} else {{
                // Remover tema escuro
                document.documentElement.removeAttribute('data-theme');
                document.body.classList.remove('dark-theme');
                
                // Remover tema escuro dos elementos do Streamlit
                document.querySelectorAll('.stApp, .main, [data-testid="stAppViewContainer"]').forEach(el => {{
                    el.classList.remove('dark-theme');
                    el.removeAttribute('data-theme');
                }});
                
                // Remover tema escuro da barra lateral
                document.querySelectorAll('[data-testid="stSidebar"]').forEach(el => {{
                    el.classList.remove('dark-theme');
                    el.removeAttribute('data-theme');
                }});
                
                // Restaurar cores padrão
                document.body.style.backgroundColor = '#FFFFFF';
                document.body.style.color = '#333333';
            }}
        </script>
    """, unsafe_allow_html=True)
    
    # Recarregar a página para aplicar o tema
    st.rerun()

# Função para inicializar os dados
def init_app_data():
    """
    Inicializa os dados da aplicação, incluindo a recuperação de dados históricos.
    Chamada uma vez no início da execução.
    
    Esta função foi aprimorada para garantir que dados de usuários nunca sejam perdidos
    durante a inicialização da aplicação.
    """
    # Registrar início da inicialização
    print("INFO: Iniciando processo de inicialização de dados da aplicação")
    
    # Criar diretórios de dados necessários
    ensure_data_dirs()
    
    # Verificar se o usuário está autenticado
    is_user_authenticated = False
    try:
        from app.database.supabase_client import is_authenticated, get_current_user
        is_user_authenticated = is_authenticated()
        if is_user_authenticated:
            user = get_current_user()
            user_id = user.get("id") if user else None
            print(f"INFO: Usuário autenticado: {user_id}")
            
            # Se o usuário estiver autenticado, garantir que o user_id esteja registrado na sessão
            st.session_state["user_id"] = user_id
    except Exception as e:
        print(f"AVISO: Erro ao verificar autenticação do usuário: {e}")
    
    # Verificar se os dados já foram carregados anteriormente nesta sessão
    if "data_loaded" in st.session_state and st.session_state["data_loaded"]:
        print("INFO: Dados já foram carregados nesta sessão")
        # Verificar se não estão vazios
        if "gastos" in st.session_state and st.session_state["gastos"]:
            print(f"INFO: Sessão atual já contém {len(st.session_state['gastos'])} gastos")
            # Já temos dados, não é necessário recarregar
            return
    
    print("INFO: Tentando carregar dados existentes")
    
    # Tentar carregar dados existentes
    dados_carregados = False
    
    # 1. Verificar se há gastos no arquivo
    try:
        if os.path.exists(data_handler.GASTOS_FILE):
            print(f"INFO: Encontrado arquivo de gastos: {data_handler.GASTOS_FILE}")
            with open(data_handler.GASTOS_FILE, 'r', encoding='utf-8') as file:
                gastos = json.load(file)
                if gastos:
                    st.session_state["gastos"] = gastos
                    print(f"INFO: Carregados {len(gastos)} gastos do arquivo para a sessão")
                    dados_carregados = True
    except Exception as e:
        print(f"AVISO: Erro ao carregar gastos do arquivo: {e}")
    
    # 2. Verificar Supabase para usuários autenticados
    if not dados_carregados and is_user_authenticated:
        try:
            from app.database.supabase_client import supabase_load_gastos
            gastos_supabase = supabase_load_gastos()
            if gastos_supabase:
                st.session_state["gastos"] = gastos_supabase
                print(f"INFO: Carregados {len(gastos_supabase)} gastos do Supabase para a sessão")
                dados_carregados = True
        except Exception as e:
            print(f"AVISO: Erro ao carregar gastos do Supabase: {e}")
    
    # 3. Se não encontrou dados em nenhuma fonte e estamos no primeiro uso, inicializar dados de exemplo
    if not dados_carregados:
        print("INFO: Nenhum dado existente encontrado, verificando necessidade de inicialização de exemplo")
        
        # Verificar se este é o primeiro uso
        config = load_config()
        primeiro_uso = config.get("primeiro_uso", True)
        
        if primeiro_uso:
            print("INFO: Inicializando dados de exemplo para primeiro uso")
            try:
                # Não inicializar dados de exemplo para usuários já autenticados
                # para evitar a sobrescrita de dados existentes
                if not is_user_authenticated:
                    init_data.reset_and_initialize_data()
                    print("INFO: Inicialização de dados de exemplo concluída")
                else:
                    print("INFO: Usuário autenticado, pulando inicialização de dados de exemplo")
            except Exception as e:
                print(f"ERRO ao inicializar dados de exemplo: {e}")
    
    # Marcar que os dados foram carregados nesta sessão
    st.session_state["data_loaded"] = True
    
    # Verificar se já inicializamos dados de exemplo anteriormente
    if not "initial_data_loaded" in st.session_state:
        st.session_state["initial_data_loaded"] = True
        print("INFO: Marcado que inicialização de dados foi verificada")
    
    # Normalizar gastos para garantir consistência de tipos
    try:
        normalizar_gastos_existentes()
        print("INFO: Normalização de gastos concluída")
    except Exception as e:
        print(f"AVISO: Erro ao normalizar gastos: {e}")
    
    print("INFO: Processo de inicialização de dados concluído")

if __name__ == "__main__":
    main() 