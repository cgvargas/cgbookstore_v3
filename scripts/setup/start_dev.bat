@echo off
REM ===============================================
REM Script para iniciar ambiente de desenvolvimento
REM CG.BookStore v3 - Redis + Django
REM ===============================================

echo.
echo ===============================================
echo  CG.BookStore v3 - Ambiente de Desenvolvimento
echo ===============================================
echo.

REM Iniciar Redis primeiro
call start_redis.bat
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Falha ao iniciar Redis. Abortando...
    pause
    exit /b 1
)

echo.
echo ===============================================
echo  Iniciando servidor Django...
echo ===============================================
echo.

REM Aguardar um momento antes de iniciar Django
timeout /t 2 >nul

REM Iniciar Django
python manage.py runserver

REM Se Django for encerrado, informar
echo.
echo ===============================================
echo  Servidor Django encerrado
echo ===============================================
echo.
echo Redis ainda esta rodando em background.
echo Para parar o Redis: docker stop cgbookstore_redis
echo.
pause
