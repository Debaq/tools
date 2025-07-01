"""
Configuración para YOLO Fine-tuning Tool
"""

import tkinter as tk

class YOLOConfig:
    """Configuración centralizada para la aplicación"""

    def __init__(self):
        self.config = {
            'yolo_version': tk.StringVar(value='yolov8'),
            'task_type': tk.StringVar(value='detect'),
            'model_source': tk.StringVar(value='pretrained'),
            'custom_url': tk.StringVar(),
            'local_model_path': tk.StringVar(),
            'pretrained_model': tk.StringVar(value='yolov8n.pt'),
            'use_gpu': tk.BooleanVar(value=True),
            'epochs': tk.IntVar(value=100),
            'batch_size': tk.IntVar(value=16),
            'img_size': tk.IntVar(value=640),
            'learning_rate': tk.DoubleVar(value=0.001),
            'dataset_path': tk.StringVar(),
            'yaml_path': tk.StringVar(),
            'output_path': tk.StringVar(),
            'patience': tk.IntVar(value=30),
            'save_period': tk.IntVar(value=10)
        }

    def get(self, key):
        """Obtener valor de configuración"""
        return self.config.get(key)

    def set(self, key, value):
        """Establecer valor de configuración"""
        if key in self.config:
            self.config[key].set(value)

# Versiones YOLO soportadas
YOLO_VERSIONS = ['yolov8', 'yolov9', 'yolov10', 'yolo11', 'yolo12']

# Tareas disponibles por versión
TASKS_BY_VERSION = {
    'yolov8': {
        'detect': 'Detección de objetos',
        'segment': 'Segmentación de instancias',
        'pose': 'Detección de poses/puntos clave',
        'classify': 'Clasificación de imágenes'
    },
    'yolov9': {
        'detect': 'Detección de objetos',
        'segment': 'Segmentación de instancias',
        'pose': 'Detección de poses/puntos clave',
        'classify': 'Clasificación de imágenes'
    },
    'yolov10': {
        'detect': 'Detección de objetos',
        'segment': 'Segmentación de instancias',
        'pose': 'Detección de poses/puntos clave',
        'classify': 'Clasificación de imágenes'
    },
    'yolo11': {
        'detect': 'Detección de objetos',
        'segment': 'Segmentación de instancias',
        'pose': 'Detección de poses/puntos clave',
        'classify': 'Clasificación de imágenes',
        'obb': 'Detección orientada (OBB)'
    },
    'yolo12': {
        'detect': 'Detección de objetos',
        'segment': 'Segmentación de instancias',
        'pose': 'Detección de poses/puntos clave',
        'classify': 'Clasificación de imágenes',
        'obb': 'Detección orientada (OBB)'
    }
}

# Sufijos de modelo por tarea
TASK_SUFFIXES = {
    'detect': '',           # yolov8n.pt
    'segment': '-seg',      # yolov8n-seg.pt
    'pose': '-pose',        # yolov8n-pose.pt
    'classify': '-cls',     # yolov8n-cls.pt
    'obb': '-obb'          # yolo11n-obb.pt
}

# Modelos base por versión
MODEL_VARIANTS = {
    'yolov8': {
        'models': ['yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x'],
        'sizes': ['n (nano)', 's (small)', 'm (medium)', 'l (large)', 'x (extra large)']
    },
    'yolov9': {
        'detect': {
            'models': ['yolov9t', 'yolov9s', 'yolov9m', 'yolov9c', 'yolov9e'],
            'sizes': ['t (tiny)', 's (small)', 'm (medium)', 'c (compact)', 'e (extended)']
        },
        'other': {
            'models': ['yolov9n', 'yolov9s', 'yolov9m'],
            'sizes': ['n (nano)', 's (small)', 'm (medium)']
        }
    },
    'yolov10': {
        'models': ['yolov10n', 'yolov10s', 'yolov10m', 'yolov10l', 'yolov10x'],
        'sizes': ['n (nano)', 's (small)', 'm (medium)', 'l (large)', 'x (extra large)']
    },
    'yolo11': {
        'models': ['yolo11n', 'yolo11s', 'yolo11m', 'yolo11l', 'yolo11x'],
        'sizes': ['n (nano)', 's (small)', 'm (medium)', 'l (large)', 'x (extra large)']
    },
    'yolo12': {
        'models': ['yolo12n', 'yolo12s', 'yolo12m', 'yolo12l', 'yolo12x'],
        'sizes': ['n (nano)', 's (small)', 'm (medium)', 'l (large)', 'x (extra large)']
    }
}

# Información por tipo de tarea (sin caracteres especiales)
TASK_INFO = {
    'detect': """
DETECCION DE OBJETOS:
Estructura del dataset:
   dataset/
   +-- train/images/     # Imagenes de entrenamiento
   +-- train/labels/     # Archivos .txt con anotaciones
   +-- val/images/       # Imagenes de validacion
   +-- val/labels/       # Anotaciones de validacion

Formato de anotaciones (.txt):
   class_id center_x center_y width height
   Ejemplo: 0 0.5 0.5 0.3 0.4

YAML: Define clases y rutas del dataset
    """,

    'segment': """
SEGMENTACION DE INSTANCIAS:
Estructura del dataset:
   dataset/
   +-- train/images/     # Imagenes de entrenamiento
   +-- train/labels/     # Archivos .txt con poligonos
   +-- val/images/       # Imagenes de validacion
   +-- val/labels/       # Poligonos de validacion

Formato de anotaciones (.txt):
   class_id x1 y1 x2 y2 x3 y3 ... xn yn
   Coordenadas normalizadas (0-1) del poligono

Conversion COCO disponible para facilitar la preparacion

YAML: Define clases y rutas del dataset
    """,

    'pose': """
DETECCION DE POSES/PUNTOS CLAVE:
Estructura del dataset:
   dataset/
   +-- train/images/     # Imagenes de entrenamiento
   +-- train/labels/     # Archivos .txt con keypoints
   +-- val/images/       # Imagenes de validacion
   +-- val/labels/       # Keypoints de validacion

Formato de anotaciones (.txt):
   class_id center_x center_y width height kpt1_x kpt1_y kpt1_v ... kptn_x kptn_y kptn_v
   kpt_v: 0=no visible, 1=visible, 2=occluded

YAML: Define clases, rutas y configuracion de keypoints
    """,

    'classify': """
CLASIFICACION DE IMAGENES:
Estructura del dataset:
   dataset/
   +-- train/
   |   +-- clase1/       # Imagenes de la clase 1
   |   +-- clase2/       # Imagenes de la clase 2
   |   +-- claseN/       # Imagenes de la clase N
   +-- val/
       +-- clase1/       # Validacion clase 1
       +-- clase2/       # Validacion clase 2
       +-- claseN/       # Validacion clase N

YAML: Define clases y rutas (generacion automatica disponible)
    """,

    'obb': """
DETECCION ORIENTADA (OBB):
Estructura del dataset:
   dataset/
   +-- train/images/     # Imagenes de entrenamiento
   +-- train/labels/     # Archivos .txt con cajas rotadas
   +-- val/images/       # Imagenes de validacion
   +-- val/labels/       # Cajas rotadas de validacion

Formato de anotaciones (.txt):
   class_id x1 y1 x2 y2 x3 y3 x4 y4
   Coordenadas de los 4 vertices de la caja rotada

YAML: Define clases y rutas del dataset
    """
}
