#!/bin/bash
# Script para configurar MoviePy antes de iniciar la aplicación

# Crear el archivo de configuración de MoviePy
mkdir -p /root/.config
cat > /root/.config/moviepy.conf << 'EOF'
[MAIN]
FFMPEG_BINARY = ffmpeg
IMAGEMAGICK_BINARY = /usr/bin/convert
EOF

# Ejecutar la aplicación
python app.py