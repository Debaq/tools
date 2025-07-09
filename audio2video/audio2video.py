import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
from PIL import Image, ImageTk
import os

class AudioVideoGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Video - Audio + Imagen")
        self.root.geometry("600x500")
        
        self.audio_path = ""
        self.image_path = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Selección de archivos
        ttk.Label(main_frame, text="Seleccionar Archivos:", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        # Audio
        ttk.Label(main_frame, text="Audio:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.audio_label = ttk.Label(main_frame, text="No seleccionado", foreground="gray")
        self.audio_label.grid(row=1, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="Seleccionar", command=self.select_audio).grid(row=1, column=2, padx=(10, 0))
        
        # Imagen
        ttk.Label(main_frame, text="Imagen:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.image_label = ttk.Label(main_frame, text="No seleccionado", foreground="gray")
        self.image_label.grid(row=2, column=1, sticky=tk.W)
        ttk.Button(main_frame, text="Seleccionar", command=self.select_image).grid(row=2, column=2, padx=(10, 0))
        
        # Configuración de video
        ttk.Separator(main_frame, orient='horizontal').grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        ttk.Label(main_frame, text="Configuración del Video:", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        # Resolución
        ttk.Label(main_frame, text="Resolución:").grid(row=5, column=0, sticky=tk.W)
        self.resolution_var = tk.StringVar(value="1920x1080")
        resolution_combo = ttk.Combobox(main_frame, textvariable=self.resolution_var, 
                                      values=["1920x1080", "1280x720", "854x480", "640x360"])
        resolution_combo.grid(row=5, column=1, sticky=tk.W, padx=(10, 0))
        
        # Modo de imagen
        ttk.Label(main_frame, text="Ajuste de imagen:").grid(row=6, column=0, sticky=tk.W, pady=(10, 0))
        self.image_mode_var = tk.StringVar(value="centrar")
        
        ttk.Radiobutton(main_frame, text="Estirar para llenar", variable=self.image_mode_var, 
                       value="estirar").grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(main_frame, text="Agrandar manteniendo proporción", variable=self.image_mode_var, 
                       value="agrandar").grid(row=8, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(main_frame, text="Centrar y rellenar con negro", variable=self.image_mode_var, 
                       value="centrar").grid(row=9, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))
        
        # Botón generar
        ttk.Separator(main_frame, orient='horizontal').grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        generate_btn = ttk.Button(main_frame, text="Generar Video", command=self.generate_video)
        generate_btn.grid(row=11, column=0, columnspan=3, pady=10)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Listo para generar video")
        self.status_label.grid(row=13, column=0, columnspan=3)
    
    def select_audio(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=[
                ("Archivos de audio", "*.mp3 *.wav *.aac *.flac *.ogg"),
                ("Todos los archivos", "*.*")
            ]
        )
        if file_path:
            self.audio_path = file_path
            self.audio_label.config(text=os.path.basename(file_path), foreground="black")
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("Todos los archivos", "*.*")
            ]
        )
        if file_path:
            self.image_path = file_path
            self.image_label.config(text=os.path.basename(file_path), foreground="black")
    
    def process_image(self, image_path, target_width, target_height, mode):
        # Cargar imagen
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        
        if mode == "estirar":
            # Estirar la imagen para llenar toda la pantalla
            processed_img = cv2.resize(img, (target_width, target_height))
        
        elif mode == "agrandar":
            # Agrandar manteniendo proporción (crop si es necesario)
            scale = max(target_width / w, target_height / h)
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(img, (new_w, new_h))
            
            # Recortar al centro si es más grande
            start_x = (new_w - target_width) // 2
            start_y = (new_h - target_height) // 2
            processed_img = resized[start_y:start_y + target_height, start_x:start_x + target_width]
        
        else:  # centrar
            # Centrar y rellenar con negro
            scale = min(target_width / w, target_height / h)
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(img, (new_w, new_h))
            
            # Crear imagen negra del tamaño objetivo
            processed_img = np.zeros((target_height, target_width, 3), dtype=np.uint8)
            
            # Centrar la imagen redimensionada
            start_x = (target_width - new_w) // 2
            start_y = (target_height - new_h) // 2
            processed_img[start_y:start_y + new_h, start_x:start_x + new_w] = resized
        
        return processed_img
    
    def generate_video(self):
        if not self.audio_path or not self.image_path:
            messagebox.showerror("Error", "Por favor selecciona tanto el audio como la imagen")
            return
        
        try:
            # Obtener configuración
            resolution = self.resolution_var.get().split('x')
            width, height = int(resolution[0]), int(resolution[1])
            mode = self.image_mode_var.get()
            
            # Solicitar ubicación de guardado
            output_path = filedialog.asksaveasfilename(
                title="Guardar video como...",
                defaultextension=".mp4",
                filetypes=[("Video MP4", "*.mp4")]
            )
            
            if not output_path:
                return
            
            # Iniciar progreso
            self.progress.start()
            self.status_label.config(text="Procesando...")
            self.root.update()
            
            # Cargar audio para obtener duración
            audio_clip = AudioFileClip(self.audio_path)
            duration = audio_clip.duration
            fps = 30
            
            # Procesar imagen
            processed_image = self.process_image(self.image_path, width, height, mode)
            
            # Crear video temporal
            temp_video = "temp_video.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
            
            # Escribir frames (imagen estática)
            total_frames = int(duration * fps)
            for i in range(total_frames):
                out.write(processed_image)
                if i % 30 == 0:  # Actualizar cada segundo
                    self.status_label.config(text=f"Generando frames: {i}/{total_frames}")
                    self.root.update()
            
            out.release()
            
            # Combinar video con audio usando moviepy
            self.status_label.config(text="Combinando audio y video...")
            self.root.update()
            
            video_clip = VideoFileClip(temp_video)
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Limpiar archivos temporales
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            os.remove(temp_video)
            
            # Finalizar
            self.progress.stop()
            self.status_label.config(text="¡Video generado exitosamente!")
            messagebox.showinfo("Éxito", f"Video guardado en:\n{output_path}")
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="Error al generar video")
            messagebox.showerror("Error", f"Error al generar el video:\n{str(e)}")

def main():
    root = tk.Tk()
    app = AudioVideoGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()