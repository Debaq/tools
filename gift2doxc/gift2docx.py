import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import random
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
import os
import collections

class GiftToDocxConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Convertidor de GIFT a DOCX")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Variables
        self.gift_files = []  # Lista de archivos seleccionados
        self.output_dir = tk.StringVar()
        self.current_step = 0
        self.questions = []
        self.answer_keys = {}
        self.selected_question_index = tk.IntVar(value=0)

        # Crear frames para cada paso
        self.frames = []
        for _ in range(4):
            frame = ttk.Frame(self.root, padding="10")
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames.append(frame)

        # Paso 1: Seleccionar archivos GIFT
        self.setup_step1()

        # Paso 2: Opciones de configuración
        self.setup_step2()

        # Paso 3: Vista previa interactiva
        self.setup_step3()

        # Paso 4: Resumen y finalización
        self.setup_step4()

        # Configurar los botones de navegación
        self.setup_navigation()

        # Mostrar el primer paso
        self.show_step(0)

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def setup_step1(self):
        frame = self.frames[0]

        # Título
        ttk.Label(frame, text="Paso 1: Seleccionar archivos GIFT", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=10, sticky="w")

        # Instrucciones
        ttk.Label(frame, text="Seleccione uno o varios archivos en formato GIFT:", wraplength=500).grid(row=1, column=0, columnspan=3, pady=10, sticky="w")

        # Lista de archivos seleccionados
        ttk.Label(frame, text="Archivos seleccionados:").grid(row=2, column=0, sticky="w", padx=5)

        self.files_listbox = tk.Listbox(frame, height=6)
        self.files_listbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Scrollbar para la lista
        files_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.files_listbox.yview)
        files_scrollbar.grid(row=3, column=2, sticky="ns", pady=5)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)

        # Botones para manejo de archivos
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")

        ttk.Button(buttons_frame, text="Agregar archivos...", command=self.add_gift_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Quitar seleccionado", command=self.remove_selected_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Limpiar todo", command=self.clear_all_files).pack(side=tk.LEFT, padx=5)

        # Configurar grid
        frame.columnconfigure(0, weight=1)

    def setup_step2(self):
        frame = self.frames[1]

        # Título
        ttk.Label(frame, text="Paso 2: Opciones de configuración", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        # Directorio de salida
        ttk.Label(frame, text="Directorio para guardar los archivos de salida:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(frame, textvariable=self.output_dir, width=50).grid(row=2, column=0, padx=5, pady=5, sticky="we")
        ttk.Button(frame, text="Examinar...", command=self.browse_output_dir).grid(row=2, column=1, padx=5, pady=5)

        # Opciones de formato
        ttk.Label(frame, text="Opciones de formato:").grid(row=3, column=0, columnspan=2, padx=5, pady=10, sticky="w")

        # Orden de preguntas
        ttk.Label(frame, text="Orden de las preguntas:").grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.question_order = tk.StringVar(value="por_archivos")
        ttk.Radiobutton(frame, text="Mantener orden por archivos", variable=self.question_order, value="por_archivos").grid(row=5, column=0, padx=40, pady=2, sticky="w")
        ttk.Radiobutton(frame, text="Aleatorio (mezclar todas)", variable=self.question_order, value="aleatorio").grid(row=6, column=0, padx=40, pady=2, sticky="w")

        # Opciones de respuestas
        self.randomize_options = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Aleatorizar opciones de respuesta", variable=self.randomize_options).grid(row=7, column=0, padx=20, pady=5, sticky="w")

        # Umbral de detección de problemas
        ttk.Label(frame, text="Detección de problemas:").grid(row=8, column=0, padx=20, pady=(10,5), sticky="w")
        umbral_frame = ttk.Frame(frame)
        umbral_frame.grid(row=9, column=0, padx=40, pady=2, sticky="w")

        ttk.Label(umbral_frame, text="Umbral diferencia de caracteres:").pack(side=tk.LEFT)
        self.threshold_var = tk.IntVar(value=10)
        threshold_spinbox = tk.Spinbox(umbral_frame, from_=5, to=50, width=5, textvariable=self.threshold_var)
        threshold_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(umbral_frame, text="caracteres").pack(side=tk.LEFT)

        # Codificación de archivos
        ttk.Label(frame, text="Codificación de archivos:").grid(row=10, column=0, padx=20, pady=(10,5), sticky="w")
        self.encoding_var = tk.StringVar(value="auto")
        encodings_frame = ttk.Frame(frame)
        encodings_frame.grid(row=11, column=0, padx=40, pady=2, sticky="w")

        ttk.Radiobutton(encodings_frame, text="Detectar automáticamente", variable=self.encoding_var, value="auto").pack(anchor="w")
        ttk.Radiobutton(encodings_frame, text="UTF-8", variable=self.encoding_var, value="utf-8").pack(anchor="w")
        ttk.Radiobutton(encodings_frame, text="Latin-1 (ISO-8859-1)", variable=self.encoding_var, value="latin-1").pack(anchor="w")
        ttk.Radiobutton(encodings_frame, text="Windows-1252", variable=self.encoding_var, value="cp1252").pack(anchor="w")

        # Configurar grid
        frame.columnconfigure(0, weight=1)

    def setup_step3(self):
        frame = self.frames[2]

        # Título
        ttk.Label(frame, text="Paso 3: Vista previa y edición", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        # Frame principal con dos paneles
        main_frame = ttk.Frame(frame)
        main_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)

        # Panel izquierdo: Lista de preguntas
        left_panel = ttk.LabelFrame(main_frame, text="Lista de preguntas", padding="5")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)

        # Listbox para preguntas con scrollbar
        self.questions_listbox = tk.Listbox(left_panel, height=20)
        self.questions_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.questions_listbox.bind("<<ListboxSelect>>", self.on_question_select)

        questions_scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=self.questions_listbox.yview)
        questions_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)
        self.questions_listbox.configure(yscrollcommand=questions_scrollbar.set)

        # Panel derecho: Editor de pregunta
        right_panel = ttk.LabelFrame(main_frame, text="Editor de pregunta", padding="5")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)

        # Información de la pregunta actual
        self.question_info_label = ttk.Label(right_panel, text="Seleccione una pregunta para editar", font=("Arial", 10, "bold"))
        self.question_info_label.grid(row=0, column=0, sticky="w", pady=5)

        # Frame scrollable para el editor
        self.editor_canvas = tk.Canvas(right_panel, highlightthickness=0)
        self.editor_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.editor_canvas.yview)
        self.editor_frame = ttk.Frame(self.editor_canvas)

        self.editor_canvas.grid(row=1, column=0, sticky="nsew")
        self.editor_scrollbar.grid(row=1, column=1, sticky="ns")
        self.editor_canvas.configure(yscrollcommand=self.editor_scrollbar.set)

        self.editor_canvas.create_window((0, 0), window=self.editor_frame, anchor="nw")
        self.editor_frame.bind("<Configure>", lambda e: self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox("all")))

        # Botones de acción
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        ttk.Button(buttons_frame, text="Cargar archivos GIFT", command=self.process_gift_files).pack(side=tk.LEFT, padx=5)

        # Frame para limpieza masiva
        cleanup_frame = ttk.LabelFrame(buttons_frame, text="Limpieza masiva", padding="5")
        cleanup_frame.pack(side=tk.LEFT, padx=10, fill="y")

        ttk.Label(cleanup_frame, text="Eliminar texto:").pack(side=tk.LEFT)
        self.cleanup_text = tk.StringVar()
        cleanup_entry = ttk.Entry(cleanup_frame, textvariable=self.cleanup_text, width=15)
        cleanup_entry.pack(side=tk.LEFT, padx=2)
        ttk.Button(cleanup_frame, text="Aplicar", command=self.apply_mass_cleanup).pack(side=tk.LEFT, padx=2)

        # Botones comunes predefinidos
        common_frame = ttk.Frame(cleanup_frame)
        common_frame.pack(side=tk.LEFT, padx=5)
        ttk.Button(common_frame, text="[html]", command=lambda: self.quick_cleanup("[html]")).pack(side=tk.TOP, pady=1)
        ttk.Button(common_frame, text="[moodle]", command=lambda: self.quick_cleanup("[moodle]")).pack(side=tk.TOP, pady=1)

        ttk.Button(buttons_frame, text="Guardar como nuevo GIFT", command=self.save_as_gift).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Procesar y continuar", command=self.apply_randomization).pack(side=tk.RIGHT, padx=5)

        # Configurar grid del frame principal
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

    def setup_step4(self):
        frame = self.frames[3]

        # Título
        ttk.Label(frame, text="Paso 4: Generar documentos", font=("Arial", 14, "bold")).grid(row=0, column=0, pady=10, sticky="w")

        # Información de resumen
        ttk.Label(frame, text="Resumen:").grid(row=1, column=0, pady=5, sticky="w")

        # Texto para el resumen
        self.summary_text = tk.Text(frame, width=60, height=10, wrap=tk.WORD)
        self.summary_text.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # Botón para generar documentos
        ttk.Button(frame, text="Generar documentos DOCX", command=self.generate_docx).grid(row=3, column=0, pady=10)

        # Configurar grid
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

    def setup_navigation(self):
        # Crear frame para los botones de navegación
        nav_frame = ttk.Frame(self.root, padding="10")
        nav_frame.grid(row=1, column=0, sticky="ew")

        # Botones de navegación
        self.back_button = ttk.Button(nav_frame, text="Atrás", command=self.go_back, state=tk.DISABLED)
        self.back_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(nav_frame, text="Siguiente", command=self.go_next)
        self.next_button.pack(side=tk.RIGHT, padx=5)

    def show_step(self, step_num):
        # Ocultar todos los frames
        for frame in self.frames:
            frame.grid_remove()

        # Mostrar el frame actual
        self.frames[step_num].grid(row=0, column=0, sticky="nsew")
        self.current_step = step_num

        # Actualizar estado de los botones de navegación
        self.back_button.config(state=tk.NORMAL if step_num > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if step_num < len(self.frames) - 1 else tk.DISABLED)

        # Cambiar texto del botón siguiente en el último paso
        if step_num == len(self.frames) - 1:
            self.next_button.config(text="Finalizar", command=self.finish)
        else:
            self.next_button.config(text="Siguiente", command=self.go_next)

    def go_back(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def go_next(self):
        if self.current_step < len(self.frames) - 1:
            # Validar antes de avanzar
            if self.current_step == 0 and not self.gift_files:
                messagebox.showerror("Error", "Debe seleccionar al menos un archivo GIFT")
                return

            if self.current_step == 1 and not self.output_dir.get():
                messagebox.showerror("Error", "Debe seleccionar un directorio de salida")
                return

            if self.current_step == 2 and not self.questions:
                messagebox.showerror("Error", "Debe cargar los archivos GIFT primero")
                return

            self.show_step(self.current_step + 1)

            # Si estamos entrando al paso 4, generar el resumen
            if self.current_step == 3:
                self.update_summary()

    def finish(self):
        """Finalizar el wizard"""
        self.root.quit()

    def add_gift_files(self):
        """Abrir selector de archivos para elegir archivos GIFT"""
        filenames = filedialog.askopenfilenames(
            title="Seleccionar archivos GIFT",
            filetypes=[
                ("Archivos GIFT", "*.gift"),
                ("Archivos de texto", "*.txt"),
                ("Archivos Markdown", "*.md"),
                ("Todos los archivos", "*.*")
            ]
        )

        for filename in filenames:
            if filename not in self.gift_files:
                self.gift_files.append(filename)

        self.update_files_listbox()

    def remove_selected_file(self):
        """Quitar el archivo seleccionado de la lista"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            del self.gift_files[index]
            self.update_files_listbox()

    def clear_all_files(self):
        """Limpiar toda la lista de archivos"""
        self.gift_files.clear()
        self.update_files_listbox()

    def update_files_listbox(self):
        """Actualizar la lista de archivos en la interfaz"""
        self.files_listbox.delete(0, tk.END)
        for file_path in self.gift_files:
            filename = os.path.basename(file_path)
            self.files_listbox.insert(tk.END, filename)

    def browse_output_dir(self):
        """Abrir selector de directorio para elegir el directorio de salida"""
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if directory:
            self.output_dir.set(directory)

    def read_file_with_encoding(self, file_path):
        """Leer archivo probando diferentes codificaciones"""
        encodings_to_try = []

        if self.encoding_var.get() == "auto":
            # Intentar múltiples codificaciones en orden de probabilidad
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        else:
            # Usar la codificación seleccionada específicamente
            encodings_to_try = [self.encoding_var.get()]

        last_error = None
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()

                # Normalizar algunos caracteres comunes problemáticos
                content = self.normalize_special_characters(content)
                return content

            except UnicodeDecodeError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue

        # Si ninguna codificación funcionó, lanzar el último error
        raise Exception(f"No se pudo leer el archivo {os.path.basename(file_path)} con ninguna codificación. Último error: {str(last_error)}")

    def normalize_special_characters(self, text):
        """Normalizar caracteres especiales comunes"""
        # Diccionario de reemplazos para caracteres problemáticos
        replacements = {
            # Superíndices comunes
            '⁰': '⁰', '¹': '¹', '²': '²', '³': '³', '⁴': '⁴', '⁵': '⁵',
            '⁶': '⁶', '⁷': '⁷', '⁸': '⁸', '⁹': '⁹', '⁺': '⁺', '⁻': '⁻',

            # Subíndices comunes
            '₀': '₀', '₁': '₁', '₂': '₂', '₃': '₃', '₄': '₄', '₅': '₅',
            '₆': '₆', '₇': '₇', '₈': '₈', '₉': '₉', '₊': '₊', '₋': '₋',

            # Flechas
            '→': '→', '←': '←', '↔': '↔', '↑': '↑', '↓': '↓',
            '⟶': '→', '⟵': '←', '⟷': '↔',

            # Símbolos matemáticos y científicos
            '±': '±', '×': '×', '÷': '÷', '≤': '≤', '≥': '≥', '≠': '≠',
            '∞': '∞', '∂': '∂', '∫': '∫', '∑': '∑', '√': '√', 'π': 'π',
            'α': 'α', 'β': 'β', 'γ': 'γ', 'δ': 'δ', 'ε': 'ε', 'θ': 'θ',
            'λ': 'λ', 'μ': 'μ', 'ν': 'ν', 'ρ': 'ρ', 'σ': 'σ', 'τ': 'τ',
            'φ': 'φ', 'χ': 'χ', 'ψ': 'ψ', 'ω': 'ω',

            # Grados y unidades
            '°': '°', '℃': '℃', '℉': '℉', 'Ω': 'Ω', 'μ': 'μ',

            # Símbolos químicos comunes
            '⁺': '⁺', '⁻': '⁻', '²⁺': '²⁺', '³⁺': '³⁺',

            # Comillas y apostrofes problemáticos
            '"': '"', '"': '"', ''': "'", ''': "'",
            '–': '-', '—': '-', '…': '...',
        }

        # Aplicar reemplazos
        for old_char, new_char in replacements.items():
            text = text.replace(old_char, new_char)

        return text

    def detect_question_problems(self, question):
        """Detectar problemas en una pregunta"""
        problems = []

        if question['type'] != 'multiple_choice':
            return problems

        # Obtener opciones correctas e incorrectas
        correct_options = [opt for opt in question['options'] if opt['is_correct']]
        incorrect_options = [opt for opt in question['options'] if not opt['is_correct']]

        if not correct_options or not incorrect_options:
            return problems

        correct_text = correct_options[0]['text']

        # 1. Detectar respuesta correcta significativamente más larga
        threshold = self.threshold_var.get()
        avg_incorrect_length = sum(len(opt['text']) for opt in incorrect_options) / len(incorrect_options)

        if len(correct_text) - avg_incorrect_length > threshold:
            problems.append(f"Respuesta correcta {int(len(correct_text) - avg_incorrect_length)} caracteres más larga que promedio")

        # 2. Detectar distractores muy cortos
        short_distractors = [opt for opt in incorrect_options if len(opt['text']) < 10]
        if short_distractors:
            problems.append(f"{len(short_distractors)} distractor(es) muy corto(s) (< 10 caracteres)")

        # 3. Detectar palabras clave problemáticas
        problematic_phrases = [
            "todas las anteriores", "todas las opciones", "todas son correctas",
            "ninguna de las anteriores", "ninguna opción", "ninguna es correcta",
            "solo a", "solo b", "solo c", "solo d",
            "a y b", "a y c", "a y d", "b y c", "b y d", "c y d",
            "a, b y c", "a, b y d", "a, c y d", "b, c y d"
        ]

        for option in question['options']:
            text_lower = option['text'].lower()
            for phrase in problematic_phrases:
                if phrase in text_lower:
                    problems.append(f"Opción contiene frase problemática: '{phrase}'")
                    break

        return problems

    def process_gift_files(self):
        """Procesar todos los archivos GIFT y extraer las preguntas"""
        if not self.gift_files:
            messagebox.showerror("Error", "Debe seleccionar al menos un archivo GIFT primero")
            return

        try:
            all_questions = []
            encoding_issues = []

            # Procesar cada archivo
            for file_path in self.gift_files:
                try:
                    # Usar la nueva función de lectura con manejo de codificaciones
                    content = self.read_file_with_encoding(file_path)

                    # Procesar el contenido GIFT
                    file_questions = self.parse_gift_questions(content, os.path.basename(file_path))
                    all_questions.extend(file_questions)

                except Exception as e:
                    error_msg = f"Error al procesar {os.path.basename(file_path)}: {str(e)}"
                    encoding_issues.append(error_msg)
                    continue

            # Mostrar advertencias de codificación si las hay
            if encoding_issues:
                messagebox.showwarning(
                    "Problemas de codificación",
                    "Se encontraron problemas al leer algunos archivos:\n\n" +
                    "\n".join(encoding_issues) +
                    "\n\nPrueba seleccionar una codificación específica en las opciones."
                )

            # Aplicar orden según configuración
            if self.question_order.get() == "aleatorio":
                random.shuffle(all_questions)

            self.questions = all_questions

            # Detectar problemas en todas las preguntas
            for question in self.questions:
                question['problems'] = self.detect_question_problems(question)

            # Actualizar lista de preguntas
            self.update_questions_list()

            processed_files = len(self.gift_files) - len(encoding_issues)
            messagebox.showinfo("Éxito", f"Se han procesado {len(self.questions)} preguntas de {processed_files} archivo(s)")

        except Exception as e:
            messagebox.showerror("Error", f"Error general al procesar archivos: {str(e)}")

    def update_questions_list(self):
        """Actualizar la lista de preguntas en el panel izquierdo"""
        self.questions_listbox.delete(0, tk.END)

        for i, question in enumerate(self.questions):
            # Determinar estado de la pregunta
            if question.get('problems'):
                status = "[!]"
            else:
                status = "[ok]"

            # Truncar texto de pregunta para mostrar en lista
            question_text = question['text'][:50] + "..." if len(question['text']) > 50 else question['text']

            # Agregar a la lista
            display_text = f"{status} {i+1}. {question_text}"
            self.questions_listbox.insert(tk.END, display_text)

    def on_question_select(self, event):
        """Manejar selección de pregunta en la lista"""
        selection = self.questions_listbox.curselection()
        if not selection:
            return

        question_index = selection[0]
        self.selected_question_index.set(question_index)
        self.show_question_editor(question_index)

    def show_question_editor(self, question_index):
        """Mostrar editor para la pregunta seleccionada"""
        if question_index >= len(self.questions):
            return

        question = self.questions[question_index]

        # Limpiar el editor anterior
        for widget in self.editor_frame.winfo_children():
            widget.destroy()

        # Información de la pregunta
        info_text = f"Pregunta {question_index + 1}"
        if question.get('source_file'):
            info_text += f" (Archivo: {question['source_file']})"
        self.question_info_label.config(text=info_text)

        row = 0

        # Mostrar problemas detectados
        if question.get('problems'):
            problems_frame = ttk.LabelFrame(self.editor_frame, text="[!] Problemas detectados", padding="5")
            problems_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
            problems_frame.columnconfigure(0, weight=1)

            for i, problem in enumerate(question['problems']):
                ttk.Label(problems_frame, text=f"- {problem}", foreground="red", wraplength=400).grid(row=i, column=0, sticky="w")

            row += 1

        # Editor del texto de la pregunta
        ttk.Label(self.editor_frame, text="Texto de la pregunta:").grid(row=row, column=0, sticky="w", padx=5, pady=(10,2))
        row += 1

        question_text_var = tk.StringVar(value=question['text'])
        question_entry = ttk.Entry(self.editor_frame, textvariable=question_text_var, width=60)
        question_entry.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        question['text_var'] = question_text_var
        row += 1

        # Editor de opciones
        if question['type'] == 'multiple_choice':
            ttk.Label(self.editor_frame, text="Opciones de respuesta:").grid(row=row, column=0, sticky="w", padx=5, pady=(10,2))
            row += 1

            option_chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

            for i, option in enumerate(question['options']):
                option_frame = ttk.Frame(self.editor_frame)
                option_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
                option_frame.columnconfigure(1, weight=1)

                # Letra de la opción
                letter_label = ttk.Label(option_frame, text=f"{option_chars[i]})", width=3)
                letter_label.grid(row=0, column=0, padx=(0,5))

                # Campo de texto editable
                option_var = tk.StringVar(value=option['text'])
                option_entry = ttk.Entry(option_frame, textvariable=option_var, width=50)
                option_entry.grid(row=0, column=1, sticky="ew")
                option['text_var'] = option_var

                # Indicador de longitud y correcto
                char_count = len(option['text'])
                correct_text = " [CORRECTA]" if option['is_correct'] else ""
                info_label = ttk.Label(option_frame, text=f"({char_count} caracteres){correct_text}")
                info_label.grid(row=0, column=2, padx=(5,0))
                option['info_label'] = info_label

                # Actualizar contador cuando cambie el texto
                def update_char_count(var, option=option):
                    new_length = len(var.get())
                    correct_text = " [CORRECTA]" if option['is_correct'] else ""
                    option['info_label'].config(text=f"({new_length} caracteres){correct_text}")

                option_var.trace('w', lambda *args, var=option_var: update_char_count(var))

                row += 1

        # Botones de acción para la pregunta
        buttons_frame = ttk.Frame(self.editor_frame)
        buttons_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=10)

        ttk.Button(buttons_frame, text="Guardar cambios", command=lambda: self.save_question_changes(question_index)).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Reanalizar problemas", command=lambda: self.reanalyze_question(question_index)).pack(side=tk.LEFT, padx=5)

        # Configurar scrolling
        self.editor_frame.columnconfigure(0, weight=1)
        self.editor_canvas.update_idletasks()
        self.editor_canvas.configure(scrollregion=self.editor_canvas.bbox("all"))

    def quick_cleanup(self, text_to_remove):
        """Aplicar limpieza rápida con texto predefinido"""
        self.cleanup_text.set(text_to_remove)
        self.apply_mass_cleanup()

    def apply_mass_cleanup(self):
        """Aplicar limpieza masiva a todas las preguntas"""
        if not self.questions:
            messagebox.showerror("Error", "No hay preguntas cargadas")
            return

        text_to_remove = self.cleanup_text.get().strip()
        if not text_to_remove:
            messagebox.showerror("Error", "Ingrese el texto a eliminar")
            return

        # Confirmar acción
        result = messagebox.askyesno(
            "Confirmar limpieza masiva",
            f"¿Está seguro de eliminar '{text_to_remove}' de todas las preguntas y opciones?\n\n"
            "Esta acción no se puede deshacer."
        )

        if not result:
            return

        changes_made = 0

        # Aplicar limpieza a todas las preguntas
        for question in self.questions:
            # Limpiar texto de pregunta
            if text_to_remove in question['text']:
                question['text'] = question['text'].replace(text_to_remove, '')
                changes_made += 1

            # Limpiar opciones
            if question['type'] == 'multiple_choice':
                for option in question['options']:
                    if text_to_remove in option['text']:
                        option['text'] = option['text'].replace(text_to_remove, '')
                        changes_made += 1

                    # Limpiar retroalimentación si existe
                    if option.get('feedback') and text_to_remove in option['feedback']:
                        option['feedback'] = option['feedback'].replace(text_to_remove, '')
                        changes_made += 1

        # Reanalizar problemas después de la limpieza
        for question in self.questions:
            question['problems'] = self.detect_question_problems(question)

        # Actualizar interfaz
        self.update_questions_list()

        # Si hay una pregunta seleccionada, actualizar el editor
        current_selection = self.questions_listbox.curselection()
        if current_selection:
            self.show_question_editor(current_selection[0])

        # Limpiar campo de entrada
        self.cleanup_text.set("")

        messagebox.showinfo(
            "Limpieza completada",
            f"Limpieza masiva completada.\n\n"
            f"Se realizaron {changes_made} cambios en total.\n"
            f"Los problemas han sido reanalizado automáticamente."
        )


    def reanalyze_question(self, question_index):
        """Reanalizar problemas de la pregunta actual"""
        if question_index >= len(self.questions):
            return

        question = self.questions[question_index]

        # Guardar cambios primero
        self.save_question_changes(question_index)

        # Mostrar editor actualizado
        self.show_question_editor(question_index)
    
    def save_question_changes(self, question_index):
        """Guardar cambios de la pregunta actual"""
        if question_index >= len(self.questions):
            return

        question = self.questions[question_index]

        # Actualizar texto de pregunta
        if hasattr(question, 'text_var'):
            question['text'] = question['text_var'].get()

        # Actualizar opciones
        if question['type'] == 'multiple_choice':
            for option in question['options']:
                if hasattr(option, 'text_var'):
                    option['text'] = option['text_var'].get()

        # Reanalizar problemas
        question['problems'] = self.detect_question_problems(question)

        # Actualizar lista de preguntas
        self.update_questions_list()

        # Reseleccionar la pregunta actual
        self.questions_listbox.selection_set(question_index)

        messagebox.showinfo("Guardado", "Cambios guardados correctamente")

    def save_as_gift(self):
        """Guardar las preguntas editadas como un nuevo archivo GIFT"""
        if not self.questions:
            messagebox.showerror("Error", "No hay preguntas para guardar")
            return

        # Solicitar nombre del archivo
        filename = filedialog.asksaveasfilename(
            title="Guardar como archivo GIFT",
            defaultextension=".gift",
            filetypes=[("Archivos GIFT", "*.gift"), ("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )

        if not filename:
            return

        try:
            # Guardar cambios de la pregunta actual si está siendo editada
            current_selection = self.questions_listbox.curselection()
            if current_selection:
                self.save_question_changes(current_selection[0])

            gift_content = self.questions_to_gift_format()

            with open(filename, 'w', encoding='utf-8') as file:
                file.write(gift_content)

            messagebox.showinfo("Guardado", f"Archivo GIFT guardado correctamente:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")

    def questions_to_gift_format(self):
        """Convertir las preguntas editadas de vuelta al formato GIFT"""
        gift_lines = []

        for question in self.questions:
            # Agregar título si existe
            if question.get('title') and question['title'] != "Sin título":
                gift_lines.append(f"::{question['title']}::")

            # Agregar texto de pregunta
            gift_lines.append(question['text'])

            # Agregar opciones si es de opción múltiple
            if question['type'] == 'multiple_choice':
                options_text = "{"

                for option in question['options']:
                    prefix = "=" if option['is_correct'] else "~"
                    option_text = option['text']

                    # Agregar retroalimentación si existe
                    if option.get('feedback'):
                        option_text += f"#{option['feedback']}"

                    options_text += f"{prefix}{option_text}"

                options_text += "}"
                gift_lines.append(options_text)

            # Línea en blanco entre preguntas
            gift_lines.append("")

        return "\n".join(gift_lines)

    def apply_randomization(self):
        """Aplicar aleatorización y continuar al siguiente paso"""
        if not self.questions:
            messagebox.showerror("Error", "No hay preguntas para procesar")
            return

        # Guardar cambios de la pregunta actual si está siendo editada
        current_selection = self.questions_listbox.curselection()
        if current_selection:
            self.save_question_changes(current_selection[0])

        # Verificar si hay problemas no resueltos
        questions_with_problems = [q for q in self.questions if q.get('problems')]

        if questions_with_problems:
            result = messagebox.askyesno(
                "Problemas detectados",
                f"Hay {len(questions_with_problems)} pregunta(s) con problemas detectados.\n\n"
                "¿Desea continuar de todos modos?"
            )
            if not result:
                return

        messagebox.showinfo("Procesado", "Preguntas procesadas. Aleatorización aplicada según configuración.")
        self.go_next()

    def parse_gift_questions(self, content, source_file=""):
        """Parsear preguntas en formato GIFT"""
        # Eliminar comentarios
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

        # Dividir en preguntas individuales
        question_blocks = re.split(r'\n\s*\n', content)

        questions = []

        for block in question_blocks:
            block = block.strip()
            if not block:
                continue

            try:
                # Extraer el título (si existe)
                title_match = re.match(r'::(.+?)::', block)
                title = title_match.group(1).strip() if title_match else "Sin título"

                # Remover el título del bloque para seguir procesando
                if title_match:
                    block = block[title_match.end():].strip()

                # Extraer el texto de la pregunta (todo hasta la primera respuesta)
                question_text_match = re.match(r'(.*?)\{', block, re.DOTALL)
                if not question_text_match:
                    continue

                question_text = question_text_match.group(1).strip()

                # Extraer las opciones y retroalimentación
                options_block = block[question_text_match.end()-1:]

                # Procesar según el tipo de pregunta
                question_data = {
                    'title': title,
                    'text': question_text,
                    'type': 'unknown',
                    'options': [],
                    'correct_answer': None,
                    'feedback': {},
                    'source_file': source_file,
                    'problems': []
                }

                # Verifica si es una pregunta de opción múltiple
                if re.match(r'\{', options_block):
                    # Dividir las opciones por ~ o = al inicio, conservando el delimitador
                    options_match = re.split(r'(?=[~=])', options_block.strip()[1:-1].strip())

                    options = []
                    for option_text in options_match:
                        option_text = option_text.strip()
                        if not option_text:
                            continue

                        is_correct = option_text.startswith('=')
                        option_text = option_text[1:].strip()  # Eliminar el prefijo ~ o =

                        # Extraer retroalimentación
                        feedback_text = ""
                        feedback_idx = option_text.find('#')

                        if feedback_idx != -1:
                            feedback_text = option_text[feedback_idx+1:].strip()
                            option_text = option_text[:feedback_idx].strip()

                        options.append({
                            'text': option_text,
                            'is_correct': is_correct,
                            'feedback': feedback_text
                        })

                        if is_correct:
                            question_data['correct_answer'] = option_text

                    question_data['type'] = 'multiple_choice'
                    question_data['options'] = options

                # Si hay al menos texto de pregunta, la añadimos
                if question_data['text']:
                    questions.append(question_data)

            except Exception as e:
                print(f"Error al procesar una pregunta en {source_file}: {str(e)}")
                continue

        return questions

    def update_summary(self):
        """Actualizar el resumen en el paso 4"""
        self.summary_text.delete(1.0, tk.END)

        if not self.questions:
            self.summary_text.insert(tk.END, "No hay preguntas para procesar.")
            return

        # Información de archivos
        self.summary_text.insert(tk.END, f"Archivos procesados: {len(self.gift_files)}\n")
        for i, file_path in enumerate(self.gift_files, 1):
            filename = os.path.basename(file_path)
            file_questions = sum(1 for q in self.questions if q['source_file'] == filename)
            self.summary_text.insert(tk.END, f"  {i}. {filename} ({file_questions} preguntas)\n")

        self.summary_text.insert(tk.END, f"\nDirectorio de salida: {self.output_dir.get()}\n\n")

        # Información de preguntas
        self.summary_text.insert(tk.END, f"Total de preguntas: {len(self.questions)}\n")
        self.summary_text.insert(tk.END, f"Preguntas de opción múltiple: {sum(1 for q in self.questions if q['type'] == 'multiple_choice')}\n")
        self.summary_text.insert(tk.END, f"Orden de preguntas: {'Aleatorio' if self.question_order.get() == 'aleatorio' else 'Por archivos'}\n")
        self.summary_text.insert(tk.END, f"Opciones aleatorizadas: {'Sí' if self.randomize_options.get() else 'No'}\n")

        # Información de problemas detectados
        questions_with_problems = [q for q in self.questions if q.get('problems')]
        self.summary_text.insert(tk.END, f"Preguntas con problemas detectados: {len(questions_with_problems)}\n\n")

        # Analizar el número de opciones por pregunta
        option_counts = [len(q['options']) for q in self.questions if q['type'] == 'multiple_choice']
        if option_counts:
            counter = collections.Counter(option_counts)
            self.summary_text.insert(tk.END, "Distribución de opciones por pregunta:\n")
            for count, frequency in sorted(counter.items()):
                self.summary_text.insert(tk.END, f"  - Preguntas con {count} opciones: {frequency}\n")

        self.summary_text.insert(tk.END, "\nSe generarán dos archivos DOCX:\n")
        self.summary_text.insert(tk.END, "1. Examen.docx - Contiene las preguntas y hoja de respuestas\n")
        self.summary_text.insert(tk.END, "2. Respuestas.docx - Contiene las respuestas correctas con estadísticas\n")

    def generate_docx(self):
        """Generar los documentos DOCX"""
        if not self.questions:
            messagebox.showerror("Error", "No hay preguntas para generar los documentos")
            return

        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "El directorio de salida no es válido")
            return

        try:
            # IMPORTANTE: Generar PRIMERO el documento de examen para llenar self.answer_keys
            exam_doc = self.create_exam_document()

            # LUEGO generar el documento de respuestas (que ya tendrá las estadísticas)
            answers_doc = self.create_answers_document()

            # Generar nombres de archivo con timestamp si ya existen
            import datetime
            
            exam_filename = "Examen.docx"
            answers_filename = "Respuestas.docx"
            
            exam_path = os.path.join(self.output_dir.get(), exam_filename)
            answers_path = os.path.join(self.output_dir.get(), answers_filename)
            
            # Si los archivos ya existen, agregar timestamp
            if os.path.exists(exam_path) or os.path.exists(answers_path):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                exam_filename = f"Examen_{timestamp}.docx"
                answers_filename = f"Respuestas_{timestamp}.docx"
                exam_path = os.path.join(self.output_dir.get(), exam_filename)
                answers_path = os.path.join(self.output_dir.get(), answers_filename)

            # Guardar documentos
            exam_doc.save(exam_path)
            answers_doc.save(answers_path)

            messagebox.showinfo(
                "Éxito",
                f"Documentos generados correctamente:\n\n"
                f"- Examen: {exam_path}\n"
                f"- Respuestas: {answers_path}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar los documentos: {str(e)}")

    def create_exam_document(self):
        """Crear documento de examen"""
        doc = Document()

        # Estilos
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(11)

        # Título
        title = doc.add_heading('EXAMEN', level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()

        # Limpiar el diccionario de respuestas
        self.answer_keys = {}

        # Analizar el número de opciones para cada pregunta
        options_per_question = {}
        for i, question in enumerate(self.questions, 1):
            if question['type'] == 'multiple_choice':
                options_per_question[i] = len(question['options'])

        # Encontrar el máximo número de opciones por pregunta
        max_options = max(options_per_question.values()) if options_per_question else 4

        # Calcular la distribución óptima de letras correctas (para que sean equitativas)
        option_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        distributions = {}

        # Agrupar preguntas por número de opciones
        for q_num, num_options in options_per_question.items():
            if num_options not in distributions:
                distributions[num_options] = []
            distributions[num_options].append(q_num)

        # Para cada grupo, asignar letras correctas de manera equitativa
        for num_options, q_numbers in distributions.items():
            # Crear una lista con la misma cantidad de cada letra posible
            valid_chars = option_chars[:num_options]
            target_answers = []
            for char in valid_chars:
                target_answers.extend([char] * (len(q_numbers) // len(valid_chars)))

            # Añadir caracteres extra si es necesario
            remaining = len(q_numbers) - len(target_answers)
            if remaining > 0:
                target_answers.extend(random.sample(valid_chars, remaining))

            # Mezclar las respuestas
            random.shuffle(target_answers)

            # Asignar a cada pregunta
            for i, q_num in enumerate(q_numbers):
                self.answer_keys[q_num] = target_answers[i]

        # Preguntas
        for i, question in enumerate(self.questions, 1):
            # Añadir texto de la pregunta
            doc.add_paragraph(f"{i}. {question['text']}")

            # Si es de opción múltiple, añadir opciones
            if question['type'] == 'multiple_choice':
                options = question['options'].copy()
                num_options = len(options)

                # Reorganizar opciones según el algoritmo mejorado
                if self.randomize_options.get() and i in self.answer_keys:
                    # Determinar qué opción es la correcta
                    correct_option = next((opt for opt in options if opt['is_correct']), None)
                    if correct_option:
                        # Reorganizar para que la respuesta correcta esté en la posición deseada
                        target_position = ord(self.answer_keys[i]) - ord('a')

                        # Remover la opción correcta de la lista
                        options.remove(correct_option)

                        # Mezclar las opciones incorrectas
                        random.shuffle(options)

                        # Insertar la opción correcta en la posición objetivo
                        if target_position < len(options) + 1:
                            options.insert(target_position, correct_option)
                        else:
                            options.append(correct_option)
                else:
                    # Aleatorización simple
                    random.shuffle(options)
                    # Actualizar la clave de respuesta
                    for j, opt in enumerate(options):
                        if opt['is_correct'] and i not in self.answer_keys:
                            self.answer_keys[i] = option_chars[j] if j < len(option_chars) else 'X'

                # Añadir opciones
                for j, opt in enumerate(options):
                    if j < len(option_chars):
                        # Usar letras mayúsculas para las opciones
                        doc.add_paragraph(f"   {option_chars[j].upper()}) {opt['text']}")

            # Espacio entre preguntas
            doc.add_paragraph()

        # Agregar salto de página antes de la hoja de respuestas
        doc.add_page_break()

        # Título de la hoja de respuestas
        answer_title = doc.add_heading('HOJA DE RESPUESTAS', level=1)
        answer_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph("Marque con una X la respuesta correcta para cada pregunta.")
        doc.add_paragraph()

        # Crear tabla para la hoja de respuestas (2 columnas)
        # Calcular número de filas necesarias
        num_questions = len(self.questions)
        rows_per_column = (num_questions + 1) // 2  # División entera redondeando hacia arriba

        # Calcular número total de columnas basado en el máximo de opciones
        cols_per_group = max_options + 1  # +1 para el número de pregunta
        total_cols = cols_per_group * 2  # Para las dos columnas de preguntas

        # Crear la tabla con suficientes columnas
        table = doc.add_table(rows=rows_per_column + 1, cols=total_cols)
        table.style = 'Table Grid'

        # Letras para los encabezados (en mayúsculas)
        header_letters = [chr(65 + i) for i in range(max_options)]  # A, B, C, D, ...

        # Encabezados primera columna
        cell = table.cell(0, 0)
        cell.text = "Preg"

        for i, letter in enumerate(header_letters):
            cell = table.cell(0, i + 1)
            cell.text = letter

        # Encabezados segunda columna
        if num_questions > rows_per_column:
            cell = table.cell(0, cols_per_group)
            cell.text = "Preg"

            for i, letter in enumerate(header_letters):
                cell = table.cell(0, cols_per_group + i + 1)
                cell.text = letter

        # Llenar la tabla con números de pregunta y marcar celdas no válidas
        # Definir un sombreado negro para las celdas no válidas
        shading_black_xml = parse_xml(f'<w:shd {nsdecls("w")} w:fill="000000"/>')

        for i in range(num_questions):
            q_num = i + 1
            row_idx = (i % rows_per_column) + 1  # +1 para saltar el encabezado

            # Obtener el número de opciones para esta pregunta
            if q_num in options_per_question:
                q_options = options_per_question[q_num]
            else:
                q_options = 0  # Fallback por si acaso

            if i < rows_per_column:  # Primera columna
                # Número de pregunta
                cell = table.cell(row_idx, 0)
                cell.text = str(q_num)

                # Sombrear celdas que superan el número de opciones
                for j in range(q_options + 1, max_options + 1):
                    cell = table.cell(row_idx, j)
                    cell._element.get_or_add_tcPr().append(shading_black_xml)
                    cell.text = ""  # Texto vacío
            else:  # Segunda columna
                # Número de pregunta
                cell = table.cell(row_idx, cols_per_group)
                cell.text = str(q_num)

                # Sombrear celdas que superan el número de opciones
                for j in range(q_options + 1, max_options + 1):
                    cell = table.cell(row_idx, cols_per_group + j)
                    cell._element.get_or_add_tcPr().append(shading_black_xml)
                    cell.text = ""  # Texto vacío

        # Ajustar ancho de columnas para mejor visualización
        for cell in table.columns[0].cells:
            cell.width = Inches(0.5)

        if cols_per_group < len(table.columns):
            for cell in table.columns[cols_per_group].cells:
                cell.width = Inches(0.5)

        return doc

    def create_answers_document(self):
        """Crear documento de respuestas"""
        doc = Document()

        # Estilos
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(11)

        # Título
        title = doc.add_heading('HOJA DE RESPUESTAS', level=1)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Añadir estadísticas de las preguntas
        doc.add_heading('Estadísticas del examen', level=2)

        p = doc.add_paragraph()
        p.add_run(f"Total de preguntas: {len(self.questions)}")

        multiple_choice_count = sum(1 for q in self.questions if q['type'] == 'multiple_choice')
        p = doc.add_paragraph()
        p.add_run(f"Preguntas de opción múltiple: {multiple_choice_count}")

        # Información de archivos procesados
        if len(self.gift_files) > 1:
            p = doc.add_paragraph()
            p.add_run("Archivos procesados:").bold = True
            for i, file_path in enumerate(self.gift_files, 1):
                filename = os.path.basename(file_path)
                file_questions = sum(1 for q in self.questions if q['source_file'] == filename)
                doc.add_paragraph(f"  {i}. {filename} ({file_questions} preguntas)")

        # Información de problemas detectados
        questions_with_problems = [q for q in self.questions if q.get('problems')]
        if questions_with_problems:
            p = doc.add_paragraph()
            p.add_run(f"Preguntas con problemas detectados: {len(questions_with_problems)}").bold = True

        # Analizar el número de opciones por pregunta
        option_counts = [len(q['options']) for q in self.questions if q['type'] == 'multiple_choice']
        if option_counts:
            counter = collections.Counter(option_counts)

            p = doc.add_paragraph()
            p.add_run("Distribución de opciones por pregunta:").bold = True

            for count, frequency in sorted(counter.items()):
                doc.add_paragraph(f"  - Preguntas con {count} opciones: {frequency}")

        # Análisis de distribución de respuestas correctas
        if self.answer_keys:
            answer_counter = collections.Counter(self.answer_keys.values())

            p = doc.add_paragraph()
            p.add_run("Distribución de alternativas correctas:").bold = True

            for letter, count in sorted(answer_counter.items()):
                doc.add_paragraph(f"  - Alternativa {letter.upper()}): {count} preguntas")
        else:
            p = doc.add_paragraph()
            p.add_run("Distribución de alternativas correctas:").bold = True
            doc.add_paragraph("  - No se pudo calcular la distribución (error en el procesamiento)")

        doc.add_paragraph()
        doc.add_heading('Respuestas correctas', level=2)

        # Preguntas y respuestas
        for i, question in enumerate(self.questions, 1):
            # Añadir información del archivo fuente si hay múltiples
            if len(self.gift_files) > 1:
                p = doc.add_paragraph()
                p.add_run(f"[Archivo: {question['source_file']}]").italic = True

            # Añadir texto de la pregunta
            p = doc.add_paragraph()
            p.add_run(f"{i}. {question['text']}").bold = True

            # Si es de opción múltiple, añadir respuesta correcta
            if question['type'] == 'multiple_choice':
                correct_letter = self.answer_keys.get(i, "?")

                # Encontrar la respuesta correcta
                correct_options = [opt for opt in question['options'] if opt['is_correct']]

                if correct_options:
                    correct_answer = correct_options[0]['text']
                    # Mostrar la letra correcta que fue asignada
                    doc.add_paragraph(f"   Respuesta correcta: {correct_letter.upper()}) {correct_answer}")

                    # Añadir retroalimentación si existe
                    if correct_options[0]['feedback']:
                        doc.add_paragraph(f"   Retroalimentación: {correct_options[0]['feedback']}")
                else:
                    doc.add_paragraph("   Respuesta correcta: No encontrada")

            # Espacio entre preguntas
            doc.add_paragraph()

        return doc

def main():
    root = tk.Tk()
    app = GiftToDocxConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
