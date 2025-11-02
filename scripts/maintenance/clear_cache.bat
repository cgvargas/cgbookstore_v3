@echo off
REM Script de atalho para limpar cache de recomendacoes
REM Uso: scripts\maintenance\clear_cache.bat

echo.
echo ========================================
echo Limpando Cache de Recomendacoes
echo ========================================
echo.

python manage.py shell -c "exec(open('scripts/maintenance/clear_recommendations_cache.py', encoding='utf-8').read())"

echo.
echo Pressione qualquer tecla para sair...
pause > nul
