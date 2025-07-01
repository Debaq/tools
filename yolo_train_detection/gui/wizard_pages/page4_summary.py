"""
Página 4 del Wizard: Resumen y Confirmación
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import os

class SummaryPage:
    """Página de resumen y confirmación"""

    def __init__(self, parent_frame, config, add_tooltip_func):
        self.parent_frame = parent_frame
        self.config = config
        self.add_tooltip = add_tooltip_func

    def create_page(self):
        """Crear la página de resumen"""
        self.clear_frame()

        ttk.Label(self.parent_frame, text="Paso 4: Resumen de Configuración",
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        # Frame con scroll para el resumen
        summary_frame = ttk.Frame(self.parent_frame)
        summary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.summary_text = scrolledtext.ScrolledText(summary_frame, height=25, width=80)
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Configurar expansión
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.rowconfigure(1, weight=1)

        # Generar resumen
        self.generate_summary()

    def generate_summary(self):
        """Generar resumen de configuración"""
        summary = f"""
CONFIGURACION DE ENTRENAMIENTO YOLO
{'-'*50}

MODELO:
- Version YOLO: {self.config.get('yolo_version').get()}
- Tipo de tarea: {self.config.get('task_type').get()}
- Fuente del modelo: {self.get_model_source_description()}

PARAMETROS DE ENTRENAMIENTO:
- Usar GPU: {'Si' if self.config.get('use_gpu').get() else 'No'}
- Epochs: {self.config.get('epochs').get()}
- Batch Size: {self.config.get('batch_size').get()}
- Tamaño de imagen: {self.config.get('img_size').get()}
- Learning Rate: {self.config.get('learning_rate').get()}
- Patience: {self.config.get('patience').get()}
- Guardar cada: {self.config.get('save_period').get()} epochs

ARCHIVOS:
- Dataset: {self.config.get('dataset_path').get() or 'No seleccionado'}
- YAML: {self.config.get('yaml_path').get() or 'No seleccionado'}
- Salida: {self.config.get('output_path').get() or 'No seleccionado'}

COMANDO DE ENTRENAMIENTO:
{self.generate_training_command()}

NOTAS:
- El entrenamiento se ejecutara en {'GPU' if self.config.get('use_gpu').get() else 'CPU'}
- Los logs se guardaran automaticamente
- Se generaran graficas de progreso
- El modelo se guardara en la carpeta de salida

Esta todo correcto? Haz clic en "Iniciar Entrenamiento" para comenzar.
        """

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)

    def get_model_source_description(self):
        """Obtener descripción de la fuente del modelo"""
        source = self.config.get('model_source').get()

        if source == 'pretrained':
            return f"Pre-entrenado oficial ({self.config.get('pretrained_model').get()})"
        elif source == 'local':
            path = self.config.get('local_model_path').get()
            return f"Archivo local ({os.path.basename(path) if path else 'No seleccionado'})"
        elif source == 'url':
            return f"URL personalizada ({self.config.get('custom_url').get()})"
        else:
            return "Desde cero (sin pesos pre-entrenados)"

    def generate_training_command(self):
        """Generar comando de entrenamiento que se ejecutará"""
        yolo_version = self.config.get('yolo_version').get()
        task_type = self.config.get('task_type').get()

        cmd_parts = [
            "from ultralytics import YOLO",
            "",
            f"# Cargar modelo",
            f"model = YOLO('{self.config.get('pretrained_model').get()}')",
            "",
            f"# Entrenar",
            f"results = model.train(",
            f"    data='{self.config.get('yaml_path').get()}',",
            f"    epochs={self.config.get('epochs').get()},",
            f"    batch={self.config.get('batch_size').get()},",
            f"    imgsz={self.config.get('img_size').get()},",
            f"    lr0={self.config.get('learning_rate').get()},",
            f"    patience={self.config.get('patience').get()},",
            f"    save_period={self.config.get('save_period').get()},",
            f"    project='{self.config.get('output_path').get()}',",
            f"    device='{'cuda' if self.config.get('use_gpu').get() else 'cpu'}',",
            f"    plots=True",
            f")"
        ]

        return "\n".join(cmd_parts)

    def clear_frame(self):
        """Limpiar el frame padre"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

    def validate_page(self):
        """Validar datos finales"""
        # Verificar que todos los archivos existen
        dataset_path = self.config.get('dataset_path').get()
        yaml_path = self.config.get('yaml_path').get()
        output_path = self.config.get('output_path').get()

        if not os.path.exists(dataset_path):
            return False, f"La carpeta del dataset no existe: {dataset_path}"

        if not os.path.exists(yaml_path):
            return False, f"El archivo YAML no existe: {yaml_path}"

        if not os.path.exists(output_path):
            return False, f"La carpeta de salida no existe: {output_path}"

        # Verificar modelo local si está seleccionado
        if self.config.get('model_source').get() == 'local':
            model_path = self.config.get('local_model_path').get()
            if not os.path.exists(model_path):
                return False, f"El archivo del modelo no existe: {model_path}"

        return True, ""
