"""
Utilidades para manejo de modelos YOLO
"""

from config.yolo_config import TASKS_BY_VERSION, TASK_SUFFIXES, MODEL_VARIANTS

def get_available_tasks(yolo_version):
    """Obtener tareas disponibles para una versión de YOLO"""
    return TASKS_BY_VERSION.get(yolo_version, {'detect': 'Detección de objetos'})

def get_model_variants(yolo_version, task_type):
    """Obtener variantes de modelo disponibles"""
    variants = MODEL_VARIANTS.get(yolo_version, {})
    
    # Manejar caso especial de YOLOv9
    if yolo_version == 'yolov9':
        if task_type in ['detect', 'segment']:
            return variants.get('detect', variants.get('models', []), variants.get('sizes', []))
        else:
            return variants.get('other', variants.get('models', []), variants.get('sizes', []))
    
    # Otros casos
    if isinstance(variants, dict) and 'models' in variants:
        return variants['models'], variants['sizes']
    
    return [], []

def build_model_filename(base_model, task_type):
    """Construir nombre de archivo del modelo"""
    suffix = TASK_SUFFIXES.get(task_type, '')
    return f"{base_model}{suffix}.pt"

def get_model_mapping(yolo_version, task_type):
    """Obtener mapeo completo de tamaños a archivos de modelo"""
    base_models, sizes = get_model_variants(yolo_version, task_type)
    
    if not base_models or not sizes:
        return {}, []
    
    # Construir nombres de archivos completos
    model_files = [build_model_filename(base_model, task_type) for base_model in base_models]
    
    # Crear mapeo
    mapping = dict(zip(sizes, model_files))
    
    return mapping, sizes

def get_task_tooltip(task_type):
    """Obtener tooltip informativo para una tarea"""
    task_info = {
        'detect': 'Detección de objetos - cajas delimitadoras',
        'segment': 'Segmentación - máscaras pixelwise', 
        'pose': 'Puntos clave - esqueletos/poses humanas',
        'classify': 'Clasificación - categorías de imagen',
        'obb': 'Detección orientada - cajas rotadas'
    }
    
    base_info = task_info.get(task_type, 'Modelo YOLO')
    return f"{base_info}. n=nano (más rápido), x=extra large (más preciso)"

def validate_model_availability(yolo_version, task_type, model_size):
    """Validar si una combinación de modelo está disponible"""
    mapping, available_sizes = get_model_mapping(yolo_version, task_type)
    return model_size in available_sizes
