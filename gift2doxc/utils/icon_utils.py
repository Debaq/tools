#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icon utilities - Descarga automática de iconos Lucide
"""

import os
import requests
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
import threading
import time

class IconManager:
    """Gestor de iconos con descarga automática desde Lucide"""
    
    def __init__(self, cache_dir="assets/icons"):
        self.cache_dir = cache_dir
        self.icons = {}
        self.downloading = set()
        self.failed_icons = set()
        
        # Crear directorio de cache si no existe
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Iconos por defecto para la aplicación
        self.app_icons = {
            "file-text": "Archivos GIFT",
            "file-pen-line": "Crear evaluaciones",
            "search": "Revisar evaluaciones", 
            "settings": "Configuración",
            "circle-plus": "Agregar pregunta",
            "trash-2": "Eliminar",
            "arrow-up": "Subir pregunta",
            "arrow-down": "Bajar pregunta",
            "save": "Guardar",
            "folder-open": "Abrir carpeta",
            "eye": "Vista previa",
            "download": "Descargar",
            "upload": "Cargar",
            "circle-check": "Completado",
            "circle-x": "Error",
            "triangle-alert": "Advertencia",
            "info": "Información"
        }
    
    def get_icon_path(self, name, size=24):
        """Obtener ruta del archivo de icono"""
        return os.path.join(self.cache_dir, f"{name}_{size}.png")
    
    def icon_exists(self, name, size=24):
        """Verificar si el icono existe localmente"""
        return os.path.exists(self.get_icon_path(name, size))
    
    def download_icon_from_lucide(self, name, size=24, color="000000"):
        """Descargar icono desde GitHub de Lucide"""
        try:
            # URL correcta de GitHub raw para Lucide
            url = f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg"
            
            # Timeout para evitar bloqueos
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            svg_content = response.text
            
            # Verificar que es un SVG válido
            if not svg_content.strip().startswith('<svg'):
                raise Exception(f"No se encontró el icono '{name}' en Lucide")
            
            # Modificar color del stroke
            svg_content = svg_content.replace('stroke="currentColor"', f'stroke="#{color}"')
            
            # Convertir SVG a PNG usando cairosvg si está disponible
            try:
                import cairosvg
                png_data = cairosvg.svg2png(
                    bytestring=svg_content.encode('utf-8'),
                    output_width=size,
                    output_height=size
                )
                
                # Guardar archivo
                icon_path = self.get_icon_path(name, size)
                with open(icon_path, "wb") as f:
                    f.write(png_data)
                
                print(f"✓ Icono {name} descargado desde GitHub")
                return True
                
            except ImportError:
                print("cairosvg no está instalado. Usando fallback...")
                # Fallback: crear icono simple
                return self.create_fallback_icon_file(name, size)
                
        except requests.exceptions.RequestException as e:
            if "404" in str(e):
                # Obtener información del caller
                import traceback
                caller_info = self.get_caller_info()
                print(f"✗ Icono '{name}' no encontrado en Lucide")
                print(f"  Solicitado desde: {caller_info}")
                print(f"  Iconos disponibles en: https://lucide.dev/icons/")
                print(f"  Sugerencia: Verificar que el nombre sea correcto")
            else:
                print(f"Error de conexión descargando icono {name}: {e}")
            return False
        except Exception as e:
            print(f"Error descargando icono {name}: {e}")
            return False
    
    def get_caller_info(self):
        """Obtener información del archivo y línea que pidió el icono"""
        import traceback
        import os
        
        # Obtener el stack trace
        stack = traceback.extract_stack()
        
        # Buscar el primer frame que no sea de icon_utils
        for frame in reversed(stack[:-2]):  # Excluir frames actuales
            filename = os.path.basename(frame.filename)
            if filename != "icon_utils.py" and not filename.startswith("__"):
                return f"{filename}:{frame.lineno} en {frame.name}()"
        
        # Fallback si no encuentra info útil
        return "ubicación desconocida"
    
    def load_icon(self, name, size=24, color="000000"):
        """Cargar icono, descargándolo si no existe"""
        key = f"{name}_{size}_{color}"
        
        # Si ya está en memoria, devolverlo
        if key in self.icons:
            return self.icons[key]
        
        # Si ya falló anteriormente, usar fallback en memoria
        if name in self.failed_icons:
            return self.create_memory_fallback(name, size)
        
        icon_path = self.get_icon_path(name, size)
        
        # Si el archivo existe, cargarlo
        if self.icon_exists(name, size):
            try:
                img = Image.open(icon_path)
                self.icons[key] = ImageTk.PhotoImage(img)
                return self.icons[key]
            except Exception as e:
                print(f"Error cargando icono {name}: {e}")
                # Si falla cargar, intentar re-descargar
                os.remove(icon_path)
        
        # Si no existe, descargarlo
        if name not in self.downloading:
            self.downloading.add(name)
            
            # CAPTURAR INFORMACIÓN DEL CALLER ANTES del threading
            caller_info = self.get_caller_info()
            
            # Descargar en hilo separado para no bloquear UI
            def download_thread():
                success = self.download_icon_from_lucide(name, size, color, caller_info)
                self.downloading.discard(name)
                
                if not success:
                    self.failed_icons.add(name)
            
            thread = threading.Thread(target=download_thread, daemon=True)
            thread.start()
        
        # Mientras tanto, devolver fallback en memoria
        return self.create_memory_fallback(name, size)
    
    def download_icon_from_lucide(self, name, size=24, color="000000", caller_info=None):
        """Descargar icono desde GitHub de Lucide"""
        try:
            # URL correcta de GitHub raw para Lucide
            url = f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg"
            
            # Timeout para evitar bloqueos
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            svg_content = response.text
            
            # Verificar que es un SVG válido
            if not svg_content.strip().startswith('<svg'):
                raise Exception(f"No se encontró el icono '{name}' en Lucide")
            
            # Modificar color del stroke
            svg_content = svg_content.replace('stroke="currentColor"', f'stroke="#{color}"')
            
            # Convertir SVG a PNG usando cairosvg si está disponible
            try:
                import cairosvg
                png_data = cairosvg.svg2png(
                    bytestring=svg_content.encode('utf-8'),
                    output_width=size,
                    output_height=size
                )
                
                # Guardar archivo
                icon_path = self.get_icon_path(name, size)
                with open(icon_path, "wb") as f:
                    f.write(png_data)
                
                print(f"✓ Icono {name} descargado desde GitHub")
                return True
                
            except ImportError:
                print("cairosvg no está instalado. Usando fallback...")
                # Fallback: crear icono simple
                return self.create_fallback_icon_file(name, size)
                
        except requests.exceptions.RequestException as e:
            if "404" in str(e):
                print(f"✗ Icono '{name}' no encontrado en Lucide")
                if caller_info:
                    print(f"  Solicitado desde: {caller_info}")
                else:
                    print(f"  Solicitado desde: ubicación desconocida")
                print(f"  Iconos disponibles en: https://lucide.dev/icons/")
                print(f"  Sugerencia: Verificar que el nombre sea correcto")
            else:
                print(f"Error de conexión descargando icono {name}: {e}")
            return False
        except Exception as e:
            print(f"Error descargando icono {name}: {e}")
            return False
    
    def get_caller_info(self):
        """Obtener información del archivo y línea que pidió el icono"""
        import traceback
        import os
        
        # Obtener el stack trace
        stack = traceback.extract_stack()
        
        # Buscar el primer frame que no sea de icon_utils ni threading
        for frame in reversed(stack[:-1]):  # Excluir frame actual
            filename = os.path.basename(frame.filename)
            if (filename != "icon_utils.py" and 
                filename != "threading.py" and 
                not filename.startswith("__") and
                "site-packages" not in frame.filename):
                
                # Obtener una línea de código si es posible
                code_line = ""
                try:
                    with open(frame.filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if 0 <= frame.lineno - 1 < len(lines):
                            code_line = f" -> {lines[frame.lineno - 1].strip()}"
                except:
                    pass
                
                return f"{filename}:{frame.lineno} en {frame.name}(){code_line}"
        
        # Fallback si no encuentra info útil
        return "ubicación desconocida"
    
    def create_fallback_icon_file(self, name, size):
        """Crear icono fallback simple y guardarlo"""
        try:
            # Crear imagen simple con letra inicial
            img = Image.new('RGBA', (size, size), (70, 130, 180, 255))  # SteelBlue
            
            # Guardar como PNG
            icon_path = self.get_icon_path(name, size)
            img.save(icon_path, "PNG")
            return True
            
        except Exception as e:
            print(f"Error creando fallback para {name}: {e}")
            return False
    
    def load_icon(self, name, size=24, color="000000"):
        """Cargar icono, descargándolo si no existe"""
        key = f"{name}_{size}_{color}"
        
        # Si ya está en memoria, devolverlo
        if key in self.icons:
            return self.icons[key]
        
        # Si ya falló anteriormente, usar fallback en memoria
        if name in self.failed_icons:
            return self.create_memory_fallback(name, size)
        
        icon_path = self.get_icon_path(name, size)
        
        # Si el archivo existe, cargarlo
        if self.icon_exists(name, size):
            try:
                img = Image.open(icon_path)
                self.icons[key] = ImageTk.PhotoImage(img)
                return self.icons[key]
            except Exception as e:
                print(f"Error cargando icono {name}: {e}")
                # Si falla cargar, intentar re-descargar
                os.remove(icon_path)
        
        # Si no existe, descargarlo
        if name not in self.downloading:
            self.downloading.add(name)
            
            # Descargar en hilo separado para no bloquear UI
            def download_thread():
                success = self.download_icon_from_lucide(name, size, color)
                self.downloading.discard(name)
                
                if not success:
                    self.failed_icons.add(name)
            
            thread = threading.Thread(target=download_thread, daemon=True)
            thread.start()
        
        # Mientras tanto, devolver fallback en memoria
        return self.create_memory_fallback(name, size)
    
    def create_memory_fallback(self, name, size):
        """Crear icono fallback en memoria"""
        key = f"fallback_{name}_{size}"
        
        if key not in self.icons:
            # Crear imagen simple con texto
            img = Image.new('RGBA', (size, size), (128, 128, 128, 255))
            
            # Intentar agregar texto si PIL lo soporta
            try:
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(img)
                
                # Usar primera letra del nombre del icono
                text = name[0].upper() if name else "?"
                
                # Intentar cargar fuente, o usar default
                try:
                    font_size = max(8, size // 3)
                    font = ImageFont.load_default()
                except:
                    font = None
                
                # Centrar texto
                if font:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = (size - text_width) // 2
                    y = (size - text_height) // 2
                    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
                
            except ImportError:
                pass  # PIL sin ImageDraw
            
            self.icons[key] = ImageTk.PhotoImage(img)
        
        return self.icons[key]
    
    def preload_app_icons(self, sizes=[16, 24, 32]):
        """Pre-cargar iconos comunes de la aplicación"""
        def preload_thread():
            for icon_name in self.app_icons.keys():
                for size in sizes:
                    if not self.icon_exists(icon_name, size):
                        self.download_icon_from_lucide(icon_name, size)
                        time.sleep(0.1)  # Pequeña pausa para no saturar la API
        
        thread = threading.Thread(target=preload_thread, daemon=True)
        thread.start()
    
    def clear_cache(self):
        """Limpiar cache de iconos"""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.png'):
                    os.remove(os.path.join(self.cache_dir, filename))
            self.icons.clear()
            self.failed_icons.clear()
            print("Cache de iconos limpiado")
        except Exception as e:
            print(f"Error limpiando cache: {e}")
    
    def get_available_icons(self):
        """Obtener lista de iconos disponibles"""
        return list(self.app_icons.keys())
    
    def install_cairosvg(self):
        """Intentar instalar cairosvg automáticamente"""
        try:
            import subprocess
            import sys
            
            print("Instalando cairosvg para mejor calidad de iconos...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "cairosvg"])
            print("cairosvg instalado correctamente")
            return True
        except Exception as e:
            print(f"No se pudo instalar cairosvg: {e}")
            return False

# Instancia global del gestor de iconos
icon_manager = IconManager()

# Funciones de conveniencia
def get_icon(name, size=24, color="000000"):
    """Función conveniente para obtener iconos"""
    return icon_manager.load_icon(name, size, color)

def preload_icons():
    """Pre-cargar iconos comunes"""
    icon_manager.preload_app_icons()

def clear_icon_cache():
    """Limpiar cache de iconos"""
    icon_manager.clear_cache()

def list_available_icons():
    """Listar iconos disponibles"""
    return icon_manager.get_available_icons()

# Inicializar automáticamente
if __name__ != "__main__":
    # Pre-cargar iconos en background cuando se importa el módulo
    preload_icons()

# Para testing
if __name__ == "__main__":
    # Test básico
    root = tk.Tk()
    root.title("Test de Iconos")
    
    frame = tk.Frame(root, padding=20)
    frame.pack()
    
    # Probar algunos iconos
    test_icons = ["file-pen-line", "search", "save", "settings"]
    
    for i, icon_name in enumerate(test_icons):
        icon = get_icon(icon_name, 32)
        btn = tk.Button(frame, text=icon_name, image=icon, compound="top")
        btn.grid(row=0, column=i, padx=10, pady=10)
    
    root.mainloop()