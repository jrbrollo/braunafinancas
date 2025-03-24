# Guia de Instalação - Brauna Finanças

Este documento descreve os passos necessários para instalar e executar o Brauna Finanças em diferentes sistemas operacionais.

## Requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes do Python)
- Acesso à internet para baixar as dependências

## Windows

1. **Instalação do Python**:
   - Baixe o instalador do Python em [python.org](https://www.python.org/downloads/)
   - Execute o instalador e marque a opção "Add Python to PATH"
   - Siga as instruções de instalação

2. **Instalação do Brauna Finanças**:
   - Baixe o código-fonte ou clone o repositório:
     ```
     git clone https://github.com/braunafinancas/brauna-financas.git
     cd brauna-financas
     ```

3. **Instalação de Dependências**:
   - Execute o comando:
     ```
     pip install -r requirements.txt
     ```

4. **Inicialização de Dados (Opcional)**:
   - Se quiser iniciar com dados de exemplo:
     ```
     python -c "from app.data.init_data import reset_and_initialize_data; reset_and_initialize_data()"
     ```

5. **Execução**:
   - Execute o arquivo batch:
     ```
     abrir_app.bat
     ```
   - Ou use o comando:
     ```
     streamlit run app/main.py
     ```

## macOS e Linux

1. **Instalação do Python**:
   - A maioria das distribuições Linux e macOS já vem com Python instalado
   - Para confirmar, abra o terminal e digite:
     ```
     python3 --version
     ```
   - Se não estiver instalado ou for uma versão antiga, instale pelo gerenciador de pacotes:
     - **Ubuntu/Debian**:
       ```
       sudo apt update
       sudo apt install python3 python3-pip
       ```
     - **macOS** (usando Homebrew):
       ```
       brew install python
       ```

2. **Instalação do Brauna Finanças**:
   - Clone o repositório:
     ```
     git clone https://github.com/braunafinancas/brauna-financas.git
     cd brauna-financas
     ```

3. **Instalação de Dependências**:
   - Use o pip:
     ```
     pip3 install -r requirements.txt
     ```

4. **Inicialização de Dados (Opcional)**:
   - Execute:
     ```
     python3 -c "from app.data.init_data import reset_and_initialize_data; reset_and_initialize_data()"
     ```

5. **Execução**:
   - Inicie o aplicativo:
     ```
     streamlit run app/main.py
     ```

## Solucionando Problemas

Se encontrar problemas durante a instalação ou execução, verifique:

1. Se o Python e o pip estão corretamente instalados
2. Se todas as dependências foram instaladas
3. Se está no diretório correto do projeto

Para ajuda adicional, consulte a documentação ou entre em contato. 