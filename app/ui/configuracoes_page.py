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
    carregar_configuracao, 
    salvar_configuracao,
    carregar_dados_usuario,
    salvar_dados_usuario,
    carregar_despesas,
    salvar_despesas,
    carregar_investimentos,
    salvar_investimentos,
    carregar_dividas,
    salvar_dividas,
    carregar_seguros,
    salvar_seguros
)

def formatar_moeda(valor):
    """Formata um valor para o formato de moeda brasileira."""
    if valor is None:
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')

def exportar_dados():
    """Exporta todos os dados do usuário para um arquivo JSON."""
    dados_export = {
        "dados_usuario": carregar_dados_usuario(),
        "despesas": carregar_despesas(),
        "investimentos": carregar_investimentos(),
        "dividas": carregar_dividas(),
        "seguros": carregar_seguros(),
        "configuracao": carregar_configuracao(),
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
        salvar_dados_usuario(dados["dados_usuario"])
        salvar_despesas(dados["despesas"])
        salvar_investimentos(dados["investimentos"])
        salvar_dividas(dados["dividas"])
        salvar_seguros(dados["seguros"])
        salvar_configuracao(dados["configuracao"])
        
        return True
    except Exception as e:
        st.error(f"Erro ao importar dados: {str(e)}")
        return False

def render_configuracoes_page():
    """Renderiza a página de configurações."""
    st.title("⚙️ Configurações")
    
    # Carregar configurações atuais
    config = carregar_configuracao()
    
    tabs = st.tabs(["Perfil do Usuário", "Aparência", "Backup e Restauração", "Sobre"])
    
    # Tab 1: Perfil do Usuário
    with tabs[0]:
        st.subheader("Perfil do Usuário")
        
        # Carregar dados do usuário
        dados_usuario = carregar_dados_usuario()
        nome = dados_usuario.get("nome", "")
        email = dados_usuario.get("email", "")
        renda_mensal = dados_usuario.get("renda_mensal", 0)
        
        with st.form("formulario_perfil"):
            nome_input = st.text_input("Nome", value=nome)
            email_input = st.text_input("Email", value=email)
            renda_input = st.number_input("Renda Mensal", 
                                          min_value=0.0, 
                                          value=float(renda_mensal),
                                          step=100.0,
                                          format="%.2f")
            
            meta_economias = st.slider(
                "Meta de Economias (% da renda)",
                min_value=5,
                max_value=50,
                value=config.get("meta_economias", 20),
                step=5
            )
            
            if st.form_submit_button("Salvar Perfil"):
                # Atualizar dados do usuário
                novos_dados = {
                    "nome": nome_input,
                    "email": email_input,
                    "renda_mensal": renda_input
                }
                salvar_dados_usuario(novos_dados)
                
                # Atualizar configuração
                config["meta_economias"] = meta_economias
                salvar_configuracao(config)
                
                st.success("Perfil atualizado com sucesso!")
    
    # Tab 2: Aparência
    with tabs[1]:
        st.subheader("Aparência")
        
        with st.form("formulario_aparencia"):
            tema_default = config.get("tema_padrao", "light")
            tema = st.radio(
                "Tema Padrão",
                options=["light", "dark"],
                index=0 if tema_default == "light" else 1,
                horizontal=True,
                format_func=lambda x: "Claro" if x == "light" else "Escuro"
            )
            
            cor_primaria = st.color_picker(
                "Cor Primária", 
                value=config.get("cor_primaria", "#0066CC")
            )
            
            mostrar_dicas = st.checkbox(
                "Mostrar Dicas e Tutoriais", 
                value=config.get("mostrar_dicas", True)
            )
            
            if st.form_submit_button("Salvar Aparência"):
                config["tema_padrao"] = tema
                config["cor_primaria"] = cor_primaria
                config["mostrar_dicas"] = mostrar_dicas
                salvar_configuracao(config)
                st.success("Configurações de aparência atualizadas!")
                
        st.info("As alterações de tema terão efeito após recarregar a aplicação.")
    
    # Tab 3: Backup e Restauração
    with tabs[2]:
        st.subheader("Backup e Restauração")
        
        st.info("Faça backup regularmente para evitar perda de dados.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Backup de Dados")
            if st.button("Gerar Backup"):
                dados_json = exportar_dados()
                data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"brauna_backup_{data_atual}.json"
                
                st.code(dados_json[:100] + "... (dados truncados)")
                st.markdown(get_download_link(dados_json, nome_arquivo, 
                                              "📥 Baixar Arquivo de Backup"), unsafe_allow_html=True)
                st.success("Backup gerado com sucesso!")
        
        with col2:
            st.markdown("### Restaurar Dados")
            st.warning("A restauração substituirá todos os dados atuais.")
            
            arquivo_upload = st.file_uploader("Selecione o arquivo de backup", type=["json"])
            
            if arquivo_upload is not None:
                if st.button("Restaurar Dados"):
                    dados_json = arquivo_upload.getvalue().decode("utf-8")
                    if importar_dados(dados_json):
                        st.success("Dados restaurados com sucesso!")
                    else:
                        st.error("Falha ao restaurar dados. Verifique o formato do arquivo.")
    
    # Tab 4: Sobre
    with tabs[3]:
        st.subheader("Sobre o Brauna Finanças")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("app/static/brauna_logo.png", width=150)
        
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