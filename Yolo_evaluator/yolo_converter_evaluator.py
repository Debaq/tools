import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from pathlib import Path
import threading
from PIL import Image, ImageTk
from ultralytics import YOLO
import torch

class YOLOConverterEvaluator:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor y Evaluador YOLO - PT a ONNX")
        self.root.geometry("1200x800")
        
        # Variables
        self.pt_model = None
        self.onnx_model = None
        self.test_images = []
        self.dataset_path = ""
        self.results_pt = []
        self.results_onnx = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pestaña 1: Conversión
        self.tab_conversion = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_conversion, text="Conversión PT → ONNX")
        self.setup_conversion_tab()
        
        # Pestaña 2: Pruebas con imágenes
        self.tab_testing = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_testing, text="Pruebas con Imágenes")
        self.setup_testing_tab()
        
        # Pestaña 3: Evaluación con dataset
        self.tab_dataset = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dataset, text="Evaluación con Dataset")
        self.setup_dataset_tab()
        
        # Pestaña 4: Métricas y comparación
        self.tab_metrics = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_metrics, text="Métricas y Comparación")
        self.setup_metrics_tab()
        
        # Pestaña 5: Visualización
        self.tab_visualization = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_visualization, text="Visualización")
        self.setup_visualization_tab()
    
    def setup_conversion_tab(self):
        # Frame principal
        main_frame = ttk.Frame(self.tab_conversion)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, text="Conversión de Modelo PT a ONNX", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Selección de archivo PT
        pt_frame = ttk.Frame(main_frame)
        pt_frame.pack(fill='x', pady=10)
        
        ttk.Label(pt_frame, text="Archivo PT:").pack(side='left')
        self.pt_path_var = tk.StringVar()
        ttk.Entry(pt_frame, textvariable=self.pt_path_var, width=60).pack(side='left', padx=10)
        ttk.Button(pt_frame, text="Seleccionar", command=self.select_pt_file).pack(side='left')
        
        # Selección de directorio de salida
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill='x', pady=10)
        
        ttk.Label(output_frame, text="Directorio salida:").pack(side='left')
        self.output_path_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_path_var, width=60).pack(side='left', padx=10)
        ttk.Button(output_frame, text="Seleccionar", command=self.select_output_dir).pack(side='left')
        
        # Botón de conversión
        ttk.Button(main_frame, text="Convertir a ONNX", command=self.convert_to_onnx).pack(pady=20)
        
        # Área de log
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill='both', expand=True, pady=10)
        
        ttk.Label(log_frame, text="Log de conversión:").pack(anchor='w')
        self.log_text = tk.Text(log_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_testing_tab(self):
        # Frame principal
        main_frame = ttk.Frame(self.tab_testing)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, text="Pruebas con Imágenes", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Cargar modelos
        models_frame = ttk.LabelFrame(main_frame, text="Modelos", padding=10)
        models_frame.pack(fill='x', pady=10)
        
        # Modelo PT
        pt_model_frame = ttk.Frame(models_frame)
        pt_model_frame.pack(fill='x', pady=5)
        ttk.Label(pt_model_frame, text="Modelo PT:").pack(side='left')
        self.pt_model_var = tk.StringVar()
        ttk.Entry(pt_model_frame, textvariable=self.pt_model_var, width=50).pack(side='left', padx=10)
        ttk.Button(pt_model_frame, text="Cargar PT", command=self.load_pt_model).pack(side='left')
        
        # Modelo ONNX
        onnx_model_frame = ttk.Frame(models_frame)
        onnx_model_frame.pack(fill='x', pady=5)
        ttk.Label(onnx_model_frame, text="Modelo ONNX:").pack(side='left')
        self.onnx_model_var = tk.StringVar()
        ttk.Entry(onnx_model_frame, textvariable=self.onnx_model_var, width=50).pack(side='left', padx=10)
        ttk.Button(onnx_model_frame, text="Cargar ONNX", command=self.load_onnx_model).pack(side='left')
        
        # Cargar imágenes
        images_frame = ttk.LabelFrame(main_frame, text="Imágenes de Prueba", padding=10)
        images_frame.pack(fill='x', pady=10)
        
        buttons_frame = ttk.Frame(images_frame)
        buttons_frame.pack(fill='x')
        ttk.Button(buttons_frame, text="Cargar Imagen", command=self.load_single_image).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Cargar Múltiples", command=self.load_multiple_images).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Ejecutar Pruebas", command=self.run_tests).pack(side='left', padx=20)
        
        # Lista de imágenes
        self.images_listbox = tk.Listbox(images_frame, height=6)
        self.images_listbox.pack(fill='x', pady=10)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding=10)
        results_frame.pack(fill='both', expand=True, pady=10)
        
        self.results_text = tk.Text(results_frame, height=10)
        results_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        self.results_text.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')
    
    def setup_dataset_tab(self):
        # Frame principal
        main_frame = ttk.Frame(self.tab_dataset)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, text="Evaluación con Dataset", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Selección de dataset
        dataset_frame = ttk.LabelFrame(main_frame, text="Dataset", padding=10)
        dataset_frame.pack(fill='x', pady=10)
        
        dataset_path_frame = ttk.Frame(dataset_frame)
        dataset_path_frame.pack(fill='x')
        ttk.Label(dataset_path_frame, text="Carpeta Dataset:").pack(side='left')
        self.dataset_path_var = tk.StringVar()
        ttk.Entry(dataset_path_frame, textvariable=self.dataset_path_var, width=60).pack(side='left', padx=10)
        ttk.Button(dataset_path_frame, text="Seleccionar", command=self.select_dataset_folder).pack(side='left')
        
        # Configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración", padding=10)
        config_frame.pack(fill='x', pady=10)
        
        # Confidence threshold
        conf_frame = ttk.Frame(config_frame)
        conf_frame.pack(fill='x', pady=5)
        ttk.Label(conf_frame, text="Confidence Threshold:").pack(side='left')
        self.conf_threshold = tk.DoubleVar(value=0.5)
        ttk.Scale(conf_frame, from_=0.0, to=1.0, variable=self.conf_threshold, orient='horizontal').pack(side='left', padx=10)
        ttk.Label(conf_frame, textvariable=self.conf_threshold).pack(side='left')
        
        # IoU threshold
        iou_frame = ttk.Frame(config_frame)
        iou_frame.pack(fill='x', pady=5)
        ttk.Label(iou_frame, text="IoU Threshold:").pack(side='left')
        self.iou_threshold = tk.DoubleVar(value=0.5)
        ttk.Scale(iou_frame, from_=0.0, to=1.0, variable=self.iou_threshold, orient='horizontal').pack(side='left', padx=10)
        ttk.Label(iou_frame, textvariable=self.iou_threshold).pack(side='left')
        
        # Botón de evaluación
        ttk.Button(main_frame, text="Evaluar Dataset", command=self.evaluate_dataset).pack(pady=20)
        
        # Progreso
        self.progress_var = tk.StringVar(value="Listo para evaluar")
        ttk.Label(main_frame, textvariable=self.progress_var).pack(pady=5)
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
    
    def setup_metrics_tab(self):
        # Frame principal
        main_frame = ttk.Frame(self.tab_metrics)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, text="Métricas y Comparación", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame para controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x', pady=10)
        
        ttk.Button(controls_frame, text="Generar Gráficos", command=self.generate_metrics_plots).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Limpiar", command=self.clear_metrics).pack(side='left', padx=5)
        
        # Frame para gráficos
        self.metrics_frame = ttk.Frame(main_frame)
        self.metrics_frame.pack(fill='both', expand=True)
        
        # Explicaciones de métricas
        explanations_frame = ttk.LabelFrame(main_frame, text="Explicación de Métricas", padding=10)
        explanations_frame.pack(fill='x', pady=10)
        
        explanations_text = """
        • Precisión: TP / (TP + FP) - Proporción de detecciones correctas
        • Recall: TP / (TP + FN) - Proporción de objetos reales detectados
        • F1-Score: 2 * (Precisión * Recall) / (Precisión + Recall) - Media armónica
        • mAP: Mean Average Precision - Precisión promedio en diferentes thresholds
        • Tiempo Inferencia: Tiempo promedio por imagen en milisegundos
        • FPS: Frames por segundo (1000 / tiempo_inferencia)
        """
        
        ttk.Label(explanations_frame, text=explanations_text, justify='left').pack(anchor='w')
    
    def setup_visualization_tab(self):
        # Frame principal
        main_frame = ttk.Frame(self.tab_visualization)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, text="Visualización de Detecciones", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x', pady=10)
        
        ttk.Label(controls_frame, text="Seleccionar imagen:").pack(side='left')
        self.image_selector = ttk.Combobox(controls_frame, width=40)
        self.image_selector.pack(side='left', padx=10)
        self.image_selector.bind('<<ComboboxSelected>>', self.show_detections)
        
        ttk.Button(controls_frame, text="Mostrar Detecciones", command=self.show_detections).pack(side='left', padx=10)
        
        # Canvas para mostrar imágenes
        self.canvas_frame = ttk.Frame(main_frame)
        self.canvas_frame.pack(fill='both', expand=True)
        
        # Scrollable canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.canvas.pack(side='left', fill='both', expand=True)
        self.v_scrollbar.pack(side='right', fill='y')
        self.h_scrollbar.pack(side='bottom', fill='x')
    
    # Métodos para pestaña de conversión
    def select_pt_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo PT",
            filetypes=[("PyTorch files", "*.pt"), ("All files", "*.*")]
        )
        if filename:
            self.pt_path_var.set(filename)
    
    def select_output_dir(self):
        dirname = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if dirname:
            self.output_path_var.set(dirname)
    
    def convert_to_onnx(self):
        if not self.pt_path_var.get():
            messagebox.showerror("Error", "Seleccione un archivo PT")
            return
        
        if not self.output_path_var.get():
            messagebox.showerror("Error", "Seleccione un directorio de salida")
            return
        
        def conversion_thread():
            try:
                self.log_message("Iniciando conversión...")
                
                # Cargar modelo
                model = YOLO(self.pt_path_var.get())
                self.log_message(f"Modelo cargado: {self.pt_path_var.get()}")
                
                # Convertir a ONNX
                pt_name = Path(self.pt_path_var.get()).stem
                onnx_path = os.path.join(self.output_path_var.get(), f"{pt_name}.onnx")
                
                model.export(format='onnx', opset=11)
                self.log_message(f"Conversión completada: {onnx_path}")
                
                messagebox.showinfo("Éxito", "Conversión completada exitosamente")
                
            except Exception as e:
                self.log_message(f"Error durante la conversión: {str(e)}")
                messagebox.showerror("Error", f"Error durante la conversión: {str(e)}")
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    # Métodos para pestaña de pruebas
    def load_pt_model(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar modelo PT",
            filetypes=[("PyTorch files", "*.pt"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.pt_model = YOLO(filename)
                self.pt_model_var.set(filename)
                messagebox.showinfo("Éxito", "Modelo PT cargado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo PT: {str(e)}")
    
    def load_onnx_model(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar modelo ONNX",
            filetypes=[("ONNX files", "*.onnx"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.onnx_model = YOLO(filename)
                self.onnx_model_var.set(filename)
                messagebox.showinfo("Éxito", "Modelo ONNX cargado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo ONNX: {str(e)}")
    
    def load_single_image(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.test_images.append(filename)
            self.images_listbox.insert(tk.END, os.path.basename(filename))
            self.update_image_selector()
    
    def load_multiple_images(self):
        filenames = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        for filename in filenames:
            self.test_images.append(filename)
            self.images_listbox.insert(tk.END, os.path.basename(filename))
        self.update_image_selector()
    
    def update_image_selector(self):
        image_names = [os.path.basename(img) for img in self.test_images]
        self.image_selector['values'] = image_names
    
    def run_tests(self):
        if not self.pt_model and not self.onnx_model:
            messagebox.showerror("Error", "Cargue al menos un modelo")
            return
        
        if not self.test_images:
            messagebox.showerror("Error", "Cargue al menos una imagen")
            return
        
        def test_thread():
            try:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "Ejecutando pruebas...\n\n")
                
                self.results_pt = []
                self.results_onnx = []
                
                for i, image_path in enumerate(self.test_images):
                    self.results_text.insert(tk.END, f"Procesando imagen {i+1}/{len(self.test_images)}: {os.path.basename(image_path)}\n")
                    
                    # Probar modelo PT
                    if self.pt_model:
                        start_time = time.time()
                        results_pt = self.pt_model(image_path)
                        pt_time = (time.time() - start_time) * 1000
                        
                        self.results_pt.append({
                            'image': image_path,
                            'results': results_pt,
                            'time': pt_time,
                            'detections': len(results_pt[0].boxes) if results_pt[0].boxes is not None else 0
                        })
                        
                        self.results_text.insert(tk.END, f"  PT: {len(results_pt[0].boxes) if results_pt[0].boxes is not None else 0} detecciones, {pt_time:.2f}ms\n")
                    
                    # Probar modelo ONNX
                    if self.onnx_model:
                        start_time = time.time()
                        results_onnx = self.onnx_model(image_path)
                        onnx_time = (time.time() - start_time) * 1000
                        
                        self.results_onnx.append({
                            'image': image_path,
                            'results': results_onnx,
                            'time': onnx_time,
                            'detections': len(results_onnx[0].boxes) if results_onnx[0].boxes is not None else 0
                        })
                        
                        self.results_text.insert(tk.END, f"  ONNX: {len(results_onnx[0].boxes) if results_onnx[0].boxes is not None else 0} detecciones, {onnx_time:.2f}ms\n")
                    
                    self.results_text.insert(tk.END, "\n")
                    self.results_text.see(tk.END)
                    self.root.update()
                
                self.results_text.insert(tk.END, "Pruebas completadas!\n")
                
            except Exception as e:
                self.results_text.insert(tk.END, f"Error durante las pruebas: {str(e)}\n")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    # Métodos para pestaña de dataset
    def select_dataset_folder(self):
        dirname = filedialog.askdirectory(title="Seleccionar carpeta del dataset")
        if dirname:
            self.dataset_path_var.set(dirname)
    
    def evaluate_dataset(self):
        if not self.dataset_path_var.get():
            messagebox.showerror("Error", "Seleccione una carpeta de dataset")
            return
        
        if not self.pt_model and not self.onnx_model:
            messagebox.showerror("Error", "Cargue al menos un modelo")
            return
        
        def evaluation_thread():
            try:
                dataset_path = self.dataset_path_var.get()
                
                # Buscar imágenes y anotaciones
                image_files = []
                annotation_files = []
                
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
                    image_files.extend(Path(dataset_path).glob(ext))
                    image_files.extend(Path(dataset_path).glob(ext.upper()))
                
                for image_file in image_files:
                    annotation_file = image_file.with_suffix('.txt')
                    if annotation_file.exists():
                        annotation_files.append(annotation_file)
                
                if not image_files:
                    messagebox.showerror("Error", "No se encontraron imágenes en el dataset")
                    return
                
                self.progress_var.set(f"Evaluando {len(image_files)} imágenes...")
                self.progress_bar['maximum'] = len(image_files)
                self.progress_bar['value'] = 0
                
                # Evaluar cada imagen
                for i, image_file in enumerate(image_files):
                    self.progress_var.set(f"Procesando {i+1}/{len(image_files)}: {image_file.name}")
                    
                    # Aquí iría la lógica de evaluación con ground truth
                    # Por simplicidad, solo ejecutamos detección
                    
                    if self.pt_model:
                        results = self.pt_model(str(image_file))
                        # Procesar resultados PT
                    
                    if self.onnx_model:
                        results = self.onnx_model(str(image_file))
                        # Procesar resultados ONNX
                    
                    self.progress_bar['value'] = i + 1
                    self.root.update()
                
                self.progress_var.set("Evaluación completada")
                messagebox.showinfo("Éxito", "Evaluación del dataset completada")
                
            except Exception as e:
                self.progress_var.set(f"Error: {str(e)}")
                messagebox.showerror("Error", f"Error durante la evaluación: {str(e)}")
        
        threading.Thread(target=evaluation_thread, daemon=True).start()
    
    # Métodos para pestaña de métricas
    def generate_metrics_plots(self):
        if not self.results_pt and not self.results_onnx:
            messagebox.showwarning("Advertencia", "No hay resultados para mostrar. Ejecute primero las pruebas.")
            return
        
        # Limpiar frame anterior
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        
        # Crear figura con subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('Comparación de Modelos PT vs ONNX', fontsize=16)
        
        # Datos para gráficos
        pt_times = [r['time'] for r in self.results_pt] if self.results_pt else []
        onnx_times = [r['time'] for r in self.results_onnx] if self.results_onnx else []
        
        pt_detections = [r['detections'] for r in self.results_pt] if self.results_pt else []
        onnx_detections = [r['detections'] for r in self.results_onnx] if self.results_onnx else []
        
        # Gráfico 1: Tiempo de inferencia
        if pt_times or onnx_times:
            axes[0, 0].boxplot([pt_times, onnx_times], labels=['PT', 'ONNX'])
            axes[0, 0].set_title('Tiempo de Inferencia (ms)')
            axes[0, 0].set_ylabel('Tiempo (ms)')
        
        # Gráfico 2: Número de detecciones
        if pt_detections or onnx_detections:
            axes[0, 1].boxplot([pt_detections, onnx_detections], labels=['PT', 'ONNX'])
            axes[0, 1].set_title('Número de Detecciones')
            axes[0, 1].set_ylabel('Detecciones')
        
        # Gráfico 3: FPS
        pt_fps = [1000/t for t in pt_times] if pt_times else []
        onnx_fps = [1000/t for t in onnx_times] if onnx_times else []
        
        if pt_fps or onnx_fps:
            axes[0, 2].boxplot([pt_fps, onnx_fps], labels=['PT', 'ONNX'])
            axes[0, 2].set_title('FPS (Frames por Segundo)')
            axes[0, 2].set_ylabel('FPS')
        
        # Gráfico 4: Comparación de tiempos por imagen
        if pt_times and onnx_times:
            x = range(len(pt_times))
            axes[1, 0].plot(x, pt_times, 'b-', label='PT', marker='o')
            axes[1, 0].plot(x, onnx_times, 'r-', label='ONNX', marker='s')
            axes[1, 0].set_title('Tiempo por Imagen')
            axes[1, 0].set_xlabel('Imagen')
            axes[1, 0].set_ylabel('Tiempo (ms)')
            axes[1, 0].legend()
        
        # Gráfico 5: Estadísticas generales
        stats_data = []
        labels = []
        
        if pt_times:
            stats_data.append([np.mean(pt_times), np.std(pt_times), np.min(pt_times), np.max(pt_times)])
            labels.append('PT')
        
        if onnx_times:
            stats_data.append([np.mean(onnx_times), np.std(onnx_times), np.min(onnx_times), np.max(onnx_times)])
            labels.append('ONNX')
        
        if stats_data:
            x_pos = np.arange(len(labels))
            metrics = ['Media', 'Std Dev', 'Min', 'Max']
            
            bar_width = 0.2
            for i, metric in enumerate(metrics):
                values = [data[i] for data in stats_data]
                axes[1, 1].bar(x_pos + i * bar_width, values, bar_width, label=metric)
            
            axes[1, 1].set_title('Estadísticas de Tiempo')
            axes[1, 1].set_xlabel('Modelo')
            axes[1, 1].set_ylabel('Tiempo (ms)')
            axes[1, 1].set_xticks(x_pos + bar_width * 1.5)
            axes[1, 1].set_xticklabels(labels)
            axes[1, 1].legend()
        
        # Gráfico 6: Tabla de métricas
        if pt_times and onnx_times:
            metrics_table = [
                ['Métrica', 'PT', 'ONNX', 'Diferencia'],
                ['Tiempo Promedio (ms)', f'{np.mean(pt_times):.2f}', f'{np.mean(onnx_times):.2f}', f'{np.mean(onnx_times) - np.mean(pt_times):.2f}'],
                ['FPS Promedio', f'{np.mean(pt_fps):.2f}', f'{np.mean(onnx_fps):.2f}', f'{np.mean(onnx_fps) - np.mean(pt_fps):.2f}'],
                ['Detecciones Promedio', f'{np.mean(pt_detections):.1f}', f'{np.mean(onnx_detections):.1f}', f'{np.mean(onnx_detections) - np.mean(pt_detections):.1f}'],
                ['Tiempo Min (ms)', f'{np.min(pt_times):.2f}', f'{np.min(onnx_times):.2f}', f'{np.min(onnx_times) - np.min(pt_times):.2f}'],
                ['Tiempo Max (ms)', f'{np.max(pt_times):.2f}', f'{np.max(onnx_times):.2f}', f'{np.max(onnx_times) - np.max(pt_times):.2f}']
            ]
            
            axes[1, 2].axis('tight')
            axes[1, 2].axis('off')
            table = axes[1, 2].table(cellText=metrics_table[1:], colLabels=metrics_table[0], 
                                   cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)
            axes[1, 2].set_title('Tabla Comparativa')
        
        plt.tight_layout()
        
        # Mostrar en tkinter
        canvas = FigureCanvasTkAgg(fig, self.metrics_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def clear_metrics(self):
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
    
    # Métodos para pestaña de visualización
    def show_detections(self, event=None):
        if not self.image_selector.get():
            return
        
        selected_image = self.image_selector.get()
        
        # Encontrar la imagen seleccionada
        image_path = None
        for img_path in self.test_images:
            if os.path.basename(img_path) == selected_image:
                image_path = img_path
                break
        
        if not image_path:
            return
        
        # Limpiar canvas
        self.canvas.delete("all")
        
        # Cargar imagen original
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Crear figura para mostrar comparación
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        
        # Encontrar resultados para esta imagen
        pt_result = None
        onnx_result = None
        
        for result in self.results_pt:
            if result['image'] == image_path:
                pt_result = result
                break
        
        for result in self.results_onnx:
            if result['image'] == image_path:
                onnx_result = result
                break
        
        # Mostrar imagen con detecciones PT
        if pt_result and self.pt_model:
            img_pt = image.copy()
            if pt_result['results'][0].boxes is not None:
                boxes = pt_result['results'][0].boxes.xyxy.cpu().numpy()
                confidences = pt_result['results'][0].boxes.conf.cpu().numpy()
                classes = pt_result['results'][0].boxes.cls.cpu().numpy()
                
                for box, conf, cls in zip(boxes, confidences, classes):
                    x1, y1, x2, y2 = box.astype(int)
                    cv2.rectangle(img_pt, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(img_pt, f'{int(cls)}: {conf:.2f}', (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            axes[0].imshow(img_pt)
            axes[0].set_title(f'Modelo PT\nDetecciones: {pt_result["detections"]}, Tiempo: {pt_result["time"]:.2f}ms')
            axes[0].axis('off')
        else:
            axes[0].imshow(image)
            axes[0].set_title('Modelo PT - No disponible')
            axes[0].axis('off')
        
        # Mostrar imagen con detecciones ONNX
        if onnx_result and self.onnx_model:
            img_onnx = image.copy()
            if onnx_result['results'][0].boxes is not None:
                boxes = onnx_result['results'][0].boxes.xyxy.cpu().numpy()
                confidences = onnx_result['results'][0].boxes.conf.cpu().numpy()
                classes = onnx_result['results'][0].boxes.cls.cpu().numpy()
                
                for box, conf, cls in zip(boxes, confidences, classes):
                    x1, y1, x2, y2 = box.astype(int)
                    cv2.rectangle(img_onnx, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img_onnx, f'{int(cls)}: {conf:.2f}', (x1, y1-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            axes[1].imshow(img_onnx)
            axes[1].set_title(f'Modelo ONNX\nDetecciones: {onnx_result["detections"]}, Tiempo: {onnx_result["time"]:.2f}ms')
            axes[1].axis('off')
        else:
            axes[1].imshow(image)
            axes[1].set_title('Modelo ONNX - No disponible')
            axes[1].axis('off')
        
        plt.tight_layout()
        
        # Mostrar en canvas
        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas.draw()
        
        # Limpiar canvas anterior si existe
        for widget in self.canvas_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()
        
        canvas.get_tk_widget().pack(fill='both', expand=True)

def main():
    root = tk.Tk()
    app = YOLOConverterEvaluator(root)
    root.mainloop()

if __name__ == "__main__":
    main()