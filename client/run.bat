@echo off
title Sistema de Propaganda - Cliente
color 0A

echo ====================================
echo   Sistema de Propaganda - Cliente
echo ====================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8 ou superior de https://www.python.org/
    echo.
    pause
    exit /b 1
)

echo [INFO] Python encontrado!
echo.

REM Verificar se o ambiente virtual existe
if not exist "venv\" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado!
    echo.
)

REM Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar/Atualizar dependências
echo [INFO] Instalando dependencias...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas!
echo.

REM Executar o cliente
echo [INFO] Iniciando cliente...
echo ====================================
echo.
python client.py %*

REM Manter janela aberta em caso de erro
if errorlevel 1 (
    echo.
    echo [ERRO] O cliente encerrou com erro!
    pause
)

deactivate
