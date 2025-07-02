#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gift Converter - Convertidor de archivos GIFT a DOCX
Punto de entrada principal de la aplicación
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Verificar e instalar dependencias opcionales"""
    missing_deps = []
    
    # Verificar dependencias principales
    try:
        import docx
    except ImportError:
        missing_deps.append("python-docx")
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print("Dependencias faltantes:", ", ".join(missing_deps))
        print("Instale con: pip install", " ".join(missing_deps))
        return False
    
    # Verificar dependencias opcionales
    try:
        import cairosvg
        print("✓ cairosvg encontrado - iconos de alta calidad habilitados")
    except ImportError:
        print("ℹ cairosvg no encontrado - se usarán iconos básicos")
        print("  Para mejor calidad: pip install cairosvg")
    
    return True

def main():
    """Función principal de la aplicación"""
    try:
        # Verificar dependencias
        if not check_dependencies():
            input("Presione Enter para salir...")
            sys.exit(1)
        
        # Importar módulos después de verificar dependencias
        try:
            from ui.main_window import MainWindow
            from utils.icon_utils import preload_icons
        except ImportError as e:
            print(f"Error importing modules: {e}")
            print("Make sure all required files are in the correct directories")
            print("Required structure:")
            print("  ui/main_window.py")
            print("  utils/icon_utils.py")
            input("Presione Enter para salir...")
            sys.exit(1)
        
        # Crear ventana principal
        root = tk.Tk()
        root.title("Gift Converter v2.0")
        #root.geometry("500x400")
        #el auto resize se ancarga
        
        # Centrar ventana en pantalla
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (500 // 2)
        y = (root.winfo_screenheight() // 2) - (400 // 2)
        root.geometry(f"500x400+{x}+{y}")
        
        # Configurar icono si existe
        try:
            # root.iconbitmap("assets/icon.ico")  # Uncomment when icon is available
            pass
        except:
            pass
        
        # Pre-cargar iconos en background
        print("Cargando iconos...")
        preload_icons()
        
        # Crear aplicación principal
        app = MainWindow(root)
        
        # Configurar cierre limpio
        def on_closing():
            if messagebox.askokcancel("Salir", "¿Está seguro que desea cerrar la aplicación?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Configurar variables de entorno para mejor renderizado
        try:
            root.tk.call('tk', 'scaling', 1.0)  # Mejorar escalado en HiDPI
        except:
            pass
        
        print("Aplicación iniciada correctamente")
        
        # Iniciar loop principal
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")
        sys.exit(0)
    except Exception as e:
        error_msg = f"Error fatal al iniciar la aplicación:\n{str(e)}"
        print(error_msg)
        try:
            messagebox.showerror("Error Fatal", error_msg)
        except:
            print("No se pudo mostrar el diálogo de error")
        sys.exit(1)

if __name__ == "__main__":
    main()