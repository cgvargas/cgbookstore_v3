#!/bin/bash
# ===============================================
# Script para iniciar Redis via Docker
# CG.BookStore v3 - Cache System
# ===============================================

echo ""
echo "==============================================="
echo " CG.BookStore v3 - Iniciando Redis Cache"
echo "==============================================="
echo ""

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "[ERRO] Docker não está rodando!"
    echo ""
    echo "Por favor, inicie o Docker e tente novamente."
    echo ""
    exit 1
fi

echo "[OK] Docker detectado e rodando"
echo ""

# Verificar se o container já existe
if docker ps -a --filter "name=cgbookstore_redis" --format "{{.Names}}" | grep -q "cgbookstore_redis"; then
    echo "[INFO] Container Redis já existe"

    # Verificar se está rodando
    if docker ps --filter "name=cgbookstore_redis" --format "{{.Names}}" | grep -q "cgbookstore_redis"; then
        echo "[OK] Redis já está rodando!"
        echo ""
        echo "Testando conexão..."
        docker exec cgbookstore_redis redis-cli ping
        echo ""
        echo "==============================================="
        echo " Redis pronto para uso!"
        echo " URL: redis://127.0.0.1:6379/1"
        echo "==============================================="
        echo ""
        exit 0
    else
        echo "[INFO] Iniciando container existente..."
        docker start cgbookstore_redis
    fi
else
    echo "[INFO] Criando e iniciando novo container Redis..."
    docker-compose up -d redis
fi

echo ""
echo "Aguardando Redis ficar pronto..."
sleep 5

# Testar conexão
echo ""
echo "Testando conexão..."
if docker exec cgbookstore_redis redis-cli ping > /dev/null 2>&1; then
    echo "[OK] Redis conectado com sucesso!"
    echo ""
    echo "==============================================="
    echo " Redis pronto para uso!"
    echo " URL: redis://127.0.0.1:6379/1"
    echo " Container: cgbookstore_redis"
    echo "==============================================="
    echo ""
    echo "Para parar o Redis: docker stop cgbookstore_redis"
    echo "Para ver logs: docker logs -f cgbookstore_redis"
    echo ""
else
    echo "[ERRO] Falha ao conectar no Redis"
    echo ""
    echo "Verificando logs..."
    docker logs cgbookstore_redis --tail 20
    echo ""
    exit 1
fi
