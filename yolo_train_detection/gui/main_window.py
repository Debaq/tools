"""
Ventana principal de la aplicación YOLO Fine-tuning Tool
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.yolo_config import YOLOConfig
from gui.wizard_pages.page1_model import ModelSelectionPage
from gui.wizard_pages.page2_training import TrainingConfigPage
from gui.wizard_pages.page3_files import FilesConfigPage
from gui.wizard_pages.page4_summary import SummaryPage

class YOLOFineTuningTool:
    """Aplicación principal"""

    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Fine-tuning Tool")
        self.root.geometry("900x700")

        # Configuración
        self.config = YOLOConfig()

        # Estado del wizard
        self.current_page = 0
        self.training_process = None
        self.training_paused = False

        # Setup logging
        self.setup_logging()

        # Crear páginas del wizard
        self.setup_pages()

        # Crear interfaz
        self.create_main_interface()

    def setup_logging(self):
        """Configurar sistema de logging"""
        log_dir = "training_logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"yolo_training_{timestamp}.log")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.log_file = log_file

    def setup_pages(self):
        """Configurar páginas del wizard"""
        # Placeholder para content_frame - se creará en create_main_interface
        self.content_frame = None

        # Lista de clases de páginas
        self.page_classes = [
            ModelSelectionPage,
            TrainingConfigPage,
            FilesConfigPage,
            SummaryPage
        ]

        # Instancias de páginas (se crearán después)
        self.pages = []

    def create_main_interface(self):
        """Crear interfaz principal"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar peso de filas y columnas
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Título
        self.title_label = ttk.Label(self.main_frame, text="YOLO Fine-tuning Wizard",
                                    font=('Arial', 16, 'bold'))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Frame para contenido de páginas
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # Configurar peso del content_frame
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Frame para botones
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Botones de navegación
        self.prev_btn = ttk.Button(self.button_frame, text="< Anterior",
                                  command=self.prev_page, state='disabled')
        self.prev_btn.pack(side=tk.LEFT)

        self.next_btn = ttk.Button(self.button_frame, text="Siguiente >",
                                  command=self.next_page)
        self.next_btn.pack(side=tk.RIGHT)

        # Crear instancias de páginas ahora que content_frame existe
        self.create_page_instances()

        # Mostrar primera página
        self.show_page(0)

    def create_page_instances(self):
        """Crear instancias de las páginas del wizard"""
        self.pages = []

        for PageClass in self.page_classes:
            page_instance = PageClass(self.content_frame, self.config, self.add_tooltip)
            self.pages.append(page_instance)

    def show_page(self, page_num):
        """Mostrar página específica del wizard"""
        self.current_page = page_num

        # Crear la página
        self.pages[page_num].create_page()

        # Actualizar botones
        self.prev_btn.config(state='normal' if page_num > 0 else 'disabled')

        if page_num < len(self.pages) - 1:
            self.next_btn.config(text="Siguiente >", command=self.next_page)
        else:
            self.next_btn.config(text="Iniciar Entrenamiento", command=self.start_training)

    def next_page(self):
        """Ir a la siguiente página"""
        # Validar página actual
        is_valid, error_message = self.pages[self.current_page].validate_page()

        if not is_valid:
            messagebox.showerror("Error de Validación", error_message)
            return

        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)

    def prev_page(self):
        """Ir a la página anterior"""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def start_training(self):
        """Iniciar proceso de entrenamiento"""
        # Validar página final
        is_valid, error_message = self.pages[self.current_page].validate_page()

        if not is_valid:
            messagebox.showerror("Error de Validacion", error_message)
            return

        # Crear ventana de entrenamiento
        self.create_training_window()

        # Iniciar entrenamiento en hilo separado
        import threading
        training_thread = threading.Thread(target=self.run_training)
        training_thread.daemon = True
        training_thread.start()

    def add_tooltip(self, widget, text):
        """Agregar tooltip mejorado a un widget"""
        def on_enter(event):
            if hasattr(widget, 'tooltip_window') and widget.tooltip_window:
                return

            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 25

            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.configure(bg='lightyellow')

            label = ttk.Label(tooltip, text=text, background="lightyellow",
                             relief="solid", borderwidth=1, wraplength=300,
                             justify='left', font=('Arial', 9))
            label.pack()

            widget.tooltip_window = tooltip

            # Auto-cerrar después de 5 segundos
            widget.after(5000, lambda: close_tooltip())

        def on_leave(event):
            close_tooltip()

        def on_click(event):
            close_tooltip()

        def close_tooltip():
            if hasattr(widget, 'tooltip_window') and widget.tooltip_window:
                try:
                    widget.tooltip_window.destroy()
                except:
                    pass
                finally:
                    widget.tooltip_window = None

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", on_click)

    def create_training_window(self):
        """Crear ventana de entrenamiento con consola en tiempo real"""
        self.training_window = tk.Toplevel(self.root)
        self.training_window.title("Entrenamiento YOLO en Progreso")
        self.training_window.geometry("1000x700")
        self.training_window.transient(self.root)

        # Frame principal
        main_frame = ttk.Frame(self.training_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(main_frame, text="Entrenamiento YOLO",
                 font=('Arial', 16, 'bold')).pack(pady=10)

        # Frame de información de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuracion", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        config_text = f"""Modelo: {self.config.get('pretrained_model').get()}
Tarea: {self.config.get('task_type').get()}
Epochs: {self.config.get('epochs').get()}
Batch Size: {self.config.get('batch_size').get()}
GPU: {'Si' if self.config.get('use_gpu').get() else 'No'}
Dataset: {self.config.get('dataset_path').get()}"""

        ttk.Label(config_frame, text=config_text, justify=tk.LEFT, font=('Courier', 9)).pack(anchor=tk.W)

        # Frame de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # Botones de control
        self.pause_btn = ttk.Button(control_frame, text="Pausar",
                                   command=self.toggle_pause, state='disabled')
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="Detener",
                                  command=self.stop_training, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Estado y progreso
        self.progress_var = tk.StringVar(value="Preparando entrenamiento...")
        self.progress_label = ttk.Label(control_frame, textvariable=self.progress_var, font=('Arial', 10, 'bold'))
        self.progress_label.pack(side=tk.RIGHT, padx=10)

        # Barra de progreso
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        ttk.Label(progress_frame, text="Progreso:").pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.epoch_label = ttk.Label(progress_frame, text="Epoch 0/0")
        self.epoch_label.pack(side=tk.RIGHT)

        # Consola de entrenamiento
        console_frame = ttk.LabelFrame(main_frame, text="Log de Entrenamiento", padding="5")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Text widget con scroll para la consola
        console_text_frame = tk.Frame(console_frame)
        console_text_frame.pack(fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(console_text_frame, height=20, bg='black', fg='green',
                                   font=('Courier', 9), wrap=tk.WORD)
        console_scrollbar = ttk.Scrollbar(console_text_frame, orient="vertical", command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=console_scrollbar.set)

        self.console_text.pack(side="left", fill="both", expand=True)
        console_scrollbar.pack(side="right", fill="y")

        # Frame de estadísticas en tiempo real
        stats_frame = ttk.LabelFrame(main_frame, text="Estadisticas", padding="5")
        stats_frame.pack(fill=tk.X, pady=5)

        self.stats_text = ttk.Label(stats_frame, text="Esperando inicio del entrenamiento...",
                                   font=('Courier', 9))
        self.stats_text.pack(anchor=tk.W)

        # Variables de control
        self.training_process = None
        self.training_paused = False

    def run_training(self):
        """Ejecutar entrenamiento YOLO en hilo separado"""
        import subprocess
        import sys
        from datetime import datetime

        try:
            self.log_to_console("Iniciando entrenamiento YOLO...")
            self.log_to_console(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.update_progress("Configurando entrenamiento...")

            # Construir comando de entrenamiento
            cmd = self.build_training_command()
            self.log_to_console(f"Comando de entrenamiento generado")
            self.log_to_console("-" * 50)

            # Ejecutar entrenamiento
            self.training_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Habilitar botones de control
            self.pause_btn.config(state='normal')
            self.stop_btn.config(state='normal')
            self.update_progress("Entrenamiento en progreso...")

            # Variables para tracking de progreso
            current_epoch = 0
            total_epochs = self.config.get('epochs').get()

            # Leer output en tiempo real
            for line in iter(self.training_process.stdout.readline, ''):
                if self.training_process.poll() is not None:
                    break

                line = line.strip()
                if line:
                    self.log_to_console(line)

                    # Extraer información de progreso
                    if 'Epoch' in line:
                        try:
                            # Buscar patrones como "Epoch 5/100" o "Epoch: 5"
                            import re
                            epoch_match = re.search(r'Epoch[:\s]*(\d+)(?:/(\d+))?', line)
                            if epoch_match:
                                current_epoch = int(epoch_match.group(1))
                                if epoch_match.group(2):
                                    total_epochs = int(epoch_match.group(2))

                                progress = (current_epoch / total_epochs) * 100 if total_epochs > 0 else 0
                                self.progress_bar.config(value=progress)
                                self.epoch_label.config(text=f"Epoch {current_epoch}/{total_epochs}")
                                self.update_progress(f"Epoch {current_epoch}/{total_epochs}")
                        except:
                            pass

                    # Extraer métricas de entrenamiento
                    if any(metric in line.lower() for metric in ['loss', 'map', 'precision', 'recall']):
                        self.update_stats(line)

            # Entrenamiento completado
            return_code = self.training_process.wait()

            if return_code == 0:
                self.log_to_console("-" * 50)
                self.log_to_console("ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
                self.log_to_console(f"Hora de finalizacion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.update_progress("Entrenamiento completado")
                self.progress_bar.config(value=100)

                # Mostrar ventana de resultados
                self.root.after(1000, self.show_results)
            else:
                self.log_to_console(f"Entrenamiento terminado con codigo de error: {return_code}")
                self.update_progress("Entrenamiento detenido")

        except Exception as e:
            self.log_to_console(f"ERROR durante el entrenamiento: {str(e)}")
            self.logger.error(f"Training error: {str(e)}")
        finally:
            # Deshabilitar botones
            if hasattr(self, 'pause_btn'):
                self.pause_btn.config(state='disabled')
            if hasattr(self, 'stop_btn'):
                self.stop_btn.config(state='disabled')

    def build_training_command(self):
        """Construir comando de entrenamiento YOLO"""
        import sys

        # Script de entrenamiento Python
        script = f'''
import sys
import os
from datetime import datetime

try:
    from ultralytics import YOLO

    print("Cargando modelo YOLO...")
    model_source = "{self.config.get('model_source').get()}"
    model_name = "{self.config.get('pretrained_model').get()}"

    if model_source == "pretrained":
        print(f"Cargando modelo pre-entrenado: {{model_name}}")
        model = YOLO(model_name)
    elif model_source == "local":
        model_path = "{self.config.get('local_model_path').get()}"
        print(f"Cargando modelo local: {{model_path}}")
        model = YOLO(model_path)
    elif model_source == "url":
        model_url = "{self.config.get('custom_url').get()}"
        print(f"Cargando modelo desde URL: {{model_url}}")
        model = YOLO(model_url)
    else:
        yolo_version = "{self.config.get('yolo_version').get()}"
        print(f"Entrenando desde cero con arquitectura: {{yolo_version}}")
        model = YOLO(f"{{yolo_version}}n.yaml")

    print("Modelo cargado exitosamente!")
    print(f"Iniciando entrenamiento...")
    print(f"Dataset: {self.config.get('yaml_path').get()}")
    print(f"Epochs: {self.config.get('epochs').get()}")
    print(f"Batch size: {self.config.get('batch_size').get()}")
    print(f"Device: {'cuda' if self.config.get('use_gpu').get() else 'cpu'}")
    print("-" * 50)

    # Parámetros de entrenamiento
    results = model.train(
        data="{self.config.get('yaml_path').get()}",
        epochs={self.config.get('epochs').get()},
        batch={self.config.get('batch_size').get()},
        imgsz={self.config.get('img_size').get()},
        lr0={self.config.get('learning_rate').get()},
        patience={self.config.get('patience').get()},
        save_period={self.config.get('save_period').get()},
        project="{self.config.get('output_path').get()}",
        name="yolo_training",
        device="{'cuda' if self.config.get('use_gpu').get() else 'cpu'}",
        verbose=True,
        plots=True,
        save=True
    )

    print("-" * 50)
    print("ENTRENAMIENTO COMPLETADO!")
    print(f"Resultados guardados en: {{results.save_dir}}")
    print(f"Mejor modelo: {{results.save_dir}}/weights/best.pt")

except ImportError as e:
    print(f"ERROR: ultralytics no esta instalado - {{str(e)}}")
    print("Instalar con: pip install ultralytics")
    sys.exit(1)
except Exception as e:
    print(f"ERROR durante el entrenamiento: {{str(e)}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

        cmd = [sys.executable, "-c", script]
        return cmd

    def log_to_console(self, message):
        """Agregar mensaje a la consola con timestamp"""
        if hasattr(self, 'console_text'):
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"

            self.console_text.insert(tk.END, formatted_message)
            self.console_text.see(tk.END)
            self.console_text.update()

            # También guardar en log file
            self.logger.info(message)

    def update_progress(self, message):
        """Actualizar mensaje de progreso"""
        if hasattr(self, 'progress_var'):
            self.progress_var.set(message)

    def update_stats(self, line):
        """Actualizar estadísticas de entrenamiento"""
        if hasattr(self, 'stats_text'):
            # Limpiar y mostrar última línea de métricas
            clean_line = line.strip()
            if len(clean_line) > 100:
                clean_line = clean_line[:100] + "..."
            self.stats_text.config(text=f"Ultima metrica: {clean_line}")

    def toggle_pause(self):
        """Pausar/reanudar entrenamiento"""
        if self.training_process and self.training_process.poll() is None:
            if not self.training_paused:
                messagebox.showinfo("Pausa", "La funcionalidad de pausa no esta disponible durante el entrenamiento YOLO")
            else:
                messagebox.showinfo("Reanudar", "La funcionalidad de pausa no esta disponible durante el entrenamiento YOLO")

    def stop_training(self):
        """Detener entrenamiento"""
        if self.training_process and self.training_process.poll() is None:
            result = messagebox.askyesno("Confirmar",
                                       "Estas seguro de que quieres detener el entrenamiento?\n" +
                                       "Se perdera el progreso no guardado.")
            if result:
                self.training_process.terminate()
                self.log_to_console("Entrenamiento detenido por el usuario")
                self.update_progress("Entrenamiento detenido")

    def show_results(self):
        """Mostrar ventana de resultados del entrenamiento"""
        messagebox.showinfo("Resultados", "Funcionalidad de resultados en desarrollo...\n" +
                          "El modelo entrenado se encuentra en la carpeta de salida especificada.")
