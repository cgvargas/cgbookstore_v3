@echo off
REM Script para limpar cache do Python no Windows

echo Limpando cache do Python...

REM Remover __pycache__ recursivamente
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM Remover arquivos .pyc
del /s /q *.pyc 2>nul

echo Cache limpo!
echo.
echo Agora execute: python manage.py test_gemini
