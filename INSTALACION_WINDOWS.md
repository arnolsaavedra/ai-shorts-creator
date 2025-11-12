# 🚀 Instalación en Windows (Sin Docker)

Esta guía te ayudará a ejecutar la aplicación directamente en Windows para poder usar la función de **auto-publicación en TikTok** (que requiere una ventana de Chrome visible).

## ✅ Pre-requisitos

### 1. Python 3.11 (Ya instalado ✓)
- Versión instalada: Python 3.11.0

### 2. FFmpeg (⚠️ REQUERIDO)

FFmpeg es necesario para procesar los videos. Elige **UNA** de estas opciones:

#### Opción A: Chocolatey (Más fácil)
1. Abre PowerShell como **Administrador**
2. Ejecuta:
```powershell
choco install ffmpeg
```
3. Cierra y vuelve a abrir la terminal

#### Opción B: winget (Windows 10/11)
1. Abre PowerShell
2. Ejecuta:
```powershell
winget install ffmpeg
```
3. Cierra y vuelve a abrir la terminal

#### Opción C: Instalación Manual
1. Ve a: https://www.gyan.dev/ffmpeg/builds/
2. Descarga: **ffmpeg-release-essentials.zip**
3. Extrae el archivo
4. Mueve la carpeta extraída a `C:\ffmpeg`
5. Agrega `C:\ffmpeg\bin` al PATH:
   - Busca "Variables de entorno" en Windows
   - En "Variables del sistema" encuentra "Path"
   - Click "Editar" → "Nuevo"
   - Agrega: `C:\ffmpeg\bin`
   - Click "Aceptar" en todas las ventanas
6. Cierra y vuelve a abrir la terminal

#### Verificar instalación de FFmpeg:
```bash
ffmpeg -version
```
Deberías ver la información de la versión de FFmpeg.

### 3. Google Chrome (Ya instalado ✓)
- Chrome encontrado en: `C:\Program Files\Google\Chrome\Application\chrome.exe`

### 4. Dependencias de Python (Ya instaladas ✓)
- Todas las dependencias ya están instaladas en el entorno virtual `venv/`

## 🎯 Cómo Usar

### 1. Configurar variables de entorno

Edita el archivo `.env` con tus credenciales:

```env
# API Keys
OPENAI_API_KEY=tu_api_key_aqui
ANTHROPIC_API_KEY=tu_api_key_aqui

# TikTok (para auto-publicación)
TIKTOK_USERNAME=stiffclipss
TIKTOK_PASSWORD=@rnolArnol123
```

### 2. Iniciar la aplicación

**Opción fácil:** Doble click en `start.bat`

**O desde la terminal:**
```bash
cd ai-shorts-creator
start.bat
```

La aplicación se abrirá en: **http://localhost:3000**

### 3. Usar la función de TikTok

Cuando actives **"Publicar automáticamente en TikTok"**:

1. ✅ Se abrirá una ventana de Chrome (VISIBLE)
2. ✅ La app intentará subir el video automáticamente
3. ⚠️ Si falla, verás instrucciones claras:
   - Ruta del video para arrastrar
   - Caption generado para copiar
   - Hashtags sugeridos
4. ✅ Tienes 2 minutos por video para completar manualmente
5. ✅ Continúa automáticamente con el siguiente video

## 🎬 Características Especiales

### Modo Normal (Videos regulares)
- Watermark de 200px arriba
- Video centrado (1400px)
- Espacio para subtítulos abajo (240px)

### Modo Split Screen (Streamers)
- Cámara arriba (50% ancho x 35% alto)
- Contenido abajo
- Watermark de 80px en la división

## ⚠️ Solución de Problemas

### Error: "FFmpeg no encontrado"
- Asegúrate de haber instalado FFmpeg
- Cierra y vuelve a abrir la terminal después de instalar
- Verifica con: `ffmpeg -version`

### Error: "ModuleNotFoundError"
- El entorno virtual ya está configurado
- Ejecuta `start.bat` que activa automáticamente el venv

### TikTok no sube el video
- Verifica que Chrome esté instalado
- Asegúrate de que tus credenciales en `.env` sean correctas
- La primera vez puede pedir verificación 2FA - complétala manualmente

### El video no se procesa
- Verifica que el video esté en formato compatible (MP4, MOV, etc.)
- Revisa que las API keys de OpenAI/Claude estén configuradas
- Mira los logs en la consola para más detalles

## 📊 Comparación: Docker vs Windows

| Característica | Docker | Windows (Este setup) |
|---------------|--------|---------------------|
| Auto-publicación TikTok | ❌ No funciona (headless) | ✅ Funciona (visible) |
| Facilidad de setup | ✅ Fácil | ⚠️ Requiere FFmpeg |
| Performance | ✅ Optimizado | ✅ Nativo |
| Debugging | ⚠️ Más difícil | ✅ Más fácil |

## 🆘 Ayuda

Si tienes problemas:
1. Revisa los logs en la consola
2. Verifica que FFmpeg esté instalado: `ffmpeg -version`
3. Verifica que las API keys estén configuradas en `.env`
4. Asegúrate de tener conexión a internet

## 🔄 Volver a Docker

Si prefieres usar Docker (sin auto-publicación en TikTok):

```bash
cd ai-shorts-creator
docker-compose up
```

La app estará en: http://localhost:3000
