# 🎬 AI Shorts Creator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-Whisper%20%26%20GPT-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Transforma videos largos en shorts virales automáticamente con Inteligencia Artificial**

[Características](#-características) • [Demo](#-demo) • [Instalación](#-instalación) • [Uso](#-uso) • [Tecnologías](#-tecnologías-utilizadas) • [Roadmap](#-roadmap-y-mejoras-futuras)

[🇬🇧 Read in English](README.md)

</div>

---

## 📖 Descripción

**AI Shorts Creator** es una aplicación web automatizada que utiliza inteligencia artificial para analizar videos largos (streams, podcasts, webinars, etc.) y extraer automáticamente los momentos más virales, convirtiéndolos en shorts optimizados para TikTok, Instagram Reels y YouTube Shorts.

### ¿Qué hace diferente a este proyecto?

- ✅ **Análisis inteligente de contenido**: Usa Whisper de OpenAI para transcripción y GPT/Claude para identificar momentos virales
- ✅ **Generación automática de títulos virales**: Cada clip obtiene un título optimizado basado en el contenido real del segmento
- ✅ **Formato vertical 9:16 perfecto**: Videos optimizados para redes sociales con subtítulos estilizados
- ✅ **Modo Split Screen para streamers**: Divide la pantalla para mostrar webcam y contenido por separado
- ✅ **Sin límite de tamaño**: Procesa videos de cualquier duración
- ✅ **Multi-idioma**: Soporte para inglés, español y detección automática

---

## ✨ Características

### 🎯 Funcionalidades Principales

| Característica | Descripción |
|----------------|-------------|
| **Transcripción Automática** | Utiliza Whisper de OpenAI para transcribir audio en múltiples idiomas |
| **Análisis de Contenido IA** | GPT-3.5/Claude identifica automáticamente los momentos más virales |
| **Generación de Subtítulos** | Subtítulos estilizados y sincronizados automáticamente |
| **Texto Viral Inteligente** | Títulos generados por IA basados en el contenido real de cada segmento |
| **Modo Split Screen** | Ideal para videos de streamers con cámara en esquina |
| **Publicación Automática TikTok** | Sube los shorts directamente a TikTok (semi-automático) |
| **Multi-proveedor de IA** | Soporta OpenAI y Anthropic Claude |
| **Configuración Flexible** | Duración de shorts, idioma del texto viral, y más |

### 🎨 Personalización de Shorts

- **Duración configurable**: Cortos (35s-1min) o Largos (1:10-1:30min)
- **Marca de agua personalizable**: Agrega tu logo en la parte superior
- **Idioma del texto viral**: Auto, Español o Inglés
- **Formato 9:16**: Optimizado para plataformas verticales
- **Calidad HD**: Output en 1080x1920px

---

## 🖼️ Demo

### Interfaz Web

```
┌─────────────────────────────────────────────┐
│  🎬 AI Shorts Creator v2.0                  │
│  Transforma videos largos en shorts virales │
└─────────────────────────────────────────────┘

📤 Sube tu video (sin límite de tamaño)
    ↓
⚙️  Configura opciones:
    • Proveedor de IA (OpenAI/Claude)
    • Duración de shorts
    • Modo de pantalla (Normal/Split Screen)
    • Idioma del texto viral
    • Auto-publicación TikTok
    ↓
🤖 La IA analiza el contenido
    ↓
✨ Genera automáticamente todos los shorts virales
    ↓
📥 Descarga los clips o publícalos en TikTok
```

### Ejemplo de Output

Cada short incluye:
- ✅ Video en formato 9:16 (1080x1920)
- ✅ Subtítulos estilizados
- ✅ Marca de agua personalizada
- ✅ Texto viral generado por IA
- ✅ Puntuación de relevancia (0-100)
- ✅ Copy optimizado para Instagram/TikTok

---

## 🚀 Instalación

### Requisitos Previos

- **Python 3.9+**
- **FFmpeg** (para procesamiento de video)
- **API Key de OpenAI** (para Whisper + GPT)
- **API Key de Anthropic** (opcional, para Claude)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/ai-shorts-creator.git
cd ai-shorts-creator
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Instalar FFmpeg

#### Windows:
```bash
# Descargar desde: https://ffmpeg.org/download.html
# O usar Chocolatey:
choco install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS:
```bash
brew install ffmpeg
```

### Paso 5: Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# OpenAI API Key (requerido)
OPENAI_API_KEY=tu_api_key_aqui

# Anthropic API Key (opcional, para usar Claude)
ANTHROPIC_API_KEY=tu_api_key_aqui

# Proveedor de IA por defecto (openai o claude)
AI_PROVIDER=openai

# Credenciales TikTok (opcional, para auto-publicación)
TIKTOK_USERNAME=tu_usuario_tiktok
TIKTOK_PASSWORD=tu_contraseña_tiktok

# Flask
FLASK_ENV=development
MAX_UPLOAD_SIZE=2147483648
```

### Paso 6: Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:3000**

---

## 📋 Uso

### 1. Subir Video

- Arrastra y suelta un video o haz clic para seleccionar
- Formatos soportados: MP4, AVI, MOV, MKV, WebM
- Sin límite de tamaño

### 2. Configurar Opciones

| Opción | Valores | Descripción |
|--------|---------|-------------|
| **Proveedor de IA** | OpenAI / Claude | Modelo para análisis de contenido |
| **Duración de Shorts** | Cortos / Largos | 35s-1min o 1:10-1:30min |
| **Modo de Pantalla** | Normal / Split Screen | Pantalla completa o división webcam+contenido |
| **Idioma Texto Viral** | Auto / Español / English | Idioma para los títulos generados |
| **Publicación TikTok** | Sí / No | Auto-publicar en TikTok |

### 3. Procesar Video

- Haz clic en **"🚀 Analizar y Generar Shorts"**
- La IA transcribirá el audio
- Analizará el contenido
- Generará automáticamente todos los shorts virales encontrados

### 4. Descargar o Publicar

- Descarga cada short individualmente
- Copia el texto optimizado para Instagram/TikTok
- O publica automáticamente en TikTok

---

## 🛠️ Tecnologías Utilizadas

### Backend

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.9+ | Lenguaje principal |
| **Flask** | 3.0.0 | Framework web |
| **OpenAI API** | 1.54.3 | Whisper (transcripción) + GPT (análisis) |
| **Anthropic API** | 0.39.0 | Claude (análisis alternativo) |
| **FFmpeg** | Latest | Procesamiento de video/audio |
| **FFprobe** | Latest | Metadatos de video |

### Frontend

- **HTML5** + **CSS3** (diseño responsivo)
- **JavaScript ES6+** (vanilla, sin frameworks)
- **Fetch API** para comunicación asíncrona

### Librerías Python

```
Flask==3.0.0              # Framework web
openai==1.54.3            # API OpenAI (Whisper + GPT)
anthropic==0.39.0         # API Anthropic (Claude)
python-dotenv==1.0.0      # Variables de entorno
selenium==4.15.2          # Auto-publicación TikTok
ffmpeg-python==0.2.0      # Interfaz Python para FFmpeg
```

### Herramientas Externas

- **Whisper** (OpenAI): Transcripción de audio multiidioma
- **GPT-3.5 Turbo**: Análisis de contenido y generación de títulos virales
- **Claude Haiku**: Alternativa para análisis de contenido

---

## 📂 Estructura del Proyecto

```
ai-shorts-creator/
├── app.py                    # Aplicación Flask principal + frontend HTML
├── video_processor.py        # Procesamiento de video con FFmpeg
├── ai_analyzer.py            # Análisis IA (transcripción + momentos virales)
├── tiktok_uploader.py        # Auto-publicación en TikTok
├── requirements.txt          # Dependencias Python
├── .env.example              # Template de variables de entorno
├── gota_agua.png             # Marca de agua (personalizable)
├── README.md                 # Versión en inglés
├── README_ES.md              # Este archivo (Español)
├── uploads/                  # Videos subidos (temporal)
├── outputs/                  # Shorts generados
└── temp/                     # Archivos temporales (audio, subtítulos)
```

---

## 🎯 Casos de Uso

### Para Creadores de Contenido
- Convertir streams largos de Twitch/YouTube en clips virales
- Extraer highlights de podcasts
- Crear contenido para TikTok/Reels sin edición manual

### Para Agencias de Marketing
- Repurposing de webinars en contenido social
- Creación rápida de anuncios cortos
- Generación de contenido para múltiples plataformas

### Para Educadores
- Extraer momentos clave de clases/conferencias
- Crear contenido educativo breve
- Compartir conocimiento en formato viral

---

## 🔮 Roadmap y Mejoras Futuras

### 🚧 En Desarrollo

- [ ] **Soporte para más plataformas**
  - Instagram Reels API
  - YouTube Shorts API
  - LinkedIn Video

- [ ] **Mejoras en análisis IA**
  - Detección de emociones (análisis de sentimiento)
  - Identificación de rostros (enfoque automático)
  - Detección de momentos "épicos" (música, reacciones)

- [ ] **Editor de shorts integrado**
  - Recortar clips manualmente
  - Agregar transiciones
  - Personalizar subtítulos (fuente, color, posición)

- [ ] **Sistema de plantillas**
  - Plantillas predefinidas por tipo de contenido
  - Personalización de marca de agua por proyecto
  - Estilos de subtítulos guardados

### 💡 Ideas para Contribuir

- [ ] Soporte para múltiples idiomas en subtítulos
- [ ] Análisis de métricas virales (predicción de engagement)
- [ ] Sistema de cola para procesamiento masivo
- [ ] Dashboard de analytics
- [ ] API REST documentada (FastAPI)
- [ ] Docker Compose con GPU support
- [ ] Tests unitarios y de integración
- [ ] CI/CD con GitHub Actions
- [ ] Interfaz de administración de proyectos
- [ ] Sistema de usuarios y autenticación

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas, encuentras bugs o quieres agregar funcionalidades:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles sobre el proceso.

### Reportar Bugs

Si encuentras un bug, por favor abre un **Issue** con:
- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Screenshots (si aplica)
- Versión de Python y sistema operativo

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- **OpenAI** por Whisper y GPT-3.5
- **Anthropic** por Claude
- **FFmpeg** por el increíble framework de procesamiento multimedia
- **Flask** por el framework web simple y poderoso

---

## 📧 Contacto

Si tienes preguntas, sugerencias o quieres colaborar:

- 📧 Email: tu-email@ejemplo.com
- 🐦 Twitter: [@tu_usuario](https://twitter.com/tu_usuario)
- 💼 LinkedIn: [Tu Nombre](https://linkedin.com/in/tu-perfil)
- 🐙 GitHub: [@tu_usuario](https://github.com/tu_usuario)

---

## ⚠️ Disclaimer

Esta herramienta está diseñada para uso educativo y de creación de contenido legítimo. Asegúrate de:

- ✅ Tener los derechos del contenido que procesas
- ✅ Respetar las políticas de uso de las plataformas donde publiques
- ✅ Cumplir con las leyes de derechos de autor de tu región
- ✅ Usar APIs con responsabilidad (costos de OpenAI/Anthropic)

---

## 🌟 Muestra tu Apoyo

Si este proyecto te ayudó, considera:

- ⭐ Darle una estrella en GitHub
- 🐛 Reportar bugs o solicitar funcionalidades
- 🤝 Contribuir al código
- 📢 Compartirlo con otros

---

<div align="center">

**Hecho con ❤️ y mucha ☕**

[🇬🇧 Read in English](README.md)

</div>
