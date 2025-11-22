@echo off
echo ========================================
echo  Listando modelos Gemini disponiveis
echo ========================================
echo.

cd /d "%~dp0.."
python scripts\list_gemini_models.py

echo.
pause
