#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}====================================${NC}"
echo -e "${CYAN}  Sistema de Propaganda - Cliente${NC}"
echo -e "${CYAN}====================================${NC}"
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERRO] Python3 não encontrado!${NC}"
    echo "Por favor, instale Python 3.8 ou superior"
    echo "Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
    echo "Fedora/RHEL: sudo dnf install python3 python3-pip"
    echo "Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo -e "${GREEN}[INFO] Python encontrado: $(python3 --version)${NC}"
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[INFO] Criando ambiente virtual...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERRO] Falha ao criar ambiente virtual!${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] Ambiente virtual criado!${NC}"
    echo ""
fi

# Ativar ambiente virtual
echo -e "${YELLOW}[INFO] Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Instalar/Atualizar dependências
echo -e "${YELLOW}[INFO] Instalando dependências...${NC}"
python -m pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERRO] Falha ao instalar dependências!${NC}"
    echo "Você pode precisar instalar dependências do sistema:"
    echo "Ubuntu/Debian: sudo apt-get install python3-opencv"
    deactivate
    exit 1
fi
echo -e "${GREEN}[OK] Dependências instaladas!${NC}"
echo ""

# Executar o cliente
echo -e "${GREEN}[INFO] Iniciando cliente...${NC}"
echo -e "${CYAN}====================================${NC}"
echo ""
python client.py "$@"

# Capturar código de saída
EXIT_CODE=$?

# Desativar ambiente virtual
deactivate

# Retornar código de saída
exit $EXIT_CODE
