#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window - Página de inicio de Gift Converter
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.window_utils import make_auto_resizable
import sys
import os

# Importar utilidades
try:
    from utils.icon_utils import get_icon
except ImportError:
    print("Warning: icon_utils not found")
    def get_icon(name, size=24, color="000000"):
        return None

class MainWindow:
    """Ventana principal con página de inicio"""
    
    def __init__(self, root):
        self.root = root
        self.auto_resizer = make_auto_resizable(root, padding=40)
        self.current_wizard = None
        self.show_home_page()
    
    def show_home_page(self):
        """Mostrar página de inicio"""
        # Limpiar ventana
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Cambiar título
        self.root.title("Gift Converter v2.0")
        
        # Crear interfaz de inicio
        self.setup_ui()
        
        # Programar auto-resize
        if self.auto_resizer:
            self.auto_resizer.schedule_resize(100)
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        # Configurar grid principal
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Crear frame principal
        main_frame = ttk.Frame(self.root, padding="40")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === HEADER ===
        self.create_header(main_frame)
        
        # === BOTONES PRINCIPALES ===
        self.create_main_buttons(main_frame)
        
        # === FOOTER ===
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Crear encabezado de la aplicación"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        header_frame.columnconfigure(0, weight=1)
        
        # Título principal
        title_label = ttk.Label(
            header_frame,
            text="Gift Converter",
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # Subtítulo
        subtitle_label = ttk.Label(
            header_frame,
            text="Convertidor de archivos GIFT a documentos DOCX",
            font=("Arial", 12),
            foreground="gray"
        )
        subtitle_label.grid(row=1, column=0)
        
        # Versión
        version_label = ttk.Label(
            header_frame,
            text="Versión 2.0",
            font=("Arial", 10),
            foreground="lightgray"
        )
        version_label.grid(row=2, column=0, pady=(5, 0))
    
    def create_main_buttons(self, parent):
        """Crear botones principales de navegación"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=1, column=0, sticky="ew", pady=20)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        
        # === BOTÓN CREAR EVALUACIONES ===
        create_frame = ttk.LabelFrame(buttons_frame, text="", padding="20")
        create_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        create_frame.columnconfigure(0, weight=1)
        
        # Icono de crear
        create_icon = get_icon("file-pen-line", 48)
        create_icon_label = ttk.Label(create_frame, image=create_icon)
        create_icon_label.grid(row=0, column=0, pady=(0, 10))
        # Mantener referencia para evitar garbage collection
        create_icon_label.image = create_icon
        
        # Título del botón
        create_title = ttk.Label(
            create_frame,
            text="Crear Evaluaciones",
            font=("Arial", 16, "bold")
        )
        create_title.grid(row=1, column=0, pady=(0, 10))
        
        # Descripción
        create_desc = ttk.Label(
            create_frame,
            text="Convertir archivos GIFT en\ndocumentos de examen DOCX\ncon hoja de respuestas",
            font=("Arial", 10),
            foreground="gray",
            justify="center"
        )
        create_desc.grid(row=2, column=0, pady=(0, 15))
        
        # Botón de acción
        create_button = ttk.Button(
            create_frame,
            text="Comenzar",
            command=self.open_creation_wizard,
            style="Accent.TButton"
        )
        create_button.grid(row=3, column=0, sticky="ew", padx=20)
        
        # === BOTÓN REVISAR EVALUACIONES ===
        review_frame = ttk.LabelFrame(buttons_frame, text="", padding="20")
        review_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        review_frame.columnconfigure(0, weight=1)
        
        # Icono de revisar
        review_icon = get_icon("search", 48, "808080")  # Gris para indicar deshabilitado
        review_icon_label = ttk.Label(review_frame, image=review_icon)
        review_icon_label.grid(row=0, column=0, pady=(0, 10))
        # Mantener referencia
        review_icon_label.image = review_icon
        
        # Título del botón
        review_title = ttk.Label(
            review_frame,
            text="Revisar Evaluaciones",
            font=("Arial", 16, "bold"),
            foreground="gray"
        )
        review_title.grid(row=1, column=0, pady=(0, 10))
        
        # Descripción
        review_desc = ttk.Label(
            review_frame,
            text="Analizar resultados de\nevaluaciones aplicadas\ny generar estadísticas",
            font=("Arial", 10),
            foreground="lightgray",
            justify="center"
        )
        review_desc.grid(row=2, column=0, pady=(0, 15))
        
        # Botón de acción (deshabilitado)
        review_button = ttk.Button(
            review_frame,
            text="Próximamente",
            command=self.show_coming_soon,
            state="disabled"
        )
        review_button.grid(row=3, column=0, sticky="ew", padx=20)
        
        # Hacer que los frames tengan la misma altura
        buttons_frame.rowconfigure(0, weight=1, uniform="buttons")
    
    def create_footer(self, parent):
        """Crear pie de página con información adicional"""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=3, column=0, sticky="ew", pady=(30, 0))
        footer_frame.columnconfigure(0, weight=1)
        
        # Separador
        separator = ttk.Separator(footer_frame, orient="horizontal")
        separator.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Frame para botones secundarios
        secondary_frame = ttk.Frame(footer_frame)
        secondary_frame.grid(row=1, column=0)
        
        # Botón de configuración
        config_icon = get_icon("settings", 16)
        config_button = ttk.Button(
            secondary_frame,
            text=" Configuración",
            image=config_icon,
            compound="left",
            command=self.open_settings
        )
        config_button.pack(side=tk.LEFT, padx=5)
        # Mantener referencia
        config_button.image = config_icon
        
        # Botón de ayuda
        help_icon = get_icon("info", 16)
        help_button = ttk.Button(
            secondary_frame,
            text=" Ayuda",
            image=help_icon,
            compound="left",
            command=self.show_help
        )
        help_button.pack(side=tk.LEFT, padx=5)
        # Mantener referencia
        help_button.image = help_icon
        
        # Información del desarrollador
        dev_info = ttk.Label(
            footer_frame,
            text="Desarrollado para conversión de archivos GIFT educativos",
            font=("Arial", 8),
            foreground="lightgray"
        )
        dev_info.grid(row=2, column=0, pady=(15, 0))
    
    def open_creation_wizard(self):
        """Cambiar a la vista del wizard de creación en la misma ventana"""
        try:
            # Importar wizard de creación
            from ui.creation.creation_wizard import CreationWizard
            
            # Limpiar la ventana actual
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Cambiar título
            self.root.title("Crear Evaluación - Gift Converter")
            
            # Crear wizard en la misma ventana, pasando referencia a self
            self.current_wizard = CreationWizard(self.root, main_window=self)
            
            # Programar auto-resize
            if self.auto_resizer:
                self.auto_resizer.schedule_resize(100)
            
        except ImportError as e:
            messagebox.showerror(
                "Error",
                f"No se pudo cargar el wizard de creación:\n{e}\n\n"
                "Asegúrese de que existe el archivo:\n"
                "ui/creation/creation_wizard.py"
            )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al abrir el wizard de creación:\n{e}"
            )
    
    def show_coming_soon(self):
        """Mostrar mensaje de próximamente"""
        messagebox.showinfo(
            "Próximamente",
            "La funcionalidad de revisión de evaluaciones\n"
            "estará disponible en una próxima versión.\n\n"
            "Por ahora, puede usar la función de\n"
            "creación de evaluaciones."
        )
    
    def open_settings(self):
        """Abrir ventana de configuración"""
        try:
            from ui.dialogs.settings_dialog import SettingsDialog
            
            dialog = SettingsDialog(self.root)
            
        except ImportError:
            messagebox.showinfo(
                "Configuración",
                "Panel de configuración en desarrollo.\n\n"
                "Las opciones de configuración están disponibles\n"
                "en el wizard de creación de evaluaciones."
            )
    
    def show_help(self):
        """Mostrar ayuda"""
        help_text = """Gift Converter v2.0

CREAR EVALUACIONES:
• Seleccione archivos GIFT (.gift, .txt)
• Configure opciones de aleatorización
• Edite preguntas y detecte problemas
• Configure formato de página
• Genere documentos DOCX

FORMATOS SOPORTADOS:
• Entrada: GIFT, TXT
• Salida: DOCX (Word)

CARACTERÍSTICAS:
• Preguntas de alternativas múltiples
• Preguntas de desarrollo
• Hoja de respuestas automática
• Detección de problemas en preguntas
• Configuración de fuentes y márgenes

Para más información, use el wizard de creación."""
        
        messagebox.showinfo("Ayuda - Gift Converter", help_text)

# Crear estilos personalizados para botones
def setup_styles(root):
    """Configurar estilos personalizados"""
    style = ttk.Style()
    
    # Estilo para botón principal
    style.configure(
        "Accent.TButton",
        font=("Arial", 11, "bold")
    )

# Función de prueba
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Gift Converter")
    root.geometry("500x400")
    
    setup_styles(root)
    app = MainWindow(root)
    
    root.mainloop()