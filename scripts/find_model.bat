@echo off
echo ========================================
echo  Buscando modelo Gemini funcional
echo ========================================
echo.

cd /d "%~dp0.."
python scripts\find_working_model.py

echo.
pause
