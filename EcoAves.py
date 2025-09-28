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
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from functools import partial
import functools
import threading
import cv2
import webbrowser
import requests
import os
import sys
import json

try:
    try:
        from kivy_garden.mapview import MapView, MapMarkerPopup, MapMarker
        MAPVIEW_AVAILABLE = True
        print("MapView disponible (kivy_garden.mapview)")
    except Exception:
        from kivy.garden.mapview import MapView, MapMarkerPopup, MapMarker
        MAPVIEW_AVAILABLE = True
        print("MapView disponible (kivy.garden.mapview)")
except Exception as e:
    print(f"Error al importar MapView: {e}")
    MAPVIEW_AVAILABLE = False
    import folium
    import tempfile
    
    class MapView:
        def __init__(self, zoom=15, lat=12.1364, lon=-86.2514, *args, **kwargs):
            self.zoom = zoom
            self.lat = lat
            self.lon = lon
            self.markers = []
            self.map = folium.Map(location=[lat, lon], zoom_start=zoom)
            
        def add_widget(self, marker):
            if hasattr(marker, 'lat') and hasattr(marker, 'lon'):
                folium.Marker([marker.lat, marker.lon]).add_to(self.map)
                
    class MapMarkerPopup:
        def __init__(self, lat, lon, *args, **kwargs):
            self.lat = lat
            self.lon = lon
            
    class MapMarker:
        def __init__(self, lat, lon, *args, **kwargs):
            self.lat = lat
            self.lon = lon
    
    def create_map_html(lat, lon, zoom=15, title="Ubicación"):
        m = folium.Map(location=[lat, lon], zoom_start=zoom)
        folium.Marker([lat, lon], popup=title).add_to(m)
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
        m.save(temp_file.name)
        temp_file.close()
        webbrowser.open(f'file://{temp_file.name}')
        return temp_file.name

# ---------- MAPA ----------
class SimpleMapView(BoxLayout):
    def __init__(self, lat, lon, zoom=15, title="Ubicación", **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
        self.title = title
        
        if MAPVIEW_AVAILABLE:
            try:
                self.map_view = MapView(
                    zoom=zoom,
                    lat=lat,
                    lon=lon,
                    size_hint=(1, 1)
                )
                marker = MapMarkerPopup(lat=lat, lon=lon)
                self.map_view.add_widget(marker)
                self.add_widget(self.map_view)
                return
            except Exception as e:
                print(f"Error usando MapView real: {e}")
        self.create_fallback_message()
    
    def create_fallback_message(self):
        info_label = Label(
            text="Mapa no disponible - Instale kivy-garden.mapview",
            color=COLORS['text_secondary'],
            size_hint=(1, None),
            height=40,
            font_size=16
        )
        self.add_widget(info_label)
        coord_label = Label(
            text=f"Coordenadas: {self.lat:.5f}, {self.lon:.5f}",
            color=COLORS['text'],
            size_hint=(1, None),
            height=30,
            font_size=14
        )
        self.add_widget(coord_label)
        
        browser_btn = RoundedButton(
            text="Abrir en Navegador",
            rect_color=COLORS['primary'],
            size_hint=(1, None),
            height=44,
            font_size=16
        )
        browser_btn.bind(on_press=self.open_google_maps)
        self.add_widget(browser_btn)
    
    def open_map(self, instance):
        try:
            import folium
            import tempfile
            
            m = folium.Map(location=[self.lat, self.lon], zoom_start=self.zoom)
            folium.Marker([self.lat, self.lon], popup=self.title).add_to(m)
            
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
            m.save(temp_file.name)
            temp_file.close()
            
            webbrowser.open(f'file://{temp_file.name}')
            print(f"Mapa abierto: {temp_file.name}")
            
        except Exception as e:
            print(f"Error creando mapa: {e}")
            self.open_google_maps(instance)
    
    def open_google_maps(self, instance):
        try:
            google_url = f"https://www.google.com/maps?q={self.lat},{self.lon}"
            webbrowser.open(google_url)
            print(f"Google Maps abierto: {google_url}")
        except Exception as e:
            print(f"Error abriendo Google Maps: {e}")

# ---------- WEBVIEW ---------
try:
    from kivy.garden.webview import WebView
    WEBVIEW_AVAILABLE = True
    print("WebView disponible")
except ImportError:
    print("kivy.garden.webview no está disponible, usando alternativas")
    WEBVIEW_AVAILABLE = False
    class WebView:
        def __init__(self, *args, **kwargs):
            pass
        def load_url(self, url):
            pass
        @property
        def url(self):
            return ""
        @url.setter
        def url(self, value):
            pass
except Exception as e:
    print("Error al importar kivy.garden.webview:", e)
    WEBVIEW_AVAILABLE = False
    class WebView:
        def __init__(self, *args, **kwargs):
            pass
        def load_url(self, url):
            pass
        @property
        def url(self):
            return ""
        @url.setter
        def url(self, value):
            pass

# ---------- DETECCIÓN DE ANDROID Y PYWEBVIEW ----------
try:
    from jnius import autoclass
    try:
        from android.runnable import run_on_ui_thread
    except Exception:
        def run_on_ui_thread(func):
            return func
    IS_ANDROID = True
except Exception:
    IS_ANDROID = False
    def run_on_ui_thread(func):
        return func

try:
    import webview as pywebview
    HAS_PYWEBVIEW = True
except Exception:
    HAS_PYWEBVIEW = False

# ---------- COLORES UI----------
GREEN_COLOR = (76/255, 175/255, 80/255, 1)

COLORS = {
    'primary': GREEN_COLOR,                   
    'secondary': GREEN_COLOR,                 
    'background': (0.95, 0.98, 0.95, 1),     
    'surface': (0.9, 0.95, 0.9, 1),          
    'text': (0.1, 0.2, 0.1, 1),              
    'text_secondary': (0.3, 0.4, 0.3, 1),    
    'accent': GREEN_COLOR,                   
    'success': GREEN_COLOR,                  
    'warning': (0.8, 0.6, 0.2, 1),           
    'error': (0.9, 0.3, 0.3, 1),             
    'gradient_start': GREEN_COLOR,            
    'gradient_end': GREEN_COLOR,             
    'white': (1.0, 1.0, 1.0, 1),             
    'light_gray': (0.9, 0.9, 0.9, 1),        
}

Window.size = (360, 640)
Window.clearcolor = COLORS['background']

APP_NAME = "EcoAves"
WEB_URL = "https://zayriaz28.github.io/EcoAves.v2/Ficha-Aves.html"
captured_birds = []
thumbnail_cache = {}

# ---------- DATOS DE LOGROS ----------
ACHIEVEMENTS = [
    {
        "id": "orgullo_nica",
        "name": "Orgullo Nica",
        "description": "Capturar foto del Guardabarranco",
        "icon": "guardabarranco",
        "rarity": "legendario",
        "unlocked": False
    },
    {
        "id": "carpintero",
        "name": "Carpintero",
        "description": "Registrar un Pájaro Carpintero",
        "icon": "carpintero",
        "rarity": "epico",
        "unlocked": False
    },
    {
        "id": "zanates",
        "name": "Zanates",
        "description": "Identificar 5 Zanates diferentes",
        "icon": "zanate",
        "rarity": "comun",
        "unlocked": False
    },
    {
        "id": "tortolitas",
        "name": "Tortolitas",
        "description": "Identificar 3 Tortolitas Comunes",
        "icon": "tortolita",
        "rarity": "comun",
        "unlocked": False
    },
    {
        "id": "explorador_mombacho",
        "name": "Explorador del Mombacho",
        "description": "Visitar la Reserva Natural Volcán Mombacho",
        "icon": "mombacho",
        "rarity": "raro",
        "unlocked": False
    },
    {
        "id": "amigo_bosque_nuboso",
        "name": "Amigo del Bosque Nuboso",
        "description": "Registrar 10 aves distintas en zonas montañosas",
        "icon": "bosque",
        "rarity": "raro",
        "unlocked": False
    },
    {
        "id": "aventurero_indio_maiz",
        "name": "Aventurero del Indio Maíz",
        "description": "Visitar la Reserva Biológica Indio Maíz",
        "icon": "indio_maiz",
        "rarity": "epico",
        "unlocked": False
    },
    {
        "id": "descubridor_colibries",
        "name": "Descubridor de Colibríes",
        "description": "Identificar 5 especies de colibríes",
        "icon": "colibri",
        "rarity": "raro",
        "unlocked": False
    },
    {
        "id": "defensor_quetzal",
        "name": "Defensor del Quetzal",
        "description": "Avistar al Quetzal",
        "icon": "quetzal",
        "rarity": "legendario",
        "unlocked": False
    },
    {
        "id": "amante_humedales",
        "name": "Amante de los Humedales",
        "description": "Visitar Isla Juan Venado",
        "icon": "humedales",
        "rarity": "raro",
        "unlocked": False
    },
    {
        "id": "conservacionista",
        "name": "Conservacionista",
        "description": "Registrar 20 aves diferentes",
        "icon": "conservacion",
        "rarity": "epico",
        "unlocked": False
    },
    {
        "id": "fotografo_naturaleza",
        "name": "Fotógrafo de la Naturaleza",
        "description": "Subir 15 fotos de aves",
        "icon": "foto",
        "rarity": "raro",
        "unlocked": False
    },
    {
        "id": "guardian_biodiversidad",
        "name": "Guardián de la Biodiversidad",
        "description": "Capturar 30 registros válidos",
        "icon": "biodiversidad",
        "rarity": "legendario",
        "unlocked": False
    },
    {
        "id": "explorador_urbano",
        "name": "Explorador Urbano",
        "description": "Identificar aves comunes en ciudad (zanate, tortolita, etc.)",
        "icon": "urbano",
        "rarity": "comun",
        "unlocked": False
    }
]

# ---------- DATOS DE GUÍAS DE AVITURISMO ----------
GUIDES = [
    {
        "nombre": "Fundación Cocibolca",
        "especialidad": "Volcán Mombacho",
        "contacto": "Tel: +505 2552-2498",
        "email": "info@fundacioncocibolca.org",
        "web": "www.fundacioncocibolca.org",
        "descripcion": "Guías especializados en el bosque nuboso del Mombacho con más de 15 años de experiencia."
    },
    {
        "nombre": "Guías Comunitarios Indio Maíz",
        "especialidad": "Reserva Biológica Indio Maíz",
        "contacto": "Tel: +505 8888-1234",
        "email": "guias@indio-maiz.org",
        "web": "www.indio-maiz.org",
        "descripcion": "Guías locales con conocimiento ancestral de la selva tropical y sus especies."
    },
    {
        "nombre": "Isla Juan Venado Tours",
        "especialidad": "Humedales y Manglares",
        "contacto": "Tel: +505 2311-5678",
        "email": "tours@juanvenado.com",
        "web": "www.juanvenado.com",
        "descripcion": "Especialistas en aves acuáticas y ecosistemas de humedales."
    },
    {
        "nombre": "Matagalpa Tours",
        "especialidad": "Aves de Montaña",
        "contacto": "Tel: +505 2772-3456",
        "email": "info@matagalpatours.com",
        "web": "www.matagalpatours.com",
        "descripcion": "Tours especializados en aves de altura y bosques de neblina."
    },
    {
        "nombre": "Careli Tours",
        "especialidad": "Aviturismo Integral",
        "contacto": "Tel: +505 2222-7890",
        "email": "careli@tours.com",
        "web": "www.carelitours.com",
        "descripcion": "Operador turístico con paquetes completos de aviturismo en Nicaragua."
    },
    {
        "nombre": "EcoTours Nicaragua",
        "especialidad": "Turismo Sostenible",
        "contacto": "Tel: +505 2550-1234",
        "email": "info@ecotoursnicaragua.com",
        "web": "www.ecotoursnicaragua.com",
        "descripcion": "Tours ecológicos y de conservación con enfoque en aves endémicas."
    }
]

# ---------- PERFIL DE USUARIO ----------
USER_PROFILE = {
    "nombre": "",
    "email": "",
    "ave_buscando": "",
    "aves_registradas": 0,
    "fotos_subidas": 0,
    "reservas_visitadas": 0,
    "logros_desbloqueados": 0
}

PROFILE_CREATED = False
PROFILE_FILE = "user_profile.json"

def save_profile():
    try:
        profile_data = {
            "profile_created": PROFILE_CREATED,
            "user_profile": USER_PROFILE
        }
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
        print(f"Perfil guardado en {PROFILE_FILE}")
    except Exception as e:
        print(f"Error guardando perfil: {e}")

def load_profile():
    global PROFILE_CREATED, USER_PROFILE
    try:
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            PROFILE_CREATED = profile_data.get("profile_created", False)
            USER_PROFILE.update(profile_data.get("user_profile", {}))
            print(f"Perfil cargado desde {PROFILE_FILE}")
            return True
    except Exception as e:
        print(f"Error cargando perfil: {e}")
    return False

# ---------- CONFIGURACIÓN DE TEMA FIJO CLARO ----------

# ---------- FUNCIONES DE PRUEBA INTEGRADAS ----------
def test_imports():
    print("Probando importaciones...")
    
    try:
        import kivy
        print("Kivy importado correctamente")
    except ImportError as e:
        print(f"Error importando Kivy: {e}")
        return False
    
    try:
        import cv2
        print("OpenCV importado correctamente")
    except ImportError as e:
        print(f"Error importando OpenCV: {e}")
        return False
    
    try:
        import webbrowser
        print("Webbrowser importado correctamente")
    except ImportError as e:
        print(f"Error importando Webbrowser: {e}")
        return False
    
    try:
        import folium
        print("Folium importado correctamente")
    except ImportError as e:
        print(f"Error importando Folium: {e}")
        return False
    
    return True

def test_camera():
    print("Probando cámara...")
    
    try:
        import cv2
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"Cámara {i} funciona correctamente")
                    cap.release()
                    return True
                cap.release()
        
        print("No se encontró cámara funcional")
        return False
        
    except Exception as e:
        print(f"Error probando cámara: {e}")
        return False

def test_maps():
    print("Probando mapas...")
    
    try:
        import folium
        import webbrowser
        import tempfile
        
        m = folium.Map(location=[12.1364, -86.2514], zoom_start=10)
        folium.Marker([12.1364, -86.2514], popup="Managua, Nicaragua").add_to(m)
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
        m.save(temp_file.name)
        temp_file.close()
        
        print(f"Mapa creado correctamente: {temp_file.name}")
        
        os.unlink(temp_file.name)
        
        return True
        
    except Exception as e:
        print(f"Error probando mapas: {e}")
        return False


# --------- RUTA BASE PARA IMÁGENES ---------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_image_path(rel_path):
    if os.path.isabs(rel_path):
        return rel_path
    abs_path = os.path.join(BASE_DIR, rel_path)
    if os.path.exists(abs_path):
        return abs_path
    return rel_path

def get_thumbnail(path, max_width=256, max_height=None):
    try:
        abs_path = get_image_path(path)
        if not os.path.exists(abs_path):
            return abs_path
        key = (abs_path, max_width, max_height)
        if key in thumbnail_cache and os.path.exists(thumbnail_cache[key]):
            return thumbnail_cache[key]
        
        import cv2
        img = cv2.imread(abs_path)
        if img is None:
            return abs_path
        
        h, w = img.shape[:2]
        
        scale_w = max_width / float(w) if w > max_width else 1.0
        scale_h = max_height / float(h) if max_height and h > max_height else 1.0
        scale = min(scale_w, scale_h)
        
        if scale < 1.0:
            new_size = (int(w * scale), int(h * scale))
            img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA) 
        
        thumb_name = os.path.join(BASE_DIR, f"thumb_{hash(key) % 1000000}.jpg")
        cv2.imwrite(thumb_name, img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        thumbnail_cache[key] = thumb_name
        return thumb_name
    except Exception:
        return get_image_path(path)

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

# ---------- DATOS DE RESERVAS ----------
RESERVAS = [
    {
        "nombre": "Reserva Biológica Indio Maíz",
        "desc": "Selva tropical densa, ideal para aviturismo y exploración de biodiversidad. Ubicación: Parte norte de la reserva, dentro del territorio nicaragüense, lejos de la frontera exacta con Costa Rica.",
        "img": "reservas/indio_maiz.jpg",
        "actividades": ["aviturismo", "senderismo", "observación"],
        "lat": 11.0560,
        "lon": -83.9330
    },
    {
        "nombre": "Reserva Natural Volcán Mombacho",
        "desc": "Bosque nuboso con especies endémicas y senderos interpretativos.",
        "img": "reservas/mombacho.jpg",
        "actividades": ["aviturismo", "bosque-nuboso", "senderismo"],
        "lat": 11.8375791,
        "lon": -85.9508923
    },
    {
        "nombre": "Reserva Natural Isla Juan Venado",
        "desc": "Humedales y manglares, santuario para aves acuáticas y tortugas.",
        "img": "reservas/juan_venado.jpg",
        "actividades": ["aviturismo", "humedales", "kayak"],
        "lat": 12.331839,
        "lon": -86.979103
    },
    {
        "nombre": "Parque Nacional Volcán Masaya",
        "desc": "Paisaje volcánico accesible, con flora y fauna adaptada a ambientes volcánicos.",
        "img": "reservas/masaya.jpg",
        "actividades": ["volcanes", "observación"],
        "lat": 11.9827778,
        "lon": -86.1619444
    }
]

# ---------- BOTÓN ----------
class ModernButton(Button):
    def __init__(self, **kwargs):
        rect_color = kwargs.pop('rect_color', COLORS['primary'])
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (1, 1, 1, 0) 
        self.color = COLORS['white']
        self.font_size = kwargs.get('font_size', 18)
        self.bold = True
        
        with self.canvas.before:
            Color(rgba=(0, 0, 0, 0.2))
            self.shadow_rect = RoundedRectangle(
                pos=(self.pos[0]+2, self.pos[1]-2),
                size=(self.size[0], self.size[1]),
                radius=[25]
            )
            
            Color(rgba=rect_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[20]
            )
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.shadow_rect.pos = (self.pos[0]+2, self.pos[1]-2)
        self.shadow_rect.size = self.size
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

RoundedButton = ModernButton

# ---------- RECONOCIMIENTO DE AVES ----------
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.environ.get("OPENAI_API_KEY", "")

def _recognize_bird_offline(image_bytes):
    try:
        import numpy as np
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            return None, "No se pudo decodificar la imagen"

        img_resized = cv2.resize(img, (256, 256))
        img_hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
        hist_img = cv2.calcHist([img_hsv], [0,1], None, [20, 20], [0,180, 0,256])
        cv2.normalize(hist_img, hist_img)

        best_score = -1.0
        best_bird = None

        for bird in NICARAGUAN_BIRDS:
            foto_path = get_image_path(bird.get('foto', ''))
            if not os.path.exists(foto_path):
                continue
            ref = cv2.imread(foto_path)
            if ref is None:
                continue
            ref_hsv = cv2.cvtColor(cv2.resize(ref, (256, 256)), cv2.COLOR_BGR2HSV)
            hist_ref = cv2.calcHist([ref_hsv], [0,1], None, [20, 20], [0,180, 0,256])
            cv2.normalize(hist_ref, hist_ref)
            score = cv2.compareHist(hist_img, hist_ref, cv2.HISTCMP_CORREL)

            if score > best_score:
                best_score = score
                best_bird = bird

        if best_bird is None:
            return None, "No se encontró coincidencia"

        confidence = max(0.0, min(1.0, (best_score + 1) / 2))
        summary = f"Posible: {best_bird['nombre_comun']} - {best_bird['nombre_cientifico']} (confianza {confidence:.2f}). {best_bird.get('descripcion','')}"
        return best_bird, summary
    except Exception as e:
        return None, f"Error en reconocimiento offline: {e}"

def _recognize_bird_android_api(image_bytes):
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        files = {"file": ("bird.jpg", image_bytes, "image/jpeg")}
        messages = [
            {"role": "system", "content": "Eres un experto ornitólogo en aves de Nicaragua."},
            {"role": "user", "content": "Identifica el ave en la imagen y proporciona: nombre común - nombre científico - breve descripción."}
        ]
        response = requests.post(API_URL, headers=headers, data={"model": "gpt-4o-mini", "messages": str(messages)}, files=files, timeout=30)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and result["choices"]:
            choice = result["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
        return "No estoy seguro"
    except Exception as e:
        return f"No se pudo analizar el ave ({e})"

def recognize_bird(image_bytes):
    if IS_ANDROID and API_KEY:
        return _recognize_bird_android_api(image_bytes)
    _, summary = _recognize_bird_offline(image_bytes)
    return summary

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
        
        button_container = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        
        self.capture_btn = RoundedButton(text="Capturar", rect_color=COLORS['accent'], size_hint=(0.5, 1))
        self.capture_btn.bind(on_press=self.capture)
        
        self.upload_btn = RoundedButton(text="Subir Imagen", rect_color=COLORS['primary'], size_hint=(0.5, 1))
        self.upload_btn.bind(on_press=self.upload_image)
        
        button_container.add_widget(self.capture_btn)
        button_container.add_widget(self.upload_btn)

        layout.add_widget(top_bar)
        layout.add_widget(self.img)
        layout.add_widget(button_container)
        layout.add_widget(self.result_label)
        self.add_widget(layout)

        self.cap = None
        self.camera_event = None
        self.bind(on_enter=self.start_camera, on_leave=self.stop_camera)

    def start_camera(self, *args):
        for i in range(5):
            try:
                self.cap = cv2.VideoCapture(i)
                if self.cap and self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.cap.set(cv2.CAP_PROP_FPS, 30)
                    self.camera_event = Clock.schedule_interval(self.update_camera_frame, 1/30)
                    self.result_label.text = f"Cámara {i} activa"
                    return
            except Exception as e:
                print(f"Error con cámara {i}: {e}")
                continue
        
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for backend in backends:
            try:
                self.cap = cv2.VideoCapture(0, backend)
                if self.cap and self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.camera_event = Clock.schedule_interval(self.update_camera_frame, 1/30)
                    self.result_label.text = "Cámara activa (backend alternativo)"
                    return
            except Exception as e:
                print(f"Error con backend {backend}: {e}")
                continue
                
        self.result_label.text = "No se encontró cámara disponible"
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
            # Mostrar automáticamente el detalle del ave
            Clock.schedule_once(lambda dt: self.show_bird_detail_auto(captured_birds[-1]), 1.0)
        Clock.schedule_once(lambda dt: setattr(self.result_label, 'text', f"Resultado: {result}"))
    
    def show_bird_detail_auto(self, bird):
        """Mostrar automáticamente el detalle del ave después del análisis"""
        try:
            detail_screen = BirdDetailScreen(bird, name="bird_detail_auto")
            if self.manager.has_screen("bird_detail_auto"):
                self.manager.remove_widget(self.manager.get_screen("bird_detail_auto"))
            self.manager.add_widget(detail_screen)
            self.manager.transition.direction = 'left'
            self.manager.current = "bird_detail_auto"
        except Exception as e:
            print(f"Error mostrando detalle automático: {e}")
    
    def upload_image(self, instance):
        """Subir imagen desde archivo - Versión estable con tkinter y fallback"""
        try:
            file_path = None

            # Método 1: tkinter (preferido en escritorio)
            try:
                from tkinter import filedialog
                import tkinter as tk

                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                file_path = filedialog.askopenfilename(
                    title="Seleccionar imagen de ave",
                    filetypes=[
                        ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif"),
                        ("Todos los archivos", "*.*")
                    ]
                )
                root.destroy()
            except Exception as e:
                print(f"Error con tkinter: {e}")

            # Método 2: abrir carpeta como fallback
            if not file_path:
                try:
                    images_dir = os.path.join(os.getcwd(), "imagenes_aves")
                    if not os.path.exists(images_dir):
                        os.makedirs(images_dir)
                    webbrowser.open(f"file://{images_dir}")
                    self.result_label.text = "Carpeta de imágenes abierta. Coloca tu imagen ahí y vuelve a intentar."
                    return
                except Exception as e:
                    print(f"Error abriendo carpeta: {e}")

            if file_path and os.path.exists(file_path):
                image = cv2.imread(file_path)
                if image is not None:
                    # Mostrar imagen
                    buf = cv2.flip(image, 0).tobytes()
                    texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='bgr')
                    texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                    self.img.texture = texture
                    
                    img_name = f"uploaded_bird_{len(captured_birds) + 1}.jpg"
                    cv2.imwrite(img_name, image)
                    _, buf = cv2.imencode('.jpg', image)
                    image_bytes = buf.tobytes()
                    
                    captured_birds.append({
                        'image': image,
                        'name': 'Analizando...',
                        'foto': img_name,
                        'nombre_comun': 'Ave subida',
                        'nombre_cientifico': 'Desconocido',
                        'descripcion': 'Imagen subida por el usuario.',
                        'caracteristicas': 'No disponibles'
                    })
                    
                    threading.Thread(target=self.analyze_image_with_ai, args=(image_bytes,)).start()
                    self.result_label.text = "Imagen subida, analizando..."
                else:
                    self.result_label.text = "Error: No se pudo cargar la imagen"
            else:
                self.result_label.text = "No se seleccionó archivo válido"
                
        except Exception as e:
            self.result_label.text = f"Error al subir imagen: {str(e)[:60]}"

class GalleryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        title = Label(text="[b]Mi Galería de Aves[/b]", markup=True, color=COLORS['text'], font_size=22, size_hint_y=None, height=40)
        layout.add_widget(title)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=14, size_hint_y=None, padding=(0, 0, 0, 10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        self.add_widget(layout)
        self.bind(on_enter=self.populate_gallery)

    def populate_gallery(self, *args):
        self.grid.clear_widgets()
        
        # Mostrar únicamente aves capturadas por el usuario
        if not captured_birds:
            no_birds_label = Label(
                text="Aún no has capturado aves.\n¡Usa el detector de aves para comenzar tu galería!",
                color=COLORS['text_secondary'],
                font_size=16,
                size_hint_y=None,
                height=100,
                halign='center',
                valign='middle'
            )
            no_birds_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
            self.grid.add_widget(no_birds_label)
            return
        
        # Mostrar solo aves capturadas con la misma interfaz que Aves cercanas
        for bird in reversed(captured_birds):
            if 'foto' in bird and os.path.exists(get_image_path(bird['foto'])):
                card = BirdCard(bird, on_press=partial(self.show_bird_detail, bird))
                self.grid.add_widget(card)

    def show_bird_detail(self, bird, *args):
        try:
            # Crear un nombre único para la pantalla de detalle
            detail_name = f"bird_detail_{id(bird)}"
            detail_screen = BirdDetailScreen(bird, name=detail_name)
            
            # Remover pantalla existente si existe
            if self.manager.has_screen(detail_name):
                self.manager.remove_widget(self.manager.get_screen(detail_name))
            
            # Agregar nueva pantalla
            self.manager.add_widget(detail_screen)
            self.manager.transition.direction = 'left'
            self.manager.current = detail_name
        except Exception as e:
            print(f"Error mostrando detalle del ave: {e}")
            pass

# --------- Pantalla de Detalle de Ave ---------
class BirdDetailScreen(Screen):
    def __init__(self, bird, **kwargs):
        super().__init__(**kwargs)
        self.bird = bird
        layout = BoxLayout(orientation='vertical', padding=(0, 0, 0, 0), spacing=0)

        # Barra superior con botón Atrás
        top_bar = BoxLayout(size_hint_y=None, height='48dp', padding=(8,0))
        back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        back_btn.bind(on_press=self.go_back)
        title = Label(text="Detalle del Ave", color=COLORS['text'], size_hint=(1, 1), halign='center', valign='middle')
        title.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        layout.add_widget(top_bar)

        # Imagen (más grande)
        img_path = bird.get('foto', None)
        if img_path and os.path.exists(get_image_path(img_path)):
            img = Image(source=get_image_path(img_path), size_hint=(1, None), height=220, allow_stretch=True, keep_ratio=True)
        else:
            img = Image(size_hint=(1, None), height=220)
        layout.add_widget(img)

        # Info centrada y más grande
        info = BoxLayout(orientation='vertical', spacing=18, padding=(16,30,16,30), size_hint=(1, 1))
        nombre = Label(
            text=f"[b]{bird.get('nombre_comun', bird.get('name', 'Ave'))}[/b]",
            markup=True,
            color=COLORS['text'],
            font_size=32,  # más grande
            size_hint_y=None,
            height=54,
            halign='center',
            valign='middle'
        )
        nombre.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        cientifico = Label(
            text=f"[i]{bird.get('nombre_cientifico', 'Desconocido')}[/i]",
            markup=True,
            color=(0.2,0.4,0.2,1),
            font_size=22,  # más grande
            size_hint_y=None,
            height=36,
            halign='center',
            valign='middle'
        )
        cientifico.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        desc_ext = bird.get('descripcion', 'Sin descripción.') + "\nHábitat: Bosques, cafetales y jardines.\nAlimentación: Insectos y frutos.\nComportamiento: Muy activo al amanecer."
        desc = Label(
            text=desc_ext,
            color=COLORS['text'],
            font_size=19,  # más grande
            size_hint_y=None,
            height=180,
            text_size=(Window.width - 48, None),
            halign='center',  # centrado
            valign='top'
        )
        carac = Label(
            text=f"[color=7CB342]Características:[/color] {bird.get('caracteristicas', 'No disponibles.')}",
            markup=True,
            color=COLORS['text'],
            font_size=17,  # más grande
            size_hint_y=None,
            height=70,
            text_size=(Window.width - 48, None),
            halign='center',  # centrado
            valign='top'
        )
        info.add_widget(nombre)
        info.add_widget(cientifico)
        info.add_widget(desc)
        info.add_widget(carac)
        layout.add_widget(info)

        self.add_widget(layout)

    def go_back(self, *args):
        self.manager.transition.direction = 'right'
        if self.manager.current == "bird_detail_auto":
            self.manager.current = 'camera'
        else:
            self.manager.current = 'nearby'
        Clock.schedule_once(lambda dt: self.manager.remove_widget(self), 0.1)

# --------- BirdCard---------
class BirdCard(BoxLayout):
    def __init__(self, bird, on_press=None, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=200, padding=12, spacing=12, **kwargs)
        
        with self.canvas.before:
            Color(rgba=(0, 0, 0, 0.1))
            self.shadow_rect = RoundedRectangle(
                pos=(self.pos[0]+2, self.pos[1]-2), 
                size=(self.size[0], self.size[1]), 
                radius=[20]
            )
            
            Color(rgba=COLORS['surface'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
            
            Color(rgba=(*COLORS['primary'][:3], 0.3))
            self.border_rect = RoundedRectangle(
                pos=(self.pos[0]+1, self.pos[1]+1), 
                size=(self.size[0]-2, self.size[1]-2), 
                radius=[16]
            )
        
        self.bind(pos=self.update_bg, size=self.update_bg)

        img_width = 120
        img_height = 120
        img_path = bird.get('foto', None)
        if img_path and os.path.exists(get_image_path(img_path)):
            thumb_path = get_thumbnail(img_path, max_width=img_width, max_height=img_height)
            img = Image(
                source=thumb_path,
                size_hint=(None, None),
                width=img_width,
                height=img_height,
                allow_stretch=True,
                keep_ratio=True
            )
        else:
            img = Image(
                size_hint=(None, None),
                width=img_width,
                height=img_height
            )
        img_container = BoxLayout(orientation='vertical', size_hint=(None, 1), width=img_width)
        img_container.add_widget(Widget(size_hint_y=None, height=0))
        img_container.add_widget(img)
        img_container.add_widget(Widget(size_hint_y=None, height=0))
        self.add_widget(img_container)

        info = BoxLayout(orientation='vertical', spacing=6, padding=(8, 0, 0, 0), size_hint=(1, 1))
        nombre = Label(
            text=f"[b]{bird.get('nombre_comun', bird.get('name', 'Ave'))}[/b]",
            markup=True,
            color=COLORS['text'],
            font_size=20,
            size_hint_y=None,
            height=32,
            halign='left',
            valign='middle'
        )
        nombre.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        cientifico = Label(
            text=f"[i]{bird.get('nombre_cientifico', 'Desconocido')}[/i]",
            markup=True,
            color=(0.2, 0.4, 0.2, 1),
            font_size=16,
            size_hint_y=None,
            height=24,
            halign='left',
            valign='middle'
        )
        cientifico.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        desc = Label(
            text=bird.get('descripcion', 'Sin descripción.'),
            color=COLORS['text'],
            font_size=14,
            size_hint_y=None,
            height=50,
            text_size=(Window.width - 120 - 80 - 48, None),  # Window.width - img - btn - paddings
            halign='left',
            valign='top'
        )
        carac = Label(
            text=f"[color=7CB342]Características:[/color] {bird.get('caracteristicas', 'No disponibles.')}",
            markup=True,
            color=COLORS['text'],
            font_size=13,
            size_hint_y=None,
            height=40,
            text_size=(Window.width - 120 - 80 - 48, None),
            halign='left',
            valign='top'
        )
        info.add_widget(nombre)
        info.add_widget(cientifico)
        info.add_widget(desc)
        info.add_widget(carac)
        self.add_widget(info)
        
        btn_container = BoxLayout(orientation='vertical', size_hint=(None, 1), width=80, padding=(0, 8))
        btn_container.add_widget(Widget())
        btn_ver = RoundedButton(
            text="Ver",
            rect_color=COLORS['primary'],
            size_hint=(None, None),
            size=(70, 35),
            font_size=16
        )
        if on_press:
            btn_ver.bind(on_press=on_press)
        btn_container.add_widget(btn_ver)
        btn_container.add_widget(Widget())
        self.add_widget(btn_container)

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
        self.shadow_rect.pos = (self.pos[0]+2, self.pos[1]-2)
        self.shadow_rect.size = self.size
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0]+1, self.pos[1]+1)
        self.border_rect.size = (self.size[0]-2, self.size[1]-2)

# --------- ReservasScreen ---------
class ReservaCard(BoxLayout):
    def __init__(self, reserva, on_press=None, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=160, padding=16, spacing=16, **kwargs)
        
        with self.canvas.before:
            Color(rgba=(0, 0, 0, 0.1))
            self.shadow_rect = RoundedRectangle(
                pos=(self.pos[0]+2, self.pos[1]-2), 
                size=(self.size[0], self.size[1]), 
                radius=[20]
            )
            
            Color(rgba=COLORS['surface'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
            
            Color(rgba=(*COLORS['success'][:3], 0.3))
            self.border_rect = RoundedRectangle(
                pos=(self.pos[0]+1, self.pos[1]+1), 
                size=(self.size[0]-2, self.size[1]-2), 
                radius=[16]
            )
        
        self.bind(pos=self.update_bg, size=self.update_bg)

        img_path = reserva.get("img", None)
        if img_path and os.path.exists(get_image_path(img_path)):
            img = Image(source=get_image_path(img_path), size_hint=(None, 1), width=110, allow_stretch=True, keep_ratio=True)
        else:
            img = Image(size_hint=(None, 1), width=110)
        self.add_widget(img)

        info = BoxLayout(orientation='vertical', spacing=6, padding=(0, 6, 0, 0))
        nombre = Label(text=f"[b]{reserva['nombre']}[/b]", markup=True, color=COLORS['text'], font_size=17, size_hint_y=None, height=28, halign='left', valign='middle')
        nombre.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        desc = Label(text=reserva.get('desc', ''), color=COLORS['text'], font_size=13, size_hint_y=None, height=40, text_size=(Window.width - 160, None), halign='left', valign='top')
        lat = reserva.get('lat', None)
        lon = reserva.get('lon', None)
        coords = ""
        if lat is not None and lon is not None:
            coords = f"[color=888888]Coordenadas:[/color] [b]{lat:.5f}, {lon:.5f}[/b]"
        coord_label = Label(text=coords, markup=True, color=COLORS['text'], font_size=12, size_hint_y=None, height=20, halign='left', valign='middle')
        coord_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        info.add_widget(nombre)
        info.add_widget(desc)
        info.add_widget(coord_label)
        self.add_widget(info)

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
        self.shadow_rect.pos = (self.pos[0]+2, self.pos[1]-2)
        self.shadow_rect.size = self.size
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.pos[0]+1, self.pos[1]+1)
        self.border_rect.size = (self.size[0]-2, self.size[1]-2)

class ReservasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        top_bar = BoxLayout(size_hint_y=None, height='48dp', padding=(0,0,0,0))
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        search_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=48, padding=(0,0,0,0), spacing=8)
        self.search_input = TextInput(
            hint_text="Buscar reserva por nombre",
            size_hint=(0.8, 1),
            height=44,
            multiline=False,
            background_color=COLORS['background'],
            foreground_color=COLORS['text'],
            padding=(16, 12, 16, 12),
            font_size=16,
            cursor_color=COLORS['primary'],
            background_normal='',
            background_active='',
            border=(16,16,16,16)
        )
        self.search_input.bind(text=lambda inst, val: self.update_list())
        search_bar.add_widget(self.search_input)
        clear_btn = RoundedButton(text="Limpiar", rect_color=COLORS['secondary'], size_hint=(0.2, 1), font_size=14)
        clear_btn.bind(on_press=lambda x: setattr(self.search_input, 'text', ''))
        search_bar.add_widget(clear_btn)
        layout.add_widget(search_bar)

        actividades = ["Todas"]
        act_set = set()
        for r in RESERVAS:
            for a in r.get('actividades', []):
                act_set.add(a)
        actividades.extend(sorted(list(act_set)))
        self.spinner = Spinner(
            text="Todas",
            values=tuple(actividades),
            size_hint_y=None,
            height=40,
            background_color=COLORS['primary'],
            color=COLORS['text'],
            font_size=15
        )
        self.spinner.bind(text=lambda inst, val: self.update_list())
        layout.add_widget(self.spinner)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=14, size_hint_y=None, padding=(0, 0, 0, 10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)
        self.add_widget(layout)
        self.bind(on_enter=self.update_list)

    def update_list(self, *args):
        self.grid.clear_widgets()
        filtro = self.spinner.text.lower()
        busqueda = self.search_input.text.lower().strip()
        found = False
        for reserva in RESERVAS:
            nombre_lower = reserva["nombre"].lower()
            match_busqueda = (busqueda == "") or (busqueda in nombre_lower)
            match_filtro = (filtro == "todas") or (filtro in [a.lower() for a in reserva.get("actividades", [])])
            if match_busqueda and match_filtro:
                card = ReservaCard(reserva, on_press=partial(self.show_reserva_detail, reserva))
                self.grid.add_widget(card)
                found = True
        if not found:
            self.grid.add_widget(Label(text="No se encontraron reservas.", color=COLORS['text'], size_hint_y=None, height=40))

    def on_marker_press(self, marker, *args):
        self.show_reserva_detail(marker.reserva)

    def create_card(self, reserva):
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=180, spacing=8, padding=12)
        img_path = reserva.get("img", None)
        if img_path and os.path.exists(get_image_path(img_path)):
            img = Image(source=get_image_path(img_path), size_hint=(1, None), height=80, allow_stretch=True, keep_ratio=True)
        else:
            img = Image(size_hint=(1, None), height=80)
        card.add_widget(img)

        info = BoxLayout(orientation='vertical', spacing=4, size_hint=(1, None), height=70)
        nombre = Label(text=f"[b]{reserva['nombre']}[/b]", markup=True, color=COLORS['text'], font_size=17, size_hint_y=None, height=28, halign='center', valign='middle')
        nombre.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        desc = Label(text=reserva.get('desc', ''), color=COLORS['text'], font_size=13, size_hint_y=None, height=32, halign='center', valign='top', text_size=(Window.width - 100, None))
        desc.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        lat = reserva.get('lat', None)
        lon = reserva.get('lon', None)
        coords = ""
        if lat is not None and lon is not None:
            coords = f"[color=888888]Coordenadas:[/color] [b]{lat:.5f}, {lon:.5f}[/b]"
        coord_label = Label(text=coords, markup=True, color=COLORS['text'], font_size=12, size_hint_y=None, height=20, halign='center', valign='middle')
        coord_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        info.add_widget(nombre)
        info.add_widget(desc)
        info.add_widget(coord_label)
        card.add_widget(info)

        btn_ver = RoundedButton(text="Ver", rect_color=COLORS['primary'], size_hint=(None, None), size=(90, 36), pos_hint={'center_x': 0.5})
        btn_ver.bind(on_press=partial(self.show_reserva_detail, reserva))
        card.add_widget(btn_ver)
        return card

    def show_reserva_detail(self, reserva, *args):
        detail_screen = ReservaDetailScreen(reserva, name="reserva_detail")
        if self.manager.has_screen("reserva_detail"):
            self.manager.remove_widget(self.manager.get_screen("reserva_detail"))
        self.manager.add_widget(detail_screen)
        self.manager.transition.direction = 'left'
        self.manager.current = "reserva_detail"

class ReservaDetailScreen(Screen):
    def __init__(self, reserva, **kwargs):
        super().__init__(**kwargs)
        self.reserva = reserva
        layout = BoxLayout(orientation='vertical', padding=16, spacing=12)
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        map_container = BoxLayout(orientation='vertical', size_hint=(1, None), height=300, padding=(0, 0, 0, 0), spacing=6)

        lat = reserva.get('lat', None)
        lon = reserva.get('lon', None)
        if lat is not None and lon is not None:
            map_title = Label(
                text=f"Ubicación: {reserva['nombre']}",
                color=COLORS['primary'],
                font_size=16,
                size_hint=(1, None),
                height=30
            )
            map_container.add_widget(map_title)
            
            simple_map = SimpleMapView(
                lat=lat, 
                lon=lon, 
                zoom=15, 
                title=reserva['nombre'],
                size_hint=(1, 1)
            )
            map_container.add_widget(simple_map)
        layout.add_widget(map_container)

        # Título centrado
        title = Label(text=f"[b]{reserva['nombre']}[/b]", markup=True, font_size=20, size_hint_y=None, height=36, halign='center', valign='middle', color=COLORS['text'])
        title.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        layout.add_widget(title)

        coords = ""
        if lat is not None and lon is not None:
            coords = f"[color=888888]Coordenadas:[/color] [b]{lat:.5f}, {lon:.5f}[/b]"
        coord_label = Label(text=coords, markup=True, font_size=13, color=COLORS['text'], size_hint_y=None, height=24, halign='center', valign='middle')
        coord_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        layout.add_widget(coord_label)

        img_path = reserva.get("img", None)
        if img_path and os.path.exists(get_image_path(img_path)):
            img = Image(source=get_thumbnail(img_path, max_width=800), size_hint=(1, None), height=140, allow_stretch=True, keep_ratio=True)
            layout.add_widget(img)


        desc = Label(text=reserva.get('desc', ''), font_size=15, size_hint_y=None, height=80, halign='center', valign='top', color=COLORS['text'])
        desc.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
        layout.add_widget(desc)


        layout.add_widget(Widget(size_hint=(1, 1)))

        self.add_widget(layout)

    def go_back(self, *args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'reservas'
        Clock.schedule_once(lambda dt: self.manager.remove_widget(self), 0.1)

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
        for bird in NICARAGUAN_BIRDS:
            card = BirdCard(bird, on_press=partial(self.show_bird_detail, bird))
            self.grid.add_widget(card)
        for bird in reversed(captured_birds):
            if 'foto' in bird and os.path.exists(get_image_path(bird['foto'])):
                card = BirdCard(bird, on_press=partial(self.show_bird_detail, bird))
                self.grid.add_widget(card)

    def show_bird_detail(self, bird, *args):
        try:

            detail_name = f"bird_detail_{id(bird)}"
            detail_screen = BirdDetailScreen(bird, name=detail_name)
            

            if self.manager.has_screen(detail_name):
                self.manager.remove_widget(self.manager.get_screen(detail_name))
            

            self.manager.add_widget(detail_screen)
            self.manager.transition.direction = 'left'
            self.manager.current = detail_name
        except Exception as e:
            print(f"Error mostrando detalle del ave: {e}")

            pass

class WebScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)


        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(
            text="Atrás",
            rect_color=COLORS['secondary'],
            size_hint=(None, None),
            size=(100, 40)
        )
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)


        title = Label(
            text="Web",
            color=COLORS['text'],
            font_size=24,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)


        self.info_label = Label(
            text="Abriendo EcoAves en el navegador web...",
            color=COLORS['text_secondary'],
            size_hint=(1, None),
            height=40
        )
        layout.add_widget(self.info_label)


        layout.add_widget(Widget(size_hint=(1, 1)))

        self.add_widget(layout)


        self.bind(on_enter=lambda *a: self.open_web_direct())

    def open_web_direct(self, *args):

        try:
            webbrowser.open(WEB_URL)
            self.info_label.text = "EcoAves abierto en el navegador web"
            Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'menu'), 2.0)
        except Exception as e:
            self.info_label.text = f"Error abriendo web: {str(e)[:50]}..."
            print(f"Error abriendo web: {e}")

        
# ---------- PANTALLA DE PERFIL DE USUARIO ----------
class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)
        
        title = Label(text="Mi Perfil", markup=True, color=COLORS['text'], font_size=24, size_hint_y=None, height=40)
        layout.add_widget(title)
        
        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=(0, 0, 0, 20))
        content.bind(minimum_height=content.setter('height'))
        
        if USER_PROFILE['nombre']:
           
            self.show_existing_profile(content)
        else:
            
            self.show_create_profile_form(content)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def show_existing_profile(self, content):
       
        info_section = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=200)
        info_title = Label(text="Información Personal", color=COLORS['primary'], font_size=18, size_hint_y=None, height=30)
        info_section.add_widget(info_title)
        
        name_label = Label(text=f"Nombre: {USER_PROFILE['nombre']}", color=COLORS['text'], font_size=16, size_hint_y=None, height=25)
        email_label = Label(text=f"Email: {USER_PROFILE['email']}", color=COLORS['text'], font_size=16, size_hint_y=None, height=25)
        bird_label = Label(text=f"Ave que buscas: {USER_PROFILE['ave_buscando']}", color=COLORS['text'], font_size=16, size_hint_y=None, height=25)
        
        info_section.add_widget(name_label)
        info_section.add_widget(email_label)
        info_section.add_widget(bird_label)
        content.add_widget(info_section)
        
        
        stats_section = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=150)
        stats_title = Label(text="Mis Estadísticas", color=COLORS['primary'], font_size=18, size_hint_y=None, height=30)
        stats_section.add_widget(stats_title)
        
        birds_label = Label(text=f"Aves registradas: {USER_PROFILE['aves_registradas']}", color=COLORS['text'], font_size=16, size_hint_y=None, height=25)
        photos_label = Label(text=f"Fotos subidas: {USER_PROFILE['fotos_subidas']}", color=COLORS['text'], font_size=16, size_hint_y=None, height=25)
        reserves_label = Label(text=f"Reservas visitadas: {USER_PROFILE['reservas_visitadas']}", color=COLORS['text'], font_size=16, size_hint_y=None, height=25)
        
        stats_section.add_widget(birds_label)
        stats_section.add_widget(photos_label)
        stats_section.add_widget(reserves_label)
        content.add_widget(stats_section)
        
        
        achievements_btn = RoundedButton(
            text="Ver Mis Logros",
            rect_color=COLORS['accent'],
            size_hint=(1, None),
            height=50
        )
        achievements_btn.bind(on_press=self.show_achievements)
        content.add_widget(achievements_btn)
        
        
        edit_btn = RoundedButton(
            text="Editar Perfil",
            rect_color=COLORS['secondary'],
            size_hint=(1, None),
            height=50
        )
        edit_btn.bind(on_press=self.edit_profile)
        content.add_widget(edit_btn)
    
    def show_create_profile_form(self, content):
        
        form_title = Label(text="Crear Mi Perfil", color=COLORS['primary'], font_size=20, size_hint_y=None, height=40)
        content.add_widget(form_title)
        
        
        self.name_input = TextInput(
            hint_text="Nombre completo",
            size_hint_y=None,
            height=50,
            background_color=COLORS['white'],
            foreground_color=COLORS['text'],
            font_size=16
        )
        content.add_widget(self.name_input)
        
        self.email_input = TextInput(
            hint_text="Correo electrónico",
            size_hint_y=None,
            height=50,
            background_color=COLORS['white'],
            foreground_color=COLORS['text'],
            font_size=16
        )
        content.add_widget(self.email_input)
        
        self.bird_input = TextInput(
            hint_text="Ave que estás buscando",
            size_hint_y=None,
            height=50,
            background_color=COLORS['white'],
            foreground_color=COLORS['text'],
            font_size=16
        )
        content.add_widget(self.bird_input)
        
        
        create_btn = RoundedButton(
            text="Crear Perfil",
            rect_color=COLORS['primary'],
            size_hint=(1, None),
            height=50
        )
        create_btn.bind(on_press=self.create_profile)
        content.add_widget(create_btn)
    
    def create_profile(self, instance):
        
        global USER_PROFILE, PROFILE_CREATED
        
        USER_PROFILE['nombre'] = self.name_input.text.strip()
        USER_PROFILE['email'] = self.email_input.text.strip()
        USER_PROFILE['ave_buscando'] = self.bird_input.text.strip()
        
        if USER_PROFILE['nombre']:
            PROFILE_CREATED = True
            save_profile()
            self.manager.current = 'profile'
        else:
            pass
    
    def edit_profile(self, instance):
        pass
    
    def show_achievements(self, instance):
        achievements_screen = AchievementsScreen(name="achievements")
        if self.manager.has_screen("achievements"):
            self.manager.remove_widget(self.manager.get_screen("achievements"))
        self.manager.add_widget(achievements_screen)
        self.manager.transition.direction = 'left'
        self.manager.current = "achievements"

# ---------- PANTALLA DE LOGROS ----------
class AchievementsScreen(Screen):
    ICON_SIZE = (80, 80)  

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)
        
        title = Label(text="Mis Logros", markup=True, color=COLORS['text'], font_size=24, size_hint_y=None, height=40)
        layout.add_widget(title)
        
        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=12, size_hint_y=None, padding=(0, 0, 0, 10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        self.bind(on_enter=self.populate_achievements)

    def get_icon_path_for_rarity(self, rarity):
        
        base_path = "Logos"
        icons = {
            'legendario': os.path.join(base_path, "icon_legendario.PNG"),
            'epico': os.path.join(base_path, "icon_epico.PNG"),
            'raro': os.path.join(base_path, "icon_raro.PNG"),
            'comun': os.path.join(base_path, "icon_comun.PNG"),
        }
        
        
        path = icons.get(rarity, icons['comun'])
        
        
        if not os.path.exists(path):
            variations = [
                path.replace(".PNG", ".png"),
                path.replace(".PNG", ".jpg"),
                path.replace(".PNG", ".JPG"),
                os.path.join("assets", "Logos", os.path.basename(path)),
                os.path.join("Logos", os.path.basename(path).replace(".PNG", ".png")),
            ]
            for var in variations:
                if os.path.exists(var):
                    return var
        return path

    def populate_achievements(self, *args):

        self.grid.clear_widgets()
        
        achievements = getattr(self, 'achievements', [
            {'nombre': 'Primer Avistamiento', 'rareza': 'comun', 'descripcion': 'Has visto tu primer ave.'},
            {'nombre': 'Ave Rara', 'rareza': 'raro', 'descripcion': 'Has visto un ave poco común.'},
            {'nombre': 'Explorador Épico', 'rareza': 'epico', 'descripcion': 'Has visto un ave épica.'},
            {'nombre': 'Maestro Legendario', 'rareza': 'legendario', 'descripcion': 'Has visto un ave legendaria.'},
        ])
        for ach in achievements:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, spacing=16, padding=(8, 8))
            icon_path = self.get_icon_path_for_rarity(ach['rareza'])
            icon = Image(source=icon_path, size_hint=(None, None), size=self.ICON_SIZE)
            row.add_widget(icon)
            text_box = BoxLayout(orientation='vertical', spacing=2)
            name_lbl = Label(text=ach['nombre'], color=COLORS['text'], font_size=18, bold=True, size_hint_y=None, height=30, halign='left', valign='middle')
            desc_lbl = Label(text=ach['descripcion'], color=COLORS['text'], font_size=14, size_hint_y=None, height=40, halign='left', valign='top')
            
            name_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            desc_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
            text_box.add_widget(name_lbl)
            text_box.add_widget(desc_lbl)
            row.add_widget(text_box)
            self.grid.add_widget(row)

    def go_back(self, instance):
        self.manager.transition.direction = 'right'
        self.manager.current = "profile"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)
        
        
        title = Label(text="Mis Logros", markup=True, color=COLORS['text'], font_size=24, size_hint_y=None, height=40)
        layout.add_widget(title)
        
        
        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=12, size_hint_y=None, padding=(0, 0, 0, 10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        self.bind(on_enter=self.populate_achievements)

    def get_icon_path_for_rarity(self, rarity):
        
        
        base_path = "Logos"
        icons = {
            'legendario': os.path.join(base_path, "icon_legendario.PNG"),
            'epico': os.path.join(base_path, "icon_epico.PNG"),
            'raro': os.path.join(base_path, "icon_raro.PNG"),
            'comun': os.path.join(base_path, "icon_comun.PNG"),
        }
        
        
        path = icons.get(rarity, icons['comun'])
        
        
        if not os.path.exists(path):
            variations = [
                path.replace(".PNG", ".png"),
                path.replace(".PNG", ".jpg"),
                path.replace(".PNG", ".JPG"),
                os.path.join("assets", "Logos", os.path.basename(path)),
                os.path.join("Logos", os.path.basename(path).replace(".PNG", ".png")),
            ]
            
            for alt_path in variations:
                if os.path.exists(alt_path):
                    return alt_path
        
        return path

    def populate_achievements(self, *args):
        
        self.grid.clear_widgets()
        
        
        rarity_colors = {
            'legendario': (1.0, 0.8, 0.0, 1), 
            'epico': (0.6, 0.2, 0.8, 1),       
            'raro': (0.2, 0.4, 0.8, 1),        
            'comun': (0.4, 0.6, 0.4, 1)        
        }
        
        from kivy.uix.image import Image
        for achievement in ACHIEVEMENTS:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=180, padding=20, spacing=12)
            
            
            rarity = achievement.get('rarity', 'comun')
            rarity_color = rarity_colors.get(rarity, rarity_colors['comun'])
            
            with card.canvas.before:
                if achievement['unlocked']:
                    Color(rgba=rarity_color)
                else:
                    Color(rgba=COLORS['surface'])
                self._bg_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[20])
            
            def update_bg_rect(instance, value):
                self._bg_rect.pos = card.pos
                self._bg_rect.size = card.size
            card.bind(pos=update_bg_rect, size=update_bg_rect)
            
            
            image_container = BoxLayout(orientation='vertical', size_hint_y=None, height=90, padding=(0, 10))
            
            
            icon_path = self.get_icon_path_for_rarity(rarity)
            icon_path = get_image_path(icon_path)  
            icon_exists = os.path.exists(icon_path)
            print(f"Intentando cargar icono para {rarity}: {icon_path} - Existe: {icon_exists}")
            if icon_exists:
                try:
                    icon_img = Image(
                        source=icon_path,
                        size_hint=(None, None),
                        size=(70, 70),  
                        allow_stretch=True,
                        keep_ratio=True,
                        pos_hint={'center_x': 0.5, 'center_y': 0.5}
                    )
                    
                    if not achievement['unlocked']:
                        icon_img.opacity = 0.4  
                    else:
                        icon_img.opacity = 1.0  
                    image_container.add_widget(icon_img)
                except Exception as e:
                    
                    image_placeholder = BoxLayout(
                        size_hint=(None, None),
                        size=(70, 70),
                        pos_hint={'center_x': 0.5, 'center_y': 0.5}
                    )
                    with image_placeholder.canvas.before:
                        Color(rgba=(0.9, 0.9, 0.9, 0.3))
                        RoundedRectangle(pos=image_placeholder.pos, size=image_placeholder.size, radius=[30])
                    temp_icon = Label(
                        text="$",
                        color=rarity_color,
                        font_size=24,
                        size_hint=(1, 1),
                        halign='center',
                        valign='middle'
                    )
                    image_placeholder.add_widget(temp_icon)
                    image_container.add_widget(image_placeholder)
            else:
                
                image_placeholder = BoxLayout(
                    size_hint=(None, None),
                    size=(70, 70),
                    pos_hint={'center_x': 0.5, 'center_y': 0.5}
                )
                with image_placeholder.canvas.before:
                    Color(rgba=(0.9, 0.9, 0.9, 0.3) if not achievement['unlocked'] else (1, 1, 1, 0.8))
                    RoundedRectangle(pos=image_placeholder.pos, size=image_placeholder.size, radius=[30])
                temp_icon = Label(
                    text="$" if achievement['unlocked'] else "○",
                    color=rarity_color if achievement['unlocked'] else COLORS['text_secondary'],
                    font_size=24,
                    size_hint=(1, 1),
                    halign='center',
                    valign='middle'
                )
                image_placeholder.add_widget(temp_icon)
                image_container.add_widget(image_placeholder)
            card.add_widget(image_container)
            
            
            info = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, height=80)
            
            
            name_label = Label(
                text=achievement['name'],
                color=COLORS['text'] if achievement['unlocked'] else COLORS['text_secondary'],
                font_size=18,
                size_hint_y=None,
                height=30,
                halign='center',
                valign='middle',
                bold=True if achievement['unlocked'] else False
            )
            name_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w, None)))
            info.add_widget(name_label)
            
            
            rarity_label = Label(
                text=rarity.upper(),
                color=rarity_color,
                font_size=14,
                size_hint_y=None,
                height=25,
                halign='center',
                valign='middle',
                bold=True
            )
            info.add_widget(rarity_label)
            
            
            desc_label = Label(
                text=achievement['description'],
                color=COLORS['text_secondary'],
                font_size=13,
                size_hint_y=None,
                height=40,
                text_size=(Window.width - 40, None),
                halign='center',
                valign='top'
            )
            desc_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 40, None)))
            info.add_widget(desc_label)
            
            card.add_widget(info)
            self.grid.add_widget(card)

    def go_back(self, *args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'profile'
        Clock.schedule_once(lambda dt: self.manager.remove_widget(self), 0.1)

# ---------- PANTALLA DE GUÍAS ----------
class GuidesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)
        
        
        title = Label(text="Guías de Aviturismo", markup=True, color=COLORS['text'], font_size=24, size_hint_y=None, height=40)
        layout.add_widget(title)
        
        
        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=1, spacing=12, size_hint_y=None, padding=(0, 0, 0, 10))
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        self.bind(on_enter=self.populate_guides)
    
    def populate_guides(self, *args):
        
        self.grid.clear_widgets()
        
        for guide in GUIDES:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=200, padding=16, spacing=8)
            
            
            with card.canvas.before:
                Color(rgba=COLORS['surface'])
                RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
            
            
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            name_label = Label(
                text=guide['nombre'],
                color=COLORS['primary'],
                font_size=18,
                size_hint=(0.7, 1),
                bold=True
            )
            specialty_label = Label(
                text=guide['especialidad'],
                color=COLORS['text_secondary'],
                font_size=14,
                size_hint=(0.3, 1)
            )
            header.add_widget(name_label)
            header.add_widget(specialty_label)
            card.add_widget(header)
            
            
            desc_label = Label(
                text=guide['descripcion'],
                color=COLORS['text'],
                font_size=14,
                size_hint_y=None,
                height=50,
                text_size=(Window.width - 32, None),
                halign='left',
                valign='top'
            )
            desc_label.bind(width=lambda inst, w: setattr(inst, 'text_size', (w - 32, None)))
            card.add_widget(desc_label)
            
            
            contact_info = BoxLayout(orientation='vertical', size_hint_y=None, height=60, spacing=4)
            contact_label = Label(
                text=f"Contacto: {guide['contacto']}",
                color=COLORS['text'],
                font_size=13,
                size_hint_y=None,
                height=20
            )
            email_label = Label(
                text=f"Email: {guide['email']}",
                color=COLORS['text'],
                font_size=13,
                size_hint_y=None,
                height=20
            )
            web_label = Label(
                text=f"Web: {guide['web']}",
                color=COLORS['text'],
                font_size=13,
                size_hint_y=None,
                height=20
            )
            contact_info.add_widget(contact_label)
            contact_info.add_widget(email_label)
            contact_info.add_widget(web_label)
            card.add_widget(contact_info)
            
            
            contact_btn = RoundedButton(
                text="Contactar",
                rect_color=COLORS['accent'],
                size_hint=(1, None),
                height=40
            )
            contact_btn.bind(on_press=partial(self.contact_guide, guide))
            card.add_widget(contact_btn)
            
            self.grid.add_widget(card)
    
    def contact_guide(self, guide, instance):
        
        try:
            
            import webbrowser
            email_url = f"mailto:{guide['email']}?subject=Consulta sobre Aviturismo&body=Hola, me interesa conocer más sobre sus servicios de aviturismo."
            webbrowser.open(email_url)
        except Exception as e:
            print(f"Error abriendo email: {e}")
        
class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        top_bar = BoxLayout(size_hint_y=None, height='48dp')
        self.back_btn = RoundedButton(text="Atrás", rect_color=COLORS['secondary'], size_hint=(None, None), size=(100, 40))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        top_bar.add_widget(self.back_btn)
        layout.add_widget(top_bar)

        title = Label(text=f"[b]Acerca de {APP_NAME}[/b]", markup=True, color=COLORS['text'], size_hint_y=None, height=40)
        layout.add_widget(title)

        about_text = (
            "ECO AVES es una aplicación diseñada para que cualquier persona pueda descubrir y "
            "disfrutar de la riqueza de las aves en Nicaragua de una manera sencilla y atractiva. "
            "En lugar de ser solo un libro digital, la aplicación permite a los visitantes apuntar la cámara "
            "de su celular hacia un ave y reconocerla al instante, a través del escáner de la aplicación; "
            "cada observación queda guardada como un recuerdo y un logro personal, lo que convierte la "
            "experiencia de avistamiento en algo divertido e interactivo. Más que una guía, ECO AVES es un "
            "compañero de viaje innovador, accesible, dinámico y atractivo, que conecta al turismo con la "
            "conservación y permite a cada explorador, vivir el avistamiento de aves como una aventura única "
            "y enriquecedora."
        )

        scroll = ScrollView(size_hint=(1, 1))
        about_label = Label(text=about_text, color=COLORS['text'], font_size=15, size_hint_y=None, halign='left', valign='top')
        about_label.bind(
            width=lambda inst, w: setattr(inst, 'text_size', (w - 20, None)),
            texture_size=lambda inst, ts: setattr(inst, 'height', ts[1] + 10)
        )
        scroll.add_widget(about_label)
        layout.add_widget(scroll)
        self.add_widget(layout)

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = FloatLayout()
        
        with main_layout.canvas.before:
            Color(rgba=COLORS['background'])
            self.bg_rect = RoundedRectangle(pos=(0, 0), size=(Window.width, Window.height))
            
        
        content_layout = BoxLayout(orientation='vertical', spacing=20, padding=(30, 40, 30, 30))
        
        logo_path = get_image_path('LogoEcoAvesPNG.png')
        logo = Image(
            source=logo_path, 
            size_hint=(0.95, None),
            height=250,
            pos_hint={'center_x': 0.5, 'center_y': 0.85}
        )
        main_layout.add_widget(logo)
        
        button_container = BoxLayout(orientation='vertical', spacing=12, size_hint_y=0.4, padding=(0, 20, 0, 20))
        
        button_configs = [
            ("profile", "Perfil", COLORS['primary'], COLORS['gradient_end']),
            ("gallery", "Galería", COLORS['success'], COLORS['gradient_start']),
            ("nearby", "Aves cercanas", COLORS['secondary'], COLORS['primary']),
            ("reservas", "Reservas", COLORS['gradient_start'], COLORS['accent']),
            ("guides", "Guías", COLORS['warning'], COLORS['success']),
            ("camera", "Detector de aves", COLORS['accent'], COLORS['warning']),
            ("achievements", "Logros", COLORS['primary'], COLORS['gradient_end']),
            ("web", "Web", COLORS['gradient_end'], COLORS['primary']),
            ("info", "Acerca de EcoAves", COLORS['text_secondary'], COLORS['accent'])
        ]
        
        for screen, text, color, glow_color in button_configs:
            btn = ModernButton(
                text=text,
                rect_color=COLORS['primary'],  
                size_hint=(0.9, None),
                height=50,
                pos_hint={'center_x': 0.5},
                font_size=16
            )
            btn.bind(on_press=partial(self.navigate_to_screen, screen))
            button_container.add_widget(btn)
        
        content_layout.add_widget(button_container)
        
        footer = Label(
            text="Explora - Descubre - Conserva",
            font_size=14,
            color=COLORS['text_secondary'],
            size_hint_y=None,
            height=40
        )
        content_layout.add_widget(footer)
        spacer = Widget(size_hint_y=None, height=20)
        content_layout.add_widget(spacer)
        
        main_layout.add_widget(content_layout)
        self.add_widget(main_layout)
    
    
    def navigate_to_screen(self, screen_name, instance):
        
        self.manager.current = screen_name


# ---------- APP ----------
class EcoAvesApp(App):
    def build(self):
        
        load_profile()
        
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(GalleryScreen(name="gallery"))
        sm.add_widget(NearbyScreen(name="nearby"))
        sm.add_widget(ReservasScreen(name="reservas"))
        sm.add_widget(AchievementsScreen(name="achievements"))
        sm.add_widget(GuidesScreen(name="guides"))
        sm.add_widget(WebScreen(name="web"))
        sm.add_widget(InfoScreen(name="info"))
        
        
        global PROFILE_CREATED
        if not PROFILE_CREATED:
            sm.current = "profile"
        
        return sm
if __name__ == "__main__":
    if not MAPVIEW_AVAILABLE:
        print("\n" + "="*60)
        print("IMPORTANTE: Para ver mapas embebidos en la app:")
        print("1. Instale kivy-garden: pip install kivy-garden")
        print("2. Instale mapview: garden install mapview")
        print("3. Reinicie la aplicación")
        print("="*60 + "\n")
    
    EcoAvesApp().run()
