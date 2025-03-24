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

# Importar manipulação de dados
from app.data.data_handler import load_config, save_config, initialize_data, ensure_data_dirs

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Brauna Finanças - Finanças Pessoais",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    # Carregar a fonte Inter do Google Fonts
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    # Aplicar a fonte ao aplicativo inteiro
    st.markdown("""
    <style>
    html, body, [class*="st-"], .stApp {
        font-family: 'Inter', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Aplicar tema escuro se necessário
    if tema == "escuro":
        st.markdown("""
        <style>
        body {
            background-color: var(--background, #121212) !important;
            color: var(--text-primary, #E0E0E0) !important;
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

def main():
    """
    Função principal que inicializa a aplicação
    """
    # Garantir que diretórios de dados existam
    ensure_data_dirs()
    
    # Inicializar dados de exemplo se for o primeiro uso
    dados_inicializados = initialize_data()
    
    # Carregar configuração
    config = load_config()
    
    # Inicializar tema se não existir
    if "tema" not in st.session_state:
        st.session_state.tema = config.get("tema", "claro")
    
    # Aplicar estilos após inicializar o tema
    apply_custom_style(st.session_state.tema)
    
    # Configurar estilo padrão para gráficos
    configure_plotly_default_style(st.session_state.tema)
    
    # Aplicar tema ao body
    if st.session_state.tema == "escuro":
        st.markdown("""
        <script>
        document.body.setAttribute('data-theme', 'dark');
        </script>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <script>
        document.body.removeAttribute('data-theme');
        </script>
        """, unsafe_allow_html=True)
    
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
        
        # Separador
        st.markdown('<div style="height: 1px; background: var(--border-color); margin: 0.5rem 0 1.5rem 0;"></div>', unsafe_allow_html=True)
        
        # Botões de navegação com estilo mais moderno
        nav_items = [
            {"icon": "dashboard", "label": "Dashboard", "id": "dashboard", "help": "Visão geral das suas finanças"},
            {"icon": "expenses", "label": "Controle de Gastos", "id": "gastos", "help": "Gerencie suas despesas"},
            {"icon": "investments", "label": "Investimentos", "id": "investimentos", "help": "Acompanhe seus investimentos"},
            {"icon": "goals", "label": "Objetivos", "id": "objetivos", "help": "Defina e acompanhe seus objetivos financeiros"},
            {"icon": "debts", "label": "Dívidas", "id": "dividas", "help": "Controle suas dívidas"},
            {"icon": "insurance", "label": "Seguros", "id": "seguros", "help": "Gerencie seus seguros"},
        ]
        
        for item in nav_items:
            # Determinar se o botão está ativo
            is_active = st.session_state.pagina_atual == item["id"]
            button_class = "active" if is_active else ""
            
            # Carregar o ícone SVG
            icon_svg = load_svg(item["icon"])
            
            # Usando markdown para estilizar o botão
            if st.markdown(f"""
            <div class="nav-item {button_class}" onclick="changePageTo('{item['id']}')" title="{item['help']}">
                <span class="nav-icon">{icon_svg}</span>
                <span>{item['label']}</span>
            </div>
            """, unsafe_allow_html=True):
                pass  # Necessário para evitar erro de sintaxe
        
        # Separador antes das configurações
        st.markdown('<div style="height: 1px; background: var(--border-color); margin: 1.5rem 0;"></div>', unsafe_allow_html=True)
        
        # Configurações
        settings_icon = load_svg("settings")
        if st.markdown(f"""
        <div class="nav-item {'active' if st.session_state.pagina_atual == 'config' else ''}" onclick="changePageTo('config')" title="Ajuste as configurações do app">
            <span class="nav-icon">{settings_icon}</span>
            <span>Configurações</span>
        </div>
        """, unsafe_allow_html=True):
            pass
        
        # Toggle para tema claro/escuro
        theme_icon = load_svg("theme")
        tema_label = "Tema Escuro" if st.session_state.tema == "claro" else "Tema Claro"
        
        if st.markdown(f"""
        <div class="nav-item" onclick="toggleTheme()" title="Alternar entre tema claro e escuro">
            <span class="nav-icon">{theme_icon}</span>
            <span>{tema_label}</span>
        </div>
        """, unsafe_allow_html=True):
            pass
        
        # JavaScript para navegação e tema
        st.markdown("""
        <script>
            function changePageTo(pageId) {
                // Alterar o estado da página e recarregar
                const key = new Date().getTime();
                sessionStorage.setItem('currentPage', pageId);
                sessionStorage.setItem('pageChange', key);
                window.location.reload();
            }
            
            function toggleTheme() {
                // Alternar tema e recarregar
                const currentTheme = sessionStorage.getItem('theme') || 'claro';
                const newTheme = currentTheme === 'claro' ? 'escuro' : 'claro';
                sessionStorage.setItem('theme', newTheme);
                sessionStorage.setItem('themeChange', new Date().getTime());
                window.location.reload();
            }
            
            // Verificar mudanças de página e tema ao carregar
            window.addEventListener('load', function() {
                const pageChange = sessionStorage.getItem('pageChange');
                if (pageChange) {
                    const page = sessionStorage.getItem('currentPage');
                    if (page) {
                        // Limpar os flags
                        sessionStorage.removeItem('pageChange');
                        
                        // Comunicar ao Streamlit
                        setTimeout(function() {
                            const pageInput = window.parent.document.querySelector('[data-testid="stForm"] input[aria-label="currentPage"]');
                            if (pageInput) {
                                pageInput.value = page;
                                pageInput.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        }, 500);
                    }
                }
                
                const themeChange = sessionStorage.getItem('themeChange');
                if (themeChange) {
                    const theme = sessionStorage.getItem('theme');
                    if (theme) {
                        // Limpar os flags
                        sessionStorage.removeItem('themeChange');
                        
                        // Comunicar ao Streamlit
                        setTimeout(function() {
                            const themeInput = window.parent.document.querySelector('[data-testid="stForm"] input[aria-label="currentTheme"]');
                            if (themeInput) {
                                themeInput.value = theme;
                                themeInput.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        }, 500);
                    }
                }
            });
        </script>
        """, unsafe_allow_html=True)
        
        # Campos ocultos para comunicação com JavaScript
        with st.form(key="nav_form", clear_on_submit=False):
            current_page = st.text_input("currentPage", value="", label_visibility="collapsed")
            current_theme = st.text_input("currentTheme", value="", label_visibility="collapsed")
            submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)
            st.markdown('<style>div[data-testid="stForm"] {border: none !important; padding: 0 !important; margin: 0 !important;} div[data-testid="stForm"] button {display: none !important;}</style>', unsafe_allow_html=True)
        
        if current_page and current_page != st.session_state.pagina_atual:
            set_pagina(current_page)
            st.rerun()
            
        if current_theme and current_theme != st.session_state.tema:
            toggle_tema()
            st.rerun()
        
        # Rodapé
        st.markdown("""
        <div style="position: absolute; bottom: 1rem; left: 0; right: 0; text-align: center; padding: 1rem; font-size: 0.75rem; color: var(--text-secondary);">
            <p style="margin: 0;">Brauna Finanças v1.0.0</p>
            <p style="margin: 0;">© 2025 Brauna Finanças</p>
        </div>
        """, unsafe_allow_html=True)
    
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
    elif pagina_atual == "config":
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