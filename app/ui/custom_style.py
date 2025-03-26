"""
Módulo para carregar estilos personalizados do aplicativo.
"""
import streamlit as st
from pathlib import Path

def load_custom_styles():
    """
    Carrega os estilos CSS personalizados do aplicativo.
    """
    # Obter o caminho do arquivo CSS
    css_file = Path(__file__).parent / "custom_style.css"
    
    # Ler o conteúdo do arquivo CSS
    with open(css_file, 'r', encoding='utf-8') as f:
        css = f.read()
    
    # Aplicar os estilos
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True) 