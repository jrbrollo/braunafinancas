#!/usr/bin/env python3
"""Script simples para iniciar o aplicativo Brauna Finanças em uma porta alternativa."""

import os
import sys
import subprocess

def main():
    """Função principal para iniciar o aplicativo."""
    # Definir porta alternativa
    porta = 8505
    
    print(f"Iniciando Brauna Finanças na porta {porta}...")
    
    # Adicionar diretório atual ao path se necessário
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # Iniciar o streamlit
    os.environ['STREAMLIT_SERVER_PORT'] = str(porta)
    subprocess.run(['streamlit', 'run', 'app/main.py'])

if __name__ == "__main__":
    main() 