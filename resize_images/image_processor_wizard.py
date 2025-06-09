import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import os
import threading
from pathlib import Path

class ImageProcessorWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Processor Wizard")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Variables de configuración
        self.source_files = []
        self.source_folder = ""
        self.is_square = tk.BooleanVar()
        self.square_size = tk.StringVar(value="512")
        self.max_side_size = tk.StringVar(value="1024")
        self.min_side_size = tk.StringVar(value="768")
        self.vertical_size = tk.StringVar(value="1024")
        self.horizontal_size = tk.StringVar(value="768")
        self.resize_mode = tk.StringVar(value="max_min")  # max_min o vert_horiz
        self.fill_color = (0, 0, 0)  # Negro por defecto
        self.export_format = tk.StringVar(value="PNG")
        self.keep_names = tk.BooleanVar(value=True)
        self.custom_name = tk.StringVar(value="image")
        self.output_folder = ""

        self.current_step = 0
        self.total_steps = 7

        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Título y progreso
        self.title_label = ttk.Label(main_frame, text="", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(main_frame, length=500, mode='determinate')
        self.progress.pack(pady=(0, 20))

        # Frame de contenido
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill="both", expand=True)

        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side="bottom", fill="x", pady=(20, 0))

        self.prev_button = ttk.Button(button_frame, text="Anterior", command=self.prev_step)
        self.prev_button.pack(side="left")

        self.next_button = ttk.Button(button_frame, text="Siguiente", command=self.next_step)
        self.next_button.pack(side="right")

        self.show_step()

    def show_step(self):
        # Limpiar contenido anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Actualizar progreso
        self.progress['value'] = (self.current_step / self.total_steps) * 100

        if self.current_step == 0:
            self.show_source_selection()
        elif self.current_step == 1:
            self.show_resize_config()
        elif self.current_step == 2:
            self.show_color_selection()
        elif self.current_step == 3:
            self.show_format_selection()
        elif self.current_step == 4:
            self.show_naming_config()
        elif self.current_step == 5:
            self.show_output_selection()
        elif self.current_step == 6:
            self.show_processing()

        # Actualizar botones
        self.prev_button['state'] = 'normal' if self.current_step > 0 else 'disabled'
        if self.current_step == self.total_steps - 1:
            self.next_button['text'] = "Procesar"
        else:
            self.next_button['text'] = "Siguiente"

    def show_source_selection(self):
        self.title_label['text'] = "Paso 1: Selección de origen"

        ttk.Label(self.content_frame, text="Selecciona el origen de las imágenes:", font=("Arial", 12)).pack(pady=(0, 20))

        ttk.Button(self.content_frame, text="Seleccionar imágenes individuales",
                  command=self.select_files, width=30).pack(pady=5)

        ttk.Button(self.content_frame, text="Seleccionar carpeta",
                  command=self.select_folder, width=30).pack(pady=5)

        # Mostrar selección actual
        self.source_info = ttk.Label(self.content_frame, text="", foreground="blue")
        self.source_info.pack(pady=(20, 0))

        self.update_source_info()

    def show_resize_config(self):
        self.title_label['text'] = "Paso 2: Configuración de redimensionado"

        ttk.Checkbutton(self.content_frame, text="¿Formato cuadrado?",
                       variable=self.is_square, command=self.toggle_square).pack(pady=(0, 20))

        # Frame para configuración cuadrada
        self.square_frame = ttk.LabelFrame(self.content_frame, text="Configuración cuadrada", padding="10")
        self.square_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(self.square_frame, text="Tamaño:").pack(side="left")
        ttk.Entry(self.square_frame, textvariable=self.square_size, width=10).pack(side="left", padx=(5, 0))
        ttk.Label(self.square_frame, text="pixels").pack(side="left", padx=(5, 0))

        # Frame para configuración personalizada
        self.custom_frame = ttk.LabelFrame(self.content_frame, text="Configuración personalizada", padding="10")
        self.custom_frame.pack(fill="x", pady=(0, 10))

        ttk.Radiobutton(self.custom_frame, text="Por lado mayor/menor",
                       variable=self.resize_mode, value="max_min").pack(anchor="w")

        max_min_frame = ttk.Frame(self.custom_frame)
        max_min_frame.pack(fill="x", padx=(20, 0), pady=(5, 10))

        ttk.Label(max_min_frame, text="Lado mayor:").grid(row=0, column=0, sticky="w")
        ttk.Entry(max_min_frame, textvariable=self.max_side_size, width=10).grid(row=0, column=1, padx=(5, 5))
        ttk.Label(max_min_frame, text="Lado menor:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Entry(max_min_frame, textvariable=self.min_side_size, width=10).grid(row=0, column=3, padx=(5, 0))

        ttk.Radiobutton(self.custom_frame, text="Por vertical/horizontal",
                       variable=self.resize_mode, value="vert_horiz").pack(anchor="w")

        vert_horiz_frame = ttk.Frame(self.custom_frame)
        vert_horiz_frame.pack(fill="x", padx=(20, 0), pady=(5, 0))

        ttk.Label(vert_horiz_frame, text="Vertical:").grid(row=0, column=0, sticky="w")
        ttk.Entry(vert_horiz_frame, textvariable=self.vertical_size, width=10).grid(row=0, column=1, padx=(5, 5))
        ttk.Label(vert_horiz_frame, text="Horizontal:").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Entry(vert_horiz_frame, textvariable=self.horizontal_size, width=10).grid(row=0, column=3, padx=(5, 0))

        self.toggle_square()

    def show_color_selection(self):
        self.title_label['text'] = "Paso 3: Color de relleno"

        ttk.Label(self.content_frame, text="Selecciona el color para rellenar los espacios:",
                 font=("Arial", 12)).pack(pady=(0, 20))

        color_frame = ttk.Frame(self.content_frame)
        color_frame.pack()

        self.color_preview = tk.Canvas(color_frame, width=100, height=50, bg=f"#{self.fill_color[0]:02x}{self.fill_color[1]:02x}{self.fill_color[2]:02x}")
        self.color_preview.pack(side="left", padx=(0, 10))

        ttk.Button(color_frame, text="Cambiar color", command=self.choose_color).pack(side="left")

    def show_format_selection(self):
        self.title_label['text'] = "Paso 4: Formato de exportación"

        ttk.Label(self.content_frame, text="Selecciona el formato de salida:",
                 font=("Arial", 12)).pack(pady=(0, 20))

        formats = ["PNG", "JPEG", "BMP", "TIFF"]
        for fmt in formats:
            ttk.Radiobutton(self.content_frame, text=fmt, variable=self.export_format,
                           value=fmt).pack(anchor="w", pady=2)

    def show_naming_config(self):
        self.title_label['text'] = "Paso 5: Configuración de nombres"

        ttk.Label(self.content_frame, text="¿Cómo quieres nombrar las imágenes procesadas?",
                 font=("Arial", 12)).pack(pady=(0, 20))

        ttk.Radiobutton(self.content_frame, text="Mantener nombres originales y estructura de carpetas",
                       variable=self.keep_names, value=True).pack(anchor="w", pady=5)

        ttk.Radiobutton(self.content_frame, text="Usar formato personalizado con numeración (mantiene estructura)",
                       variable=self.keep_names, value=False).pack(anchor="w", pady=5)

        custom_frame = ttk.Frame(self.content_frame)
        custom_frame.pack(fill="x", padx=(20, 0), pady=(10, 0))

        ttk.Label(custom_frame, text="Nombre base:").pack(side="left")
        ttk.Entry(custom_frame, textvariable=self.custom_name, width=20).pack(side="left", padx=(5, 0))
        ttk.Label(custom_frame, text="(se agregará _001, _002, etc.)").pack(side="left", padx=(5, 0))

    def show_output_selection(self):
        self.title_label['text'] = "Paso 6: Carpeta de destino"

        ttk.Label(self.content_frame, text="¿Dónde quieres guardar las imágenes procesadas?",
                 font=("Arial", 12)).pack(pady=(0, 20))

        ttk.Button(self.content_frame, text="Seleccionar carpeta personalizada",
                  command=self.select_output_folder, width=30).pack(pady=5)

        ttk.Label(self.content_frame, text="(Si no seleccionas nada, se creará una carpeta 'out' junto al origen)",
                 font=("Arial", 10), foreground="gray").pack(pady=(10, 0))

        self.output_info = ttk.Label(self.content_frame, text="", foreground="blue")
        self.output_info.pack(pady=(20, 0))

        self.update_output_info()

    def show_processing(self):
        self.title_label['text'] = "Paso 7: Procesando imágenes"

        self.processing_progress = ttk.Progressbar(self.content_frame, length=400, mode='determinate')
        self.processing_progress.pack(pady=(50, 20))

        self.processing_label = ttk.Label(self.content_frame, text="Preparando...")
        self.processing_label.pack()

        self.next_button['state'] = 'disabled'
        self.prev_button['state'] = 'disabled'

        # Iniciar procesamiento en hilo separado
        threading.Thread(target=self.process_images, daemon=True).start()

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif")]
        )
        if files:
            self.source_files = list(files)
            self.source_folder = ""
            self.update_source_info()

    def select_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta con imágenes")
        if folder:
            self.source_folder = folder
            self.source_files = []
            self.update_source_info()

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if folder:
            self.output_folder = folder
            self.update_output_info()

    def choose_color(self):
        color = colorchooser.askcolor(title="Seleccionar color de relleno")
        if color[0]:
            self.fill_color = tuple(int(c) for c in color[0])
            self.color_preview.config(bg=f"#{self.fill_color[0]:02x}{self.fill_color[1]:02x}{self.fill_color[2]:02x}")

    def toggle_square(self):
        if self.is_square.get():
            self.square_frame.pack(fill="x", pady=(0, 10))
            self.custom_frame.pack_forget()
        else:
            self.square_frame.pack_forget()
            self.custom_frame.pack(fill="x", pady=(0, 10))

    def update_source_info(self):
        if self.source_files:
            self.source_info['text'] = f"Seleccionadas {len(self.source_files)} imágenes"
        elif self.source_folder:
            # Contar imágenes en la carpeta
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}
            count = 0
            for root, dirs, files in os.walk(self.source_folder):
                count += sum(1 for f in files if Path(f).suffix.lower() in image_extensions)
            self.source_info['text'] = f"Carpeta seleccionada: {count} imágenes encontradas"
        else:
            self.source_info['text'] = "No se ha seleccionado origen"

    def update_output_info(self):
        if self.output_folder:
            self.output_info['text'] = f"Destino: {self.output_folder}/out"
        else:
            self.output_info['text'] = "Se creará carpeta 'out' junto al origen"

    def get_all_images(self):
        """Obtiene todas las imágenes a procesar"""
        images = []
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif'}

        if self.source_files:
            images = self.source_files
        elif self.source_folder:
            for root, dirs, files in os.walk(self.source_folder):
                for file in files:
                    if Path(file).suffix.lower() in image_extensions:
                        images.append(os.path.join(root, file))

        return images

    def calculate_new_size(self, original_size):
        """Calcula el nuevo tamaño manteniendo proporción"""
        width, height = original_size

        if self.is_square.get():
            size = int(self.square_size.get())
            return (size, size)

        if self.resize_mode.get() == "max_min":
            max_size = int(self.max_side_size.get())
            min_size = int(self.min_side_size.get())

            if width > height:
                return (max_size, min_size)
            else:
                return (min_size, max_size)
        else:  # vert_horiz
            vert_size = int(self.vertical_size.get())
            horiz_size = int(self.horizontal_size.get())
            return (horiz_size, vert_size)

    def process_single_image(self, image_path, output_path):
        """Procesa una sola imagen"""
        with Image.open(image_path) as img:
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Calcular nuevo tamaño
            target_size = self.calculate_new_size(img.size)

            # Calcular el escalado manteniendo proporción
            scale = min(target_size[0] / img.size[0], target_size[1] / img.size[1])
            new_size = (int(img.size[0] * scale), int(img.size[1] * scale))

            # Redimensionar imagen
            img_resized = img.resize(new_size, Image.Resampling.LANCZOS)

            # Crear imagen con el tamaño objetivo y color de relleno
            final_img = Image.new('RGB', target_size, self.fill_color)

            # Centrar la imagen redimensionada
            x = (target_size[0] - new_size[0]) // 2
            y = (target_size[1] - new_size[1]) // 2
            final_img.paste(img_resized, (x, y))

            # Guardar
            final_img.save(output_path, format=self.export_format.get())

    def process_images(self):
        try:
            images = self.get_all_images()

            if not images:
                messagebox.showerror("Error", "No se encontraron imágenes para procesar")
                return

            # Crear carpeta de salida
            if self.output_folder:
                output_dir = os.path.join(self.output_folder, "out")
            else:
                if self.source_files:
                    base_dir = os.path.dirname(self.source_files[0])
                else:
                    base_dir = self.source_folder
                output_dir = os.path.join(base_dir, "out")

            os.makedirs(output_dir, exist_ok=True)

            total_images = len(images)
            extension = f".{self.export_format.get().lower()}"

            # Contador global para numeración personalizada
            global_counter = 1

            for i, image_path in enumerate(images):
                # Actualizar progreso
                progress = (i / total_images) * 100
                self.processing_progress['value'] = progress
                self.processing_label['text'] = f"Procesando {i+1}/{total_images}: {os.path.basename(image_path)}"
                self.root.update()

                # Determinar estructura de carpetas y nombre de salida
                if self.source_files:
                    # Para archivos individuales, todo va directo a out/
                    if self.keep_names.get():
                        original_name = Path(image_path).stem
                        output_name = f"{original_name}{extension}"
                    else:
                        output_name = f"{self.custom_name.get()}_{global_counter:03d}{extension}"
                        global_counter += 1

                    output_path = os.path.join(output_dir, output_name)

                else:
                    # Para carpeta, mantener estructura relativa
                    rel_path = os.path.relpath(image_path, self.source_folder)
                    rel_dir = os.path.dirname(rel_path)

                    # Crear estructura de carpetas en destino
                    if rel_dir:
                        target_dir = os.path.join(output_dir, rel_dir)
                        os.makedirs(target_dir, exist_ok=True)
                    else:
                        target_dir = output_dir

                    # Determinar nombre del archivo
                    if self.keep_names.get():
                        original_name = Path(image_path).stem
                        output_name = f"{original_name}{extension}"
                    else:
                        output_name = f"{self.custom_name.get()}_{global_counter:03d}{extension}"
                        global_counter += 1

                    output_path = os.path.join(target_dir, output_name)

                # Procesar imagen
                self.process_single_image(image_path, output_path)

            # Completado
            self.processing_progress['value'] = 100
            self.processing_label['text'] = f"¡Completado! {total_images} imágenes procesadas"

            messagebox.showinfo("Completado", f"Se procesaron {total_images} imágenes exitosamente.\nGuardadas en: {output_dir}")

            # Mostrar opción para procesar más imágenes
            self.show_completion_options()

        except Exception as e:
            messagebox.showerror("Error", f"Error durante el procesamiento: {str(e)}")
            self.show_completion_options()

    def validate_step(self):
        """Valida si se puede avanzar al siguiente paso"""
        if self.current_step == 0:
            return bool(self.source_files or self.source_folder)
        elif self.current_step == 1:
            try:
                if self.is_square.get():
                    int(self.square_size.get())
                else:
                    if self.resize_mode.get() == "max_min":
                        int(self.max_side_size.get())
                        int(self.min_side_size.get())
                    else:
                        int(self.vertical_size.get())
                        int(self.horizontal_size.get())
                return True
            except ValueError:
                return False
        return True

    def next_step(self):
        if not self.validate_step():
            if self.current_step == 0:
                messagebox.showwarning("Advertencia", "Debe seleccionar imágenes o una carpeta")
            elif self.current_step == 1:
                messagebox.showwarning("Advertencia", "Debe ingresar valores numéricos válidos")
            return

        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.show_step()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()

    def show_completion_options(self):
        """Muestra opciones después del procesamiento"""
        # Limpiar el contenido actual
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.title_label['text'] = "¡Procesamiento completado!"

        ttk.Label(self.content_frame, text="¿Qué deseas hacer ahora?",
                 font=("Arial", 12)).pack(pady=(50, 30))

        ttk.Button(self.content_frame, text="Procesar otras imágenes",
                  command=self.restart_wizard, width=25).pack(pady=10)

        ttk.Button(self.content_frame, text="Salir",
                  command=self.root.quit, width=25).pack(pady=5)

        # Ocultar botones de navegación
        self.next_button.pack_forget()
        self.prev_button.pack_forget()

    def restart_wizard(self):
        """Reinicia el wizard manteniendo algunas configuraciones"""
        # Limpiar solo la selección de origen y output
        self.source_files = []
        self.source_folder = ""
        self.output_folder = ""

        # Mantener configuraciones de formato, color, naming, etc.

        # Volver al paso 1
        self.current_step = 0

        # Restaurar botones de navegación
        self.next_button.pack(side="right")
        self.prev_button.pack(side="left")

        # Reactivar botones
        self.next_button['state'] = 'normal'
        self.prev_button['state'] = 'normal'

        self.show_step()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageProcessorWizard()
    app.run()
