"""
Módulo da página de configurações do sistema Brauna Finanças.
Permite gerenciar temas, backup de dados, e configurações do usuário.
"""

import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import base64

from app.data.data_handler import (
    load_config, 
    save_config,
    load_user_data,
    save_user_data,
    load_gastos,
    save_gastos,
    load_investimentos,
    save_investimentos,
    load_dividas,
    save_dividas,
    load_seguros,
    save_seguros
)

# Importar função de obtenção do usuário atual
from app.database.supabase_client import get_current_user

def formatar_moeda(valor):
    """Formata um valor para o formato de moeda brasileira."""
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def exportar_dados():
    """Exporta todos os dados do usuário para um arquivo JSON."""
    dados_export = {
        "dados_usuario": load_user_data(),
        "despesas": load_gastos(),
        "investimentos": load_investimentos(),
        "dividas": load_dividas(),
        "seguros": load_seguros(),
        "configuracao": load_config(),
        "data_exportacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return json.dumps(dados_export, indent=4, ensure_ascii=False)

def get_download_link(dados, filename, text):
    """Gera um link para download de dados."""
    b64 = base64.b64encode(dados.encode()).decode()
    href = f'data:file/txt;base64,{b64}'
    return f'<a href="{href}" download="{filename}">{text}</a>'

def importar_dados(dados_json):
    """Importa dados do usuário a partir de um arquivo JSON."""
    try:
        dados = json.loads(dados_json)
        
        # Validar estrutura básica dos dados
        campos_obrigatorios = ["dados_usuario", "despesas", "investimentos", 
                              "dividas", "seguros", "configuracao"]
        
        for campo in campos_obrigatorios:
            if campo not in dados:
                st.error(f"Arquivo inválido! Campo '{campo}' não encontrado.")
                return False
        
        # Salvar dados
        save_user_data(dados["dados_usuario"])
        save_gastos(dados["despesas"])
        save_investimentos(dados["investimentos"])
        save_dividas(dados["dividas"])
        save_seguros(dados["seguros"])
        save_config(dados["configuracao"])
        
        return True
    except Exception as e:
        st.error(f"Erro ao importar dados: {str(e)}")
        return False

def render_settings_page():
    """
    Renderiza a página de configurações do aplicativo.
    """
    st.header("Configurações", anchor=False)
    
    st.markdown("### Configurações do Aplicativo")
    
    # Dados do usuário atual
    dados_usuario = load_user_data()
    
    # Configuração do tema
    tema_label = "Tema do Aplicativo"
    tema_options = ["claro", "escuro"]
    tema_labels = {"claro": "Claro", "escuro": "Escuro"}
    
    # Verificar se o tema atual existe na lista de opções
    tema_atual = st.session_state.tema if "tema" in st.session_state else "claro"
    if tema_atual not in tema_options:
        # Converter temas em inglês para português se necessário
        if tema_atual == "light":
            tema_atual = "claro"
        elif tema_atual == "dark":
            tema_atual = "escuro"
    
    col1, col2 = st.columns([1, 3])
    with col1:
        tema_selecionado = st.selectbox(
            tema_label,
            options=tema_options,
            format_func=lambda x: tema_labels.get(x, x),
            index=tema_options.index(tema_atual)
        )
    
    if tema_selecionado != tema_atual:
        st.session_state.tema = tema_selecionado
        st.rerun()
    
    # Informações pessoais
    st.markdown("### Informações Pessoais")
    
    # Inicializar com valores padrão ou existentes
    if dados_usuario is None:
        dados_usuario = {}
    
    nome = dados_usuario.get("nome", "")
    email = dados_usuario.get("email", "")
    
    with st.form("configuracoes_form"):
        nome_input = st.text_input("Nome", value=nome)
        email_readonly = st.text_input("Email", value=email, disabled=True)
        
        # Renda mensal
        renda_mensal = dados_usuario.get("renda_mensal", 0.0)
        
        renda_mensal_input = st.number_input(
            "Renda Mensal",
            min_value=0.0,
            value=renda_mensal,
            step=100.0,
            format="%.2f",
            help="Valor total da sua renda mensal (salários, investimentos, etc.)"
        )
        
        # Botão para salvar configurações
        submitted = st.form_submit_button("Salvar Configurações")
        
        if submitted:
            # Atualizar os dados
            dados_usuario["nome"] = nome_input
            dados_usuario["email"] = email
            dados_usuario["renda_mensal"] = renda_mensal_input
            
            try:
                # Salvar os dados
                if "user_id" not in dados_usuario and get_current_user():
                    dados_usuario["user_id"] = get_current_user()["id"]
                
                save_user_data(dados_usuario)
                st.success("Configurações salvas com sucesso!")
                
                # Atualizar a sessão
                if "user_data" in st.session_state:
                    st.session_state.user_data.update(dados_usuario)
                
            except Exception as e:
                st.error(f"Erro ao salvar configurações: {e}")
    
    # Opções de backup e exportação
    st.markdown("### Backup e Exportação de Dados")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Exportar Todos os Dados"):
            dados_exportados = exportar_dados()
            
            if dados_exportados:
                st.success("Dados exportados com sucesso!")
                # Criar um download para o arquivo JSON
                st.download_button(
                    label="Baixar Arquivo de Backup",
                    data=dados_exportados,
                    file_name=f"brauna_financas_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            else:
                st.error("Erro ao exportar dados. Verifique os logs.")
    
    with col2:
        uploaded_file = st.file_uploader("Importar Backup", type=["json"])
        
        if uploaded_file:
            try:
                backup_content = uploaded_file.read().decode()
                
                if st.button("Restaurar Backup"):
                    if importar_dados(backup_content):
                        st.success("Backup restaurado com sucesso!")
                    else:
                        st.error("Erro ao restaurar backup. Verifique os logs.")
            except Exception as e:
                st.error(f"Arquivo de backup inválido: {str(e)}")
    
    # Opções de exclusão de conta
    st.markdown("### Danger Zone")
    
    with st.expander("⚠️ Excluir Conta e Dados"):
        st.warning(
            "Esta ação excluirá permanentemente sua conta e todos os dados associados. "
            "Esta ação não pode ser desfeita!"
        )
        
        confirmar_exclusao = st.text_input(
            "Digite 'EXCLUIR' para confirmar a exclusão da conta",
            help="Esta ação é irreversível"
        )
        
        if st.button("Excluir Minha Conta Permanentemente") and confirmar_exclusao == "EXCLUIR":
            # Lógica para excluir a conta
            # TODO: Implementar exclusão de conta no Supabase
            st.error("Funcionalidade ainda não implementada.")
            
            # Logout após exclusão
            # logout()

    # Sobre o aplicativo
    st.markdown("### Sobre o Brauna Finanças")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div style="font-size: 80px; text-align: center;">💰</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Brauna Finanças - Seu Gerenciador Financeiro Pessoal")
        st.markdown("Versão 1.0.0")
        st.markdown("Desenvolvido com ❤️ para ajudar no controle financeiro.")
    
    st.markdown("---")
    st.markdown("### Recursos")
    
    recursos = [
        "✅ Dashboard financeiro completo",
        "✅ Controle detalhado de gastos",
        "✅ Gestão de investimentos",
        "✅ Acompanhamento de dívidas",
        "✅ Gerenciamento de seguros",
        "✅ Backup e restauração de dados"
    ]
    
    for recurso in recursos:
        st.markdown(recurso)
    
    st.markdown("---")
    st.markdown("### Licença")
    st.markdown("Este software é distribuído sob a licença MIT.")
    st.markdown("Para mais informações, consulte o arquivo LICENSE incluído no projeto.") 