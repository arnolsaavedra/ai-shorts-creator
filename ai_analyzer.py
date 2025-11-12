import os
import json
import time
try:
    from openai import OpenAI
except ImportError:
    import openai
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    import anthropic
    Anthropic = None

class AIAnalyzer:
    def __init__(self, provider='openai'):
        self.provider = provider
        
        # Inicializar valores por defecto de duración
        self.min_duration = 35
        self.max_duration = 60
        self.optimal_duration = 50
        
        if provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY no configurada")
            
            if OpenAI:
                self.client = OpenAI(api_key=api_key)
            else:
                openai.api_key = api_key
                self.client = None
                
        elif provider == 'claude':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY no configurada")
            
            if Anthropic:
                self.client = Anthropic(api_key=api_key)
            else:
                anthropic.api_key = api_key
                self.client = None
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")
    
    def transcribe_audio(self, audio_path):
        """
        Transcribe el audio usando Whisper de OpenAI
        Para archivos grandes, divide en chunks
        """
        print(f"🎤 Transcribiendo audio con Whisper...")
        
        # Verificar tamaño del audio
        audio_size = os.path.getsize(audio_path)
        max_size = 24 * 1024 * 1024  # 24MB (límite de Whisper es 25MB)
        
        if audio_size > max_size:
            print(f"⚠️  Audio muy grande ({audio_size/1024/1024:.1f}MB), dividiendo en chunks...")
            return self._transcribe_audio_chunked(audio_path)
        
        return self._transcribe_audio_single(audio_path)
    
    def _transcribe_audio_single(self, audio_path):
        """Transcribe audio completo de una vez"""
        if self.provider == 'openai':
            client = self.client
        else:
            print("⚠️  Claude no soporta transcripción. Usando OpenAI Whisper...")
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        with open(audio_path, 'rb') as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        return {
            'text': transcript.text,
            'segments': [
                {
                    'start': seg.start,
                    'end': seg.end,
                    'text': seg.text
                }
                for seg in transcript.segments
            ]
        }
    
    def _transcribe_audio_chunked(self, audio_path):
        """Transcribe audio en chunks para archivos grandes"""
        from pydub import AudioSegment
        
        print("📊 Dividiendo audio en chunks...")
        
        # Cargar audio
        audio = AudioSegment.from_file(audio_path)
        duration_ms = len(audio)
        chunk_length_ms = 10 * 60 * 1000  # 10 minutos
        
        all_segments = []
        chunk_num = 1
        
        if self.provider == 'openai':
            client = self.client
        else:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Procesar en chunks
        for start_ms in range(0, duration_ms, chunk_length_ms):
            end_ms = min(start_ms + chunk_length_ms, duration_ms)
            chunk = audio[start_ms:end_ms]
            
            # Guardar chunk temporal
            chunk_path = audio_path.replace('.mp3', f'_chunk_{chunk_num}.mp3')
            chunk.export(chunk_path, format="mp3", bitrate="64k")
            
            print(f"🎤 Transcribiendo chunk {chunk_num} ({start_ms/1000:.0f}s - {end_ms/1000:.0f}s)...")
            
            try:
                # Reintentos para rate limits
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        with open(chunk_path, 'rb') as audio_file:
                            transcript = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                response_format="verbose_json",
                                timestamp_granularities=["segment"]
                            )
                        
                        # Ajustar timestamps al offset del chunk
                        offset_seconds = start_ms / 1000
                        for seg in transcript.segments:
                            all_segments.append({
                                'start': seg.start + offset_seconds,
                                'end': seg.end + offset_seconds,
                                'text': seg.text
                            })
                        
                        print(f"  ✅ Chunk {chunk_num} transcrito")
                        
                        # Delay entre chunks
                        if start_ms + chunk_length_ms < duration_ms:
                            time.sleep(2)
                        
                        break  # Éxito
                        
                    except Exception as e:
                        error_str = str(e)
                        if 'rate_limit' in error_str.lower() or '429' in error_str:
                            if attempt < max_retries - 1:
                                wait_time = 20 * (attempt + 1)
                                print(f"  ⏳ Rate limit en transcripción, esperando {wait_time}s...")
                                time.sleep(wait_time)
                            else:
                                raise
                        else:
                            raise
                
            except Exception as e:
                print(f"  ⚠️  Error en chunk {chunk_num}: {e}")
            
            finally:
                # Limpiar chunk temporal
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
            
            chunk_num += 1
        
        # Combinar texto completo
        full_text = ' '.join([seg['text'] for seg in all_segments])
        
        print(f"✅ Transcripción completa: {len(all_segments)} segmentos")
        
        return {
            'text': full_text,
            'segments': all_segments
        }
    
    def find_viral_moments(self, transcript, video_duration, short_duration='short'):
        """
        Analiza la transcripción y encuentra TODOS los momentos virales
        short_duration: 'short' (35-60s) o 'long' (70-90s)
        """
        # Configurar rangos según duración seleccionada
        if short_duration == 'long':
            self.min_duration = 70
            self.max_duration = 90
            self.optimal_duration = 80
            duration_text = "70-90 segundos (IDEAL: 75-85 segundos)"
            example_end = 85
        else:  # short
            self.min_duration = 35
            self.max_duration = 60
            self.optimal_duration = 50
            duration_text = "35-60 segundos (IDEAL: 45-55 segundos)"
            example_end = 55

        print(f"🔍 Analizando contenido para encontrar momentos virales ({duration_text})...")

        # Calcular tokens estimados (aproximadamente 1 token = 4 caracteres en promedio)
        transcript_text = json.dumps(transcript['segments'])
        estimated_tokens = len(transcript_text) // 4

        # Límite de tokens: GPT-3.5-turbo tiene 16K, dejamos margen para el prompt y respuesta
        max_tokens = 10000  # Límite seguro para el contenido

        print(f"📊 Tokens estimados: {estimated_tokens:,}")

        # Si excede el límite, usar método chunked
        if estimated_tokens > max_tokens:
            print(f"⚠️  Transcripción muy grande ({estimated_tokens:,} tokens > {max_tokens:,}), procesando en chunks...")
            return self._find_viral_moments_chunked(transcript, video_duration, duration_text, example_end)

        return self._find_viral_moments_single(transcript, video_duration, duration_text, example_end)
    
    def _find_viral_moments_single(self, transcript, video_duration, duration_text, example_end):
        """Procesa toda la transcripción de una vez"""
        prompt = f"""Analiza la siguiente transcripción de video y encuentra TODOS los momentos interesantes y virales para crear shorts.

Transcripción con timestamps:
{json.dumps(transcript['segments'], indent=2)}

Duración total del video: {video_duration} segundos

CRITERIOS IMPORTANTES:
1. Cada momento debe tener {duration_text}
2. Encuentra TODOS los momentos buenos - no hay límite de cantidad
3. Busca momentos con:
   - Hooks fuertes al inicio (primeros 3 segundos cruciales)
   - Contenido valioso, entretenido o sorprendente
   - Conclusiones o punchlines satisfactorias
   - Potencial viral máximo
4. Los momentos NO deben sobrelaparse
5. Prioriza contenido auto-contenido (que funcione sin contexto)
6. NO importa si los clips están en secuencia - pueden estar dispersos en el video

7. **MUY IMPORTANTE - COPY PARA REDES SOCIALES:**
   Para cada momento, genera un COPY que:
   - **DEBE HABLAR ESPECÍFICAMENTE del contenido de ESE clip**
   - Lee la transcripción del momento y menciona las frases/temas exactos que se dicen
   - Usa las palabras clave del momento para que el copy sea relevante
   - Enganche desde la primera línea mencionando el tema específico
   - Use emojis relacionados con el tema del clip
   - Sea corto pero impactante (2-4 líneas máximo)
   - Incluya 3-5 hashtags relevantes AL TEMA del clip

Responde ÚNICAMENTE con un JSON válido en este formato:
{{
  "moments": [
    {{
      "start_time": 10.5,
      "end_time": {example_end},
      "title": "Título específico sobre LO QUE SE DICE en este momento",
      "description": "Descripción de QUÉ SE HABLA exactamente en este segmento",
      "score": 95,
      "key_phrases": ["FRASE VIRAL CORTA Y DIRECTA DEL CONTENIDO (máximo 5-8 palabras)", "otra frase clave"],
      "instagram_copy": "🔥 [Mención específica del tema del clip]\\n\\n[Frase o concepto que se menciona en el clip]\\n\\n#hashtag1 #hashtag2 #hashtag3"
    }}
  ]
}}

**MUY IMPORTANTE - KEY_PHRASES:**
- La PRIMERA key_phrase se mostrará como TEXTO GRANDE en el video
- DEBE ser una frase CORTA, DIRECTA y VIRAL (máximo 5-8 palabras)
- DEBE extraerse ÚNICAMENTE del texto que se dice ENTRE start_time y end_time de ESE momento específico
- Lee SOLO la transcripción de ese segmento temporal, NO mezcles contenido de otros momentos
- DEBE captar la atención inmediatamente
- Puede ser vulgar, controversial o llamativa si eso aparece en el video
- NO uses frases genéricas
- NO uses información de otros momentos del video

EJEMPLO CORRECTO:
Si entre 10.5s y 55.5s el clip dice "Los perros pueden detectar el cáncer con un 95% de precisión":
- key_phrases: ["Perros detectan cáncer 95%", "diagnóstico temprano"]
- instagram_copy: "🐕 ¿Sabías que los perros detectan cáncer con 95% de precisión?\\n\\nEsto cambia todo lo que sabíamos sobre diagnóstico temprano\\n\\n#perros #cancer #ciencia #viral"

EJEMPLO INCORRECTO (genérico o de otro momento):
- key_phrases: ["momento interesante", "contenido viral"]  ← Genérico
- key_phrases: ["tema que se habla después del minuto 2"]  ← De otro momento
- instagram_copy: "🔥 No te pierdas esto\\n\\nContenido increíble\\n\\n#viral #fyp"  ← Genérico

**IMPORTANTE**: Para cada momento, PRIMERO identifica qué texto aparece EXACTAMENTE entre start_time y end_time en la transcripción, LUEGO genera la key_phrase basándote SOLO en ese texto.

Genera tantos momentos como encuentres (mínimo 2, máximo 15). Prioriza CALIDAD sobre cantidad.
Asegúrate de que el JSON sea válido, los tiempos estén dentro de 0 a {video_duration} segundos, y que CADA copy hable del contenido REAL del clip."""

        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=[
                        {"role": "system", "content": "Eres un experto en crear contenido viral para redes sociales. DEBES analizar cada momento individualmente mirando SOLO el texto entre start_time y end_time de ese momento. Las key_phrases y copies deben reflejar ÚNICAMENTE lo que se dice en ESE segmento temporal específico, NO mezcles contenido de otros momentos. Respondes únicamente con JSON válido sin texto adicional."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7
                )

                content = response.choices[0].message.content
                # Limpiar posibles caracteres extra o texto antes/después del JSON
                content = content.strip()
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = content[start:end]
                else:
                    json_str = content

                result = json.loads(json_str)

            else:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )

                content = response.content[0].text
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
                result = json.loads(json_str)

        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear JSON de la respuesta de IA: {e}")
            print(f"📄 Respuesta recibida (primeros 500 chars): {content[:500] if 'content' in locals() else 'N/A'}")
            print(f"🔧 JSON extraído: {json_str[:500] if 'json_str' in locals() else 'N/A'}")

            # Fallback: crear una respuesta mínima
            print("⚠️  Usando fallback: generando momentos básicos desde transcripción...")
            result = {
                "moments": []
            }

            # Intentar crear al menos 2 momentos básicos desde la transcripción
            if len(transcript['segments']) > 0:
                segment_duration = video_duration / max(1, len(transcript['segments']))
                mid_point = len(transcript['segments']) // 2

                result["moments"].append({
                    "start_time": 0,
                    "end_time": min(45, video_duration),
                    "title": "Momento inicial del video",
                    "description": "Clip del inicio del contenido",
                    "score": 70,
                    "key_phrases": ["contenido inicial"],
                    "instagram_copy": "🎬 Mira este momento!\n\n#viral #shorts #contenido"
                })

                if video_duration > 60:
                    result["moments"].append({
                        "start_time": max(0, video_duration // 2 - 20),
                        "end_time": min(video_duration // 2 + 25, video_duration),
                        "title": "Momento destacado",
                        "description": "Clip del medio del contenido",
                        "score": 70,
                        "key_phrases": ["momento destacado"],
                        "instagram_copy": "🔥 No te pierdas esto!\n\n#viral #shorts #contenido"
                    })
        
        moments = []
        for moment in result.get('moments', []):
            duration = moment['end_time'] - moment['start_time']
            
            # Ajustar duración según el rango configurado
            if duration < self.min_duration:
                moment['end_time'] = min(moment['start_time'] + self.optimal_duration, video_duration)
            elif duration > self.max_duration:
                moment['end_time'] = moment['start_time'] + self.max_duration
            elif duration < (self.min_duration + 5):
                moment['end_time'] = min(moment['start_time'] + self.optimal_duration, video_duration)
            
            # Asegurar que no exceda la duración del video
            if moment['end_time'] > video_duration:
                moment['end_time'] = video_duration
                moment['start_time'] = max(0, video_duration - self.optimal_duration)
            
            if 'instagram_copy' not in moment:
                moment['instagram_copy'] = self._generate_default_copy(moment)
            
            moments.append(moment)
        
        print(f"✅ Se encontraron {len(moments)} momentos virales")
        return moments
    
    def _find_viral_moments_chunked(self, transcript, video_duration, duration_text, example_end):
        """Procesa la transcripción en chunks para videos muy largos"""
        segments = transcript['segments']
        chunk_duration = 600  # 10 minutos por chunk
        all_moments = []

        current_time = 0
        chunk_num = 1

        while current_time < video_duration:
            end_time = min(current_time + chunk_duration, video_duration)

            chunk_segments = [
                seg for seg in segments
                if seg['start'] >= current_time and seg['end'] <= end_time
            ]

            if not chunk_segments:
                current_time = end_time
                continue

            print(f"📊 Analizando chunk {chunk_num} ({current_time}s - {end_time}s)...")

            # Resumir segmentos largos para reducir tokens
            # Tomar cada 3er segmento si hay demasiados
            if len(chunk_segments) > 100:
                sample_segments = chunk_segments[::3]
                print(f"   Reduciendo de {len(chunk_segments)} a {len(sample_segments)} segmentos para análisis")
            else:
                sample_segments = chunk_segments

            prompt = f"""Analiza este segmento de video (de {current_time}s a {end_time}s) y encuentra momentos virales de {duration_text}.

Segmento (muestra):
{json.dumps(sample_segments[:80], indent=2)}  

IMPORTANTE:
- Busca 1-3 momentos buenos en este segmento
- Cada momento: {duration_text}
- Los tiempos deben estar entre {current_time} y {end_time} segundos
- Genera copy atractivo para Instagram

Responde ÚNICAMENTE con JSON válido:
{{
  "moments": [
    {{
      "start_time": {current_time + 10},
      "end_time": {current_time + example_end},
      "title": "Título llamativo",
      "description": "Por qué es viral",
      "score": 90,
      "key_phrases": ["frase clave"],
      "instagram_copy": "🔥 Copy con emojis y CTA\\n\\n#hashtag1 #hashtag2"
    }}
  ]
}}"""

            try:
                # Reintentos para rate limits
                max_retries = 3
                retry_delay = 10
                
                for attempt in range(max_retries):
                    try:
                        if self.provider == 'openai':
                            response = self.client.chat.completions.create(
                                model="gpt-3.5-turbo-1106",
                                messages=[
                                    {"role": "system", "content": "Analista de contenido viral. Responde solo JSON."},
                                    {"role": "user", "content": prompt}
                                ],
                                response_format={"type": "json_object"},
                                temperature=0.7
                            )
                            result = json.loads(response.choices[0].message.content)
                        else:
                            response = self.client.messages.create(
                                model="claude-3-haiku-20240307",
                                max_tokens=2048,
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.7
                            )
                            content = response.content[0].text
                            start = content.find('{')
                            end = content.rfind('}') + 1
                            json_str = content[start:end]
                            result = json.loads(json_str)
                        
                        break  # Éxito
                        
                    except Exception as e:
                        error_str = str(e)
                        if 'rate_limit' in error_str.lower() or '429' in error_str:
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (attempt + 1)
                                print(f"  ⏳ Rate limit alcanzado, esperando {wait_time}s...")
                                time.sleep(wait_time)
                            else:
                                raise
                        else:
                            raise
                
                # Agregar momentos de este chunk
                chunk_moments = result.get('moments', [])
                for moment in chunk_moments:
                    if 'instagram_copy' not in moment:
                        moment['instagram_copy'] = self._generate_default_copy(moment)
                    all_moments.append(moment)
                
                print(f"  ✅ Encontrados {len(chunk_moments)} momentos en chunk {chunk_num}")
                
                # Delay entre chunks
                if current_time < video_duration - chunk_duration:
                    if self.provider == 'claude':
                        time.sleep(3)
                    else:
                        time.sleep(1)
                
            except Exception as e:
                print(f"  ⚠️  Error en chunk {chunk_num}: {e}")
            
            current_time = end_time
            chunk_num += 1
        
        # Validar y ajustar duraciones
        final_moments = []
        for moment in all_moments:
            duration = moment['end_time'] - moment['start_time']
            
            if duration < self.min_duration:
                moment['end_time'] = min(moment['start_time'] + self.optimal_duration, video_duration)
            elif duration > self.max_duration:
                moment['end_time'] = moment['start_time'] + self.max_duration
            
            if moment['end_time'] > video_duration:
                moment['end_time'] = video_duration
                moment['start_time'] = max(0, video_duration - self.optimal_duration)
            
            final_moments.append(moment)
        
        # Ordenar por score y eliminar solapamientos
        final_moments.sort(key=lambda x: x.get('score', 0), reverse=True)
        unique_moments = []
        
        for moment in final_moments:
            overlap = False
            for existing in unique_moments:
                if (moment['start_time'] < existing['end_time'] and 
                    moment['end_time'] > existing['start_time']):
                    overlap = True
                    break
            
            if not overlap:
                unique_moments.append(moment)
        
        print(f"✅ Total: {len(unique_moments)} momentos únicos encontrados")
        return unique_moments
    
    def _generate_default_copy(self, moment):
        """Genera un copy por defecto si la IA no lo proporciona"""
        title = moment.get('title', 'Momento destacado')
        description = moment.get('description', 'Contenido viral')
        
        copy = f"🎯 {title}\n\n"
        copy += f"{description}\n\n"
        copy += "💬 ¿Qué opinas? Comenta abajo 👇\n\n"
        copy += "#viral #contenido #shorts"
        
        return copy
    
    def generate_subtitles(self, transcript, start_time, end_time):
        """Genera subtítulos optimizados para el segmento específico"""
        print(f"💬 Generando subtítulos para segmento {start_time}-{end_time}s...")
        
        relevant_segments = [
            seg for seg in transcript['segments']
            if (seg['start'] >= start_time and seg['end'] <= end_time) or
               (seg['start'] <= start_time and seg['end'] >= start_time) or
               (seg['start'] <= end_time and seg['end'] >= end_time)
        ]
        
        subtitles = []
        for seg in relevant_segments:
            sub_start = max(0, seg['start'] - start_time)
            sub_end = min(end_time - start_time, seg['end'] - start_time)
            
            text = seg['text'].strip()
            words = text.split()
            
            if len(words) <= 8:
                subtitles.append({
                    'start': sub_start,
                    'end': sub_end,
                    'text': text
                })
            else:
                chunk_duration = (sub_end - sub_start) / len(words)
                current_time = sub_start
                
                for i in range(0, len(words), 7):
                    chunk = ' '.join(words[i:i+7])
                    chunk_end = current_time + (len(words[i:i+7]) * chunk_duration)
                    
                    subtitles.append({
                        'start': current_time,
                        'end': min(chunk_end, sub_end),
                        'text': chunk
                    })
                    
                    current_time = chunk_end
        
        return subtitles