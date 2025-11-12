@echo off
echo ============================================
echo  Verificando instalacion...
echo ============================================
echo.

REM Verificar Python
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] Python NO encontrado
    goto :error
) else (
    echo [OK] Python encontrado
    python --version
)
echo.

REM Verificar FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] FFmpeg NO encontrado
    echo.
    echo     Necesitas instalar FFmpeg:
    echo     1. choco install ffmpeg
    echo     2. winget install ffmpeg
    echo     3. https://www.gyan.dev/ffmpeg/builds/
    echo.
    goto :error
) else (
    echo [OK] FFmpeg encontrado
    ffmpeg -version | findstr "version"
)
echo.

REM Verificar Chrome
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo [OK] Google Chrome encontrado
) else (
    echo [!] Google Chrome no encontrado en la ubicacion predeterminada
    echo     Selenium puede no funcionar correctamente
)
echo.

REM Verificar entorno virtual
if exist venv\Scripts\activate.bat (
    echo [OK] Entorno virtual encontrado
) else (
    echo [X] Entorno virtual NO encontrado
    echo.
    echo     Ejecuta: python -m venv venv
    echo.
    goto :error
)
echo.

REM Verificar dependencias en el venv
echo Verificando dependencias de Python...
call venv\Scripts\activate.bat
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo [X] Flask NO instalado
    echo.
    echo     Ejecuta: venv\Scripts\pip install -r requirements.txt
    echo.
    goto :error
) else (
    echo [OK] Flask instalado
)

python -c "import selenium" 2>nul
if %errorlevel% neq 0 (
    echo [X] Selenium NO instalado
    goto :error
) else (
    echo [OK] Selenium instalado
)

python -c "import openai" 2>nul
if %errorlevel% neq 0 (
    echo [X] OpenAI NO instalado
    goto :error
) else (
    echo [OK] OpenAI instalado
)
echo.

REM Verificar archivo .env
if exist .env (
    echo [OK] Archivo .env encontrado
) else (
    echo [!] Archivo .env NO encontrado
    echo     Necesitas crear .env con tus API keys
)
echo.

echo ============================================
echo  TODO LISTO! Ejecuta start.bat
echo ============================================
echo.
pause
exit /b 0

:error
echo.
echo ============================================
echo  HAY ERRORES - Revisa arriba
echo ============================================
echo.
echo Lee INSTALACION_WINDOWS.md para mas detalles
echo.
pause
exit /b 1
