@echo off
echo ========================================
echo  Testando modelos Gemini gratuitos
echo ========================================
echo.

cd /d "%~dp0.."
python scripts\test_free_models.py

echo.
pause
