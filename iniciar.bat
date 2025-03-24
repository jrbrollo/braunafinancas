@echo off
echo Iniciando o Brauna Finanças...
echo.
echo Verificando dependencias...
py run.py --check

echo.
echo Inicializando dados...
py run.py --init

echo.
echo Iniciando aplicacao...
py -m streamlit run app/main.py --server.port=8505

pause 