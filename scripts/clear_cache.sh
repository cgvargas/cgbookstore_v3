#!/bin/bash
# Script para limpar cache do Python no Linux/Mac

echo "Limpando cache do Python..."

# Remover __pycache__ recursivamente
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Remover arquivos .pyc
find . -type f -name "*.pyc" -delete 2>/dev/null

echo "Cache limpo!"
echo ""
echo "Agora execute: python manage.py test_gemini"
