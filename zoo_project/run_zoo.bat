@echo off
chcp 65001 >nul
cls

echo ================================================
echo    🦁 باغ وحش هوشمند - Zoo Management Game 🦁
echo ================================================
echo.
echo در حال بارگذاری بازی...
echo.

cd /d "%~dp0"

if not exist "zoo_bot.py" (
    echo ❌ خطا: فایل zoo_bot.py پیدا نشد!
    echo مطمئن شوید فایل‌ها در پوشه صحیح قرار دارند.
    pause
    exit /b 1
)

python zoo_bot.py

if errorlevel 1 (
    echo.
    echo ❌ خطا در اجرای بازی!
    echo مطمئن شوید پایتون نصب است.
    pause
)
