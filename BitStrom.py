import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from functools import partial
import threading
import cv2
import webbrowser
import requests
import os
import sys

# ---------- COLORES ----------
COLORS = {
    'primary': (234/255, 245/255, 234/255, 1),     # #eaf5ea
    'secondary': (236/255, 236/255, 236/255, 1),   # #ececec
    'background': (238/255, 238/255, 238/255, 1),  # #eeeeee
    'text': (43/255, 34/255, 29/255, 1),           # #2b221d
    'highlight': (234/255, 245/255, 234/255, 1),   # #eaf5ea
    'accent': (160/255, 210/255, 160/255, 1)
}

Window.size = (360, 640)
Window.clearcolor = COLORS['background']

APP_NAME = "EcoAves"
WEB_URL = "https://zayriaz28.github.io/EcoAves.v2/Ficha-Aves.html"
captured_birds = []

# --------- RUTA BASE PARA IMÁGENES ---------
# Calcula la ruta absoluta al directorio del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_image_path(rel_path):
    # Si la ruta ya es absoluta, la retorna tal cual
    if os.path.isabs(rel_path):
        return rel_path
    # Si existe en la ruta relativa al script, retorna esa
    abs_path = os.path.join(BASE_DIR, rel_path)
    if os.path.exists(abs_path):
        return abs_path
    # Si no existe, retorna la ruta original (por si acaso)
    return rel_path

# ---------- DATOS DE AVES NICARAGÜENSES ----------
NICARAGUAN_BIRDS = [
    {
        "nombre_comun": "Cenzontle",
        "nombre_cientifico": "Mimus gilvus",
        "descripcion": "Ave imitadora de cantos, muy activa y adaptable.",
        "caracteristicas": "Gris con pecho claro, cola larga.",
        "foto": "aves/cenzontle.jpg"
    },
    {
        "nombre_comun": "Chachalaca",
        "nombre_cientifico": "Ortalis vetula",
        "descripcion": "Ave de hábitos gregarios, conocida por su canto fuerte y ronco.",
        "caracteristicas": "Marrón con garganta blanca, tamaño mediano a grande.",
        "foto": "aves/chachalaca.jpg"
    },
    {
        "nombre_comun": "Chorcha",
        "nombre_cientifico": "Psarocolius montezuma",
        "descripcion": "Ave grande y llamativa, famosa por su canto peculiar y su nido colgante.",
        "caracteristicas": "Negra con pico amarillo y cola marrón, muy vistosa.",
        "foto": "aves/chorcha.jpg"
    },
    {
        "nombre_comun": "Colibrí",
        "nombre_cientifico": "Trochilidae (varias especies)",
        "descripcion": "Pequeñas aves de rápido vuelo, muy comunes en jardines y áreas rurales.",
        "caracteristicas": "Plumaje brillante, pico largo y delgado, aleteo rápido.",
        "foto": "aves/colibri.jpg"
    },
    {
        "nombre_comun": "Garza Tigre",
        "nombre_cientifico": "Tigrisoma mexicanum",
        "descripcion": "Garza de hábitos solitarios, frecuenta ríos y lagunas.",
        "caracteristicas": "Rayas marrones y negras, cuello largo.",
        "foto": "aves/garzaTigre.jpg"
    },
    {
        "nombre_comun": "Gavilán",
        "nombre_cientifico": "Buteo magnirostris",
        "descripcion": "Ave rapaz frecuente en zonas rurales y bosques, cazadora de pequeños animales.",
        "caracteristicas": "Color marrón, pecho claro, pico ganchudo.",
        "foto": "aves/gavilan.jpg"
    },
    {
        "nombre_comun": "Guardabarranco",
        "nombre_cientifico": "Eumomota superciliosa",
        "descripcion": "Ave nacional de Nicaragua, reconocida por su cola en forma de raqueta y colores vibrantes azul y verde.",
        "caracteristicas": "Colores azul, verde y naranja. Vive en áreas abiertas, cafetales y bosques.",
        "foto": "aves/guardabarrancos.jpg"
    },
    {
        "nombre_comun": "Lora Cabeza Amarilla",
        "nombre_cientifico": "Amazona oratrix",
        "descripcion": "Loro muy popular en Nicaragua, conocido por su cabeza amarilla y su capacidad de imitar sonidos.",
        "caracteristicas": "Verde con cabeza amarilla, tamaño mediano, muy sociable.",
        "foto": "aves/loraAmarilla.jpg"
    },
    {
        "nombre_comun": "Pájaro Carpintero",
        "nombre_cientifico": "Melanerpes hoffmannii",
        "descripcion": "Carpintero común en Nicaragua, fácil de identificar por su cabeza roja.",
        "caracteristicas": "Negro, blanco y rojo en la cabeza, tamborilea en troncos.",
        "foto": "aves/carpintero.jpg"
    },
    {
        "nombre_comun": "Pato Real",
        "nombre_cientifico": "Cairina moschata",
        "descripcion": "Pato grande, domesticado y silvestre, común en lagunas y ríos.",
        "caracteristicas": "Negro con blanco, carúnculas rojas en la cara.",
        "foto": "aves/patoReal.jpg"
    },
    {
        "nombre_comun": "Perico Pecho Sucio",
        "nombre_cientifico": "Eupsittula nana",
        "descripcion": "Pequeño perico verde, muy ruidoso y sociable, común en bandadas.",
        "caracteristicas": "Verde con pecho amarillento y manchas oscuras.",
        "foto": "aves/pericoPechoSucio.jpg"
    },
    {
        "nombre_comun": "Quetzal",
        "nombre_cientifico": "Pharomachrus mocinno",
        "descripcion": "Ave emblemática de Mesoamérica, apreciada por su plumaje verde y rojo y su larga cola.",
        "caracteristicas": "Verde metálico, pecho rojo, cola larga y elegante.",
        "foto": "aves/quetzal.jpg"
    },
    {
        "nombre_comun": "Tortolita Común",
        "nombre_cientifico": "Columbina passerina",
        "descripcion": "Pequeña paloma muy común en patios y parques.",
        "caracteristicas": "Gris con tonos marrones, tamaño pequeño.",
        "foto": "aves/tortolitaComun.jpg"
    },
    {
        "nombre_comun": "Zanate",
        "nombre_cientifico": "Quiscalus mexicanus",
        "descripcion": "Ave muy común en zonas urbanas y rurales, conocida por su canto fuerte y su color negro brillante.",
        "caracteristicas": "Negro iridiscente, cola larga, adaptable a diferentes ambientes.",
        "foto": "aves/zanate.jpg"
    },
    {
        "nombre_comun": "Zorzal",
        "nombre_cientifico": "Turdus grayi",
        "descripcion": "Ave de canto melodioso, muy común en jardines y parques.",
        "caracteristicas": "Color grisáceo, pecho claro, tamaño mediano.",
        "foto": "aves/zorzal.jpg"
    }
]

# ---------- BOTON REDONDEADO ----------
class RoundedButton(Button):
    def __init__(self, **kwargs):
        rect_color = kwargs.pop('rect_color', COLORS['primary'])
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.rect_color_val = rect_color

        with self.canvas.before:
            self.rect_color = Color(rgba=self.rect_color_val)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.color = COLORS['text']
        self.font_size = kwargs.get('font_size', 18)
        self.bold = True

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# ---------- FUNCIONES DE RECONOCIMIENTO (con API) ----------
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = "TU_API_KEY_AQUI"  # pon aquí tu API Key

def recognize_bird(image_bytes):
    """
    Envía la imagen a la API para intentar identificar el ave.
    Devuelve texto con la identificación/descripción o mensaje de error.
    """
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        files = {
            "file": ("bird.jpg", image_bytes, "image/jpeg")
        }
        messages = [
            {"role": "system", "content": "Eres un experto ornitólogo en aves de Nicaragua."},
            {"role": "user", "content": "Identifica el ave en la imagen y proporciona: nombre común - nombre científico - breve descripción. Si no puedes identificarla, responde 'No estoy seguro'."}
        ]
        # Nota: Ajusta este llamado según el endpoint/forma que uses realmente.
        response = requests.post(
            API_URL,
            headers=headers,
            data={"model": "gpt-4o-mini", "messages": str(messages)},
            files=files,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
            elif "text" in choice:
                return choice["text"]
        return str(result)
    except Exception as e:
        return f"No se pudo analizar el ave ({e})"

# ---------- PANTALLAS ----------
class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)

        self.img = Image(size_hint=(1, 0.7))
        self.result_label = Label(text="Apunta la cámara a un ave", color=COLORS['text'], size_hint=(1, 0.1))
        self.capture_btn = RoundedButton(text="Capturar Ave", rect_color=COLORS['accent'], size_hint=(0.8, 0.1), pos_hint={'center_x': 0.5})
        self.capture_btn.bind(on_press=self.capture)

        layout.add_widget(top_bar)
        layout.add_widget(self.img)
        layout.add_widget(self.capture_btn)
        layout.add_widget(self.result_label)
        self.add_widget(layout)

        self.cap = None
        self.camera_event = None
        self.bind(on_enter=self.start_camera, on_leave=self.stop_camera)

    def start_camera(self, *args):
        # intenta varias cámaras (0-4)
        for i in range(5):
            try:
                self.cap = cv2.VideoCapture(i)
                if self.cap and self.cap.isOpened():
                    self.camera_event = Clock.schedule_interval(self.update_camera_frame, 1/30)
                    return
            except Exception:
                continue
        self.result_label.text = "No se encontró cámara"
        self.cap = None

    def stop_camera(self, *args):
        if self.camera_event:
            self.camera_event.cancel()
            self.camera_event = None
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

    def update_camera_frame(self, dt):
        if not self.cap: return
        ret, frame = self.cap.read()
        if ret:
            # convertir BGR->Texture para Kivy
            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img.texture = texture

    def capture(self, instance):
        if not self.cap: return
        ret, frame = self.cap.read()
        if ret:
            # Guardar captura en disco y en lista para la galería
            img_name = f"captured_bird_{len(captured_birds) + 1}.jpg"
            cv2.imwrite(img_name, frame)
            _, buf = cv2.imencode('.jpg', frame)
            image_bytes = buf.tobytes()
            captured_birds.append({
                'image': frame,
                'name': 'Analizando...',
                'foto': img_name,
                'nombre_comun': 'Ave capturada',
                'nombre_cientifico': 'Desconocido',
                'descripcion': 'Imagen capturada por el usuario.',
                'caracteristicas': 'No disponibles'
            })
            # análisis en hilo
            threading.Thread(target=self.analyze_image_with_ai, args=(image_bytes,)).start()

    def analyze_image_with_ai(self, image_bytes):
        result = recognize_bird(image_bytes)
        # actualizar último elemento
        if captured_birds:
            captured_birds[-1]['name'] = result
            captured_birds[-1]['descripcion'] = result
        Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', f"Resultado: {result}"))

class GalleryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=1, spacing=12, size_hint_y=None, padding=(12,12,12,12))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        self.add_widget(layout)
        self.bind(on_enter=self.populate_gallery)

    def populate_gallery(self, *args):
        self.grid.clear_widgets()
        if not captured_birds:
            self.grid.add_widget(Label(text="Aún no has capturado aves.", color=COLORS['text']))
            return
        # mostrar cada captura con mini tarjeta
        for bird in reversed(captured_birds):
            card = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, padding=8, spacing=10)
            img_path = bird.get('foto', None)
            if img_path and os.path.exists(get_image_path(img_path)):
                thumb = Image(source=get_image_path(img_path), size_hint=(None, 1), width=120, allow_stretch=True, keep_ratio=True)
            else:
                thumb = Image(size_hint=(None, 1), width=120)
            info = BoxLayout(orientation='vertical', spacing=4)
            name_label = Label(text=bird.get('name', bird.get('nombre_comun', 'Ave')), color=COLORS['text'], font_size=16, size_hint_y=None, height=28, halign='left', valign='middle')
            name_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
            desc_label = Label(text=bird.get('descripcion', ''), color=COLORS['text'], font_size=13, size_hint_y=None, height=48, halign='left', valign='top')
            desc_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
            info.add_widget(name_label)
            info.add_widget(desc_label)
            # botón ver detalle
            btn_ver = RoundedButton(text="Ver", rect_color=COLORS['primary'], size_hint=(None, None), size=(80, 36))
            btn_ver.bind(on_press=partial(self.show_detail_from_gallery, bird))
            right = BoxLayout(orientation='vertical', size_hint=(None, 1), width=90, padding=(0,8))
            right.add_widget(Widget())
            right.add_widget(btn_ver)
            card.add_widget(thumb)
            card.add_widget(info)
            card.add_widget(right)
            self.grid.add_widget(card)

    def show_detail_from_gallery(self, bird, *args):
        # reutilizar mecanismo de nearby para mostrar detalle
        if hasattr(self.manager, 'get_screen') and self.manager:
            # creación y navegación a detalle
            detail_screen = BirdDetailScreen(bird, name="bird_detail")
            if self.manager.has_screen("bird_detail"):
                self.manager.remove_widget(self.manager.get_screen("bird_detail"))
            self.manager.add_widget(detail_screen)
            self.manager.transition.direction = 'left'
            self.manager.current = "bird_detail"

# --------- Pantalla de Detalle de Ave ---------
class BirdDetailScreen(Screen):
    def __init__(self, bird, **kwargs):
        super().__init__(**kwargs)
        self.bird = bird
        layout = BoxLayout(orientation='vertical', padding=16, spacing=12)
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        # Imagen (más grande)
        img_path = bird.get('foto', None)
        if img_path and os.path.exists(get_image_path(img_path)):
            img = Image(source=get_image_path(img_path), size_hint=(1, 0.5), allow_stretch=True, keep_ratio=True)
        else:
            img = Image(size_hint=(1, 0.5))
        layout.add_widget(img)

        # Info centrada hacia arriba
        info = BoxLayout(orientation='vertical', spacing=8, padding=(0,0,0,0), size_hint=(1, 0.5))
        nombre = Label(text=f"[b]{bird.get('nombre_comun', bird.get('name', 'Ave'))}[/b]", markup=True, color=COLORS['text'], font_size=20, size_hint_y=None, height=36, halign='center', valign='middle')
        nombre.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        cientifico = Label(text=f"[i]{bird.get('nombre_cientifico', 'Desconocido')}[/i]", markup=True, color=(0.2,0.4,0.2,1), font_size=15, size_hint_y=None, height=24, halign='center', valign='middle')
        cientifico.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        desc = Label(text=bird.get('descripcion', 'Sin descripción.'), color=COLORS['text'], font_size=14, size_hint_y=None, height=80, text_size=(Window.width - 48, None), halign='left', valign='top')
        carac = Label(text=f"[color=7CB342]Características:[/color] {bird.get('caracteristicas', 'No disponibles.')}", markup=True, color=COLORS['text'], font_size=13, size_hint_y=None, height=56, text_size=(Window.width - 48, None), halign='left', valign='top')
        info.add_widget(nombre)
        info.add_widget(cientifico)
        info.add_widget(desc)
        info.add_widget(carac)
        layout.add_widget(info)

        self.add_widget(layout)

    def go_back(self, *args):
        # Regresar a nearby
        self.manager.transition.direction = 'right'
        self.manager.current = 'nearby'
        # limpiar pantalla detalle para evitar duplicados
        Clock.schedule_once(lambda dt: self.manager.remove_widget(self), 0.1)

# --------- BirdCard mejorado ---------
class BirdCard(BoxLayout):
    def __init__(self, bird, on_press=None, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=170, padding=12, spacing=14, **kwargs)
        with self.canvas.before:
            Color(rgba=COLORS['primary'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Imagen ampliada
        img_path = bird.get('foto', None)
        if img_path and os.path.exists(get_image_path(img_path)):
            img = Image(source=get_image_path(img_path), size_hint=(None, 1), width=130, allow_stretch=True, keep_ratio=True)
        else:
            img = Image(size_hint=(None, 1), width=130)
        self.add_widget(img)

        # Info (centrada hacia arriba)
        info = BoxLayout(orientation='vertical', spacing=6, padding=(0, 6, 0, 0))
        nombre = Label(text=f"[b]{bird.get('nombre_comun', bird.get('name', 'Ave'))}[/b]", markup=True, color=COLORS['text'], font_size=18, size_hint_y=None, height=30, halign='left', valign='middle')
        nombre.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        cientifico = Label(text=f"[i]{bird.get('nombre_cientifico', 'Desconocido')}[/i]", markup=True, color=(0.2, 0.4, 0.2, 1), font_size=14, size_hint_y=None, height=22, halign='left', valign='middle')
        cientifico.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        desc = Label(text=bird.get('descripcion', 'Sin descripción.'), color=COLORS['text'], font_size=13, size_hint_y=None, height=46, text_size=(Window.width - 190, None), halign='left', valign='top')
        carac = Label(text=f"[color=7CB342]Características:[/color] {bird.get('caracteristicas', 'No disponibles.')}", markup=True, color=COLORS['text'], font_size=12, size_hint_y=None, height=36, text_size=(Window.width - 190, None), halign='left', valign='top')
        info.add_widget(nombre)
        info.add_widget(cientifico)
        info.add_widget(desc)
        info.add_widget(carac)
        self.add_widget(info)

        # Hacer clic para ver detalle si on_press provisto
        if on_press:
            self.on_press_callback = on_press
            self.bind(on_touch_down=self._on_touch)

    def _on_touch(self, instance, touch):
        if self.collide_point(*touch.pos):
            try:
                self.on_press_callback()
            except Exception:
                pass
            return True
        return False

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class NearbyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        top_bar = BoxLayout(size_hint_y=None, height='48dp', padding=(0,0,0,0))
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        title = Label(text="[b]Aves de Nicaragua[/b]", markup=True, color=COLORS['text'], font_size=22, size_hint_y=None, height=40)
        layout.add_widget(title)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=14, size_hint_y=None, padding=(0, 0, 0, 10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        self.add_widget(layout)
        self.bind(on_enter=self.populate_birds)

    def populate_birds(self, *args):
        self.grid.clear_widgets()
        # mostrar especies registradas
        for bird in NICARAGUAN_BIRDS:
            card = BirdCard(bird, on_press=partial(self.show_bird_detail, bird))
            self.grid.add_widget(card)
        # luego mostrar capturas del usuario (si las hay) al final
        for bird in reversed(captured_birds):
            if 'foto' in bird and os.path.exists(get_image_path(bird['foto'])):
                card = BirdCard(bird, on_press=partial(self.show_bird_detail, bird))
                self.grid.add_widget(card)

    def show_bird_detail(self, bird, *args):
        # Crear pantalla de detalle y navegar
        detail_screen = BirdDetailScreen(bird, name="bird_detail")
        if self.manager.has_screen("bird_detail"):
            self.manager.remove_widget(self.manager.get_screen("bird_detail"))
        self.manager.add_widget(detail_screen)
        self.manager.transition.direction = 'left'
        self.manager.current = "bird_detail"

class WebScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        web_btn = RoundedButton(text="Ir a la Web", rect_color=COLORS['primary'], size_hint=(0.8, None), height=50, pos_hint={'center_x': 0.5})
        web_btn.bind(on_press=lambda x: webbrowser.open(WEB_URL))
        layout.add_widget(web_btn)
        self.add_widget(layout)

class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10)
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        label = Label(text=f"Acerca de {APP_NAME}", color=COLORS['text'])
        layout.add_widget(label)
        self.add_widget(layout)

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        logo_path = get_image_path('LogoEcoAvesPNG.png')
        logo = Image(source=logo_path, size_hint_y=0.25)
        layout.add_widget(logo)

        button_args = {'size_hint': (0.8, 0.12), 'pos_hint': {'center_x': 0.5}, 'font_size': 18}
        screens = ["camera", "gallery", "nearby", "web", "info"]
        texts = ["Reconocer Ave", "Galería", "Aves Cercanas", "Web", "Acerca de"]
        colors = [COLORS['accent'], COLORS['primary'], COLORS['primary'], COLORS['primary'], COLORS['secondary']]
        for s, t, c in zip(screens, texts, colors):
            btn = RoundedButton(text=t, rect_color=c, **button_args)
            btn.bind(on_press=partial(lambda scr, x: setattr(self.manager, 'current', scr), s))
            layout.add_widget(btn)
        self.add_widget(layout)

# ---------- APP ----------
class EcoAvesApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(GalleryScreen(name="gallery"))
        sm.add_widget(NearbyScreen(name="nearby"))
        sm.add_widget(WebScreen(name="web"))
        sm.add_widget(InfoScreen(name="info"))
        # Note: BirdDetailScreen is added dynamically when needed
        return sm

if __name__ == "__main__":
    EcoAvesApp().run()
