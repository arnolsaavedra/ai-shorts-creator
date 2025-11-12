@echo off
echo ============================================
echo  AI Shorts Creator - Iniciando...
echo ============================================
echo.

REM Verificar si FFmpeg esta instalado
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] FFmpeg no esta instalado!
    echo.
    echo Por favor instala FFmpeg primero:
    echo   1. Opcion facil: choco install ffmpeg
    echo   2. Manual: https://www.gyan.dev/ffmpeg/builds/
    echo.
    pause
    exit /b 1
)

echo [OK] FFmpeg encontrado
echo.

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar que el archivo .env existe
if not exist .env (
    echo [ADVERTENCIA] Archivo .env no encontrado
    echo Creando .env desde .env.example...
    if exist .env.example (
        copy .env.example .env
    ) else (
        echo Necesitas configurar tu archivo .env con las API keys
    )
    echo.
)

REM Iniciar la aplicacion
echo.
echo ============================================
echo  Iniciando servidor en http://localhost:3000
echo ============================================
echo.
echo IMPORTANTE:
echo   - La app se abrira en modo VISIBLE (no headless)
echo   - Veras una ventana de Chrome cuando subas a TikTok
echo   - Puedes intervenir manualmente si es necesario
echo.
echo Presiona Ctrl+C para detener el servidor
echo.
echo Abriendo navegador en http://localhost:3000...
timeout /t 3 >nul
start http://localhost:3000

python app.py

pause
