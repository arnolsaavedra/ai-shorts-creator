"""
Configuración de MoviePy para desactivar ImageMagick
Este archivo debe ejecutarse antes de importar MoviePy
"""
import os

# Desactivar ImageMagick completamente
os.environ['IMAGEMAGICK_BINARY'] = ''

# Configurar MoviePy para no usar ImageMagick
try:
    from moviepy.config import change_settings
    change_settings({"IMAGEMAGICK_BINARY": None})
except:
    pass