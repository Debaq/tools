#!/usr/bin/env python3
# marknote.py - Editor Markdown Inteligente

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QTextEdit, QMenuBar, QMenu, QFileDialog, QMessageBox, QLineEdit, 
    QPushButton, QDialog, QDialogButtonBox, QLabel, QFrame, 
    QComboBox, QSpinBox, QInputDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QAction, QKeySequence, QTextCursor, QFontDatabase, QTextDocument, QKeyEvent
import markdown

# Importar módulos propios
from styles import get_main_theme, get_dialog_theme, get_overlay_style, get_markdown_css
from markdown_document import MarkdownDocument
from markdown_processor import MarkdownProcessor

class CommentOverlay(QFrame):
    """Overlay flotante para mostrar comentarios"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setStyleSheet(get_overlay_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("background: transparent; border: none; padding: 0; color: #ffffff;")
        layout.addWidget(label)
        
        self.setMaximumWidth(280)
        self.setMinimumWidth(200)
        self.adjustSize()
        
        self.setWindowFlags(Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)

class CommentDialog(QDialog):
    """Diálogo para agregar comentarios"""
    
    def __init__(self, parent=None, existing_text=""):
        super().__init__(parent)
        self.setWindowTitle("Agregar Comentario")
        self.setModal(True)
        self.resize(400, 150)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Comentario:"))
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(existing_text)
        self.text_edit.setMaximumHeight(80)
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setStyleSheet(get_dialog_theme())
    
    def get_comment(self):
        return self.text_edit.toPlainText().strip()

class ElementEditDialog(QDialog):
    """Diálogo para editar código markdown de un elemento"""
    
    def __init__(self, parent=None, markdown_code=""):
        super().__init__(parent)
        self.setWindowTitle("Editar Elemento - Código Markdown")
        self.setModal(True)
        self.resize(700, 300)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Editar código Markdown del elemento:"))
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(markdown_code)
        self.text_edit.setFont(QFont("Consolas", 12))
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setStyleSheet(get_dialog_theme())
    
    def get_markdown(self):
        return self.text_edit.toPlainText()

class MarkdownViewer(QTextEdit):
    """Visor inteligente de markdown con preservación de formato"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Componentes principales
        self.document = MarkdownDocument()
        self.processor = MarkdownProcessor()
        
        # Configuración de renderizado
        self.current_font_size = 16
        self.current_font_family = "Roboto"
        self.is_rendering = False
        
        # Overlays de comentarios
        self.overlays = []
        
        # Mapeo de posiciones
        self.element_boundaries = []  # (start_pos, end_pos, element_index)
        
        # Configuración del editor
        self.setAcceptRichText(False)
    
    def set_font_properties(self, family, size):
        """Cambiar fuente y tamaño"""
        self.current_font_family = family
        self.current_font_size = size
        self.render_document()
    
    def load_markdown_file(self, content):
        """Cargar contenido de archivo markdown"""
        print(f"📁 CARGANDO ARCHIVO MARKDOWN")
        self.document.load_from_markdown(content)
        self.render_document()
    
    def render_document(self):
        """Renderizar documento completo"""
        if self.is_rendering:
            return
            
        self.is_rendering = True
        
        print(f"🎨 RENDERIZANDO DOCUMENTO:")
        
        # Obtener elementos para renderizado
        elements = self.document.get_elements_for_rendering()
        html_parts = []
        self.element_boundaries = []
        
        current_position = 0
        
        for i, markdown_content in enumerate(elements):
            if not markdown_content.strip():
                # Elemento vacío
                html_parts.append("<p><br></p>")
                rendered_text = "\n"
            else:
                # Renderizar markdown
                md = markdown.Markdown(extensions=['fenced_code', 'tables', 'codehilite'])
                html = md.convert(markdown_content)
                html_parts.append(html)
                
                # Obtener texto plano para calcular posiciones
                temp_doc = QTextDocument()
                temp_doc.setHtml(html)
                rendered_text = temp_doc.toPlainText()
            
            # Guardar límites del elemento
            end_position = current_position + len(rendered_text)
            self.element_boundaries.append((current_position, end_position, i))
            
            print(f"  Elemento {i}: pos {current_position}-{end_position}")
            print(f"    MD: {repr(markdown_content[:50])}")
            print(f"    Texto: {repr(rendered_text[:50])}")
            
            current_position = end_position + 1  # +1 para separación entre elementos
        
        # Combinar HTML final
        combined_html = get_markdown_css(self.current_font_family, self.current_font_size)
        combined_html += f"<body>{''.join(html_parts)}</body>"
        
        # Actualizar contenido preservando cursor
        cursor_pos = self.textCursor().position()
        
        self.blockSignals(True)
        self.setHtml(combined_html)
        self.blockSignals(False)
        
        # Restaurar cursor
        cursor = self.textCursor()
        cursor.setPosition(min(cursor_pos, len(self.toPlainText())))
        self.setTextCursor(cursor)
        
        self.update_comment_overlays()
        self.is_rendering = False
        
        print(f"✅ RENDERIZADO COMPLETO\n")
    
    def get_element_at_cursor(self):
        """Obtener índice del elemento donde está el cursor"""
        cursor_pos = self.textCursor().position()
        
        for start_pos, end_pos, element_index in self.element_boundaries:
            if start_pos <= cursor_pos <= end_pos:
                return element_index
        
        # Si no se encuentra, devolver el último
        return len(self.document.elements) - 1 if self.document.elements else -1
    
    def get_element_rendered_text(self, element_index):
        """Obtener texto renderizado de un elemento específico"""
        if not (0 <= element_index < len(self.element_boundaries)):
            return ""
        
        start_pos, end_pos, _ = self.element_boundaries[element_index]
        full_text = self.toPlainText()
        
        return full_text[start_pos:end_pos].strip()
    
    def keyPressEvent(self, event):
        """Manejar eventos de teclado"""
        if event.key() == Qt.Key_Return:
            if event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter: Dividir elemento
                self.split_current_element()
            else:
                # Enter: Procesar elemento actual
                self.process_current_element()
        elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier:
            # Ctrl+Z: Deshacer
            if self.document.undo():
                self.render_document()
        elif event.key() == Qt.Key_Y and event.modifiers() & Qt.ControlModifier:
            # Ctrl+Y: Rehacer
            if self.document.redo():
                self.render_document()
        else:
            super().keyPressEvent(event)
    
    def process_current_element(self):
        """Procesar elemento actual con lógica inteligente"""
        element_index = self.get_element_at_cursor()
        if element_index < 0:
            return
        
        # Obtener texto renderizado actual
        current_rendered = self.get_element_rendered_text(element_index)
        
        # Obtener elemento original
        element = self.document.get_element(element_index)
        if not element:
            return
        
        original_md = element.markdown_code
        
        print(f"🧠 PROCESANDO ELEMENTO {element_index}")
        print(f"  Texto renderizado: {repr(current_rendered)}")
        print(f"  MD original: {repr(original_md)}")
        
        # Usar procesador inteligente
        new_markdown = self.processor.smart_update_markdown(original_md, current_rendered)
        
        # Actualizar si hay cambios
        if new_markdown != original_md:
            print(f"✅ Actualizando con: {repr(new_markdown)}")
            self.document.update_element(element_index, new_markdown)
            
            # Re-renderizar después de un delay
            QTimer.singleShot(100, self.render_document)
        else:
            print(f"🔄 Sin cambios necesarios")
    
    def split_current_element(self):
        """Dividir elemento actual"""
        element_index = self.get_element_at_cursor()
        if element_index >= 0:
            print(f"✂️ DIVIDIENDO ELEMENTO {element_index}")
            self.document.split_element(element_index)
            
            # Crear evento de Enter manualmente
            enter_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Return, Qt.NoModifier)
            super().keyPressEvent(enter_event)
            
            # Re-renderizar después de un delay
            QTimer.singleShot(100, self.render_document)
    
    def mousePressEvent(self, event):
        """Manejar clics del mouse"""
        if event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())
        super().mousePressEvent(event)
    
    def show_context_menu(self, position):
        """Mostrar menú contextual"""
        element_index = self.get_element_at_cursor()
        
        menu = QMenu(self)
        
        # Opciones de elemento
        edit_action = menu.addAction("✏️ Editar elemento (MD)")
        edit_action.triggered.connect(lambda: self.edit_element(element_index))
        
        comment_action = menu.addAction("💬 Agregar comentario")
        comment_action.triggered.connect(lambda: self.add_comment_to_element(element_index))
        
        menu.addSeparator()
        
        # Opciones de estructura
        split_action = menu.addAction("✂️ Dividir elemento")
        split_action.triggered.connect(lambda: self.split_current_element())
        
        if element_index > 0:
            merge_action = menu.addAction("🔗 Fusionar con anterior")
            merge_action.triggered.connect(lambda: self.merge_with_previous(element_index))
        
        menu.exec(position)
    
    def edit_element(self, element_index):
        """Editar código markdown de un elemento"""
        element = self.document.get_element(element_index)
        if element:
            dialog = ElementEditDialog(self, element.markdown_code)
            if dialog.exec() == QDialog.Accepted:
                new_markdown = dialog.get_markdown()
                print(f"✏️ EDITANDO ELEMENTO {element_index}: {repr(new_markdown)}")
                self.document.update_element(element_index, new_markdown)
                self.render_document()
    
    def add_comment_to_element(self, element_index):
        """Agregar comentario a un elemento"""
        dialog = CommentDialog(self)
        if dialog.exec() == QDialog.Accepted:
            comment = dialog.get_comment()
            if comment:
                print(f"💬 AGREGANDO COMENTARIO A ELEMENTO {element_index}: {comment}")
                self.document.add_comment_to_element(element_index, comment)
                self.render_document()
    
    def merge_with_previous(self, element_index):
        """Fusionar elemento con el anterior"""
        if element_index > 0:
            print(f"🔗 FUSIONANDO ELEMENTOS {element_index-1} y {element_index}")
            self.document.merge_elements(element_index - 1, element_index)
            self.render_document()
    
    def update_comment_overlays(self):
        """Actualizar overlays de comentarios"""
        # Limpiar overlays existentes
        for overlay in self.overlays:
            overlay.deleteLater()
        self.overlays.clear()
        
        # Mostrar comentarios del elemento actual
        element_index = self.get_element_at_cursor()
        element = self.document.get_element(element_index)
        
        if element:
            comments = element.get_comments()
            for i, comment in enumerate(comments):
                overlay = CommentOverlay(comment, self)
                overlay.move(self.width() - 320, 100 + (i * 70))
                overlay.show()
                self.overlays.append(overlay)
    
    def get_markdown_content(self):
        """Obtener contenido markdown completo"""
        return self.document.get_full_markdown()

class MarkNote(QMainWindow):
    """Ventana principal de MarkNote"""
    
    def __init__(self):
        super().__init__()
        
        # Estado de la aplicación
        self.current_file = None
        self.is_wide = False
        
        # Configuración inicial
        self.setWindowTitle("MarkNote - Editor Markdown Inteligente")
        self.setGeometry(100, 100, 1400, 900)
        
        # Inicializar componentes
        self.setup_fonts()
        self.setup_ui()
        self.setup_menu()
        self.apply_theme()
        
        # Timer para actualizar estado
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # Cada 2 segundos
    
    def setup_fonts(self):
        """Configurar fuentes disponibles"""
        self.available_fonts = {
            "Roboto": "Roboto",
            "Source Serif Pro": "Source Serif Pro", 
            "Source Sans Pro": "Source Sans Pro",
            "Crimson Text": "Crimson Text",
            "Libre Baskerville": "Libre Baskerville",
            "Georgia": "Georgia",
            "Times New Roman": "Times New Roman"
        }
        
        # Verificar fuentes disponibles en el sistema
        available_system_fonts = QFontDatabase.families()
        self.working_fonts = {}
        
        for name, family in self.available_fonts.items():
            if family in available_system_fonts:
                self.working_fonts[name] = family
        
        # Fallback si no hay fuentes
        if not self.working_fonts:
            self.working_fonts = {"Georgia": "Georgia", "Times New Roman": "Times New Roman"}
    
    def setup_ui(self):
        """Configurar interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Barra de controles superior
        controls_layout = QHBoxLayout()
        
        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar en el documento...")
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self.search_text)
        
        # Controles de fuente
        font_label = QLabel("Fuente:")
        self.font_combo = QComboBox()
        self.font_combo.addItems(list(self.working_fonts.keys()))
        self.font_combo.currentTextChanged.connect(self.change_font)
        
        # Controles de zoom
        zoom_label = QLabel("Tamaño:")
        zoom_out_btn = QPushButton("A-")
        zoom_in_btn = QPushButton("A+")
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(10, 24)
        self.size_spinbox.setValue(16)
        self.size_spinbox.setSuffix("px")
        self.size_spinbox.valueChanged.connect(self.change_font_size)
        
        zoom_out_btn.clicked.connect(lambda: self.size_spinbox.setValue(self.size_spinbox.value() - 1))
        zoom_in_btn.clicked.connect(lambda: self.size_spinbox.setValue(self.size_spinbox.value() + 1))
        
        # Botón de ancho
        self.width_button = QPushButton("📏 Expandir")
        self.width_button.clicked.connect(self.toggle_width)
        
        # Barra de estado
        self.status_label = QLabel("Listo")
        
        # Agregar controles al layout
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(search_button)
        controls_layout.addWidget(QLabel("|"))
        controls_layout.addWidget(font_label)
        controls_layout.addWidget(self.font_combo)
        controls_layout.addWidget(QLabel("|"))
        controls_layout.addWidget(zoom_label)
        controls_layout.addWidget(zoom_out_btn)
        controls_layout.addWidget(self.size_spinbox)
        controls_layout.addWidget(zoom_in_btn)
        controls_layout.addWidget(QLabel("|"))
        controls_layout.addWidget(self.width_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.status_label)
        
        main_layout.addLayout(controls_layout)
        
        # Contenedor del documento con márgenes
        self.document_container = QWidget()
        container_layout = QHBoxLayout(self.document_container)
        
        # Espaciadores laterales
        self.left_spacer = QWidget()
        self.right_spacer = QWidget()
        
        # Editor principal
        self.editor = MarkdownViewer()
        
        # Configurar proporciones (60% por defecto)
        container_layout.addWidget(self.left_spacer, 2)
        container_layout.addWidget(self.editor, 6)
        container_layout.addWidget(self.right_spacer, 2)
        
        main_layout.addWidget(self.document_container)
    
    def setup_menu(self):
        """Configurar menús"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("📁 Archivo")
        
        open_action = QAction("Abrir", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Guardar", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Guardar como...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        new_element_action = QAction("Nuevo elemento", self)
        new_element_action.setShortcut(QKeySequence("Ctrl+L"))
        new_element_action.triggered.connect(self.add_new_element)
        file_menu.addAction(new_element_action)
        
        # Menú Editar
        edit_menu = menubar.addMenu("✏️ Editar")
        
        undo_action = QAction("Deshacer", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Rehacer", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        # Menú Comentarios
        comment_menu = menubar.addMenu("💬 Comentarios")
        
        add_comment_action = QAction("Agregar Comentario", self)
        add_comment_action.setShortcut(QKeySequence("Ctrl+N"))
        add_comment_action.triggered.connect(self.add_comment_current_element)
        comment_menu.addAction(add_comment_action)
    
    def apply_theme(self):
        """Aplicar tema visual"""
        self.setStyleSheet(get_main_theme())
    
    def toggle_width(self):
        """Alternar ancho del documento"""
        layout = self.document_container.layout()
        
        if not self.is_wide:
            # Expandir a 90%
            layout.setStretch(0, 1)  # left spacer
            layout.setStretch(1, 8)  # editor
            layout.setStretch(2, 1)  # right spacer
            self.width_button.setText("📏 Contraer")
            self.is_wide = True
        else:
            # Contraer a 60%
            layout.setStretch(0, 2)  # left spacer
            layout.setStretch(1, 6)  # editor
            layout.setStretch(2, 2)  # right spacer
            self.width_button.setText("📏 Expandir")
            self.is_wide = False
    
    def change_font(self, font_name):
        """Cambiar fuente del editor"""
        if font_name in self.working_fonts:
            font_family = self.working_fonts[font_name]
            self.editor.set_font_properties(font_family, self.size_spinbox.value())
    
    def change_font_size(self, size):
        """Cambiar tamaño de fuente"""
        current_font = self.font_combo.currentText()
        if current_font in self.working_fonts:
            font_family = self.working_fonts[current_font]
            self.editor.set_font_properties(font_family, size)
    
    def update_status(self):
        """Actualizar barra de estado"""
        stats = self.editor.document.get_stats()
        status_text = f"Elementos: {stats['content_elements']}/{stats['total_elements']} | "
        status_text += f"Historial: {stats['history_size']} | "
        status_text += f"Comentarios: {stats['total_comments']}"
        
        if stats['can_undo']:
            status_text += " | ↶"
        if stats['can_redo']:
            status_text += " | ↷"
            
        self.status_label.setText(status_text)
    
    def open_file(self):
        """Abrir archivo markdown"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo Markdown", "", "Archivos Markdown (*.md *.markdown *.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.current_file = file_path
                self.editor.load_markdown_file(content)
                self.setWindowTitle(f"MarkNote - {os.path.basename(file_path)}")
                
                print(f"📁 Archivo cargado: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")
    
    def save_file(self):
        """Guardar archivo actual"""
        if not self.current_file:
            return self.save_file_as()
        
        try:
            content = self.editor.get_markdown_content()
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            
            print(f"💾 Archivo guardado: {self.current_file}")
            QMessageBox.information(self, "Guardado", "Archivo guardado exitosamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{str(e)}")
    
    def save_file_as(self):
        """Guardar archivo como..."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo", "", "Archivos Markdown (*.md)"
        )
        
        if file_path:
            self.current_file = file_path
            self.save_file()
            self.setWindowTitle(f"MarkNote - {os.path.basename(file_path)}")
    
    def add_new_element(self):
        """Agregar nuevo elemento"""
        content, ok = QInputDialog.getText(
            self, "Nuevo Elemento", 
            "Contenido markdown (opcional):"
        )
        
        if ok:
            element_index = self.editor.get_element_at_cursor()
            self.editor.document.insert_element(element_index + 1, content)
            self.editor.render_document()
    
    def undo(self):
        """Deshacer cambio"""
        if self.editor.document.undo():
            self.editor.render_document()
    
    def redo(self):
        """Rehacer cambio"""
        if self.editor.document.redo():
            self.editor.render_document()
    
    def add_comment_current_element(self):
        """Agregar comentario al elemento actual"""
        element_index = self.editor.get_element_at_cursor()
        self.editor.add_comment_to_element(element_index)
    
    def search_text(self):
        """Buscar texto en el documento"""
        search_term = self.search_input.text()
        if search_term:
            self.editor.find(search_term)

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    print("🎨 MarkNote - Editor Markdown Inteligente")
    print("=" * 50)
    print("Controles:")
    print("  Enter = Procesar elemento actual (preserva/detecta MD)")
    print("  Shift+Enter = Dividir elemento")
    print("  Ctrl+Z = Deshacer | Ctrl+Y = Rehacer")
    print("  Ctrl+N = Agregar comentario")
    print("  Ctrl+L = Nuevo elemento")
    print("  Clic derecho = Menú contextual")
    print("=" * 50)
    print()
    
    # Crear y mostrar ventana principal
    window = MarkNote()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()