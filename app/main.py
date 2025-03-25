import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime

# Adicionar o diretório pai ao path para poder importar módulos personalizados
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

# Importar os módulos de UI
from app.ui.dashboard_page import render_dashboard_page
from app.ui.gastos_page import render_gastos_page
from app.ui.investimentos_page import render_investimentos_page
from app.ui.dividas_page import render_dividas_page
from app.ui.seguros_page import render_seguros_page
# from app.ui.config_page import render_configuracoes_page  # Nome antigo
from app.ui.settings_page import render_settings_page
from app.ui.objetivos_page import render_objetivos_page
from app.ui.auth_page import render_auth_page, logout

# Importar manipulação de dados
from app.data.data_handler import load_config, save_config, initialize_data, ensure_data_dirs

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
    
    # Renderizar o cabeçalho da barra lateral com o logo
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">
            <img src="https://img.icons8.com/color/48/null/money-bag.png" style="width: 36px; height: 36px; margin-bottom: 8px;">
            <div>Brauna Finanças</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Informações do usuário na barra lateral
    st.sidebar.markdown(f"""
    <div style="padding: 0 10px 20px 10px; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1);">
        <div style="display: flex; align-items: center;">
            <div style="width: 40px; height: 40px; background-color: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                <span style="font-size: 20px;">👤</span>
            </div>
            <div>
                <div style="font-weight: 600; color: white; font-size: 14px;">{nome}</div>
                <div style="font-size: 12px; color: rgba(255,255,255,0.7);">{email}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botões de navegação
    if st.sidebar.button("📊 Dashboard", key="nav_dashboard"):
        set_pagina("dashboard")
    
    if st.sidebar.button("💸 Controle de Gastos", key="nav_gastos"):
        set_pagina("gastos")
    
    if st.sidebar.button("📈 Investimentos", key="nav_investimentos"):
        set_pagina("investimentos")
    
    if st.sidebar.button("🎯 Objetivos", key="nav_objetivos"):
        set_pagina("objetivos")
    
    if st.sidebar.button("💳 Dívidas", key="nav_dividas"):
        set_pagina("dividas")
    
    if st.sidebar.button("🔒 Seguros", key="nav_seguros"):
        set_pagina("seguros")
    
    # Linha separadora
    st.sidebar.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # Botões de configuração e logout
    if st.sidebar.button("⚙️ Configurações", key="nav_settings"):
        set_pagina("settings")
    
    if st.sidebar.button("🚪 Sair", key="nav_logout"):
        logout()
        st.rerun()

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
        
    # Inicializar dados de exemplo se for o primeiro uso (somente após autenticação)
    dados_inicializados = initialize_data()
    
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

if __name__ == "__main__":
    main() 