@echo off
REM ===============================================
REM Script para iniciar Redis via Docker
REM CG.BookStore v3 - Cache System
REM ===============================================

echo.
echo ===============================================
echo  CG.BookStore v3 - Iniciando Redis Cache
echo ===============================================
echo.

REM Verificar se Docker está rodando
docker info >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Docker nao esta rodando!
    echo.
    echo Por favor, inicie o Docker Desktop e tente novamente.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker detectado e rodando
echo.

REM Verificar se o container já existe
docker ps -a --filter "name=cgbookstore_redis" --format "{{.Names}}" | findstr "cgbookstore_redis" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Container Redis ja existe

    REM Verificar se está rodando
    docker ps --filter "name=cgbookstore_redis" --format "{{.Names}}" | findstr "cgbookstore_redis" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [OK] Redis ja esta rodando!
        echo.
        echo Testando conexao...
        docker exec cgbookstore_redis redis-cli ping
        echo.
        echo ===============================================
        echo  Redis pronto para uso!
        echo  URL: redis://127.0.0.1:6379/1
        echo ===============================================
        echo.
        timeout /t 3 >nul
        exit /b 0
    ) else (
        echo [INFO] Iniciando container existente...
        docker start cgbookstore_redis
    )
) else (
    echo [INFO] Criando e iniciando novo container Redis...
    docker-compose up -d redis
)

echo.
echo Aguardando Redis ficar pronto...
timeout /t 5 >nul

REM Testar conexão
echo.
echo Testando conexao...
docker exec cgbookstore_redis redis-cli ping >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Redis conectado com sucesso!
    echo.
    echo ===============================================
    echo  Redis pronto para uso!
    echo  URL: redis://127.0.0.1:6379/1
    echo  Container: cgbookstore_redis
    echo ===============================================
    echo.
    echo Para parar o Redis: docker stop cgbookstore_redis
    echo Para ver logs: docker logs -f cgbookstore_redis
    echo.
) else (
    echo [ERRO] Falha ao conectar no Redis
    echo.
    echo Verificando logs...
    docker logs cgbookstore_redis --tail 20
    echo.
    pause
    exit /b 1
)

timeout /t 3 >nul
