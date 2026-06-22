@echo off
echo =============================================
echo   Herbalife CRM ishga tushirilmoqda...
echo =============================================

:: Python virtual environment bo'lmasa o'rnatamiz
if not exist ".venv" (
    echo Virtual muhit yaratilmoqda...
    python -m venv .venv
)

:: Aktivatsiya
call .venv\Scripts\activate.bat

:: Kutubxonalar o'rnatish
echo Kutubxonalar tekshirilmoqda...
pip install -r requirements.txt -q

:: Ilovani ishga tushirish
echo.
echo   Login: admin
echo   Parol: herbalife123
echo.
python app.py

pause
