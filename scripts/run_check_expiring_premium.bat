@echo off
REM Script para executar verificacao de Premium expirando
REM Usado pelo Task Scheduler do Windows

echo ============================================================
echo VERIFICACAO DE PREMIUM EXPIRANDO
echo Data/Hora: %date% %time%
echo ============================================================
echo.

REM Ativar ambiente virtual
cd /d "C:\ProjectsDjango\cgbookstore_v3"
call .venv\Scripts\activate.bat

REM Executar comando
python manage.py check_expiring_premium

REM Gravar resultado
echo.
echo ============================================================
echo EXECUCAO CONCLUIDA: %date% %time%
echo ============================================================

REM Desativar ambiente virtual
deactivate
