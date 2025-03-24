import streamlit as st

st.title("Teste do Streamlit")
st.write("Se você está vendo esta mensagem, o Streamlit está funcionando corretamente!")

# Adicionar um botão de teste
if st.button("Clique Aqui"):
    st.success("Botão clicado com sucesso!") 