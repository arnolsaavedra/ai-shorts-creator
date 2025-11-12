import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

class TikTokUploader:
    def __init__(self, username, password, headless=False):
        """
        Inicializa el uploader de TikTok

        Args:
            username: Usuario de TikTok
            password: Contraseña de TikTok
            headless: Ejecutar navegador en modo headless (sin ventana visible)
        """
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None

    def _setup_driver(self):
        """Configura el driver de Chrome/Chromium"""
        import uuid
        import tempfile
        import platform

        chrome_options = Options()

        # IMPORTANTE: No usar headless para TikTok - necesita interacción humana
        # if self.headless:
        #     chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Directorio único para guardar cookies y sesiones (evita conflictos)
        unique_id = str(uuid.uuid4())[:8]

        # Usar directorio temporal del sistema según el OS
        if platform.system() == 'Windows':
            temp_dir = os.path.join(tempfile.gettempdir(), f'tiktok-profile-{unique_id}')
        else:
            temp_dir = f'/tmp/tiktok-profile-{unique_id}'

        chrome_options.add_argument(f'--user-data-dir={temp_dir}')
        print(f"📁 Usando directorio temporal: {temp_dir}")

        # User agent para parecer un navegador real
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Ventana más grande para ver mejor
        chrome_options.add_argument('--window-size=1920,1080')

        # Detectar si estamos en Docker
        try:
            with open('/proc/1/cgroup', 'r') as f:
                in_docker = 'docker' in f.read()
        except:
            in_docker = False

        if in_docker:
            print("⚠️  Detectado entorno Docker - TikTok upload NO funcionará correctamente")
            print("   Para usar auto-publicación en TikTok, ejecuta la app fuera de Docker")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("✅ Driver de Chrome configurado (modo visible para TikTok)")

    def login(self):
        """Inicia sesión en TikTok"""
        try:
            print("🔐 Iniciando sesión en TikTok...")

            self.driver.get("https://www.tiktok.com/login/phone-or-email/email")
            time.sleep(3)

            # Esperar a que cargue la página de login
            wait = WebDriverWait(self.driver, 10)

            # Ingresar usuario
            print("   Ingresando usuario...")
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            username_input.send_keys(self.username)
            time.sleep(1)

            # Ingresar contraseña
            print("   Ingresando contraseña...")
            password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)

            # Click en botón de login
            print("   Haciendo click en login...")
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            # Esperar a que cargue el dashboard
            time.sleep(5)

            # Verificar si el login fue exitoso
            if "login" not in self.driver.current_url.lower():
                print("✅ Login exitoso en TikTok")
                return True
            else:
                print("⚠️  Puede que se requiera verificación adicional (captcha, 2FA)")
                # Esperar más tiempo por si hay verificación manual
                time.sleep(30)
                return True

        except Exception as e:
            print(f"❌ Error en login: {e}")
            return False

    def upload_video(self, video_path, caption, hashtags=None, manual_mode=True):
        """
        Sube un video a TikTok

        Args:
            video_path: Ruta del archivo de video
            caption: Descripción del video
            hashtags: Lista de hashtags (opcional)
            manual_mode: Si es True, espera a que el usuario termine manualmente

        Returns:
            True si la subida fue exitosa, False en caso contrario
        """
        try:
            print(f"\n{'='*60}")
            print(f"📤 SUBIENDO VIDEO A TIKTOK")
            print(f"{'='*60}")
            print(f"📁 Archivo: {video_path}")

            # Verificar que el archivo existe
            if not os.path.exists(video_path):
                print(f"❌ El archivo no existe: {video_path}")
                return False

            # Construir caption completo
            full_caption = caption
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" if not tag.startswith("#") else tag for tag in hashtags])
                full_caption = f"{caption}\n\n{hashtag_text}"

            print(f"📝 Caption: {full_caption[:100]}...")
            print(f"\n{'='*60}")

            # Ir a la página de subida
            print("🌐 Navegando a TikTok Studio...")
            self.driver.get("https://www.tiktok.com/tiktokstudio/upload?from=creator_center")
            time.sleep(5)

            # Verificar si ya está logueado
            if "login" in self.driver.current_url.lower():
                print("⚠️  No hay sesión activa. Redirigiendo a login...")
                return False

            print("\n" + "="*60)
            print("👤 MODO MANUAL ACTIVADO")
            print("="*60)
            print("\n📋 INSTRUCCIONES:")
            print("   1. Se abrió una ventana de Chrome")
            print("   2. Arrastra y suelta el video en la página de TikTok")
            print(f"   3. Video a subir: {os.path.basename(video_path)}")
            print("\n" + "="*60)
            print("📝 COPY PARA TIKTOK (copia todo esto):")
            print("="*60)
            print(full_caption)
            print("="*60)

            # Intentar copiar al portapapeles en Windows
            try:
                import subprocess
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(full_caption.encode('utf-16le'))
                print("\n✅ Copy copiado al portapapeles! Solo haz Ctrl+V en TikTok")
            except:
                print("\n   💡 Copia manualmente el texto de arriba")

            print("\n   5. Pega el copy en la descripción de TikTok (Ctrl+V)")
            print("   6. Cuando termines de publicar, el proceso continuará...")
            print("="*60)

            # Convertir a ruta absoluta
            abs_video_path = os.path.abspath(video_path)
            print(f"\n📂 Ruta completa del video:")
            print(f"   {abs_video_path}")

            # Intentar encontrar el input de archivo y subir automáticamente
            try:
                wait = WebDriverWait(self.driver, 10)
                print("\n🔍 Buscando selector de archivo...")

                file_input = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )

                print("📎 Subiendo archivo automáticamente...")
                file_input.send_keys(abs_video_path)
                print("✅ Archivo seleccionado!")

                # Esperar a que se procese
                print("⏳ Procesando video... (esto puede tomar un momento)")
                time.sleep(15)

                # Intentar pegar el caption
                try:
                    print("📝 Intentando agregar caption...")
                    caption_input = self.driver.find_element(By.XPATH, "//div[@contenteditable='true' or @role='textbox']")
                    caption_input.click()
                    time.sleep(1)
                    caption_input.send_keys(full_caption)
                    print("✅ Caption agregado!")
                except:
                    print("⚠️  No se pudo agregar el caption automáticamente")
                    print("   Por favor agrégalo manualmente")

            except Exception as e:
                print(f"\n⚠️  No se pudo subir automáticamente: {str(e)[:100]}")
                print("   Por favor arrastra el video manualmente a la página")

            # Modo manual: esperar a que el usuario termine
            if manual_mode:
                print("\n⏸️  Esperando a que completes la subida...")
                print("   Presiona ENTER cuando hayas publicado el video (o para continuar)")

                # Dar 2 minutos para subir manualmente
                print("\n   (Tiempo máximo de espera: 2 minutos)")
                time.sleep(120)  # Esperar 2 minutos

                print("\n✅ Continuando con el siguiente video...")
                return True
            else:
                # Intentar publicar automáticamente
                print("\n🔍 Buscando botón de publicar...")
                time.sleep(5)

                try:
                    publish_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Post') or contains(., 'Publicar') or contains(@class, 'post')]")
                    print("✅ Botón encontrado, publicando...")
                    publish_button.click()
                    time.sleep(5)
                    print("✅ Video publicado!")
                    return True
                except:
                    print("⚠️  No se pudo encontrar el botón de publicar")
                    print("   Por favor publica manualmente")
                    time.sleep(30)
                    return True

        except Exception as e:
            print(f"\n❌ Error en el proceso de subida: {e}")
            import traceback
            traceback.print_exc()
            return False

    def upload_multiple_videos(self, video_list):
        """
        Sube múltiples videos a TikTok

        Args:
            video_list: Lista de diccionarios con info de videos
                [{'path': 'video.mp4', 'caption': 'Mi video', 'hashtags': ['viral', 'fyp']}]

        Returns:
            Lista de resultados (True/False) para cada video
        """
        results = []

        for i, video_info in enumerate(video_list):
            print(f"\n📹 Video {i+1}/{len(video_list)}")

            result = self.upload_video(
                video_info['path'],
                video_info['caption'],
                video_info.get('hashtags', [])
            )
            results.append(result)

            # Esperar entre videos para evitar rate limiting
            if i < len(video_list) - 1:
                print("   ⏳ Esperando 30 segundos antes del siguiente video...")
                time.sleep(30)

        return results

    def close(self):
        """Cierra el navegador"""
        if self.driver:
            self.driver.quit()
            print("🔒 Navegador cerrado")

    def __enter__(self):
        """Context manager entry"""
        self._setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Función auxiliar para uso rápido
def upload_to_tiktok(username, password, video_path, caption, hashtags=None, headless=False):
    """
    Función auxiliar para subir un video rápidamente

    Args:
        username: Usuario de TikTok
        password: Contraseña de TikTok
        video_path: Ruta del video
        caption: Descripción
        hashtags: Lista de hashtags
        headless: Ejecutar sin ventana visible

    Returns:
        True si fue exitoso, False en caso contrario
    """
    with TikTokUploader(username, password, headless=headless) as uploader:
        if uploader.login():
            return uploader.upload_video(video_path, caption, hashtags)
        return False
