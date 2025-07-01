"""
Página 2 del Wizard: Configuración de Entrenamiento
"""

import tkinter as tk
from tkinter import ttk

class TrainingConfigPage:
    """Página de configuración de parámetros de entrenamiento"""
    
    def __init__(self, parent_frame, config, add_tooltip_func):
        self.parent_frame = parent_frame
        self.config = config
        self.add_tooltip = add_tooltip_func
        
    def create_page(self):
        """Crear la página de configuración de entrenamiento"""
        self.clear_frame()
        
        ttk.Label(self.parent_frame, text="Paso 2: Parámetros de Entrenamiento", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Hardware
        self.create_hardware_section()
        
        # Parámetros básicos
        self.create_basic_params_section()
        
        # Parámetros avanzados
        self.create_advanced_params_section()
        
    def create_hardware_section(self):
        """Crear sección de configuración de hardware"""
        gpu_frame = ttk.LabelFrame(self.parent_frame, text="Hardware", padding="5")
        gpu_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        gpu_check = ttk.Checkbutton(gpu_frame, text="Usar GPU (CUDA)", 
                                   variable=self.config.get('use_gpu'))
        gpu_check.grid(row=0, column=0, sticky=tk.W)
        self.add_tooltip(gpu_check, "Requiere CUDA instalado. GPU acelera significativamente el entrenamiento")
        
    def create_basic_params_section(self):
        """Crear sección de parámetros básicos"""
        basic_frame = ttk.LabelFrame(self.parent_frame, text="Parámetros Básicos", padding="5")
        basic_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Epochs
        ttk.Label(basic_frame, text="Epochs:").grid(row=0, column=0, sticky=tk.W, pady=2)
        epochs_spin = ttk.Spinbox(basic_frame, from_=1, to=1000, textvariable=self.config.get('epochs'), width=10)
        epochs_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.add_tooltip(epochs_spin, "Número de veces que se entrena con todo el dataset. Más epochs = más entrenamiento")
        
        # Batch size
        ttk.Label(basic_frame, text="Batch Size:").grid(row=0, column=2, sticky=tk.W, padx=(20,0), pady=2)
        batch_spin = ttk.Spinbox(basic_frame, from_=1, to=128, textvariable=self.config.get('batch_size'), width=10)
        batch_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.add_tooltip(batch_spin, "Número de imágenes procesadas simultáneamente. Mayor = más memoria GPU requerida")
        
        # Image size
        ttk.Label(basic_frame, text="Tamaño imagen:").grid(row=1, column=0, sticky=tk.W, pady=2)
        img_spin = ttk.Spinbox(basic_frame, from_=320, to=1280, increment=32, 
                              textvariable=self.config.get('img_size'), width=10)
        img_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        self.add_tooltip(img_spin, "Resolución de entrada. Mayor = más precisión pero más lento")
        
        # Learning rate
        ttk.Label(basic_frame, text="Learning Rate:").grid(row=1, column=2, sticky=tk.W, padx=(20,0), pady=2)
        lr_entry = ttk.Entry(basic_frame, textvariable=self.config.get('learning_rate'), width=10)
        lr_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        self.add_tooltip(lr_entry, "Velocidad de aprendizaje. 0.001 es un buen valor inicial")
        
    def create_advanced_params_section(self):
        """Crear sección de parámetros avanzados"""
        advanced_frame = ttk.LabelFrame(self.parent_frame, text="Parámetros Avanzados", padding="5")
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Patience
        ttk.Label(advanced_frame, text="Patience:").grid(row=0, column=0, sticky=tk.W, pady=2)
        patience_spin = ttk.Spinbox(advanced_frame, from_=5, to=100, 
                                   textvariable=self.config.get('patience'), width=10)
        patience_spin.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        self.add_tooltip(patience_spin, "Epochs sin mejora antes de parar automáticamente (early stopping)")
        
        # Save period
        ttk.Label(advanced_frame, text="Guardar cada:").grid(row=0, column=2, sticky=tk.W, padx=(20,0), pady=2)
        save_spin = ttk.Spinbox(advanced_frame, from_=1, to=50, 
                               textvariable=self.config.get('save_period'), width=10)
        save_spin.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.add_tooltip(save_spin, "Guardar checkpoint cada N epochs")
        
    def clear_frame(self):
        """Limpiar el frame padre"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
            
    def validate_page(self):
        """Validar datos de la página"""
        # Validaciones básicas
        try:
            epochs = self.config.get('epochs').get()
            batch_size = self.config.get('batch_size').get()
            img_size = self.config.get('img_size').get()
            lr = self.config.get('learning_rate').get()
            
            if epochs <= 0:
                return False, "Epochs debe ser mayor a 0"
            if batch_size <= 0:
                return False, "Batch size debe ser mayor a 0"
            if img_size < 320:
                return False, "Tamaño de imagen debe ser al menos 320"
            if lr <= 0:
                return False, "Learning rate debe ser mayor a 0"
                
        except:
            return False, "Verifica que todos los valores numéricos sean válidos"
            
        return True, ""
