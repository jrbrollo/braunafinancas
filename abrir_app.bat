@echo off
echo Iniciando Brauna Financas...
echo.

:: Verificar se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python nao foi encontrado! Por favor, instale o Python 3.8 ou superior.
    echo Visite: https://www.python.org/downloads/
    pause
    exit /b
)

:: Verificar dependências e inicializar banco de dados
echo Verificando dependencias...
python run.py --check

echo.
echo Inicializando banco de dados...
python run.py --init

echo.
echo Iniciando aplicacao...
echo Pressione Ctrl+C para encerrar o aplicativo quando desejar.
echo.

:: Iniciar a aplicação
python run.py --run

pause 