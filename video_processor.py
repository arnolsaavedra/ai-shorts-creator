import os
import subprocess
import json

class VideoProcessor:
    def __init__(self, temp_folder):
        self.temp_folder = temp_folder
        os.makedirs(temp_folder, exist_ok=True)
    
    def get_video_duration(self, video_path):
        """Obtiene la duración del video en segundos usando FFprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"Error obteniendo duración: {e}")
            return 0
    
    def extract_audio(self, video_path):
        """Extrae el audio del video usando FFmpeg"""
        # Usar un nombre de archivo más corto para evitar problemas con rutas largas
        import hashlib
        video_hash = hashlib.md5(video_path.encode()).hexdigest()[:8]
        audio_path = os.path.join(self.temp_folder, f"audio_{video_hash}.mp3")

        try:
            print(f"📂 Ruta del video: {video_path}")
            print(f"📂 Ruta del audio: {audio_path}")

            # Verificar que el video existe y sus permisos
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"El video no existe: {video_path}")

            video_size = os.path.getsize(video_path)
            print(f"📊 Tamaño del video: {video_size / 1024 / 1024:.2f} MB")

            # Verificar que ffmpeg está disponible
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
                print(f"✅ FFmpeg disponible")
            except FileNotFoundError:
                raise Exception("FFmpeg no está instalado o no está en el PATH")

            # Asegurar que la carpeta temp existe
            os.makedirs(self.temp_folder, exist_ok=True)

            cmd = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-vn',  # Sin video
                '-acodec', 'libmp3lame',
                '-ar', '16000',  # 16kHz para Whisper
                '-ac', '1',  # Mono
                '-b:a', '128k',
                audio_path
            ]

            print(f"🔧 Ejecutando comando FFmpeg para extraer audio...")
            print(f"   Comando: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if os.path.exists(audio_path):
                audio_size = os.path.getsize(audio_path)
                print(f"✅ Audio extraído: {audio_path} ({audio_size / 1024:.2f} KB)")
            else:
                raise Exception("El archivo de audio no se creó")

            return audio_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Error extrayendo audio:")
            print(f"   Código de salida: {e.returncode}")
            print(f"   Comando: {' '.join(cmd)}")
            print(f"   STDOUT: {e.stdout}")
            print(f"   STDERR: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def create_short(self, input_video, output_path, start_time, end_time, subtitles, split_screen_mode=None, viral_text=None):
        """
        Crea un short en formato vertical 9:16 con subtítulos usando solo FFmpeg

        Args:
            input_video: Ruta del video original
            output_path: Ruta donde guardar el short
            start_time: Tiempo de inicio en segundos
            end_time: Tiempo de fin en segundos
            subtitles: Lista de diccionarios con subtítulos [{'start': 0, 'end': 2, 'text': 'Hola'}]
            split_screen_mode: None, 'webcam_corner', 'auto'
                - None: Modo normal (escala completo)
                - 'webcam_corner': Divide pantalla - webcam arriba, contenido abajo
                - 'auto': Intenta detectar automáticamente (por ahora usa webcam_corner)
            viral_text: Texto viral para mostrar entre marca de agua y video (opcional)
        """
        try:
            print(f"🎬 Creando short: {start_time}s - {end_time}s")
            duration = end_time - start_time

            # Crear archivo ASS para subtítulos
            ass_path = None
            if subtitles and len(subtitles) > 0:
                print(f"💬 Generando {len(subtitles)} subtítulos...")
                ass_path = os.path.join(self.temp_folder, f"subs_{os.path.basename(output_path)}.ass")
                self._create_ass_file(subtitles, ass_path)

            # Obtener información del video original
            video_info = self._get_video_info(input_video)
            original_width = video_info['width']
            original_height = video_info['height']

            # Calcular ratios
            target_ratio = 9 / 16
            current_ratio = original_width / original_height

            print(f"📐 Dimensiones originales: {original_width}x{original_height}")
            print(f"📊 Ratio actual: {current_ratio:.3f}, Ratio objetivo: {target_ratio:.3f}")

            # Verificar si ya es 9:16 (con tolerancia de ±5%)
            ratio_tolerance = 0.05
            is_already_9_16 = abs(current_ratio - target_ratio) < (target_ratio * ratio_tolerance)

            # MODO SPLIT SCREEN para streamers con cámara en esquina
            if split_screen_mode in ['webcam_corner', 'auto']:
                print(f"🎮 Modo Split Screen activado: dividiendo pantalla para streamer")
                video_filter = self._create_split_screen_filter(
                    original_width,
                    original_height,
                    split_screen_mode
                )
            elif is_already_9_16:
                # El video ya es 9:16, solo escalarlo a 1080x1920 sin cortar
                print(f"✅ Video ya está en formato 9:16, escalando sin cortar...")
                video_filter = self._create_normal_filter_with_watermark("scale=1080:1920:flags=lanczos", viral_text)
            else:
                # El video NO es 9:16, escalarlo para llenar TODO el ancho (sin márgenes laterales)
                print(f"📏 Video no es 9:16, escalando para llenar todo el ancho...")

                # Escalar el video para que llene TODO el ancho de 1080px
                # Si es horizontal (16:9), se escalará por ancho y se cortará arriba/abajo si es necesario
                # Si es más vertical, se escalará para llenar el ancho
                base_filter = "scale=1080:-2:flags=lanczos"
                video_filter = self._create_normal_filter_with_watermark(base_filter, viral_text)

            # Agregar subtítulos si existen (solo para modo NO split screen)
            # En modo split screen, los subtítulos se agregan después del filtro complejo
            if ass_path and os.path.exists(ass_path) and split_screen_mode not in ['webcam_corner', 'auto']:
                # Escapar la ruta para FFmpeg
                ass_path_escaped = ass_path.replace('\\', '/').replace(':', '\\:')
                video_filter += f",ass='{ass_path_escaped}'"
            elif ass_path and os.path.exists(ass_path) and split_screen_mode in ['webcam_corner', 'auto']:
                # Para split screen, agregar subtítulos al final del filtro complejo
                ass_path_escaped = ass_path.replace('\\', '/').replace(':', '\\:')
                video_filter += f",ass='{ass_path_escaped}'"

            # Comando FFmpeg completo
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',  # Sobrescribir sin preguntar
                '-ss', str(start_time),  # Tiempo de inicio
                '-t', str(duration),  # Duración
                '-i', input_video,  # Video de entrada
                '-vf', video_filter,  # Filtros de video
                '-c:v', 'libx264',  # Codec de video
                '-preset', 'medium',  # Preset de velocidad/calidad
                '-crf', '23',  # Calidad (18-28, menor = mejor calidad)
                '-c:a', 'aac',  # Codec de audio
                '-b:a', '192k',  # Bitrate de audio
                '-ar', '44100',  # Sample rate
                '-movflags', '+faststart',  # Optimizar para streaming
                output_path
            ]
            
            print(f"🔧 Ejecutando FFmpeg...")
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Error de FFmpeg: {result.stderr}")
                raise Exception(f"FFmpeg falló: {result.stderr}")
            
            # Limpiar archivo de subtítulos temporal
            if ass_path and os.path.exists(ass_path):
                os.remove(ass_path)
            
            print(f"✅ Short creado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando short: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _get_video_info(self, video_path):
        """Obtiene información del video usando ffprobe"""
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'json',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        return {
            'width': info['streams'][0]['width'],
            'height': info['streams'][0]['height']
        }
    
    def _create_ass_file(self, subtitles, ass_path):
        """Crea un archivo ASS con subtítulos estilizados"""
        # Header del archivo ASS con estilos
        ass_content = """[Script Info]
Title: Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,45,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,80,80,360,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Agregar cada subtítulo
        for sub in subtitles:
            start_time = self._format_ass_time(sub['start'])
            end_time = self._format_ass_time(sub['end'])
            # Escapar texto para ASS y limpiar
            text = sub['text'].strip().replace('\n', ' ').replace('\\', '\\\\')
            
            # Dividir texto largo en dos líneas si es necesario
            if len(text) > 40:
                words = text.split()
                mid = len(words) // 2
                text = ' '.join(words[:mid]) + '\\N' + ' '.join(words[mid:])
            
            ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n"
        
        # Escribir archivo
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        
        print(f"📝 Archivo de subtítulos creado: {ass_path}")
    
    def _format_ass_time(self, seconds):
        """Convierte segundos a formato de tiempo ASS (H:MM:SS.CC)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

    def _create_normal_filter_with_watermark(self, base_filter, viral_text=None):
        """
        Agrega marca de agua al filtro normal (modo no split screen)
        Layout: Marca de agua arriba - Texto viral - Video en medio - Espacio negro abajo (subtítulos)

        Args:
            base_filter: Filtro base de video (scale, pad, etc)
            viral_text: Texto viral extraído del contenido del video (opcional)

        Returns:
            Filtro completo con marca de agua, texto viral y espacio para subtítulos
        """
        # Dimensiones finales
        output_width = 1080
        output_height = 1920

        # Distribución del espacio vertical:
        # - Logo arriba: ~280px (incluye padding) - 100px más para bajar la marca
        # - Video medio: ~1400px
        # - Subtítulos abajo: ~240px (espacio negro)

        watermark_height = 280  # Espacio para marca de agua arriba (180 + 100)
        subtitle_height = 240   # Espacio negro abajo para subtítulos
        video_height = output_height - watermark_height - subtitle_height  # ~1400px

        # Ruta de la marca de agua (logo)
        watermark_path = os.path.join(os.path.dirname(__file__), 'gota_agua.png')

        # Verificar si existe la marca de agua
        if os.path.exists(watermark_path):
            print(f"   💧 Creando layout: Marca de agua ({watermark_height}px) - Video ({video_height}px) - Subtítulos ({subtitle_height}px)")
            # Escapar la ruta para FFmpeg
            watermark_path_escaped = watermark_path.replace('\\', '/').replace(':', '\\:')

            # Crear filtro complejo con layout de 3 secciones
            filter_complex = (
                # 1. Escalar video a ancho completo (1080px) manteniendo aspect ratio
                # El video ocupará TODO el ancho, pero puede tener barras negras arriba/abajo
                # NO se recorta nada - se mantiene todo el contenido original
                f"[0:v]{base_filter},scale={output_width}:-2:flags=lanczos,"
                f"pad={output_width}:{video_height}:0:(oh-ih)/2:black,"
                f"pad={output_width}:{output_height}:0:{watermark_height}:black[video_padded];"

                # 2. Cargar marca de agua y redimensionarla (300px de ancho)
                f"movie='{watermark_path_escaped}',scale=300:-1[watermark];"

                # 3. Overlay de la marca de agua centrada en la sección superior
                # X = (W-w)/2 (centrado horizontalmente)
                # Y = 100 (margen de 100px desde arriba)
                f"[video_padded][watermark]overlay=(W-w)/2:100[with_watermark]"
            )

            # 4. Agregar texto viral si está disponible
            if viral_text:
                # Limpiar texto para FFmpeg (escapar caracteres especiales)
                # Mantener \n para saltos de línea
                viral_text_escaped = viral_text.replace("'", "'\\\\\\''").replace(":", "\\:")

                print(f"   📝 Texto viral (con saltos de línea): {viral_text}")

                # Agregar drawtext para el texto viral con fondo blanco
                # Usamos box=1 para crear el fondo blanco
                # No especificamos fontfile para usar la fuente sans-serif por defecto del sistema
                # FFmpeg interpreta \n como salto de línea automáticamente
                filter_complex += (
                    f";[with_watermark]drawtext="
                    f"text='{viral_text_escaped}':"
                    f"fontsize=50:"
                    f"fontcolor=black:"  # Letras negras
                    f"box=1:"  # Activar caja de fondo
                    f"boxcolor=white@1.0:"  # Fondo blanco opaco
                    f"boxborderw=15:"  # Padding del fondo (espacio alrededor del texto)
                    f"line_spacing=10:"  # Espacio entre líneas (si FFmpeg lo soporta)
                    f"x=(w-text_w)/2:"  # Centrado horizontal
                    f"y=530"  # Posición vertical
                )

            return filter_complex
        else:
            print(f"   ⚠️  Marca de agua no encontrada, usando layout simple con espacio para subtítulos")

            # Sin marca de agua, pero con espacio para subtítulos
            filter_complex = (
                # Escalar video y agregar padding arriba y abajo
                f"[0:v]{base_filter},scale={output_width}:{video_height}:force_original_aspect_ratio=decrease,"
                f"pad={output_width}:{output_height}:(ow-iw)/2:{watermark_height}:black"
            )

            return filter_complex

    def _create_split_screen_filter(self, original_width, original_height, mode):
        """
        Crea un filtro FFmpeg para dividir la pantalla en dos secciones verticales

        Para videos de streamers donde la cámara está en una esquina:
        - Sección superior: Zoom a la región de la cámara (esquina típicamente)
        - Sección inferior: Zoom a la región del contenido (pantalla)

        Args:
            original_width: Ancho del video original
            original_height: Alto del video original
            mode: 'webcam_corner' o 'auto'

        Returns:
            String con el filtro FFmpeg completo
        """
        print(f"📐 Creando layout split screen...")

        # Dimensiones finales del output
        output_width = 1080
        output_height = 1920

        # Altura de cada sección (dividir en mitades)
        section_height = output_height // 2  # 960 cada uno

        # ESTRATEGIA COMÚN PARA STREAMERS:
        # - Cámara típicamente está en una esquina (20-30% del video)
        # - Contenido/pantalla ocupa el centro-completo

        # Para videos 16:9 (1920x1080), asumimos:
        # - Webcam en esquina inferior derecha/izquierda
        # - Contenido principal es toda la pantalla

        if mode == 'webcam_corner' or mode == 'auto':
            # SECCIÓN SUPERIOR: Enfoque en webcam (parte superior/central del video)
            # Crop de la región superior donde típicamente está la cámara
            webcam_crop_width = int(original_width * 0.50)  # 50% del ancho (zona central-superior)
            webcam_crop_height = int(original_height * 0.35)  # 35% del alto (parte superior)

            # Posición: parte superior central del video
            webcam_x = (original_width - webcam_crop_width) // 2  # Centrado horizontalmente
            webcam_y = 0  # Desde arriba

            # SECCIÓN INFERIOR: Contenido completo (toda la pantalla escalada)
            # Usamos el video completo para mostrar el contenido

            print(f"   📹 Webcam crop: {webcam_crop_width}x{webcam_crop_height} desde ({webcam_x},{webcam_y})")
            print(f"   🖥️  Contenido: video completo")

            # Ruta de la marca de agua (logo)
            watermark_path = os.path.join(os.path.dirname(__file__), 'gota_agua.png')

            # Verificar si existe la marca de agua
            if os.path.exists(watermark_path):
                print(f"   💧 Marca de agua encontrada: {watermark_path}")
                # Escapar la ruta para FFmpeg
                watermark_path_escaped = watermark_path.replace('\\', '/').replace(':', '\\:')

                # Crear filtro complejo con marca de agua
                filter_complex = (
                    # Dividir el input en 2 streams
                    f"[0:v]split=2[full][webcam];"

                    # Stream 1: Webcam (crop + scale a sección superior)
                    f"[webcam]crop={webcam_crop_width}:{webcam_crop_height}:{webcam_x}:{webcam_y},"
                    f"scale={output_width}:{section_height}:flags=lanczos[webcam_scaled];"

                    # Stream 2: Contenido completo (scale manteniendo aspect ratio + pad)
                    f"[full]scale={output_width}:{section_height}:force_original_aspect_ratio=decrease,"
                    f"pad={output_width}:{section_height}:(ow-iw)/2:(oh-ih)/2:black[content_scaled];"

                    # Combinar ambos streams verticalmente
                    f"[webcam_scaled][content_scaled]vstack=inputs=2[combined];"

                    # Cargar marca de agua y redimensionarla (pequeña, 80px de ancho)
                    f"movie='{watermark_path_escaped}',scale=80:-1[watermark];"

                    # Overlay de la marca de agua en el centro de la división
                    # Y = section_height - 40 (en el medio de la línea divisoria)
                    # X = (output_width - 80) / 2 (centrado horizontalmente)
                    f"[combined][watermark]overlay=(W-w)/2:{section_height}-40[final];"

                    # Output final con marca de agua
                    f"[final]scale={output_width}:{output_height}:flags=lanczos"
                )
            else:
                print(f"   ⚠️  Marca de agua no encontrada en: {watermark_path}")
                print(f"   ℹ️  Continuando sin marca de agua...")

                # Filtro sin marca de agua
                filter_complex = (
                    # Dividir el input en 2 streams
                    f"[0:v]split=2[full][webcam];"

                    # Stream 1: Webcam (crop + scale a sección superior)
                    f"[webcam]crop={webcam_crop_width}:{webcam_crop_height}:{webcam_x}:{webcam_y},"
                    f"scale={output_width}:{section_height}:flags=lanczos[webcam_scaled];"

                    # Stream 2: Contenido completo (scale manteniendo aspect ratio + pad)
                    f"[full]scale={output_width}:{section_height}:force_original_aspect_ratio=decrease,"
                    f"pad={output_width}:{section_height}:(ow-iw)/2:(oh-ih)/2:black[content_scaled];"

                    # Combinar ambos streams verticalmente
                    f"[webcam_scaled][content_scaled]vstack=inputs=2[combined];"

                    # Output final
                    f"[combined]scale={output_width}:{output_height}:flags=lanczos"
                )

            return filter_complex

        return f"scale={output_width}:{output_height}:flags=lanczos"

    def get_video_info(self, video_path):
        """Obtiene información detallada del video usando ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            return info
        except Exception as e:
            print(f"Error obteniendo información del video: {e}")
            return None