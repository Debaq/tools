# Image Processor Wizard

Una aplicación de escritorio con interfaz gráfica para procesar imágenes en lote, redimensionándolas mientras mantiene las proporciones y rellena con color personalizable.

## Características principales

- **Interfaz wizard intuitiva** de 7 pasos
- **Selección flexible** de origen (archivos individuales o carpeta completa)
- **Redimensionado inteligente** manteniendo proporciones
- **Múltiples opciones de tamaño** (cuadrado, por lados mayor/menor, por vertical/horizontal)
- **Color de relleno personalizable** para espacios vacíos
- **Múltiples formatos de exportación** (PNG, JPEG, BMP, TIFF)
- **Nomenclatura configurable** (mantener nombres originales o formato personalizado)
- **Preservación de estructura de carpetas** cuando se procesa una carpeta
- **Procesamiento con progreso visual** y opción de reinicio

## Requisitos del sistema

- Python 3.7 o superior
- Bibliotecas requeridas:
  ```bash
  pip install Pillow
  ```

## Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:
   ```bash
   pip install Pillow
   ```
3. Ejecuta la aplicación:
   ```bash
   python image_processor_wizard.py
   ```

## Funcionamiento del wizard

### Paso 1: Selección de origen
- **Imágenes individuales**: Selecciona una o varias imágenes específicas
- **Carpeta completa**: Procesa todas las imágenes de una carpeta y sus subcarpetas

**Formatos soportados**: PNG, JPG, JPEG, BMP, TIFF, GIF

### Paso 2: Configuración de redimensionado
Elige entre diferentes modos de redimensionado:

#### Formato cuadrado
- Especifica un tamaño único (ej: 512x512)
- Ideal para entrenar modelos de AI

#### Formato personalizado
**Opción A - Por lado mayor/menor:**
- Define el tamaño del lado más largo y más corto
- La imagen se ajusta automáticamente según su orientación

**Opción B - Por vertical/horizontal:**
- Define específicamente el ancho y alto deseados
- Control preciso sobre las dimensiones finales

### Paso 3: Color de relleno
- Selecciona el color para rellenar los espacios vacíos
- Preview visual del color seleccionado
- Por defecto: negro (RGB 0,0,0)

### Paso 4: Formato de exportación
Formatos disponibles:
- **PNG**: Sin pérdida, ideal para gráficos
- **JPEG**: Comprimido, ideal para fotografías
- **BMP**: Sin compresión
- **TIFF**: Alta calidad, sin pérdida

### Paso 5: Configuración de nombres
**Mantener nombres originales:**
- Conserva los nombres de archivo originales
- Cambia solo la extensión según el formato elegido
- Mantiene la estructura de carpetas

**Formato personalizado con numeración:**
- Define un nombre base (ej: "imagen")
- Se genera numeración automática: imagen_001, imagen_002, etc.
- Mantiene la estructura de carpetas con numeración global

### Paso 6: Carpeta de destino
- **Carpeta personalizada**: Elige dónde guardar (se crea subcarpeta "out")
- **Automática**: Se crea carpeta "out" junto al origen seleccionado

### Paso 7: Procesamiento
- Barra de progreso en tiempo real
- Información del archivo actual siendo procesado
- Al finalizar: opción de procesar más imágenes o salir

## Comportamiento del procesamiento

### Mantenimiento de proporciones
La aplicación siempre mantiene las proporciones originales de las imágenes:

1. **Calcula el factor de escala** basado en el tamaño objetivo
2. **Redimensiona la imagen** manteniendo la proporción
3. **Centra la imagen** en el lienzo del tamaño objetivo
4. **Rellena los espacios** vacíos con el color seleccionado

### Estructura de carpetas

**Para archivos individuales:**
```
out/
├── imagen1.png
├── imagen2.png
└── imagen3.png
```

**Para carpeta con subcarpetas:**
```
Origen/
├── fotos/
│   ├── vacation1.jpg
│   └── vacation2.jpg
└── screenshots/
    └── capture1.png

Resultado en out/
├── fotos/
│   ├── vacation1.png
│   └── vacation2.png
└── screenshots/
    └── capture1.png
```

## Casos de uso típicos

### Entrenamiento de modelos de AI
1. Selecciona carpeta con dataset
2. Configura formato cuadrado (512x512 o 1024x1024)
3. Elige PNG para máxima calidad
4. Usa formato personalizado: "train_001", "train_002", etc.

### Redimensionado para web
1. Selecciona imágenes específicas
2. Configura por lado mayor (ej: 1920px máximo)
3. Elige JPEG para menor tamaño de archivo
4. Mantiene nombres originales

### Normalización de galería
1. Selecciona carpeta con fotos de diferentes tamaños
2. Configura formato cuadrado uniforme
3. Elige color de relleno apropiado
4. Mantiene estructura de carpetas original

## Especificaciones técnicas

### Algoritmo de redimensionado
- **Método**: Lanczos resampling (alta calidad)
- **Preservación**: Mantiene proporciones exactas
- **Centrado**: Automático en el lienzo objetivo

### Manejo de formatos
- **Conversión automática** a RGB cuando es necesario
- **Soporte completo** para transparencias en PNG
- **Optimización** según el formato de salida elegido

### Rendimiento
- **Procesamiento en hilo separado** para evitar bloqueo de interfaz
- **Progreso en tiempo real** con información detallada
- **Manejo robusto de errores** con mensajes informativos

### Compatibilidad
- **Multiplataforma**: Windows, macOS, Linux
- **Interfaz nativa**: Tkinter (incluido con Python)
- **Sin dependencias externas** complejas

## Troubleshooting

**Error: "No module named 'PIL'"**
```bash
pip install Pillow
```

**Error: "No se encontraron imágenes"**
- Verifica que la carpeta contenga archivos de imagen válidos
- Revisa que las extensiones sean soportadas

**Imágenes procesadas se ven pixeladas**
- Evita aumentar mucho el tamaño original
- Usa PNG en lugar de JPEG para mayor calidad

**El procesamiento se detiene**
- Revisa que tengas permisos de escritura en la carpeta destino
- Verifica que haya suficiente espacio en disco

## Licencia

Este proyecto está disponible bajo licencia MIT. Puedes usarlo, modificarlo y distribuirlo libremente.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

## Contacto

Para reportar bugs o solicitar features, por favor abre un issue en este repositorio.