"""
Página 1 del Wizard: Selección de Modelo
"""

import tkinter as tk
from tkinter import ttk, filedialog
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.yolo_config import YOLO_VERSIONS
try:
    from utils.model_utils import get_available_tasks, get_model_mapping, get_task_tooltip
except ImportError:
    # Fallback si no se puede importar
    def get_available_tasks(version):
        return {'detect': 'Detección de objetos', 'segment': 'Segmentación'}

    def get_model_mapping(version, task):
        return {'n (nano)': f'{version}n.pt'}, ['n (nano)']

    def get_task_tooltip(task):
        return "Modelo YOLO"

class ModelSelectionPage:
    """Página de selección de modelo y tarea"""

    def __init__(self, parent_frame, config, add_tooltip_func):
        self.parent_frame = parent_frame
        self.config = config
        self.add_tooltip = add_tooltip_func

        # Referencias a widgets que necesitamos actualizar
        self.task_combo = None
        self.pretrained_combo = None
        self.pretrained_frame = None
        self.local_frame = None
        self.url_frame = None
        self.browse_model_btn = None
        self.url_entry = None

        # Mapeos internos
        self.task_mapping = {}
        self.model_mapping = {}

    def create_page(self):
        """Crear la página de selección de modelo"""
        self.clear_frame()

        ttk.Label(self.parent_frame, text="Paso 1: Configuración de Modelo",
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        # Selección de versión YOLO
        ttk.Label(self.parent_frame, text="Versión de YOLO:").grid(row=1, column=0, sticky=tk.W, pady=5)
        yolo_combo = ttk.Combobox(self.parent_frame, textvariable=self.config.get('yolo_version'),
                                 values=YOLO_VERSIONS, state='readonly', width=15)
        yolo_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        yolo_combo.bind('<<ComboboxSelected>>', self.on_yolo_version_change)
        self.add_tooltip(yolo_combo, "Selecciona la versión de YOLO a utilizar")

        # Selección de tipo de tarea
        ttk.Label(self.parent_frame, text="Tipo de tarea:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.task_combo = ttk.Combobox(self.parent_frame, textvariable=self.config.get('task_type'),
                                      state='readonly', width=30)
        self.task_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.task_combo.bind('<<ComboboxSelected>>', self.on_task_type_change)
        self.add_tooltip(self.task_combo, "Tipo de tarea a realizar con YOLO")

        # Separador
        ttk.Separator(self.parent_frame, orient='horizontal').grid(row=3, column=0, columnspan=2,
                                                                   sticky=(tk.W, tk.E), pady=15)

        # Fuente del modelo
        ttk.Label(self.parent_frame, text="Fuente del modelo base:",
                 font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)

        self.create_model_source_options()

        # Actualizar tareas disponibles y configurar inicial
        self.update_available_tasks()
        self.on_model_source_change()

    def create_model_source_options(self):
        """Crear opciones de fuente del modelo"""
        # Opción 1: Modelo pre-entrenado
        ttk.Radiobutton(self.parent_frame, text="Modelo pre-entrenado oficial",
                       variable=self.config.get('model_source'), value='pretrained',
                       command=self.on_model_source_change).grid(row=5, column=0, columnspan=2, sticky=tk.W)

        self.pretrained_frame = ttk.Frame(self.parent_frame)
        self.pretrained_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=20)

        ttk.Label(self.pretrained_frame, text="Tamaño:").grid(row=0, column=0, sticky=tk.W)
        self.pretrained_combo = ttk.Combobox(self.pretrained_frame, textvariable=self.config.get('pretrained_model'),
                                           state='readonly', width=20)
        self.pretrained_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.pretrained_combo.bind('<<ComboboxSelected>>', self.on_model_size_change)

        # Opción 2: Modelo local
        ttk.Radiobutton(self.parent_frame, text="Cargar modelo desde PC (.pt)",
                       variable=self.config.get('model_source'), value='local',
                       command=self.on_model_source_change).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(10,0))

        self.local_frame = ttk.Frame(self.parent_frame)
        self.local_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=20)

        ttk.Entry(self.local_frame, textvariable=self.config.get('local_model_path'),
                 width=40, state='disabled').grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.browse_model_btn = ttk.Button(self.local_frame, text="Examinar",
                                          command=self.browse_model, state='disabled')
        self.browse_model_btn.grid(row=0, column=1, padx=5)

        # Opción 3: URL personalizada
        ttk.Radiobutton(self.parent_frame, text="Descargar desde URL personalizada",
                       variable=self.config.get('model_source'), value='url',
                       command=self.on_model_source_change).grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(10,0))

        self.url_frame = ttk.Frame(self.parent_frame)
        self.url_frame.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=20)

        self.url_entry = ttk.Entry(self.url_frame, textvariable=self.config.get('custom_url'),
                                  width=50, state='disabled')
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.add_tooltip(self.url_entry, "URL directa al archivo .pt del modelo")

        # Opción 4: Desde cero
        ttk.Radiobutton(self.parent_frame, text="Entrenar desde cero (sin pesos pre-entrenados)",
                       variable=self.config.get('model_source'), value='scratch',
                       command=self.on_model_source_change).grid(row=11, column=0, columnspan=2, sticky=tk.W, pady=(10,0))

    def clear_frame(self):
        """Limpiar el frame padre"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

    def on_yolo_version_change(self, event=None):
        """Manejar cambio de versión YOLO"""
        self.update_available_tasks()
        self.update_pretrained_models()

    def update_available_tasks(self):
        """Actualizar tareas disponibles según versión YOLO"""
        yolo_version = self.config.get('yolo_version').get()
        tasks = get_available_tasks(yolo_version)

        if self.task_combo:
            task_values = [f"{key} - {value}" for key, value in tasks.items()]
            self.task_combo['values'] = task_values

            # Mantener selección actual si es válida
            current_task = self.config.get('task_type').get()
            if current_task in tasks:
                current_display = f"{current_task} - {tasks[current_task]}"
                self.task_combo.set(current_display)
            else:
                self.task_combo.set(task_values[0])
                self.config.get('task_type').set('detect')

        self.task_mapping = tasks

    def on_task_type_change(self, event=None):
        """Manejar cambio de tipo de tarea"""
        selected_display = self.task_combo.get()
        if ' - ' in selected_display:
            task_key = selected_display.split(' - ')[0]
            self.config.get('task_type').set(task_key)

        self.update_pretrained_models()

    def update_pretrained_models(self):
        """Actualizar modelos pre-entrenados disponibles"""
        yolo_version = self.config.get('yolo_version').get()
        task_type = self.config.get('task_type').get()

        mapping, sizes = get_model_mapping(yolo_version, task_type)

        if self.pretrained_combo:
            self.pretrained_combo['values'] = sizes
            if sizes:
                self.pretrained_combo.set(sizes[0])
                if mapping and sizes[0] in mapping:
                    self.config.get('pretrained_model').set(mapping[sizes[0]])

            # Actualizar tooltip
            tooltip_text = get_task_tooltip(task_type)
            self.add_tooltip(self.pretrained_combo, tooltip_text)

        self.model_mapping = mapping

    def on_model_size_change(self, event=None):
        """Manejar cambio de tamaño de modelo"""
        if hasattr(self, 'model_mapping'):
            selected_size = self.pretrained_combo.get()
            if selected_size in self.model_mapping:
                model_file = self.model_mapping[selected_size]
                self.config.get('pretrained_model').set(model_file)

    def on_model_source_change(self):
        """Manejar cambio de fuente del modelo"""
        source = self.config.get('model_source').get()

        if not hasattr(self, 'pretrained_frame'):
            return

        # Mostrar/ocultar frames según selección
        if source == 'pretrained':
            self.pretrained_frame.grid()
        else:
            self.pretrained_frame.grid_remove()

        if source == 'local':
            self.local_frame.grid()
            self.browse_model_btn.config(state='normal')
        else:
            self.local_frame.grid_remove()
            if hasattr(self, 'browse_model_btn'):
                self.browse_model_btn.config(state='disabled')

        if source == 'url':
            self.url_frame.grid()
            self.url_entry.config(state='normal')
        else:
            self.url_frame.grid_remove()
            if hasattr(self, 'url_entry'):
                self.url_entry.config(state='disabled')

    def browse_model(self):
        """Examinar archivo de modelo"""
        filename = filedialog.askopenfilename(
            title="Seleccionar modelo",
            filetypes=[("PyTorch models", "*.pt"), ("All files", "*.*")]
        )
        if filename:
            self.config.get('local_model_path').set(filename)

    def validate_page(self):
        """Validar datos de la página"""
        source = self.config.get('model_source').get()

        if source == 'local' and not self.config.get('local_model_path').get():
            return False, "Selecciona un archivo de modelo local"
        elif source == 'url' and not self.config.get('custom_url').get():
            return False, "Ingresa una URL válida"

        return True, ""
