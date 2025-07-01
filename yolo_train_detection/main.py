#!/usr/bin/env python3
"""
YOLO Fine-tuning Tool - Archivo Principal
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gui.main_window import YOLOFineTuningTool
except ImportError as e:
    print(f"Error al importar modulos: {e}")
    print("\nPosibles soluciones:")
    print("1. Ejecutar: python setup_project.py")
    print("2. Verificar que todos los archivos esten en sus carpetas")
    print("3. Instalar dependencias: pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Función principal"""
    print("Iniciando YOLO Fine-tuning Tool...")

    try:
        root = tk.Tk()
        app = YOLOFineTuningTool(root)

        # Configurar cierre de aplicación
        def on_closing():
            if hasattr(app, 'training_process') and app.training_process and app.training_process.poll() is None:
                result = messagebox.askyesno("Salir",
                                           "Hay un entrenamiento en progreso.\n" +
                                           "Quieres detenerlo y salir?")
                if result:
                    app.training_process.terminate()
                    root.destroy()
            else:
                root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_closing)

        # Centrar ventana
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

        print("Aplicacion iniciada correctamente!")
        root.mainloop()

    except Exception as e:
        print(f"Error al iniciar la aplicacion: {e}")
        messagebox.showerror("Error", f"Error al iniciar la aplicacion:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
