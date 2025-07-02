#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creation Wizard - Wizard principal para creación de evaluaciones
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Importar utilidades
try:
    from utils.window_utils import setup_wizard_window
    from utils.icon_utils import get_icon
except ImportError as e:
    print(f"Warning: utils not found - {e}")
    def setup_wizard_window(window, **kwargs):
        return None
    def get_icon(name, size=24, color="000000"):
        return None

class CreationWizard:
    """Wizard principal para creación de evaluaciones"""
    
    def __init__(self, root, main_window=None):
        self.root = root
        self.main_window = main_window  # Referencia al MainWindow
        self.current_step = 0
        self.total_steps = 5
        
        # Configurar ventana como wizard (sin setup_wizard_window ya que está en la misma ventana)
        self.auto_resizer = None
        
        # Variables compartidas entre steps
        self.shared_data = {
            'gift_files': [],
            'questions': [],
            'answer_keys': {},
            'config': {}
        }
        
        # Lista de steps
        self.steps = []
        self.step_frames = []
        
        # Configurar UI
        self.setup_ui()
        self.load_steps()
        self.show_step(0)
    
    def setup_ui(self):
        """Configurar interfaz principal del wizard"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # === SIDEBAR ===
        self.create_sidebar(main_frame)
        
        # === CONTENIDO PRINCIPAL ===
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(20, 0))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Frame para steps
        self.steps_container = ttk.Frame(content_frame)
        self.steps_container.grid(row=0, column=0, sticky="nsew")
        self.steps_container.columnconfigure(0, weight=1)
        self.steps_container.rowconfigure(0, weight=1)
        
        # === NAVEGACIÓN ===
        self.create_navigation(content_frame)
        
        # Configurar grid principal
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def create_sidebar(self, parent):
        """Crear sidebar con progreso del wizard"""
        sidebar = ttk.LabelFrame(parent, text="Progreso", padding="15")
        sidebar.grid(row=0, column=0, sticky="nsew", rowspan=2, padx=(0, 10))
        sidebar.columnconfigure(0, weight=1)
        
        # Título del wizard
        title_label = ttk.Label(
            sidebar,
            text="Crear Evaluación",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Lista de steps
        self.step_labels = []
        step_names = [
            "1. Seleccionar archivos",
            "2. Configurar opciones", 
            "3. Editar preguntas",
            "4. Formato de página",
            "5. Generar documentos"
        ]
        
        for i, step_name in enumerate(step_names):
            # Frame para cada step
            step_frame = ttk.Frame(sidebar)
            step_frame.grid(row=i+1, column=0, sticky="ew", pady=2)
            step_frame.columnconfigure(1, weight=1)
            
            # Icono de estado
            pending_icon = get_icon("circle", 12, "999999")  # Gris para pendiente
            status_label = ttk.Label(step_frame, image=pending_icon)
            status_label.grid(row=0, column=0, padx=(0, 10))
            if pending_icon:
                status_label.image = pending_icon
            
            # Nombre del step
            name_label = ttk.Label(
                step_frame,
                text=step_name,
                font=("Arial", 10)
            )
            name_label.grid(row=0, column=1, sticky="w")
            
            self.step_labels.append({
                'frame': step_frame,
                'status': status_label,
                'name': name_label
            })
        
        # Información adicional
        separator = ttk.Separator(sidebar, orient="horizontal")
        separator.grid(row=len(step_names)+1, column=0, sticky="ew", pady=20)
        
        # Estadísticas
        self.stats_frame = ttk.Frame(sidebar)
        self.stats_frame.grid(row=len(step_names)+2, column=0, sticky="ew")
        self.update_stats()
    
    def create_navigation(self, parent):
        """Crear botones de navegación"""
        nav_frame = ttk.Frame(parent)
        nav_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        nav_frame.columnconfigure(2, weight=1)
        
        # Botón Inicio
        home_icon = get_icon("house", 16)
        self.home_button = ttk.Button(
            nav_frame,
            text=" Inicio",
            image=home_icon,
            compound="left",
            command=self.go_home
        )
        self.home_button.grid(row=0, column=0, padx=(0, 10))
        if home_icon:
            self.home_button.image = home_icon
        
        # Botón Atrás
        back_icon = get_icon("arrow-left", 16)
        self.back_button = ttk.Button(
            nav_frame,
            text=" Atrás",
            image=back_icon,
            compound="left",
            command=self.go_back,
            state="disabled"
        )
        self.back_button.grid(row=0, column=1, padx=(0, 10))
        if back_icon:
            self.back_button.image = back_icon
        
        # Indicador de progreso
        self.progress_label = ttk.Label(
            nav_frame,
            text="Paso 1 de 5",
            font=("Arial", 10),
            foreground="gray"
        )
        self.progress_label.grid(row=0, column=2)
        
        # Botón Siguiente
        next_icon = get_icon("arrow-right", 16)
        self.next_button = ttk.Button(
            nav_frame,
            text="Siguiente ",
            image=next_icon,
            compound="right",
            command=self.go_next
        )
        self.next_button.grid(row=0, column=3, padx=(10, 0))
        if next_icon:
            self.next_button.image = next_icon
    
    def load_steps(self):
        """Cargar todos los steps del wizard"""
        try:
            # Importar steps
            from ui.creation.step1_files import Step1Files
            from ui.creation.step2_options import Step2Options
            from ui.creation.step3_preview import Step3Preview
            from ui.creation.step4_page_config import Step4PageConfig
            from ui.creation.step5_generate import Step5Generate
            
            # Crear instancias de steps
            step_classes = [
                Step1Files,
                Step2Options,
                Step3Preview,
                Step4PageConfig,
                Step5Generate
            ]
            
            for i, StepClass in enumerate(step_classes):
                # Crear frame para el step
                step_frame = ttk.Frame(self.steps_container, padding="10")
                step_frame.grid(row=0, column=0, sticky="nsew")
                step_frame.columnconfigure(0, weight=1)
                step_frame.rowconfigure(0, weight=1)
                
                # Crear instancia del step
                step_instance = StepClass(step_frame, self.shared_data, self)
                
                self.steps.append(step_instance)
                self.step_frames.append(step_frame)
                
                # Ocultar todos los frames inicialmente
                step_frame.grid_remove()
            
        except ImportError as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar los steps del wizard:\n{e}\n\n"
                "Asegúrese de que existan todos los archivos:\n"
                "- ui/creation/step1_files.py\n"
                "- ui/creation/step2_options.py\n"
                "- ui/creation/step3_preview.py\n"
                "- ui/creation/step4_page_config.py\n"
                "- ui/creation/step5_generate.py"
            )
            # Crear steps dummy para evitar errores
            self.create_dummy_steps()
    
    def create_dummy_steps(self):
        """Crear steps dummy si no se pueden cargar los reales"""
        for i in range(self.total_steps):
            step_frame = ttk.Frame(self.steps_container, padding="20")
            step_frame.grid(row=0, column=0, sticky="nsew")
            step_frame.columnconfigure(0, weight=1)
            step_frame.rowconfigure(0, weight=1)
            
            # Contenido dummy
            ttk.Label(
                step_frame,
                text=f"Step {i+1} - En construcción",
                font=("Arial", 16, "bold")
            ).grid(row=0, column=0, pady=20)
            
            ttk.Label(
                step_frame,
                text=f"Este step será implementado próximamente.\n\n"
                     f"Archivo requerido: ui/creation/step{i+1}_*.py",
                justify="center",
                foreground="gray"
            ).grid(row=1, column=0)
            
            self.steps.append(None)
            self.step_frames.append(step_frame)
            step_frame.grid_remove()
    
    def show_step(self, step_num):
        """Mostrar step específico"""
        if not (0 <= step_num < self.total_steps):
            return
        
        # Ocultar step actual
        if 0 <= self.current_step < len(self.step_frames):
            self.step_frames[self.current_step].grid_remove()
        
        # Mostrar nuevo step
        self.current_step = step_num
        self.step_frames[step_num].grid(row=0, column=0, sticky="nsew")
        
        # Actualizar UI
        self.update_navigation()
        self.update_sidebar()
        self.update_stats()
        
        # Llamar al método on_show del step si existe
        if self.steps[step_num] and hasattr(self.steps[step_num], 'on_show'):
            self.steps[step_num].on_show()
        
        # Programar auto-resize
        if self.auto_resizer:
            self.auto_resizer.schedule_resize()
    
    def update_navigation(self):
        """Actualizar botones de navegación"""
        # Botón Atrás
        self.back_button.config(state="normal" if self.current_step > 0 else "disabled")
        
        # Botón Siguiente/Finalizar
        if self.current_step == self.total_steps - 1:
            self.next_button.config(text="Finalizar", command=self.finish)
        else:
            self.next_button.config(text="Siguiente ", command=self.go_next)
        
        # Indicador de progreso
        self.progress_label.config(text=f"Paso {self.current_step + 1} de {self.total_steps}")
    
    def update_sidebar(self):
        """Actualizar sidebar con progreso"""
        for i, step_info in enumerate(self.step_labels):
            if i < self.current_step:
                # Step completado - icono check
                completed_icon = get_icon("circle-check", 12, "22c55e")  # Verde
                step_info['status'].config(image=completed_icon)
                if completed_icon:
                    step_info['status'].image = completed_icon
                step_info['name'].config(foreground="green")
            elif i == self.current_step:
                # Step actual - icono filled circle
                current_icon = get_icon("circle-play", 12, "3b82f6")  # Azul
                step_info['status'].config(image=current_icon)
                if current_icon:
                    step_info['status'].image = current_icon
                step_info['name'].config(foreground="blue", font=("Arial", 10, "bold"))
            else:
                # Step pendiente - icono circle
                pending_icon = get_icon("circle", 12, "999999")  # Gris
                step_info['status'].config(image=pending_icon)
                if pending_icon:
                    step_info['status'].image = pending_icon
                step_info['name'].config(foreground="gray", font=("Arial", 10, "normal"))
    
    def update_stats(self):
        """Actualizar estadísticas en sidebar"""
        # Limpiar frame de estadísticas
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Obtener estadísticas de shared_data
        num_files = len(self.shared_data.get('gift_files', []))
        num_questions = len(self.shared_data.get('questions', []))
        
        if num_files > 0 or num_questions > 0:
            ttk.Label(
                self.stats_frame,
                text="Estadísticas:",
                font=("Arial", 10, "bold")
            ).grid(row=0, column=0, sticky="w", pady=(0, 5))
            
            if num_files > 0:
                ttk.Label(
                    self.stats_frame,
                    text=f"Archivos: {num_files}",
                    font=("Arial", 9)
                ).grid(row=1, column=0, sticky="w", pady=1)
            
            if num_questions > 0:
                ttk.Label(
                    self.stats_frame,
                    text=f"Preguntas: {num_questions}",
                    font=("Arial", 9)
                ).grid(row=2, column=0, sticky="w", pady=1)
    
    def go_back(self):
        """Ir al step anterior"""
        if self.current_step > 0:
            # Llamar al método on_leave del step actual si existe
            if self.steps[self.current_step] and hasattr(self.steps[self.current_step], 'on_leave'):
                if not self.steps[self.current_step].on_leave():
                    return  # El step canceló la salida
            
            self.show_step(self.current_step - 1)
    
    def go_next(self):
        """Ir al siguiente step"""
        if self.current_step < self.total_steps - 1:
            # Validar step actual
            if self.steps[self.current_step] and hasattr(self.steps[self.current_step], 'validate'):
                if not self.steps[self.current_step].validate():
                    return  # Validación falló
            
            # Llamar al método on_leave del step actual si existe
            if self.steps[self.current_step] and hasattr(self.steps[self.current_step], 'on_leave'):
                if not self.steps[self.current_step].on_leave():
                    return  # El step canceló la salida
            
            self.show_step(self.current_step + 1)
    
    def go_home(self):
        """Volver a la página de inicio"""
        # Confirmar si hay trabajo sin guardar
        if self.shared_data['questions'] or self.shared_data['gift_files']:
            result = messagebox.askyesno(
                "Volver al inicio",
                "¿Está seguro de volver al inicio?\n\n"
                "Se perderá todo el progreso no guardado."
            )
            if not result:
                return
        
        # Volver al inicio si tenemos referencia al MainWindow
        if self.main_window and hasattr(self.main_window, 'show_home_page'):
            self.main_window.show_home_page()
        else:
            # Fallback: cerrar la aplicación
            self.root.quit()
    
    def finish(self):
        """Finalizar wizard"""
        # Validar step final
        if self.steps[self.current_step] and hasattr(self.steps[self.current_step], 'validate'):
            if not self.steps[self.current_step].validate():
                return
        
        # Llamar al método finish del step final si existe
        if self.steps[self.current_step] and hasattr(self.steps[self.current_step], 'finish'):
            if not self.steps[self.current_step].finish():
                return
        
        # Mostrar mensaje de éxito
        result = messagebox.showinfo(
            "Wizard Completado",
            "El wizard de creación se ha completado exitosamente.\n\n"
            "¿Desea volver al inicio?"
        )
        
        # Volver al inicio
        self.go_home()
    
    def update_shared_data(self, key, value):
        """Actualizar datos compartidos y estadísticas"""
        self.shared_data[key] = value
        self.update_stats()
    
    def get_shared_data(self, key, default=None):
        """Obtener datos compartidos"""
        return self.shared_data.get(key, default)

# Para testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Creation Wizard")
    
    wizard = CreationWizard(root)
    
    root.mainloop()