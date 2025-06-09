# YOLO Fine-tuning Tool

Una herramienta gráfica completa para realizar fine-tuning de modelos YOLO con interfaz wizard intuitiva, monitoreo en tiempo real y análisis de resultados.

## 🚀 Características Principales

### 📋 Wizard de Configuración (4 Pasos)
- **Paso 1**: Selección de versión YOLO y modelo base
- **Paso 2**: Configuración de parámetros de entrenamiento
- **Paso 3**: Selección de archivos y carpetas
- **Paso 4**: Resumen y confirmación

### 🎯 Versiones YOLO Soportadas
- YOLOv8
- YOLOv9
- YOLOv10
- YOLOv11
- YOLOv12

### 🔧 Opciones de Modelo Base
- **Modelos Pre-entrenados**: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
- **Modelo Local**: Cargar archivo .pt desde PC
- **URL Personalizada**: Descargar modelo desde URL
- **Desde Cero**: Entrenar sin pesos pre-entrenados

### ⚙️ Parámetros Configurables
- **Hardware**: Uso de GPU (CUDA)
- **Básicos**: Epochs, Batch Size, Tamaño de Imagen, Learning Rate
- **Avanzados**: Patience, Período de Guardado

### 🖥️ Entrenamiento en Tiempo Real
- **Terminal integrado** con log completo
- **Controles**: Pausar/Reanudar/Detener entrenamiento
- **Barra de progreso** con epochs actuales
- **Guardado automático** de logs con timestamp

### 📊 Análisis de Resultados
- **Gráficas automatizadas**: Loss, Precision/Recall, mAP, Learning Rate
- **Métricas detalladas**: Precisión, Recall, F1-Score, tiempo de inferencia
- **Recomendaciones inteligentes** basadas en resultados
- **Exportación completa** de resultados

## 🛠️ Instalación

### Requisitos del Sistema
- Python 3.8+
- CUDA (opcional, para GPU)

### Dependencias
```bash
pip install ultralytics matplotlib tkinter numpy
```

### Instalación Opcional (para mejor rendimiento)
```bash
# Para GPU (NVIDIA)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Para datasets grandes
pip install pandas pillow
```

## 🚀 Uso Rápido

### 1. Ejecutar la Herramienta
```bash
python yolo_finetuning_tool.py
```

### 2. Configuración Paso a Paso

#### **Paso 1: Modelo**
1. Selecciona la versión de YOLO
2. Elige el tipo de modelo base:
   - **Pre-entrenado**: Recomendado para la mayoría de casos
   - **Local**: Si tienes un modelo previamente entrenado
   - **URL**: Para modelos personalizados online
   - **Desde cero**: Solo para casos específicos

#### **Paso 2: Parámetros**
- **GPU**: Habilitar si tienes CUDA instalado
- **Epochs**: 100 es un buen punto de partida
- **Batch Size**: Ajustar según memoria GPU disponible
- **Learning Rate**: 0.001 es valor recomendado inicial

#### **Paso 3: Archivos**
- **Dataset**: Carpeta con estructura YOLO (train/val/test)
- **YAML**: Archivo de configuración del dataset
- **Salida**: Donde se guardarán los resultados

#### **Paso 4: Confirmar**
- Revisar configuración completa
- Hacer clic en "Iniciar Entrenamiento"

### 3. Monitoreo del Entrenamiento
- Observar progreso en terminal integrado
- Usar controles para pausar/reanudar si es necesario
- El log se guarda automáticamente

### 4. Análisis de Resultados
- Revisar gráficas de rendimiento
- Analizar métricas finales
- Seguir recomendaciones para mejoras
- Exportar resultados si es necesario

## 📁 Estructura de Archivos

### Dataset YOLO
```
dataset/
├── train/
│   ├── images/
│   └── labels/
├── val/
│   ├── images/
│   └── labels/
└── test/ (opcional)
    ├── images/
    └── labels/
```

### Archivo YAML
```yaml
# dataset.yaml
path: /path/to/dataset
train: train/images
val: val/images
test: test/images  # opcional

names:
  0: clase1
  1: clase2
  2: clase3
```

### Resultados Generados
```
output/
├── yolo_training/
│   ├── weights/
│   │   ├── best.pt
│   │   └── last.pt
│   ├── results.csv
│   └── plots/
└── training_logs/
    └── yolo_training_YYYYMMDD_HHMMSS.log
```

## 🎯 Consejos y Mejores Prácticas

### Selección de Modelo
- **YOLOv8n**: Más rápido, menor precisión, ideal para tiempo real
- **YOLOv8s**: Balance entre velocidad y precisión
- **YOLOv8m**: Buena precisión, velocidad moderada
- **YOLOv8l/x**: Máxima precisión, más lento

### Configuración de Parámetros
- **Batch Size**: Empezar con 16, ajustar según memoria GPU
- **Epochs**: 100-300 para datasets pequeños, 50-100 para grandes
- **Learning Rate**: 0.001 inicial, reducir si no converge
- **Patience**: 30-50 para evitar overfitting

### Preparación de Dataset
- **Imágenes**: Mínimo 100 por clase, idealmente 1000+
- **Anotaciones**: Usar herramientas como Roboflow o LabelImg
- **Validación**: 20% del dataset para validación
- **Calidad**: Imágenes variadas y representativas

## 🔧 Funcionalidades Avanzadas

### Transfer Learning
- Partir de modelos pre-entrenados acelera convergencia
- Usar modelos propios previamente entrenados
- Combinar diferentes arquitecturas según necesidad

### Control de Entrenamiento
- **Pausar**: Útil para ajustar parámetros del sistema
- **Reanudar**: Continuar desde el punto de pausa
- **Detener**: Finalizar entrenamiento manualmente

### Análisis de Rendimiento
- **mAP@0.5**: Precisión general de detección
- **mAP@0.5:0.95**: Precisión de localización
- **Precision/Recall**: Balance entre detecciones correctas y completas

## 🐛 Solución de Problemas

### Errores Comunes

#### Error de Memoria GPU
```
OutOfMemoryError: CUDA out of memory
```
**Solución**: Reducir batch size o tamaño de imagen

#### Ultralytics No Instalado
```
ImportError: No module named 'ultralytics'
```
**Solución**: `pip install ultralytics`

#### Dataset No Encontrado
```
FileNotFoundError: Dataset path not found
```
**Solución**: Verificar rutas en archivo YAML y estructura de carpetas

#### CUDA No Disponible
```
CUDA not available
```
**Solución**: Instalar CUDA o usar CPU (deshabilitar GPU en configuración)

### Optimización de Rendimiento

#### Para Datasets Grandes
- Usar GPU con mínimo 8GB VRAM
- Incrementar batch size gradualmente
- Considerar mixed precision training

#### Para Entrenamiento Rápido
- Usar modelos nano (n) o small (s)
- Reducir resolución de imagen
- Implementar early stopping con patience bajo

## 📊 Interpretación de Métricas

### Métricas Principales
- **Precision**: % de detecciones correctas
- **Recall**: % de objetos detectados del total
- **mAP@0.5**: Precisión promedio con IoU > 0.5
- **F1-Score**: Balance entre precision y recall

### Curvas de Entrenamiento
- **Loss decreciente**: Entrenamiento progresando correctamente
- **Validation loss estable**: Modelo no está overfitting
- **mAP creciente**: Mejora en precisión de detección

## 🤝 Contribución

Para contribuir al proyecto:
1. Fork el repositorio
2. Crear rama para nueva funcionalidad
3. Implementar cambios con tests
4. Enviar pull request con descripción detallada

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo LICENSE para detalles.

## 🆘 Soporte

Para soporte técnico:
- Crear issue en GitHub con detalles del problema
- Incluir logs de entrenamiento
- Especificar configuración del sistema
- Proporcionar ejemplo reproducible

## 🔗 Enlaces Útiles

- [Documentación Ultralytics](https://docs.ultralytics.com/)
- [YOLO Papers](https://github.com/ultralytics/ultralytics#documentation)
- [Dataset Preparation Guide](https://docs.ultralytics.com/datasets/)
- [CUDA Installation](https://developer.nvidia.com/cuda-downloads)

---

**Desarrollado con ❤️ para la comunidad de Computer Vision**