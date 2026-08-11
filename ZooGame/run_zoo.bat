@echo off
chcp 65001 >nul
color 0A
cls

:menu
cls
echo.
echo ================================================
echo           🦁 باغ وحش هوشمند - منوی اجرا 🦁
echo ================================================
echo.
echo   1. 🚀 اجرای بازی
echo   2. 📊 نمایش مانیتورینگ سریع
echo   3. 🗑️ حذف داده‌های بازی (شروع مجدد)
echo   4. 📂 باز کردن پوشه بازی
echo   5. ❌ خروج
echo.
echo ================================================
echo.
set /p choice="انتخاب کنید (1-5): "

if "%choice%"=="1" goto run_game
if "%choice%"=="2" goto show_monitoring
if "%choice%"=="3" goto reset_game
if "%choice%"=="4" goto open_folder
if "%choice%"=="5" goto exit_program
goto menu

:run_game
cls
echo در حال اجرای بازی...
echo.
python zoo_bot.py
pause
goto menu

:show_monitoring
cls
echo.
echo ================================================
echo        📊 مانیتورینگ سریع باغ وحش 📊
echo ================================================
echo.
python -c "import json; import os; f='zoo_data.json'; data=json.load(open(f,encoding='utf-8')) if os.path.exists(f) else {}; print('💰 پول:', f\"{data.get('money',0):,} تومان\" if data else 'بازی شروع نشده'); print('📅 روز:', data.get('day',1) if data else 1); print('🌤️ آب و هوا:', data.get('weather','نامشخص') if data else 'نامشخص'); print('👥 بازدیدکنندگان امروز:', data.get('visitors_today',0) if data else 0); print('🦁 حیوانات زنده:', len([a for a in data.get('animals',[]) if a.get('alive',False)]) if data else 0); print('🧹 میانگین تمیزی:', f\"{sum(e.get('cleanliness',0) for e in data.get('enclosures',[]))/max(1,len(data.get('enclosures',[]))):.1f}%\" if data and data.get('enclosures') else 'N/A'); print('==============================================')"
echo.
pause
goto menu

:reset_game
echo.
set /p confirm="آیا مطمئن هستید؟ تمام داده‌ها حذف می‌شوند! (y/n): "
if /i "%confirm%"=="y" (
    del zoo_data.json 2>nul
    echo ✅ داده‌ها حذف شدند!
) else (
    echo ❌ عملیات لغو شد.
)
pause
goto menu

:open_folder
start .
goto menu

:exit_program
echo.
echo خداحافظ! 👋
timeout /t 2 >nul
exit
