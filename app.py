from flask import Flask, request, jsonify, send_file, render_template_string
import os
import json
import uuid
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import threading
from video_processor import VideoProcessor
from ai_analyzer import AIAnalyzer
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = None  # Sin límite de tamaño
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['TEMP_FOLDER'] = 'temp'

# Crear directorios si no existen
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['TEMP_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Almacenamiento en memoria de trabajos
jobs = {}

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No se encontró el archivo de video'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de archivo no permitido'}), 400
    
    # Guardar archivo
    job_id = str(uuid.uuid4())
    filename = secure_filename(f"{job_id}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    print(f"📤 Guardando video...")
    print(f"   Job ID: {job_id}")
    print(f"   Nombre archivo: {filename}")
    print(f"   Ruta completa: {filepath}")
    
    try:
        file.save(filepath)
        print(f"✅ Video guardado exitosamente")
        
        # Verificar que existe
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / (1024 * 1024 * 1024)
            print(f"✅ Archivo verificado: {file_size:.2f} GB")
        else:
            raise Exception(f"El archivo no se guardó correctamente: {filepath}")
            
    except Exception as e:
        print(f"❌ Error guardando archivo: {e}")
        return jsonify({'error': f'Error al guardar el archivo: {str(e)}'}), 500
    
    # Crear trabajo
    jobs[job_id] = {
        'id': job_id,
        'status': 'uploaded',
        'filename': filename,
        'filepath': filepath,
        'progress': 0,
        'message': 'Video cargado correctamente',
        'shorts': [],
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'job_id': job_id, 'message': 'Video cargado correctamente'})

@app.route('/api/process/<job_id>', methods=['POST'])
def process_video(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Trabajo no encontrado'}), 404
    
    job = jobs[job_id]
    
    if job['status'] == 'processing':
        return jsonify({'error': 'El video ya está siendo procesado'}), 400
    
    # Obtener configuración
    data = request.get_json() or {}
    ai_provider = data.get('ai_provider', os.getenv('AI_PROVIDER', 'openai'))
    short_duration = data.get('short_duration', 'short')  # 'short' o 'long'
    split_screen_mode = data.get('split_screen_mode', None)  # None, 'webcam_corner', 'auto'
    auto_publish_tiktok = data.get('auto_publish_tiktok', False)  # Auto publicar en TikTok
    viral_text_language = data.get('viral_text_language', 'auto')  # 'auto', 'es', 'en'

    # Iniciar procesamiento en segundo plano
    thread = threading.Thread(
        target=process_video_background,
        args=(job_id, ai_provider, short_duration, split_screen_mode, auto_publish_tiktok, viral_text_language)
    )
    thread.daemon = True
    thread.start()

    return jsonify({'message': 'Procesamiento iniciado', 'job_id': job_id})

def process_video_background(job_id, ai_provider, short_duration, split_screen_mode=None, auto_publish_tiktok=False, viral_text_language='auto'):
    try:
        job = jobs[job_id]
        job['status'] = 'processing'
        job['progress'] = 5
        job['message'] = 'Inicializando procesamiento...'
        
        # Inicializar procesadores
        video_processor = VideoProcessor(app.config['TEMP_FOLDER'])
        ai_analyzer = AIAnalyzer(ai_provider)
        
        # Extraer audio y transcribir
        job['progress'] = 10
        job['message'] = 'Extrayendo audio del video...'
        
        audio_path = video_processor.extract_audio(job['filepath'])
        
        job['progress'] = 20
        job['message'] = 'Transcribiendo audio...'
        
        transcript = ai_analyzer.transcribe_audio(audio_path)
        
        # Analizar contenido y encontrar momentos relevantes
        job['progress'] = 40
        job['message'] = 'Analizando contenido y buscando momentos destacados...'
        
        video_duration = video_processor.get_video_duration(job['filepath'])
        
        # Pasar short_duration al analizador
        moments = ai_analyzer.find_viral_moments(transcript, video_duration, short_duration)
        
        # Crear shorts
        job['progress'] = 50
        job['message'] = f'Generando {len(moments)} shorts...'
        
        shorts = []
        for i, moment in enumerate(moments):
            progress = 50 + (40 * (i + 1) / len(moments))
            job['progress'] = int(progress)
            job['message'] = f'Creando short {i+1} de {len(moments)}...'
            
            # Generar subtítulos
            subtitles = ai_analyzer.generate_subtitles(
                transcript,
                moment['start_time'],
                moment['end_time']
            )
            
            # Crear short con subtítulos
            output_filename = f"short_{job_id}_{i+1}.mp4"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

            # Extraer texto viral DIRECTAMENTE de la transcripción del segmento
            viral_text = None

            # Función para extraer el texto real del segmento temporal
            def extract_segment_text(transcript, start_time, end_time):
                """Extrae el texto completo del segmento temporal de la transcripción"""
                segment_text = ""
                for seg in transcript['segments']:
                    seg_start = seg.get('start', 0)
                    seg_end = seg.get('end', 0)

                    # Si el segmento está dentro del rango del momento
                    if (seg_start >= start_time and seg_start < end_time) or \
                       (seg_end > start_time and seg_end <= end_time) or \
                       (seg_start <= start_time and seg_end >= end_time):
                        text = seg.get('text', '').strip()
                        if text:
                            segment_text += " " + text

                return segment_text.strip() if segment_text else None

            def generate_viral_title(segment_text, language='auto'):
                """Genera un título viral usando IA basado en el contenido del segmento"""
                if not segment_text:
                    return None

                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

                    # Configurar idioma del prompt
                    language_instruction = ""
                    if language == 'es':
                        language_instruction = "- El título DEBE estar en ESPAÑOL."
                    elif language == 'en':
                        language_instruction = "- El título DEBE estar en INGLÉS (English)."
                    else:  # auto
                        language_instruction = "- Detecta el idioma del contenido y usa ese mismo idioma para el título."

                    prompt = f"""Analiza el siguiente fragmento de un video y crea un título viral de MÁXIMO 8 PALABRAS.

CONTENIDO DEL VIDEO:
"{segment_text}"

INSTRUCCIONES:
- Máximo 8 palabras (ESTRICTO)
{language_instruction}
- Usa EXACTAMENTE el mismo tono y lenguaje que el contenido (formal, informal, vulgar, técnico, etc.)
- Si el contenido usa jerga, slang o palabras vulgares, ÚSALAS en el título
- NO censures ni suavices el lenguaje - mantén la autenticidad
- El título debe captar la esencia más viral o impactante del fragmento
- Debe generar curiosidad o impacto inmediato
- NO uses comillas ni puntos al final
- Si el contenido tiene datos específicos (números, porcentajes, nombres), INCLÚYELOS

EJEMPLOS DE TÍTULOS SEGÚN EL TONO:
- Contenido técnico: "IA supera humanos en diagnóstico médico"
- Contenido informal: "No vas a creer lo que pasó"
- Contenido vulgar: "Esta mierda cambió mi vida completamente"
- Contenido motivacional: "El secreto que nadie te cuenta"

Responde SOLO con el título, sin explicaciones ni comillas."""

                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Eres un experto en crear títulos virales para redes sociales. Te adaptas perfectamente al tono y lenguaje del contenido original."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=50,
                        temperature=0.7
                    )

                    title = response.choices[0].message.content.strip()
                    # Limpiar comillas si las agregó
                    title = title.strip('"').strip("'")

                    # Dividir en dos líneas si tiene más de 4 palabras
                    words = title.split()
                    if len(words) > 4:
                        mid_point = len(words) // 2
                        line1 = " ".join(words[:mid_point])
                        line2 = " ".join(words[mid_point:])
                        title = f"{line1}\n{line2}"

                    return title

                except Exception as e:
                    print(f"⚠️  Error generando título viral: {str(e)}")
                    return None

            # Extraer texto completo del segmento
            segment_text = extract_segment_text(transcript, moment['start_time'], moment['end_time'])

            # Generar título viral con IA
            viral_text = None
            if segment_text:
                print(f"📝 Contenido del segmento ({moment['start_time']}s - {moment['end_time']}s):")
                print(f"   '{segment_text[:100]}...'")
                viral_text = generate_viral_title(segment_text, viral_text_language)

            if viral_text:
                print(f"📝 Texto viral extraído del segmento ({moment['start_time']}s - {moment['end_time']}s): '{viral_text}'")
            else:
                print(f"⚠️  No se pudo extraer texto del segmento, usando fallback...")

            # Fallback a key_phrases si no se pudo extraer texto
            if not viral_text:
                if moment.get('key_phrases') and len(moment['key_phrases']) > 0:
                    viral_text = moment['key_phrases'][0]
                    print(f"   Usando key_phrase: '{viral_text}'")
                elif moment.get('title'):
                    viral_text = moment['title']
                    print(f"   Usando título: '{viral_text}'")

            video_processor.create_short(
                job['filepath'],
                output_path,
                moment['start_time'],
                moment['end_time'],
                subtitles,
                split_screen_mode,
                viral_text
            )
            
            shorts.append({
                'id': i + 1,
                'filename': output_filename,
                'title': moment['title'],
                'description': moment['description'],
                'start_time': moment['start_time'],
                'end_time': moment['end_time'],
                'duration': moment['end_time'] - moment['start_time'],
                'relevance_score': moment['score'],
                'instagram_copy': moment.get('instagram_copy', '')
            })
        
        # Publicar en TikTok si está activado
        if auto_publish_tiktok:
            job['progress'] = 90
            job['message'] = 'Publicando en TikTok...'

            try:
                from tiktok_uploader import TikTokUploader

                # Credenciales de TikTok desde variables de entorno
                tiktok_username = os.getenv('TIKTOK_USERNAME', 'stiffclipss')
                tiktok_password = os.getenv('TIKTOK_PASSWORD', 'password')

                print(f"🎵 Publicando {len(shorts)} shorts en TikTok...")
                print("⚠️  Se abrirá una ventana de Chrome para la subida semi-automática")

                with TikTokUploader(tiktok_username, tiktok_password, headless=False) as uploader:
                    if uploader.login():
                        for i, short in enumerate(shorts):
                            video_path = os.path.join(app.config['OUTPUT_FOLDER'], short['filename'])

                            # Usar el título y descripción generados por la IA
                            caption = short['title']
                            hashtags = ['viral', 'fyp', 'shorts', 'tiktok']

                            # Si hay copy de Instagram, usarlo como base
                            if short.get('instagram_copy'):
                                # Extraer hashtags del copy
                                copy_lines = short['instagram_copy'].split('\n')
                                for line in copy_lines:
                                    if line.strip().startswith('#'):
                                        tags = line.strip().split()
                                        hashtags.extend([tag.replace('#', '') for tag in tags if tag.startswith('#')])

                            # Eliminar duplicados
                            hashtags = list(dict.fromkeys(hashtags))[:5]  # Máximo 5 hashtags

                            print(f"   📤 Publicando short {i+1}/{len(shorts)}: {short['title']}")
                            success = uploader.upload_video(video_path, caption, hashtags)

                            if success:
                                short['tiktok_published'] = True
                                print(f"   ✅ Short {i+1} publicado en TikTok")
                            else:
                                short['tiktok_published'] = False
                                print(f"   ⚠️  Error publicando short {i+1}")

                            # Esperar entre publicaciones
                            if i < len(shorts) - 1:
                                time.sleep(30)

                        print("✅ Todos los shorts han sido publicados en TikTok")
                    else:
                        print("❌ No se pudo iniciar sesión en TikTok")

            except Exception as e:
                print(f"⚠️  Error publicando en TikTok: {e}")
                import traceback
                traceback.print_exc()

        # Limpiar archivos temporales
        job['progress'] = 95
        job['message'] = 'Finalizando...'

        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"🧹 Archivo de audio temporal eliminado")

        # Limpiar archivos huérfanos en uploads (archivos de audio que no deberían estar ahí)
        try:
            for file in os.listdir(app.config['UPLOAD_FOLDER']):
                if file.endswith('.mp3'):
                    orphan_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
                    os.remove(orphan_path)
                    print(f"🧹 Archivo huérfano eliminado: {file}")
        except Exception as e:
            print(f"⚠️  No se pudieron limpiar archivos huérfanos: {e}")

        # Completar trabajo
        job['status'] = 'completed'
        job['progress'] = 100

        published_count = sum(1 for s in shorts if s.get('tiktok_published', False))
        if auto_publish_tiktok and published_count > 0:
            job['message'] = f'¡Completado! {len(shorts)} shorts generados y {published_count} publicados en TikTok'
        else:
            job['message'] = f'¡Completado! {len(shorts)} shorts generados'

        job['shorts'] = shorts
        
    except Exception as e:
        job['status'] = 'error'
        job['message'] = f'Error: {str(e)}'
        print(f"Error procesando video {job_id}: {e}")
        import traceback
        traceback.print_exc()

@app.route('/api/status/<job_id>')
def get_status(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Trabajo no encontrado'}), 404
    
    return jsonify(jobs[job_id])

@app.route('/api/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Archivo no encontrado'}), 404
    
    return send_file(filepath, as_attachment=True)

@app.route('/api/jobs')
def list_jobs():
    return jsonify(list(jobs.values()))

# Template HTML (continúa en el siguiente mensaje debido al límite de longitud)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Shorts Creator v2.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding: 20px;
        }
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }
        .upload-zone {
            border: 3px dashed #667eea;
            border-radius: 20px;
            padding: 80px 40px;
            cursor: pointer;
            transition: all 0.3s ease;
            background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
            text-align: center;
        }
        .upload-zone:hover {
            border-color: #764ba2;
            background: linear-gradient(135deg, #f0f2ff 0%, #e8ebff 100%);
            transform: scale(1.02);
        }
        .upload-icon {
            font-size: 5rem;
            margin-bottom: 20px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 45px;
            border: none;
            border-radius: 50px;
            font-size: 1.2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            font-weight: 600;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.6);
        }
        .config-section {
            display: none;
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
        }
        .config-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        .config-item {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 15px;
        }
        .config-item label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .config-item select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
        }
        .progress-section { display: none; margin-top: 30px; }
        .progress-bar-container {
            background: #e0e0e0;
            border-radius: 15px;
            height: 40px;
            overflow: hidden;
            margin-bottom: 15px;
        }
        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            width: 0%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .results-section { display: none; margin-top: 30px; }
        .shorts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }
        .short-card {
            background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        .download-btn {
            width: 100%;
            background: #28a745;
            color: white;
            padding: 15px;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            cursor: pointer;
            font-weight: 600;
        }
        #fileInput { display: none; }
        .info-badge {
            display: inline-block;
            background: #e8ebff;
            color: #667eea;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 AI Shorts Creator v2.0</h1>
            <p>Transforma videos largos en shorts virales con inteligencia artificial</p>
        </div>
        
        <div class="main-card">
            <div id="uploadSection">
                <div class="upload-zone" id="uploadZone">
                    <div class="upload-icon">🎥</div>
                    <h2>Arrastra tu video aquí</h2>
                    <p>o haz clic para seleccionar un archivo</p>
                    <button class="btn" onclick="document.getElementById('fileInput').click()">
                        📂 Seleccionar Video
                    </button>
                    <p style="margin-top: 15px; font-size: 0.9rem; color: #999;">
                        Formatos soportados: MP4, MOV, AVI, MKV, WebM | Sin límite de tamaño ✨
                    </p>
                    <div style="margin-top: 25px;">
                        <span class="info-badge">Formatos: MP4, AVI, MOV, MKV, WebM</span>
                        <span class="info-badge">Sin límite de tamaño</span>
                    </div>
                </div>
                <input type="file" id="fileInput" accept="video/*">
                
                <div class="config-section" id="configSection">
                    <h3 style="color: #333; margin-bottom: 20px;">⚙️ Configuración</h3>
                    <div class="config-grid">
                        <div class="config-item">
                            <label for="aiProvider">🤖 Proveedor de IA</label>
                            <select id="aiProvider">
                                <option value="openai">OpenAI (GPT-3.5 Turbo + Whisper)</option>
                                <option value="claude">Claude (Haiku + Whisper)</option>
                            </select>
                        </div>
                        <div class="config-item">
                            <label for="shortDuration">⏱️ Duración de Shorts</label>
                            <select id="shortDuration">
                                <option value="short">Cortos: 35s - 1 min</option>
                                <option value="long">Largos: 1:10 min - 1:30 min</option>
                            </select>
                        </div>
                        <div class="config-item">
                            <label for="splitScreenMode">📹 Modo de Pantalla</label>
                            <select id="splitScreenMode">
                                <option value="">Normal (Pantalla completa)</option>
                                <option value="webcam_corner">Split Screen - Webcam + Contenido</option>
                            </select>
                        </div>
                        <div class="config-item">
                            <label for="autoPublishTikTok">🎵 Publicación Automática</label>
                            <select id="autoPublishTikTok">
                                <option value="false">No publicar automáticamente</option>
                                <option value="true">Publicar en TikTok automáticamente</option>
                            </select>
                        </div>
                        <div class="config-item">
                            <label for="viralTextLanguage">🌐 Idioma del Texto Viral</label>
                            <select id="viralTextLanguage">
                                <option value="auto">Automático (detectar del video)</option>
                                <option value="es">Español</option>
                                <option value="en">English</option>
                            </select>
                        </div>
                    </div>
                    <p style="color: #666; margin: 15px 0;">
                        💡 La IA analizará todo el video y creará automáticamente todos los shorts virales que encuentre
                    </p>
                    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 8px; margin: 15px 0;">
                        <p style="color: #856404; margin: 0; font-size: 0.9rem;">
                            <strong>🎮 Modo Split Screen:</strong> Ideal para videos de streamers con cámara en esquina. Divide la pantalla en dos: webcam arriba y contenido abajo.
                        </p>
                    </div>
                    <div style="background: #d4edda; border-left: 4px solid #28a745; padding: 12px; border-radius: 8px; margin: 15px 0;">
                        <p style="color: #155724; margin: 0; font-size: 0.9rem;">
                            <strong>🎵 Publicación Automática TikTok:</strong> Los shorts generados se publicarán automáticamente en tu cuenta @stiffclipss con hashtags optimizados para viralidad.
                        </p>
                    </div>
                    <button class="btn" id="processBtn" onclick="startProcessing()" style="margin-top: 20px;">
                        🚀 Analizar y Generar Shorts
                    </button>
                </div>
            </div>
            
            <div class="progress-section" id="progressSection">
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progressBar">0%</div>
                </div>
                <div id="progressMessage" style="text-align: center; color: #666; margin-top: 10px;">
                    Iniciando...
                </div>
            </div>
            
            <div class="results-section" id="resultsSection">
                <h2 style="text-align: center; margin-bottom: 20px;">✨ Shorts Generados</h2>
                <div id="shortsGrid" class="shorts-grid"></div>
                <button class="btn" onclick="location.reload()" style="margin-top: 30px; display: block; margin-left: auto; margin-right: auto;">
                    🔄 Procesar Otro Video
                </button>
            </div>
        </div>
    </div>
    
    <script>
        let currentJobId = null;
        let statusCheckInterval = null;
        
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const configSection = document.getElementById('configSection');
        const uploadSection = document.getElementById('uploadSection');
        const progressSection = document.getElementById('progressSection');
        const resultsSection = document.getElementById('resultsSection');
        
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            
            console.log('📥 Archivo soltado');
            
            if (e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                console.log('📄 Archivo:', file.name, 'Tamaño:', (file.size / 1024 / 1024 / 1024).toFixed(2), 'GB');
                
                if (file.type && !file.type.startsWith('video/')) {
                    alert('⚠️ Por favor selecciona un archivo de video.');
                    return;
                }
                
                uploadVideo(file);
            }
        });
        
        // Debug: verificar que el elemento existe
        console.log('🔍 fileInput element:', fileInput);
        console.log('🔍 uploadZone element:', uploadZone);

        fileInput.addEventListener('change', (e) => {
            console.log('📂 Archivo seleccionado - evento disparado!');
            console.log('📂 Event:', e);
            console.log('📂 Files:', e.target.files);

            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                console.log('📄 Archivo:', file.name, 'Tamaño:', (file.size / 1024 / 1024 / 1024).toFixed(2), 'GB');

                if (file.type && !file.type.startsWith('video/')) {
                    alert('⚠️ Por favor selecciona un archivo de video.');
                    return;
                }

                uploadVideo(file);
            } else {
                console.log('⚠️ No hay archivos seleccionados');
            }
        });
        
        function uploadVideo(file) {
            console.log('🚀 Iniciando subida de:', file.name);
            
            const formData = new FormData();
            formData.append('video', file);
            
            uploadSection.style.display = 'none';
            progressSection.style.display = 'block';
            resultsSection.style.display = 'none';
            
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 50);
                    updateProgress(percent, 'Subiendo video...');
                    console.log('📊 Progreso:', percent + '%');
                }
            });
            
            xhr.addEventListener('load', () => {
                console.log('✅ Respuesta recibida, status:', xhr.status);
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        console.log('📦 Respuesta:', response);
                        
                        if (response.job_id) {
                            currentJobId = response.job_id;
                            configSection.style.display = 'block';
                            uploadSection.style.display = 'block';
                            progressSection.style.display = 'none';
                            uploadZone.style.opacity = '0.5';
                            uploadZone.style.pointerEvents = 'none';
                        } else {
                            alert('❌ Error: ' + (response.error || 'Error desconocido'));
                            location.reload();
                        }
                    } catch (e) {
                        console.error('❌ Error parseando respuesta:', e);
                        alert('Error al procesar la respuesta del servidor');
                        location.reload();
                    }
                } else {
                    console.error('❌ Error HTTP:', xhr.status);
                    alert('Error al subir el archivo');
                    location.reload();
                }
            });
            
            xhr.addEventListener('error', () => {
                console.error('❌ Error de red');
                alert('Error de conexión');
                location.reload();
            });
            
            console.log('📡 Enviando petición POST...');
            xhr.open('POST', '/api/upload', true);
            xhr.send(formData);
        }
        
        async function startProcessing() {
            if (!currentJobId) return;

            const aiProvider = document.getElementById('aiProvider').value;
            const shortDuration = document.getElementById('shortDuration').value;
            const splitScreenMode = document.getElementById('splitScreenMode').value;
            const autoPublishTikTok = document.getElementById('autoPublishTikTok').value === 'true';
            const viralTextLanguage = document.getElementById('viralTextLanguage').value;

            try {
                const response = await fetch('/api/process/' + currentJobId, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        ai_provider: aiProvider,
                        short_duration: shortDuration,
                        split_screen_mode: splitScreenMode || null,
                        auto_publish_tiktok: autoPublishTikTok,
                        viral_text_language: viralTextLanguage
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    uploadSection.style.display = 'none';
                    progressSection.style.display = 'block';
                    startStatusCheck();
                } else {
                    alert('❌ Error: ' + data.error);
                }
            } catch (error) {
                alert('❌ Error al iniciar procesamiento: ' + error.message);
            }
        }
        
        function startStatusCheck() {
            statusCheckInterval = setInterval(checkStatus, 2000);
        }
        
        async function checkStatus() {
            if (!currentJobId) return;
            
            try {
                const response = await fetch(`/api/status/${currentJobId}`);
                const data = await response.json();
                
                document.getElementById('progressBar').style.width = data.progress + '%';
                document.getElementById('progressBar').textContent = data.progress + '%';
                document.getElementById('progressMessage').textContent = data.message;
                
                if (data.status === 'completed') {
                    clearInterval(statusCheckInterval);
                    showResults(data.shorts);
                } else if (data.status === 'error') {
                    clearInterval(statusCheckInterval);
                    alert('❌ ' + data.message);
                    location.reload();
                }
            } catch (error) {
                console.error('Error checking status:', error);
            }
        }
        
        function showResults(shorts) {
            progressSection.style.display = 'none';
            resultsSection.style.display = 'block';
            
            const grid = document.getElementById('shortsGrid');
            grid.innerHTML = '';
            
            shorts.forEach(short => {
                const card = document.createElement('div');
                card.className = 'short-card';

                let htmlContent = '<div style="display: flex; justify-content: space-between; margin-bottom: 15px;">';
                htmlContent += '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;">';
                htmlContent += short.id;
                htmlContent += '</div>';
                htmlContent += '<div style="background: #ffc107; color: #333; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9rem;">';
                htmlContent += '⭐ ' + short.relevance_score + '/100';
                htmlContent += '</div></div>';
                htmlContent += '<div style="color: #333; font-size: 1.3rem; font-weight: 600; margin-bottom: 10px;">' + short.title + '</div>';
                htmlContent += '<div style="color: #666; font-size: 0.95rem; line-height: 1.6; margin-bottom: 15px;">' + short.description + '</div>';
                htmlContent += '<div style="display: flex; gap: 15px; margin-bottom: 15px; color: #999; font-size: 0.9rem;">';
                htmlContent += '<span>⏱️ ' + Math.round(short.duration) + 's</span>';
                htmlContent += '<span>📐 9:16</span>';
                htmlContent += '<span>🕐 ' + formatTime(short.start_time) + '</span>';
                htmlContent += '</div>';

                if (short.instagram_copy) {
                    htmlContent += '<div style="background: #f8f9ff; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #667eea;">';
                    htmlContent += '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">';
                    htmlContent += '<strong style="color: #667eea;">📱 Copy para Instagram:</strong>';
                    htmlContent += '<button id="btn-copy-' + short.id + '" onclick="copiarTexto(' + short.id + ')" style="background: #667eea; color: white; border: none; padding: 5px 12px; border-radius: 5px; cursor: pointer; font-size: 0.85rem;">';
                    htmlContent += '📋 Copiar</button></div>';
                    htmlContent += '<pre id="copy-' + short.id + '" style="white-space: pre-wrap; font-family: inherit; color: #333; margin: 0; font-size: 0.9rem; line-height: 1.6;"></pre>';
                    htmlContent += '</div>';
                }

                htmlContent += '<button class="download-btn" onclick="downloadShort(&quot;' + short.filename + '&quot;)">';
                htmlContent += '⬇️ Descargar Short</button>';

                card.innerHTML = htmlContent;
                grid.appendChild(card);

                // Agregar el contenido del Instagram copy de forma segura
                if (short.instagram_copy) {
                    const copyElement = document.getElementById('copy-' + short.id);
                    if (copyElement) {
                        copyElement.textContent = short.instagram_copy;
                    }
                }
            });
        }
        
        function downloadShort(filename) {
            window.location.href = `/api/download/${filename}`;
        }
        
        function formatTime(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${mins}:${secs.toString().padStart(2, '0')}`;
        }
        
        function copiarTexto(shortId) {
            const texto = document.getElementById(`copy-${shortId}`).textContent;
            const btn = document.getElementById(`btn-copy-${shortId}`);
            
            navigator.clipboard.writeText(texto).then(() => {
                const textoOriginal = btn.textContent;
                btn.textContent = '✅ Copiado!';
                btn.style.background = '#28a745';
                setTimeout(() => {
                    btn.textContent = textoOriginal;
                    btn.style.background = '#667eea';
                }, 2000);
            }).catch(err => {
                console.error('Error al copiar:', err);
                alert('Error al copiar. Selecciona el texto manualmente.');
            });
        }
        
        function updateProgress(percent, message) {
            document.getElementById('progressBar').style.width = percent + '%';
            document.getElementById('progressBar').textContent = percent + '%';
            document.getElementById('progressMessage').textContent = message;
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🚀 Iniciando AI Shorts Creator...")
    print("📍 Servidor disponible en: http://localhost:3000")
    app.run(host='0.0.0.0', port=3000, debug=True)
