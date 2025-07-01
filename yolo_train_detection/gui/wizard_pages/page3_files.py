"""
Página 3 del Wizard: Selección de Archivos
"""

import tkinter as tk
from tkinter import ttk, filedialog
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from config.yolo_config import TASK_INFO
except ImportError:
    # Fallback si no se puede importar
    TASK_INFO = {
        'detect': 'Información de detección no disponible',
        'segment': 'Información de segmentación no disponible'
    }

class FilesConfigPage:
    """Página de configuración de archivos y carpetas"""

    def __init__(self, parent_frame, config, add_tooltip_func):
        self.parent_frame = parent_frame
        self.config = config
        self.add_tooltip = add_tooltip_func

    def create_page(self):
        """Crear la página de selección de archivos"""
        self.clear_frame()

        ttk.Label(self.parent_frame, text="Paso 3: Archivos y Carpetas",
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)

        # Selección de archivos
        self.create_file_selection()

        # Información específica de la tarea
        self.create_task_info()

        # Herramientas disponibles
        self.create_tools_section()

    def create_file_selection(self):
        """Crear sección de selección de archivos"""
        files_frame = ttk.LabelFrame(self.parent_frame, text="Archivos Requeridos", padding="10")
        files_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Dataset
        ttk.Label(files_frame, text="Carpeta del Dataset:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(files_frame, textvariable=self.config.get('dataset_path'),
                 width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(files_frame, text="Examinar",
                  command=self.browse_dataset).grid(row=0, column=2, pady=5)

        # YAML
        ttk.Label(files_frame, text="Archivo YAML:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(files_frame, textvariable=self.config.get('yaml_path'),
                 width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(files_frame, text="Examinar",
                  command=self.browse_yaml).grid(row=1, column=2, pady=5)

        # Output
        ttk.Label(files_frame, text="Carpeta de salida:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(files_frame, textvariable=self.config.get('output_path'),
                 width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(files_frame, text="Examinar",
                  command=self.browse_output).grid(row=2, column=2, pady=5)

        # Configurar expansión de columnas
        files_frame.columnconfigure(1, weight=1)

    def create_task_info(self):
        """Crear sección de información específica de la tarea"""
        info_frame = ttk.LabelFrame(self.parent_frame, text="Información de la Tarea", padding="10")
        info_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Frame con scroll para información
        canvas = tk.Canvas(info_frame, height=200)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Contenido de información
        self.info_label = ttk.Label(scrollable_frame, justify=tk.LEFT, wraplength=600)
        self.info_label.pack(fill=tk.BOTH, expand=True)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Actualizar información
        self.update_task_info()

    def create_tools_section(self):
        """Crear sección de herramientas"""
        tools_frame = ttk.LabelFrame(self.parent_frame, text="Herramientas", padding="5")
        tools_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # Frame para botones de herramientas
        self.tools_button_frame = ttk.Frame(tools_frame)
        self.tools_button_frame.pack(fill=tk.X)

        # Actualizar herramientas disponibles
        self.update_available_tools()

    def update_task_info(self):
        """Actualizar información específica de la tarea"""
        task_type = self.config.get('task_type').get()
        info_text = TASK_INFO.get(task_type, "Selecciona un tipo de tarea para ver información específica")

        if hasattr(self, 'info_label'):
            self.info_label.config(text=info_text)

    def update_available_tools(self):
        """Actualizar herramientas disponibles según la tarea"""
        # Limpiar botones anteriores
        for widget in self.tools_button_frame.winfo_children():
            widget.destroy()

        task_type = self.config.get('task_type').get()

        # Herramientas comunes
        ttk.Button(self.tools_button_frame, text="Validar Dataset",
                  command=self.validate_dataset).pack(side=tk.LEFT, padx=5)

        # Herramientas específicas por tarea
        if task_type == 'segment':
            ttk.Button(self.tools_button_frame, text="Convertir COCO->YOLO",
                      command=self.convert_coco_to_yolo).pack(side=tk.LEFT, padx=5)

        elif task_type == 'classify':
            ttk.Button(self.tools_button_frame, text="Generar YAML",
                      command=self.generate_classification_yaml).pack(side=tk.LEFT, padx=5)

    def clear_frame(self):
        """Limpiar el frame padre"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

    def browse_dataset(self):
        """Examinar carpeta de dataset"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta del dataset")
        if folder:
            self.config.get('dataset_path').set(folder)

    def browse_yaml(self):
        """Examinar archivo YAML"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo YAML",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if filename:
            self.config.get('yaml_path').set(filename)

    def browse_output(self):
        """Examinar carpeta de salida"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder:
            self.config.get('output_path').set(folder)

    def validate_dataset(self):
        """Validar estructura del dataset según la tarea"""
        dataset_path = self.config.get('dataset_path').get()

        if not dataset_path:
            from tkinter import messagebox
            messagebox.showwarning("Advertencia", "Selecciona primero la carpeta del dataset")
            return

        # Crear ventana de validación
        validation_window = tk.Toplevel(self.parent_frame.master)
        validation_window.title("Validacion de Dataset")
        validation_window.geometry("800x600")
        validation_window.transient(self.parent_frame.master)
        validation_window.grab_set()

        # Frame principal
        main_frame = ttk.Frame(validation_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(main_frame, text="Validacion de Dataset",
                 font=('Arial', 14, 'bold')).pack(pady=10)

        # Frame de información básica
        info_frame = ttk.LabelFrame(main_frame, text="Informacion del Dataset", padding="10")
        info_frame.pack(fill=tk.X, pady=5)

        ttk.Label(info_frame, text=f"Ruta: {dataset_path}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Tarea: {self.config.get('task_type').get()}").pack(anchor=tk.W)

        # Area de resultados con scroll
        results_frame = ttk.LabelFrame(main_frame, text="Resultados de Validacion", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Text widget con scrollbar
        text_frame = tk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Validar",
                  command=lambda: self.run_validation(dataset_path, text_widget)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar",
                  command=lambda: text_widget.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Guardar Reporte",
                  command=lambda: self.save_validation_report(text_widget)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cerrar",
                  command=validation_window.destroy).pack(side=tk.RIGHT, padx=5)

        # Ejecutar validación automáticamente
        validation_window.after(100, lambda: self.run_validation(dataset_path, text_widget))

    def run_validation(self, dataset_path, text_widget):
        """Ejecutar validación del dataset"""
        import os
        from pathlib import Path

        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, "Iniciando validacion del dataset...\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        text_widget.update()

        try:
            task_type = self.config.get('task_type').get()
            dataset_dir = Path(dataset_path)

            # Verificar que la carpeta existe
            if not dataset_dir.exists():
                text_widget.insert(tk.END, "ERROR: La carpeta del dataset no existe\n")
                return

            text_widget.insert(tk.END, f"Validando dataset para tarea: {task_type.upper()}\n")
            text_widget.insert(tk.END, f"Ruta: {dataset_path}\n\n")

            if task_type in ['detect', 'segment', 'pose', 'obb']:
                self.validate_detection_like_dataset(dataset_dir, task_type, text_widget)
            elif task_type == 'classify':
                self.validate_classification_dataset(dataset_dir, text_widget)
            else:
                text_widget.insert(tk.END, f"Tipo de tarea '{task_type}' no soportado para validacion\n")

        except Exception as e:
            text_widget.insert(tk.END, f"\nERROR durante la validacion: {str(e)}\n")

        text_widget.insert(tk.END, "\n" + "=" * 50 + "\n")
        text_widget.insert(tk.END, "Validacion completada!\n")
        text_widget.see(tk.END)

    def validate_detection_like_dataset(self, dataset_dir, task_type, text_widget):
        """Validar dataset tipo detección (detect, segment, pose, obb)"""
        from pathlib import Path

        # Subdirectorios esperados
        subdirs = ['train', 'val']
        optional_subdirs = ['test']

        text_widget.insert(tk.END, "ESTRUCTURA DE CARPETAS:\n")
        text_widget.insert(tk.END, "-" * 30 + "\n")

        valid_structure = True

        for subdir in subdirs:
            images_dir = dataset_dir / subdir / 'images'
            labels_dir = dataset_dir / subdir / 'labels'

            # Verificar images
            if images_dir.exists():
                image_count = len([f for f in images_dir.iterdir()
                                 if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']])
                text_widget.insert(tk.END, f"  {subdir}/images/: {image_count} imagenes\n")
            else:
                text_widget.insert(tk.END, f"  {subdir}/images/: NO EXISTE\n")
                valid_structure = False

            # Verificar labels
            if labels_dir.exists():
                label_count = len([f for f in labels_dir.iterdir() if f.suffix == '.txt'])
                text_widget.insert(tk.END, f"  {subdir}/labels/: {label_count} archivos .txt\n")
            else:
                text_widget.insert(tk.END, f"  {subdir}/labels/: NO EXISTE\n")
                valid_structure = False

        # Verificar subdirectorios opcionales
        for subdir in optional_subdirs:
            subdir_path = dataset_dir / subdir
            if subdir_path.exists():
                images_dir = subdir_path / 'images'
                labels_dir = subdir_path / 'labels'

                if images_dir.exists():
                    image_count = len([f for f in images_dir.iterdir()
                                     if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']])
                    text_widget.insert(tk.END, f"  {subdir}/images/: {image_count} imagenes (opcional)\n")

                if labels_dir.exists():
                    label_count = len([f for f in labels_dir.iterdir() if f.suffix == '.txt'])
                    text_widget.insert(tk.END, f"  {subdir}/labels/: {label_count} archivos .txt (opcional)\n")

        text_widget.insert(tk.END, f"\nEstructura basica: {'VALIDA' if valid_structure else 'INVALIDA'}\n\n")

        if valid_structure:
            # Análisis detallado
            self.analyze_image_label_correspondence(dataset_dir, subdirs, text_widget)
            self.analyze_annotation_format(dataset_dir, subdirs, task_type, text_widget)
            self.analyze_dataset_statistics(dataset_dir, subdirs, text_widget)

    def validate_classification_dataset(self, dataset_dir, text_widget):
        """Validar dataset de clasificación"""
        from pathlib import Path

        text_widget.insert(tk.END, "ESTRUCTURA DE CLASIFICACION:\n")
        text_widget.insert(tk.END, "-" * 30 + "\n")

        subdirs = ['train', 'val']
        valid_structure = True
        total_classes = set()

        for subdir in subdirs:
            subdir_path = dataset_dir / subdir

            if subdir_path.exists():
                class_dirs = [d for d in subdir_path.iterdir() if d.is_dir()]

                if class_dirs:
                    text_widget.insert(tk.END, f"  {subdir}/: {len(class_dirs)} clases\n")

                    for class_dir in class_dirs:
                        image_count = len([f for f in class_dir.iterdir()
                                         if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']])
                        text_widget.insert(tk.END, f"    - {class_dir.name}: {image_count} imagenes\n")
                        total_classes.add(class_dir.name)
                else:
                    text_widget.insert(tk.END, f"  {subdir}/: NO CONTIENE CLASES\n")
                    valid_structure = False
            else:
                text_widget.insert(tk.END, f"  {subdir}/: NO EXISTE\n")
                valid_structure = False

        text_widget.insert(tk.END, f"\nTotal de clases unicas: {len(total_classes)}\n")
        text_widget.insert(tk.END, f"Clases: {', '.join(sorted(total_classes))}\n")
        text_widget.insert(tk.END, f"\nEstructura: {'VALIDA' if valid_structure else 'INVALIDA'}\n\n")

        if valid_structure:
            self.analyze_classification_balance(dataset_dir, subdirs, text_widget)

    def analyze_image_label_correspondence(self, dataset_dir, subdirs, text_widget):
        """Analizar correspondencia entre imágenes y etiquetas"""
        from pathlib import Path

        text_widget.insert(tk.END, "CORRESPONDENCIA IMAGENES-ETIQUETAS:\n")
        text_widget.insert(tk.END, "-" * 40 + "\n")

        for subdir in subdirs:
            images_dir = dataset_dir / subdir / 'images'
            labels_dir = dataset_dir / subdir / 'labels'

            if images_dir.exists() and labels_dir.exists():
                # Obtener conjuntos de archivos
                image_stems = {f.stem for f in images_dir.iterdir()
                              if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']}
                label_stems = {f.stem for f in labels_dir.iterdir() if f.suffix == '.txt'}

                # Análisis
                missing_labels = image_stems - label_stems
                missing_images = label_stems - image_stems
                perfect_match = len(missing_labels) == 0 and len(missing_images) == 0

                text_widget.insert(tk.END, f"  {subdir.upper()}:\n")
                text_widget.insert(tk.END, f"    Imagenes: {len(image_stems)}\n")
                text_widget.insert(tk.END, f"    Etiquetas: {len(label_stems)}\n")
                text_widget.insert(tk.END, f"    Correspondencia: {'PERFECTA' if perfect_match else 'IMPERFECTA'}\n")

                if missing_labels:
                    text_widget.insert(tk.END, f"    Imagenes sin etiquetas: {len(missing_labels)}\n")
                    if len(missing_labels) <= 5:
                        text_widget.insert(tk.END, f"      Ejemplos: {', '.join(list(missing_labels)[:5])}\n")

                if missing_images:
                    text_widget.insert(tk.END, f"    Etiquetas sin imagenes: {len(missing_images)}\n")
                    if len(missing_images) <= 5:
                        text_widget.insert(tk.END, f"      Ejemplos: {', '.join(list(missing_images)[:5])}\n")

        text_widget.insert(tk.END, "\n")

    def analyze_annotation_format(self, dataset_dir, subdirs, task_type, text_widget):
        """Analizar formato de anotaciones"""
        from pathlib import Path

        text_widget.insert(tk.END, "FORMATO DE ANOTACIONES:\n")
        text_widget.insert(tk.END, "-" * 30 + "\n")

        format_issues = []
        sample_annotations = []

        for subdir in subdirs:
            labels_dir = dataset_dir / subdir / 'labels'

            if labels_dir.exists():
                label_files = list(labels_dir.glob('*.txt'))

                if label_files:
                    # Analizar algunos archivos de muestra
                    sample_files = label_files[:5]

                    for label_file in sample_files:
                        try:
                            with open(label_file, 'r') as f:
                                lines = f.readlines()

                            if lines:
                                for i, line in enumerate(lines[:3]):  # Primeras 3 líneas
                                    parts = line.strip().split()

                                    if task_type == 'detect':
                                        expected_parts = 5  # class_id x y w h
                                    elif task_type in ['segment', 'obb']:
                                        expected_parts = None  # Variable
                                    elif task_type == 'pose':
                                        expected_parts = None  # Variable, depende de keypoints
                                    else:
                                        expected_parts = None

                                    sample_annotations.append({
                                        'file': label_file.name,
                                        'line': i + 1,
                                        'content': line.strip(),
                                        'parts': len(parts)
                                    })

                                    # Validaciones básicas
                                    if len(parts) < 1:
                                        format_issues.append(f"{label_file.name}:{i+1} - Linea vacia")
                                        continue

                                    try:
                                        class_id = int(parts[0])
                                        if class_id < 0:
                                            format_issues.append(f"{label_file.name}:{i+1} - class_id negativo")
                                    except ValueError:
                                        format_issues.append(f"{label_file.name}:{i+1} - class_id no es entero")

                                    if task_type == 'detect' and len(parts) != 5:
                                        format_issues.append(f"{label_file.name}:{i+1} - Formato deteccion requiere 5 valores")

                        except Exception as e:
                            format_issues.append(f"{label_file.name} - Error leyendo archivo: {str(e)}")

        # Mostrar resultados
        text_widget.insert(tk.END, f"  Archivos analizados: {len(sample_files) if 'sample_files' in locals() else 0}\n")
        text_widget.insert(tk.END, f"  Problemas encontrados: {len(format_issues)}\n")

        if format_issues:
            text_widget.insert(tk.END, "  \n  PROBLEMAS DETECTADOS:\n")
            for issue in format_issues[:10]:  # Mostrar primeros 10
                text_widget.insert(tk.END, f"    - {issue}\n")
            if len(format_issues) > 10:
                text_widget.insert(tk.END, f"    ... y {len(format_issues) - 10} mas\n")

        if sample_annotations:
            text_widget.insert(tk.END, "  \n  EJEMPLOS DE ANOTACIONES:\n")
            for sample in sample_annotations[:5]:
                text_widget.insert(tk.END, f"    {sample['file']}:{sample['line']} -> {sample['content']}\n")

        text_widget.insert(tk.END, "\n")

    def analyze_dataset_statistics(self, dataset_dir, subdirs, text_widget):
        """Analizar estadísticas del dataset"""
        from pathlib import Path

        text_widget.insert(tk.END, "ESTADISTICAS DEL DATASET:\n")
        text_widget.insert(tk.END, "-" * 30 + "\n")

        total_images = 0
        total_annotations = 0
        class_counts = {}

        for subdir in subdirs:
            images_dir = dataset_dir / subdir / 'images'
            labels_dir = dataset_dir / subdir / 'labels'

            if images_dir.exists():
                subdir_images = len([f for f in images_dir.iterdir()
                                   if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']])
                total_images += subdir_images

            if labels_dir.exists():
                for label_file in labels_dir.glob('*.txt'):
                    try:
                        with open(label_file, 'r') as f:
                            lines = f.readlines()

                        for line in lines:
                            parts = line.strip().split()
                            if parts:
                                try:
                                    class_id = int(parts[0])
                                    class_counts[class_id] = class_counts.get(class_id, 0) + 1
                                    total_annotations += 1
                                except ValueError:
                                    pass
                    except Exception:
                        pass

        text_widget.insert(tk.END, f"  Total de imagenes: {total_images}\n")
        text_widget.insert(tk.END, f"  Total de anotaciones: {total_annotations}\n")

        # Calcular promedio de anotaciones por imagen
        avg_annotations = total_annotations / total_images if total_images > 0 else 0
        text_widget.insert(tk.END, f"  Promedio anotaciones/imagen: {avg_annotations:.2f}\n")

        text_widget.insert(tk.END, f"  Clases detectadas: {len(class_counts)}\n")

        if class_counts:
            text_widget.insert(tk.END, "  \n  DISTRIBUCION POR CLASE:\n")
            sorted_classes = sorted(class_counts.items())
            for class_id, count in sorted_classes:
                percentage = (count / total_annotations) * 100 if total_annotations > 0 else 0
                text_widget.insert(tk.END, f"    Clase {class_id}: {count} anotaciones ({percentage:.1f}%)\n")

        text_widget.insert(tk.END, "\n")

    def analyze_classification_balance(self, dataset_dir, subdirs, text_widget):
        """Analizar balance de clases en clasificación"""
        from pathlib import Path

        text_widget.insert(tk.END, "BALANCE DE CLASES:\n")
        text_widget.insert(tk.END, "-" * 20 + "\n")

        for subdir in subdirs:
            subdir_path = dataset_dir / subdir

            if subdir_path.exists():
                class_counts = {}
                total_images = 0

                for class_dir in subdir_path.iterdir():
                    if class_dir.is_dir():
                        count = len([f for f in class_dir.iterdir()
                                   if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']])
                        class_counts[class_dir.name] = count
                        total_images += count

                text_widget.insert(tk.END, f"  {subdir.upper()} ({total_images} imagenes):\n")

                if class_counts:
                    sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)

                    for class_name, count in sorted_classes:
                        percentage = (count / total_images) * 100 if total_images > 0 else 0
                        text_widget.insert(tk.END, f"    {class_name}: {count} imagenes ({percentage:.1f}%)\n")

                    # Análisis de balance
                    max_count = max(class_counts.values()) if class_counts.values() else 0
                    min_count = min(class_counts.values()) if class_counts.values() else 0
                    balance_ratio = min_count / max_count if max_count > 0 else 0

                    text_widget.insert(tk.END, f"    \n    Ratio de balance: {balance_ratio:.2f}\n")
                    if balance_ratio < 0.1:
                        text_widget.insert(tk.END, f"    WARNING: Dataset muy desbalanceado\n")
                    elif balance_ratio < 0.5:
                        text_widget.insert(tk.END, f"    INFO: Dataset moderadamente desbalanceado\n")
                    else:
                        text_widget.insert(tk.END, f"    OK: Dataset relativamente balanceado\n")

        text_widget.insert(tk.END, "\n")

    def save_validation_report(self, text_widget):
        """Guardar reporte de validación"""
        from tkinter import filedialog
        from datetime import datetime

        content = text_widget.get(1.0, tk.END)

        filename = filedialog.asksaveasfilename(
            title="Guardar Reporte de Validacion",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialname=f"dataset_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                from tkinter import messagebox
                messagebox.showinfo("Exito", f"Reporte guardado en:\n{filename}")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"Error guardando reporte:\n{str(e)}")

    def convert_coco_to_yolo(self):
        """Herramienta para convertir COCO a formato YOLO segmentación"""
        converter_window = tk.Toplevel(self.parent_frame.master)
        converter_window.title("Convertir COCO a YOLO Segmentacion")
        converter_window.geometry("800x700")
        converter_window.transient(self.parent_frame.master)
        converter_window.grab_set()

        # Frame principal
        main_frame = ttk.Frame(converter_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Convertir Dataset COCO a YOLO Segmentacion",
                 font=('Arial', 14, 'bold')).pack(pady=10)

        # Información
        info_frame = ttk.LabelFrame(main_frame, text="Informacion", padding="10")
        info_frame.pack(fill=tk.X, pady=5)

        info_text = """Esta herramienta convierte datasets en formato COCO a formato YOLO para segmentacion.

Archivos necesarios:
- Archivo JSON de anotaciones COCO (ej: annotations.json, result_coco.json)
- Carpeta con todas las imagenes referenciadas en el JSON
- Carpeta base donde crear el dataset (se creara automaticamente dataset/ dentro)

La herramienta creara automaticamente la estructura:
carpeta_base/
└── dataset/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/ (opcional)
    │   ├── images/
    │   └── labels/
    └── dataset.yaml"""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=750).pack()

        # Selección de archivos
        files_frame = ttk.LabelFrame(main_frame, text="Archivos de Entrada", padding="10")
        files_frame.pack(fill=tk.X, pady=5)

        # Variables para archivos
        coco_file_var = tk.StringVar()
        images_folder_var = tk.StringVar()
        output_folder_var = tk.StringVar()

        # JSON COCO
        ttk.Label(files_frame, text="Archivo JSON COCO:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(files_frame, textvariable=coco_file_var, width=60).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(files_frame, text="Examinar",
                  command=lambda: self.browse_coco_file(coco_file_var)).grid(row=0, column=2, pady=2)

        # Carpeta imágenes
        ttk.Label(files_frame, text="Carpeta imagenes:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(files_frame, textvariable=images_folder_var, width=60).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(files_frame, text="Examinar",
                  command=lambda: self.browse_images_folder(images_folder_var)).grid(row=1, column=2, pady=2)

        # Carpeta salida
        ttk.Label(files_frame, text="Carpeta base de salida:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(files_frame, textvariable=output_folder_var, width=60).grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(files_frame, text="Examinar",
                  command=lambda: self.browse_output_folder(output_folder_var)).grid(row=2, column=2, pady=2)

        # Información sobre la estructura
        ttk.Label(files_frame, text="(Se creara: carpeta_base/dataset/train/ y carpeta_base/dataset/val/)",
                 font=('Arial', 8), foreground='gray').grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0,5))

        # Configurar expansión de columnas
        files_frame.columnconfigure(1, weight=1)

        # Opciones adicionales
        options_frame = ttk.LabelFrame(main_frame, text="Opciones", padding="10")
        options_frame.pack(fill=tk.X, pady=5)

        # Opciones de conversión
        create_val_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Crear conjunto de validacion (20% de las imagenes)",
                       variable=create_val_var).pack(anchor=tk.W)

        shuffle_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Mezclar imagenes antes de dividir",
                       variable=shuffle_var).pack(anchor=tk.W)

        # Log de conversión
        log_frame = ttk.LabelFrame(main_frame, text="Log de Conversion", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Text widget con scrollbar
        log_text_frame = tk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True)

        log_text = tk.Text(log_text_frame, height=15, font=('Courier', 9))
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient="vertical", command=log_text.yview)
        log_text.configure(yscrollcommand=log_scrollbar.set)

        log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        convert_btn = ttk.Button(button_frame, text="Convertir",
                                command=lambda: self.run_coco_conversion(
                                    coco_file_var.get(),
                                    images_folder_var.get(),
                                    output_folder_var.get(),
                                    create_val_var.get(),
                                    shuffle_var.get(),
                                    log_text
                                ))
        convert_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(button_frame, text="Limpiar Log",
                              command=lambda: log_text.delete(1.0, tk.END))
        clear_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Cerrar",
                  command=converter_window.destroy).pack(side=tk.RIGHT, padx=5)

    def browse_coco_file(self, var):
        """Examinar archivo COCO JSON"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo JSON COCO",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)

    def browse_images_folder(self, var):
        """Examinar carpeta de imágenes"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de imagenes")
        if folder:
            var.set(folder)

    def browse_output_folder(self, var):
        """Examinar carpeta base de salida"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta base (se creara dataset/ dentro)")
        if folder:
            var.set(folder)

    def run_coco_conversion(self, coco_file, images_folder, output_folder, create_val, shuffle_data, log_widget):
        """Ejecutar conversión COCO a YOLO"""
        import json
        import shutil
        import random
        from pathlib import Path
        from datetime import datetime

        # Validar entradas
        if not all([coco_file, images_folder, output_folder]):
            log_widget.insert(tk.END, "ERROR: Faltan archivos de entrada\n")
            return

        if not os.path.exists(coco_file):
            log_widget.insert(tk.END, f"ERROR: Archivo COCO no existe: {coco_file}\n")
            return

        if not os.path.exists(images_folder):
            log_widget.insert(tk.END, f"ERROR: Carpeta de imagenes no existe: {images_folder}\n")
            return

        try:
            log_widget.insert(tk.END, f"Iniciando conversion COCO -> YOLO...\n")
            log_widget.insert(tk.END, f"Hora inicio: {datetime.now().strftime('%H:%M:%S')}\n")
            log_widget.insert(tk.END, f"Archivo COCO: {coco_file}\n")
            log_widget.insert(tk.END, f"Carpeta imagenes: {images_folder}\n")
            log_widget.insert(tk.END, f"Carpeta base: {output_folder}\n")
            log_widget.insert(tk.END, "-" * 50 + "\n\n")
            log_widget.update()

            # Crear carpeta dataset dentro de la carpeta base
            base_path = Path(output_folder)
            dataset_path = base_path / "dataset"

            log_widget.insert(tk.END, f"Creando dataset en: {dataset_path}\n")

            # Crear estructura de carpetas dentro de dataset/
            train_images_path = dataset_path / "train" / "images"
            train_labels_path = dataset_path / "train" / "labels"

            train_images_path.mkdir(parents=True, exist_ok=True)
            train_labels_path.mkdir(parents=True, exist_ok=True)

            if create_val:
                val_images_path = dataset_path / "val" / "images"
                val_labels_path = dataset_path / "val" / "labels"
                val_images_path.mkdir(parents=True, exist_ok=True)
                val_labels_path.mkdir(parents=True, exist_ok=True)
                log_widget.insert(tk.END, f"Estructura creada: dataset/train/ y dataset/val/\n")
            else:
                log_widget.insert(tk.END, f"Estructura creada: dataset/train/\n")

            log_widget.update()

            # Leer archivo COCO
            log_widget.insert(tk.END, f"Cargando archivo COCO...\n")
            with open(coco_file, 'r', encoding='utf-8') as f:
                coco_data = json.load(f)

            log_widget.insert(tk.END, f"Archivo COCO cargado exitosamente\n")
            log_widget.insert(tk.END, f"Imagenes en COCO: {len(coco_data.get('images', []))}\n")
            log_widget.insert(tk.END, f"Anotaciones en COCO: {len(coco_data.get('annotations', []))}\n")
            log_widget.insert(tk.END, f"Categorias en COCO: {len(coco_data.get('categories', []))}\n\n")
            log_widget.update()

            # Crear mapeo de image_id a información de imagen
            image_info = {img['id']: img for img in coco_data.get('images', [])}

            # Preparar lista de imágenes para procesamiento
            image_list = list(image_info.keys())

            if shuffle_data:
                random.shuffle(image_list)
                log_widget.insert(tk.END, f"Imagenes mezcladas aleatoriamente\n")

            # Dividir en train/val si es necesario
            if create_val:
                split_idx = int(len(image_list) * 0.8)  # 80% train, 20% val
                train_images = image_list[:split_idx]
                val_images = image_list[split_idx:]
                log_widget.insert(tk.END, f"Division: {len(train_images)} train, {len(val_images)} val\n\n")
            else:
                train_images = image_list
                val_images = []
                log_widget.insert(tk.END, f"Todas las imagenes van a entrenamiento: {len(train_images)}\n\n")

            log_widget.update()

            # Procesar imágenes de entrenamiento
            processed_count = 0
            log_widget.insert(tk.END, f"Procesando imagenes de entrenamiento...\n")

            for img_id in train_images:
                img_data = image_info[img_id]
                success = self.process_single_image(
                    img_data, coco_data, images_folder,
                    train_images_path, train_labels_path,
                    log_widget
                )

                if success:
                    processed_count += 1

                if processed_count % 50 == 0:
                    log_widget.insert(tk.END, f"Procesadas: {processed_count} imagenes de entrenamiento\n")
                    log_widget.update()

            log_widget.insert(tk.END, f"Entrenamiento completado: {processed_count} imagenes procesadas\n\n")

            # Procesar imágenes de validación
            if create_val and val_images:
                processed_val_count = 0
                log_widget.insert(tk.END, f"Procesando imagenes de validacion...\n")

                for img_id in val_images:
                    img_data = image_info[img_id]
                    success = self.process_single_image(
                        img_data, coco_data, images_folder,
                        val_images_path, val_labels_path,
                        log_widget
                    )

                    if success:
                        processed_val_count += 1

                    if processed_val_count % 20 == 0:
                        log_widget.insert(tk.END, f"Procesadas: {processed_val_count} imagenes de validacion\n")
                        log_widget.update()

                log_widget.insert(tk.END, f"Validacion completada: {processed_val_count} imagenes procesadas\n\n")

            # Crear archivo dataset.yaml
            self.create_dataset_yaml(coco_data, dataset_path, create_val, log_widget)

            # Resumen final
            log_widget.insert(tk.END, "-" * 50 + "\n")
            log_widget.insert(tk.END, f"CONVERSION COMPLETADA EXITOSAMENTE!\n")
            log_widget.insert(tk.END, f"Hora fin: {datetime.now().strftime('%H:%M:%S')}\n")
            log_widget.insert(tk.END, f"Dataset creado en: {dataset_path}\n")
            log_widget.insert(tk.END, f"Total imagenes procesadas: {processed_count}")
            if create_val:
                log_widget.insert(tk.END, f" + {processed_val_count if 'processed_val_count' in locals() else 0} val")
            log_widget.insert(tk.END, f"\n")
            log_widget.insert(tk.END, f"Archivo YAML: {dataset_path}/dataset.yaml\n")
            log_widget.insert(tk.END, f"Estructura final:\n")
            log_widget.insert(tk.END, f"{base_path.name}/\n")
            log_widget.insert(tk.END, f"+-- dataset/\n")
            log_widget.insert(tk.END, f"    +-- train/images/ ({processed_count} imagenes)\n")
            log_widget.insert(tk.END, f"    +-- train/labels/ ({processed_count} archivos)\n")
            if create_val:
                val_count = processed_val_count if 'processed_val_count' in locals() else 0
                log_widget.insert(tk.END, f"    +-- val/images/ ({val_count} imagenes)\n")
                log_widget.insert(tk.END, f"    +-- val/labels/ ({val_count} archivos)\n")
            log_widget.insert(tk.END, f"    +-- dataset.yaml\n")
            log_widget.insert(tk.END, "-" * 50 + "\n")

        except Exception as e:
            log_widget.insert(tk.END, f"\nERROR durante la conversion: {str(e)}\n")
            import traceback
            log_widget.insert(tk.END, f"Detalles del error:\n{traceback.format_exc()}\n")

        log_widget.see(tk.END)

    def process_single_image(self, img_data, coco_data, images_folder, target_images_path, target_labels_path, log_widget):
        """Procesar una sola imagen y sus anotaciones"""
        import shutil
        from pathlib import Path

        try:
            file_name = img_data['file_name']
            width = img_data['width']
            height = img_data['height']
            img_id = img_data['id']

            # Copiar imagen
            src_image = Path(images_folder) / file_name
            dst_image = target_images_path / file_name

            if not src_image.exists():
                log_widget.insert(tk.END, f"WARNING: Imagen no encontrada: {file_name}\n")
                return False

            shutil.copy2(src_image, dst_image)

            # Crear archivo de etiquetas correspondiente
            label_file = target_labels_path / f"{Path(file_name).stem}.txt"

            # Buscar todas las anotaciones para esta imagen
            annotations = [ann for ann in coco_data.get('annotations', []) if ann.get('image_id') == img_id]

            with open(label_file, 'w') as f:
                for ann in annotations:
                    # YOLO usa category_id - 1 (0-indexed)
                    class_id = ann.get('category_id', 1) - 1

                    # Convertir segmentación a formato YOLO
                    if 'segmentation' in ann and ann['segmentation']:
                        segmentation = ann['segmentation']

                        # Manejar diferentes formatos de segmentación
                        if isinstance(segmentation, list) and len(segmentation) > 0:
                            if isinstance(segmentation[0], list):
                                # Formato: [[x1,y1,x2,y2,...]]
                                polygon = segmentation[0]
                            else:
                                # Formato: [x1,y1,x2,y2,...]
                                polygon = segmentation

                            # Convertir coordenadas absolutas a normalizadas
                            normalized_coords = []
                            for i in range(0, len(polygon), 2):
                                if i + 1 < len(polygon):
                                    x = polygon[i] / width
                                    y = polygon[i + 1] / height
                                    # Asegurar que las coordenadas estén en rango [0,1]
                                    x = max(0, min(1, x))
                                    y = max(0, min(1, y))
                                    normalized_coords.extend([x, y])

                            # Escribir línea YOLO: class_id x1 y1 x2 y2 ... xn yn
                            if normalized_coords:
                                coords_str = ' '.join([f"{coord:.6f}" for coord in normalized_coords])
                                f.write(f"{class_id} {coords_str}\n")

            return True

        except Exception as e:
            log_widget.insert(tk.END, f"ERROR procesando {img_data.get('file_name', 'unknown')}: {str(e)}\n")
            return False

    def create_dataset_yaml(self, coco_data, output_path, create_val, log_widget):
        """Crear archivo dataset.yaml"""
        from datetime import datetime

        try:
            # Obtener categorías del archivo COCO
            categories = {cat['id']: cat['name'] for cat in coco_data.get('categories', [])}

            log_widget.insert(tk.END, f"Creando archivo dataset.yaml...\n")
            log_widget.insert(tk.END, f"Categorias encontradas: {categories}\n")

            # Crear contenido YAML
            dataset_path = output_path.absolute()
            yaml_content = f"""# Dataset YOLO generado desde COCO
# Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Conversion automatica de formato COCO a YOLO

path: {dataset_path}
train: train/images
"""

            if create_val:
                yaml_content += "val: val/images\n"
            else:
                yaml_content += "val: train/images  # Usar mismo conjunto para validacion\n"

            yaml_content += f"\n# Numero de clases\nnc: {len(categories)}\n\n# Nombres de clases (YOLO usa indices 0-based)\nnames:\n"

            # Escribir nombres de clases dinámicamente
            # COCO usa 1-based, YOLO usa 0-based
            sorted_categories = sorted(categories.items())  # Ordenar por ID para consistencia

            for cat_id, cat_name in sorted_categories:
                yolo_class_id = cat_id - 1  # Convertir de 1-based a 0-based
                yaml_content += f"  {yolo_class_id}: {cat_name}\n"

            # Agregar información adicional
            yaml_content += f"\n# Informacion adicional\n"
            yaml_content += f"# Total categorias COCO: {len(categories)}\n"
            yaml_content += f"# Mapeo COCO ID -> YOLO ID:\n"
            for cat_id, cat_name in sorted_categories:
                yaml_content += f"#   COCO {cat_id} -> YOLO {cat_id - 1}: {cat_name}\n"

            # Guardar archivo
            yaml_file = output_path / "dataset.yaml"
            with open(yaml_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)

            log_widget.insert(tk.END, f"Archivo YAML creado exitosamente: {yaml_file}\n")
            log_widget.insert(tk.END, f"Numero de clases: {len(categories)}\n")
            log_widget.insert(tk.END, f"Mapeo de clases (COCO ID -> YOLO ID):\n")

            # Mostrar mapeo detallado en el log
            for cat_id, cat_name in sorted_categories:
                yolo_id = cat_id - 1
                log_widget.insert(tk.END, f"  {cat_id} -> {yolo_id}: {cat_name}\n")

            log_widget.insert(tk.END, f"\nContenido del YAML:\n")
            log_widget.insert(tk.END, "-" * 30 + "\n")

            # Mostrar contenido del YAML en el log (versión resumida)
            yaml_lines = yaml_content.split('\n')
            for line in yaml_lines:
                if line.strip() and not line.startswith('#'):
                    log_widget.insert(tk.END, f"{line}\n")
            log_widget.insert(tk.END, "-" * 30 + "\n")

        except Exception as e:
            log_widget.insert(tk.END, f"ERROR creando YAML: {str(e)}\n")
            import traceback
            log_widget.insert(tk.END, f"Detalles: {traceback.format_exc()}\n")

    def generate_classification_yaml(self):
        """Placeholder para generar YAML de clasificación"""
        from tkinter import messagebox
        messagebox.showinfo("Generar YAML", "Funcionalidad en desarrollo...")

    def validate_page(self):
        """Validar datos de la página"""
        dataset_path = self.config.get('dataset_path').get()
        yaml_path = self.config.get('yaml_path').get()
        output_path = self.config.get('output_path').get()

        if not dataset_path:
            return False, "Selecciona la carpeta del dataset"
        if not yaml_path:
            return False, "Selecciona el archivo YAML"
        if not output_path:
            return False, "Selecciona la carpeta de salida"

        return True, ""
