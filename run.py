#!/usr/bin/env python3
"""
Script para inicializar e executar o aplicativo Brauna Finanças.
Compatível com execução local e no Streamlit Cloud.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def is_streamlit_cloud():
    """
    Verifica se o app está rodando no Streamlit Cloud.
    """
    return os.environ.get("STREAMLIT_SHARING", "") == "true" or os.environ.get("STREAMLIT_CLOUD", "") == "true"

def check_dependencies():
    """
    Verifica se todas as dependências necessárias estão instaladas.
    
    Returns:
        bool: True se todas as dependências estão instaladas, False caso contrário
    """
    # No Streamlit Cloud, as dependências são instaladas automaticamente
    if is_streamlit_cloud():
        return True
        
    print("Verificando dependências...")
    dependencies = [
        "streamlit", "pandas", "numpy", "plotly", "matplotlib",
        "pyyaml", "pydantic", "pillow"
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            # Tentativa alternativa de importação para evitar falsos negativos
            try:
                if dep == "pyyaml":
                    import yaml
                    print(f"✓ {dep} (como yaml)")
                    continue
                elif dep == "pillow":
                    from PIL import Image
                    print(f"✓ {dep} (como PIL)")
                    continue
                # Se chegou aqui, realmente está faltando
                missing.append(dep)
                print(f"✗ {dep}")
            except ImportError:
                missing.append(dep)
                print(f"✗ {dep}")
    
    if missing:
        print("\nDependências ausentes encontradas.")
        # Não impedir a execução por causa de dependências
        return True
    else:
        print("\nTodas as dependências estão instaladas.")
        return True

def install_dependencies():
    """
    Instala todas as dependências necessárias.
    
    Returns:
        bool: True se a instalação foi bem-sucedida, False caso contrário
    """
    # No Streamlit Cloud, as dependências são instaladas automaticamente
    if is_streamlit_cloud():
        return True
        
    print("Instalando dependências...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("Dependências instaladas com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências: {e}")
        return False

def initialize_data():
    """
    Inicializa o banco de dados com dados de exemplo.
    
    Returns:
        bool: True se a inicialização foi bem-sucedida, False caso contrário
    """
    print("Inicializando banco de dados com dados de exemplo...")
    try:
        from app.data.init_data import reset_and_initialize_data
        reset_and_initialize_data()
        print("Banco de dados inicializado com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        return False

def run_application():
    """
    Executa a aplicação Streamlit.
    
    Returns:
        bool: True se a aplicação foi executada com sucesso, False caso contrário
    """
    # No Streamlit Cloud, a aplicação é executada automaticamente
    if is_streamlit_cloud():
        # Apenas inicializar os dados
        initialize_data()
        # Importa diretamente o app/main.py
        import app.main
        return True
        
    print("Iniciando aplicação Brauna Finanças...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app/main.py"
        ])
        return True
    except Exception as e:
        print(f"Erro ao executar aplicação: {e}")
        return False

def main():
    """
    Função principal que analisa os argumentos de linha de comando e executa
    as funções apropriadas.
    """
    # Se estiver no Streamlit Cloud, ir direto para a execução da aplicação
    if is_streamlit_cloud():
        run_application()
        return
        
    parser = argparse.ArgumentParser(
        description="Script para executar o aplicativo Brauna Finanças")
    
    parser.add_argument("--check", action="store_true",
                        help="Verificar dependências")
    parser.add_argument("--install", action="store_true",
                        help="Instalar dependências")
    parser.add_argument("--init", action="store_true",
                        help="Inicializar banco de dados")
    parser.add_argument("--run", action="store_true",
                        help="Executar aplicação")
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi passado, executar a aplicação
    if not (args.check or args.install or args.init or args.run):
        args.run = True
    
    # Verificar dependências
    if args.check:
        check_dependencies()
    
    # Instalar dependências
    if args.install:
        install_dependencies()
    
    # Inicializar banco de dados
    if args.init:
        initialize_data()
    
    # Executar aplicação
    if args.run:
        run_application()

if __name__ == "__main__":
    main() 