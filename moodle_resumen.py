import sys
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QSplitter, QLineEdit, QTextEdit, 
                               QPushButton, QLabel, QMessageBox, QFileDialog, 
                               QScrollArea, QGroupBox, QCheckBox, QFormLayout,
                               QComboBox)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QClipboard
import os

class ModuleGeneratorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Módulos Académicos - Live Preview")
        self.setGeometry(100, 100, 1400, 800)
        
        # Paletas de colores predefinidas
        self.color_palettes = {
            "Azul Académico": {
                "primary": "#2c5aa0",
                "info_bg": "#e7f3ff",
                "info_border": "#b3d9ff",
                "concepts_bg": "#d4edda",
                "concepts_border": "#c3e6cb",
                "warning_bg": "#fff3cd",
                "warning_border": "#ffeaa7"
            },
            "Verde Natura": {
                "primary": "#28a745",
                "info_bg": "#d4f8d4",
                "info_border": "#a3d9a3",
                "concepts_bg": "#e8f5e8",
                "concepts_border": "#c3e6cb",
                "warning_bg": "#fff3cd",
                "warning_border": "#ffeaa7"
            },
            "Púrpura Moderno": {
                "primary": "#6f42c1",
                "info_bg": "#f3e5ff",
                "info_border": "#d1b3ff",
                "concepts_bg": "#f8e8ff",
                "concepts_border": "#e6ccff",
                "warning_bg": "#fff3cd",
                "warning_border": "#ffeaa7"
            },
            "Naranja Energético": {
                "primary": "#fd7e14",
                "info_bg": "#fff3e0",
                "info_border": "#ffccaa",
                "concepts_bg": "#fff8f3",
                "concepts_border": "#ffe6d1",
                "warning_bg": "#fff3cd",
                "warning_border": "#ffeaa7"
            }
        }
        
        self.current_palette = "Azul Académico"
        
        # Listas dinámicas
        self.key_info_items = []
        self.practical_items = []
        self.concepts_items = []
        
        # Estados de secciones
        self.sections_enabled = {
            'header': True,
            'general': True,
            'interactive': False,
            'key_info': True,
            'practical': False,
            'concepts': True,
            'warning': False,
            'evaluation': True,
            'closing': True
        }
        
        # Timer para actualizaciones en vivo
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.setSingleShot(True)
        
        self.init_ui()
        self.add_default_items()
        self.update_preview()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo - Controles
        self.create_controls_panel(splitter)
        
        # Panel derecho - Vista previa
        self.create_preview_panel(splitter)
        
        # Configurar proporciones
        splitter.setSizes([500, 900])
        
    def create_controls_panel(self, parent):
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        # Título
        title = QLabel("Editor de Módulo")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(title)
        
        # Paleta de colores
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Paleta:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(list(self.color_palettes.keys()))
        self.color_combo.currentTextChanged.connect(self.change_color_palette)
        color_layout.addWidget(self.color_combo)
        controls_layout.addLayout(color_layout)
        
        # Botones principales
        buttons_layout = QHBoxLayout()
        
        load_json_btn = QPushButton("Cargar JSON")
        load_json_btn.clicked.connect(self.load_json)
        buttons_layout.addWidget(load_json_btn)
        
        save_json_btn = QPushButton("Guardar JSON")
        save_json_btn.clicked.connect(self.save_json)
        buttons_layout.addWidget(save_json_btn)
        
        copy_prompt_btn = QPushButton("Copiar Prompt")
        copy_prompt_btn.clicked.connect(self.copy_prompt)
        buttons_layout.addWidget(copy_prompt_btn)
        
        save_html_btn = QPushButton("Guardar HTML")
        save_html_btn.clicked.connect(self.save_html)
        buttons_layout.addWidget(save_html_btn)
        
        controls_layout.addLayout(buttons_layout)
        
        # Área de scroll para controles
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.controls_layout = QVBoxLayout(scroll_widget)
        
        self.create_all_controls()
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        controls_layout.addWidget(scroll)
        
        parent.addWidget(controls_widget)
        
    def create_all_controls(self):
        # Encabezado
        self.create_header_controls()
        
        # Información General
        self.create_general_controls()
        
        # Contenido Interactivo
        self.create_interactive_controls()
        
        # Información Clave (dinámico)
        self.create_key_info_controls()
        
        # Actividades Prácticas (dinámico)
        self.create_practical_controls()
        
        # Conceptos (dinámico)
        self.create_concepts_controls()
        
        # Aviso
        self.create_warning_controls()
        
        # Evaluación
        self.create_evaluation_controls()
        
        # Cierre
        self.create_closing_controls()
        
    def create_header_controls(self):
        group = QGroupBox("Encabezado")
        layout = QFormLayout(group)
        
        self.header_enabled = QCheckBox("Activar sección")
        self.header_enabled.setChecked(self.sections_enabled['header'])
        self.header_enabled.stateChanged.connect(self.on_section_toggle)
        layout.addRow(self.header_enabled)
        
        self.titulo_modulo = QLineEdit("Título del Módulo")
        self.titulo_modulo.textChanged.connect(self.schedule_update)
        layout.addRow("Título:", self.titulo_modulo)
        
        self.subtitulo = QLineEdit("Subtítulo Descriptivo")
        self.subtitulo.textChanged.connect(self.schedule_update)
        layout.addRow("Subtítulo:", self.subtitulo)
        
        self.controls_layout.addWidget(group)
        
    def create_general_controls(self):
        group = QGroupBox("Información General")
        layout = QFormLayout(group)
        
        self.general_enabled = QCheckBox("Activar sección")
        self.general_enabled.setChecked(self.sections_enabled['general'])
        self.general_enabled.stateChanged.connect(self.on_section_toggle)
        layout.addRow(self.general_enabled)
        
        self.descripcion_general = QTextEdit("Descripción general del módulo...")
        self.descripcion_general.setMaximumHeight(60)
        self.descripcion_general.textChanged.connect(self.schedule_update)
        layout.addRow("Descripción:", self.descripcion_general)
        
        self.objetivos = QLineEdit("Objetivo 1;Objetivo 2;Objetivo 3;Objetivo 4")
        self.objetivos.textChanged.connect(self.schedule_update)
        layout.addRow("Objetivos (separados por ;):", self.objetivos)
        
        self.modalidades = QLineEdit("Modalidad 1;Modalidad 2;Modalidad 3;Modalidad 4;Modalidad 5;Modalidad 6")
        self.modalidades.textChanged.connect(self.schedule_update)
        layout.addRow("Modalidades (separadas por ;):", self.modalidades)
        
        self.controls_layout.addWidget(group)
        
    def create_interactive_controls(self):
        group = QGroupBox("Contenido Interactivo")
        layout = QFormLayout(group)
        
        self.interactive_enabled = QCheckBox("Activar sección")
        self.interactive_enabled.setChecked(self.sections_enabled['interactive'])
        self.interactive_enabled.stateChanged.connect(self.on_section_toggle)
        layout.addRow(self.interactive_enabled)
        
        self.titulo_interactivo = QLineEdit("Modelo 3D Interactivo")
        self.titulo_interactivo.textChanged.connect(self.schedule_update)
        layout.addRow("Título:", self.titulo_interactivo)
        
        self.descripcion_interactivo = QLineEdit("Descripción del contenido...")
        self.descripcion_interactivo.textChanged.connect(self.schedule_update)
        layout.addRow("Descripción:", self.descripcion_interactivo)
        
        self.contenido_interactivo = QTextEdit('<p>Contenido interactivo aquí...</p>')
        self.contenido_interactivo.setMaximumHeight(80)
        self.contenido_interactivo.textChanged.connect(self.schedule_update)
        layout.addRow("HTML:", self.contenido_interactivo)
        
        self.controls_layout.addWidget(group)
        
    def create_key_info_controls(self):
        self.key_info_group = QGroupBox("Información Clave")
        layout = QVBoxLayout(self.key_info_group)
        
        # Header con checkbox y botón
        header_layout = QHBoxLayout()
        self.key_info_enabled = QCheckBox("Activar sección")
        self.key_info_enabled.setChecked(self.sections_enabled['key_info'])
        self.key_info_enabled.stateChanged.connect(self.on_section_toggle)
        header_layout.addWidget(self.key_info_enabled)
        
        add_key_info_btn = QPushButton("Agregar Item")
        add_key_info_btn.clicked.connect(self.add_key_info_item)
        header_layout.addWidget(add_key_info_btn)
        layout.addLayout(header_layout)
        
        # Container para items dinámicos
        self.key_info_container = QWidget()
        self.key_info_layout = QVBoxLayout(self.key_info_container)
        layout.addWidget(self.key_info_container)
        
        self.controls_layout.addWidget(self.key_info_group)
        
    def create_practical_controls(self):
        self.practical_group = QGroupBox("Actividades Prácticas")
        layout = QVBoxLayout(self.practical_group)
        
        # Header con checkbox y botón
        header_layout = QHBoxLayout()
        self.practical_enabled = QCheckBox("Activar sección")
        self.practical_enabled.setChecked(self.sections_enabled['practical'])
        self.practical_enabled.stateChanged.connect(self.on_section_toggle)
        header_layout.addWidget(self.practical_enabled)
        
        add_practical_btn = QPushButton("Agregar Actividad")
        add_practical_btn.clicked.connect(self.add_practical_item)
        header_layout.addWidget(add_practical_btn)
        layout.addLayout(header_layout)
        
        # Duración y modalidad
        info_layout = QFormLayout()
        self.duracion_practica = QLineEdit("90 min")
        self.duracion_practica.textChanged.connect(self.schedule_update)
        info_layout.addRow("Duración:", self.duracion_practica)
        
        self.modalidad_practica = QLineEdit("Laboratorio")
        self.modalidad_practica.textChanged.connect(self.schedule_update)
        info_layout.addRow("Modalidad:", self.modalidad_practica)
        layout.addLayout(info_layout)
        
        # Container para actividades dinámicas
        self.practical_container = QWidget()
        self.practical_layout = QVBoxLayout(self.practical_container)
        layout.addWidget(self.practical_container)
        
        self.controls_layout.addWidget(self.practical_group)
        
    def create_concepts_controls(self):
        self.concepts_group = QGroupBox("Conceptos Fundamentales")
        layout = QVBoxLayout(self.concepts_group)
        
        # Header con checkbox y botón
        header_layout = QHBoxLayout()
        self.concepts_enabled = QCheckBox("Activar sección")
        self.concepts_enabled.setChecked(self.sections_enabled['concepts'])
        self.concepts_enabled.stateChanged.connect(self.on_section_toggle)
        header_layout.addWidget(self.concepts_enabled)
        
        add_concept_btn = QPushButton("Agregar Concepto")
        add_concept_btn.clicked.connect(self.add_concept_item)
        header_layout.addWidget(add_concept_btn)
        layout.addLayout(header_layout)
        
        # Container para conceptos dinámicos
        self.concepts_container = QWidget()
        self.concepts_layout = QVBoxLayout(self.concepts_container)
        layout.addWidget(self.concepts_container)
        
        self.controls_layout.addWidget(self.concepts_group)
        
    def create_warning_controls(self):
        group = QGroupBox("Aviso Importante")
        layout = QFormLayout(group)
        
        self.warning_enabled = QCheckBox("Activar sección")
        self.warning_enabled.setChecked(self.sections_enabled['warning'])
        self.warning_enabled.stateChanged.connect(self.on_section_toggle)
        layout.addRow(self.warning_enabled)
        
        self.mensaje_importante = QLineEdit("Mensaje importante para el módulo")
        self.mensaje_importante.textChanged.connect(self.schedule_update)
        layout.addRow("Mensaje:", self.mensaje_importante)
        
        self.controls_layout.addWidget(group)
        
    def create_evaluation_controls(self):
        group = QGroupBox("Evaluación")
        layout = QFormLayout(group)
        
        self.evaluation_enabled = QCheckBox("Activar sección")
        self.evaluation_enabled.setChecked(self.sections_enabled['evaluation'])
        self.evaluation_enabled.stateChanged.connect(self.on_section_toggle)
        layout.addRow(self.evaluation_enabled)
        
        self.formato_formativa = QLineEdit("20")
        self.formato_formativa.textChanged.connect(self.schedule_update)
        layout.addRow("N° Preguntas Formativa:", self.formato_formativa)
        
        self.evaluaciones_adicionales = QTextEdit('<td style="vertical-align: top; padding: 8px; border: 1px solid #eee; background: #f8f9fa;">Evaluación adicional...</td>')
        self.evaluaciones_adicionales.setMaximumHeight(60)
        self.evaluaciones_adicionales.textChanged.connect(self.schedule_update)
        layout.addRow("Evaluaciones Adicionales:", self.evaluaciones_adicionales)
        
        self.criterios = QLineEdit("Criterio 1;Criterio 2;Criterio 3;Criterio 4")
        self.criterios.textChanged.connect(self.schedule_update)
        layout.addRow("Criterios (separados por ;):", self.criterios)
        
        self.controls_layout.addWidget(group)
        
    def create_closing_controls(self):
        group = QGroupBox("Cierre")
        layout = QFormLayout(group)
        
        self.closing_enabled = QCheckBox("Activar sección")
        self.closing_enabled.setChecked(self.sections_enabled['closing'])
        self.closing_enabled.stateChanged.connect(self.on_section_toggle)
        layout.addRow(self.closing_enabled)
        
        self.titulo_cierre = QLineEdit("¿Preguntas o dudas sobre el módulo?")
        self.titulo_cierre.textChanged.connect(self.schedule_update)
        layout.addRow("Título:", self.titulo_cierre)
        
        self.mensaje_cierre = QLineEdit("Use las horas de consulta.")
        self.mensaje_cierre.textChanged.connect(self.schedule_update)
        layout.addRow("Mensaje:", self.mensaje_cierre)
        
        self.controls_layout.addWidget(group)
        
    def add_default_items(self):
        # Agregar items por defecto
        self.add_key_info_item("Organización del Tallo", "Contenido técnico...")
        self.add_key_info_item("Exploración Clínica", "Contenido práctico...")
        
        self.add_practical_item("Mapa de Núcleos", "Ubicación de núcleos", "Atlas/Modelo 3D")
        self.add_practical_item("Exploración por Pares", "Protocolos estandarizados", "Guía de exploración")
        
        self.add_concept_item("Concepto 1", "Descripción del concepto 1")
        self.add_concept_item("Concepto 2", "Descripción del concepto 2")
        
    def add_key_info_item(self, titulo="Título", contenido="Contenido..."):
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        
        # Primera fila: título
        titulo_layout = QHBoxLayout()
        titulo_layout.addWidget(QLabel("Título:"))
        titulo_field = QLineEdit(titulo)
        titulo_field.textChanged.connect(self.schedule_update)
        titulo_layout.addWidget(titulo_field)
        
        remove_btn = QPushButton("X")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_key_info_item(item_widget))
        titulo_layout.addWidget(remove_btn)
        
        item_layout.addLayout(titulo_layout)
        
        # Segunda fila: contenido
        contenido_field = QTextEdit(contenido)
        contenido_field.setMaximumHeight(50)
        contenido_field.textChanged.connect(self.schedule_update)
        item_layout.addWidget(contenido_field)
        
        self.key_info_items.append({'widget': item_widget, 'titulo': titulo_field, 'contenido': contenido_field})
        self.key_info_layout.addWidget(item_widget)
        
    def add_practical_item(self, actividad="Actividad", enfoque="Enfoque", recursos="Recursos"):
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        
        # Primera fila: actividad y botón eliminar
        first_row = QHBoxLayout()
        first_row.addWidget(QLabel("Actividad:"))
        actividad_field = QLineEdit(actividad)
        actividad_field.textChanged.connect(self.schedule_update)
        first_row.addWidget(actividad_field)
        
        remove_btn = QPushButton("X")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_practical_item(item_widget))
        first_row.addWidget(remove_btn)
        item_layout.addLayout(first_row)
        
        # Segunda fila: enfoque
        second_row = QHBoxLayout()
        second_row.addWidget(QLabel("Enfoque:"))
        enfoque_field = QLineEdit(enfoque)
        enfoque_field.textChanged.connect(self.schedule_update)
        second_row.addWidget(enfoque_field)
        item_layout.addLayout(second_row)
        
        # Tercera fila: recursos
        third_row = QHBoxLayout()
        third_row.addWidget(QLabel("Recursos:"))
        recursos_field = QLineEdit(recursos)
        recursos_field.textChanged.connect(self.schedule_update)
        third_row.addWidget(recursos_field)
        item_layout.addLayout(third_row)
        
        self.practical_items.append({
            'widget': item_widget, 
            'actividad': actividad_field, 
            'enfoque': enfoque_field, 
            'recursos': recursos_field
        })
        self.practical_layout.addWidget(item_widget)
        
    def add_concept_item(self, titulo="Concepto", descripcion="Descripción"):
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        
        # Primera fila: título y botón eliminar
        first_row = QHBoxLayout()
        first_row.addWidget(QLabel("Concepto:"))
        titulo_field = QLineEdit(titulo)
        titulo_field.textChanged.connect(self.schedule_update)
        first_row.addWidget(titulo_field)
        
        remove_btn = QPushButton("X")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_concept_item(item_widget))
        first_row.addWidget(remove_btn)
        item_layout.addLayout(first_row)
        
        # Segunda fila: descripción
        descripcion_field = QLineEdit(descripcion)
        descripcion_field.textChanged.connect(self.schedule_update)
        item_layout.addWidget(descripcion_field)
        
        self.concepts_items.append({'widget': item_widget, 'titulo': titulo_field, 'descripcion': descripcion_field})
        self.concepts_layout.addWidget(item_widget)
        
    def remove_key_info_item(self, widget):
        self.key_info_items = [item for item in self.key_info_items if item['widget'] != widget]
        widget.deleteLater()
        self.schedule_update()
        
    def remove_practical_item(self, widget):
        self.practical_items = [item for item in self.practical_items if item['widget'] != widget]
        widget.deleteLater()
        self.schedule_update()
        
    def remove_concept_item(self, widget):
        self.concepts_items = [item for item in self.concepts_items if item['widget'] != widget]
        widget.deleteLater()
        self.schedule_update()
        
    def create_preview_panel(self, parent):
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_title = QLabel("Vista Previa en Tiempo Real")
        preview_title.setFont(QFont("Arial", 14, QFont.Bold))
        preview_title.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(preview_title)
        
        # Vista previa web
        self.web_view = QWebEngineView()
        preview_layout.addWidget(self.web_view)
        
        parent.addWidget(preview_widget)
        
    def change_color_palette(self, palette_name):
        self.current_palette = palette_name
        self.schedule_update()
        
    def get_current_colors(self):
        return self.color_palettes[self.current_palette]
        
    def on_section_toggle(self):
        sender = self.sender()
        if sender == self.header_enabled:
            self.sections_enabled['header'] = sender.isChecked()
        elif sender == self.general_enabled:
            self.sections_enabled['general'] = sender.isChecked()
        elif sender == self.interactive_enabled:
            self.sections_enabled['interactive'] = sender.isChecked()
        elif sender == self.key_info_enabled:
            self.sections_enabled['key_info'] = sender.isChecked()
        elif sender == self.practical_enabled:
            self.sections_enabled['practical'] = sender.isChecked()
        elif sender == self.concepts_enabled:
            self.sections_enabled['concepts'] = sender.isChecked()
        elif sender == self.warning_enabled:
            self.sections_enabled['warning'] = sender.isChecked()
        elif sender == self.evaluation_enabled:
            self.sections_enabled['evaluation'] = sender.isChecked()
        elif sender == self.closing_enabled:
            self.sections_enabled['closing'] = sender.isChecked()
        
        self.schedule_update()
        
    def schedule_update(self):
        self.update_timer.start(300)  # 300ms delay
        
    def update_preview(self):
        colors = self.get_current_colors()
        sections_html = []
        
        # Header
        if self.sections_enabled['header']:
            header_html = f'''<h2 style="text-align: center; color: {colors['primary']}; margin: 0 0 8px 0;">{self.titulo_modulo.text()}</h2>
<p style="text-align: center; margin: 0 0 16px 0;"><strong>{self.subtitulo.text()}</strong></p>'''
            sections_html.append(header_html)
            
        # General
        if self.sections_enabled['general']:
            objetivos_list = '\n'.join([f'<li>{obj.strip()}</li>' for obj in self.objetivos.text().split(';') if obj.strip()])
            modalidades_list = '\n'.join([f'<li>{mod.strip()}</li>' for mod in self.modalidades.text().split(';') if mod.strip()])
            
            general_html = f'''<div style="background: {colors['info_bg']}; border: 1px solid {colors['info_border']}; border-radius: 6px; padding: 12px; margin: 12px 0;">
    <h3 style="margin: 0 0 8px 0; color: {colors['primary']};">📚 Información General del Módulo</h3>
    <p style="margin: 0 0 12px 0;">{self.descripcion_general.toPlainText()}</p>
    <table style="width: 100%; border-collapse: collapse;" role="presentation">
      <tbody>
        <tr>
          <td style="vertical-align: top; padding: 8px; border: 1px solid {colors['info_border']};">
            <h4 style="margin: 0 0 6px 0; color: {colors['primary']};">Objetivos Principales</h4>
            <ul style="margin: 0 0 0 16px; padding: 0;">
              {objetivos_list}
            </ul>
          </td>
          <td style="vertical-align: top; padding: 8px; border: 1px solid {colors['info_border']};">
            <h4 style="margin: 0 0 6px 0; color: {colors['primary']};">Modalidades de Aprendizaje</h4>
            <ul style="margin: 0 0 0 16px; padding: 0;">
              {modalidades_list}
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
  </div>'''
            sections_html.append(general_html)
            
        # Interactive
        if self.sections_enabled['interactive']:
            interactive_html = f'''<h3 style="color: {colors['primary']}; margin: 16px 0 8px 0;">🧠 {self.titulo_interactivo.text()}</h3>
<div style="border: 2px solid {colors['primary']}; border-radius: 6px; padding: 12px; margin: 8px 0;">
    <p style="margin: 0 0 8px 0;"><strong>Explore:</strong> {self.descripcion_interactivo.text()}</p>
    {self.contenido_interactivo.toPlainText()}
</div>'''
            sections_html.append(interactive_html)
            
        # Key Info
        if self.sections_enabled['key_info'] and self.key_info_items:
            # Crear filas de 2 columnas
            key_info_rows = []
            for i in range(0, len(self.key_info_items), 2):
                item1 = self.key_info_items[i]
                item2 = self.key_info_items[i+1] if i+1 < len(self.key_info_items) else None
                
                col1 = f'''<td style="vertical-align: top; padding: 8px; border: 1px solid #eee; background: #f8f9fa;">
            <h4 style="margin: 0 0 6px 0; color: {colors['primary']};">{item1['titulo'].text()}</h4>
            {item1['contenido'].toPlainText().replace(chr(10), '<br>')}
          </td>'''
                
                if item2:
                    col2 = f'''<td style="vertical-align: top; padding: 8px; border: 1px solid #eee; background: #f8f9fa;">
            <h4 style="margin: 0 0 6px 0; color: {colors['primary']};">{item2['titulo'].text()}</h4>
            {item2['contenido'].toPlainText().replace(chr(10), '<br>')}
          </td>'''
                else:
                    col2 = '<td style="vertical-align: top; padding: 8px; border: 1px solid #eee; background: #f8f9fa;"></td>'
                
                key_info_rows.append(f'<tr>{col1}{col2}</tr>')
            
            key_info_tables = '\n'.join([f'<table style="width: 100%; border-collapse: collapse; margin-top: 8px;" role="presentation"><tbody>{row}</tbody></table>' for row in key_info_rows])
            
            key_info_html = f'''<h3 style="color: {colors['primary']}; margin: 16px 0 8px 0;">📖 Información Clave</h3>
{key_info_tables}'''
            sections_html.append(key_info_html)
            
        # Practical
        if self.sections_enabled['practical'] and self.practical_items:
            practical_rows = []
            for item in self.practical_items:
                practical_rows.append(f'''<tr>
        <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>{item['actividad'].text()}</strong></td>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">{item['enfoque'].text()}</td>
        <td style="padding: 8px; border-bottom: 1px solid #eee;">{item['recursos'].text()}</td>
      </tr>''')
            
            practical_html = f'''<h3 style="color: {colors['primary']}; margin: 16px 0 8px 0;">🔬 Actividades del Práctico</h3>
<div style="background: {colors['info_bg']}; border: 1px solid {colors['info_border']}; border-radius: 6px; padding: 8px; margin: 8px 0;">
    <p style="margin: 0;"><strong>Duración:</strong> {self.duracion_practica.text()} · <strong>Modalidad:</strong> {self.modalidad_practica.text()}</p>
</div>
<table style="width: 100%; border-collapse: collapse;">
    <thead>
      <tr>
        <th style="text-align: left; background: {colors['primary']}; color: #fff; padding: 8px;">Actividad</th>
        <th style="text-align: left; background: {colors['primary']}; color: #fff; padding: 8px;">Enfoque</th>
        <th style="text-align: left; background: {colors['primary']}; color: #fff; padding: 8px;">Recursos</th>
      </tr>
    </thead>
    <tbody>
      {''.join(practical_rows)}
    </tbody>
</table>'''
            sections_html.append(practical_html)
            
        # Concepts
        if self.sections_enabled['concepts'] and self.concepts_items:
            concepts_list = '\n'.join([f'<li><strong>{item["titulo"].text()}:</strong> {item["descripcion"].text()}</li>' 
                                     for item in self.concepts_items if item['titulo'].text().strip()])
            
            concepts_html = f'''<div style="background: {colors['concepts_bg']}; border: 1px solid {colors['concepts_border']}; border-radius: 6px; padding: 12px; margin: 12px 0;">
    <h3 style="margin: 0 0 8px 0;">💡 Conceptos Fundamentales</h3>
    <ul style="margin: 0 0 0 16px; padding: 0;">
      {concepts_list}
    </ul>
</div>'''
            sections_html.append(concepts_html)
            
        # Warning
        if self.sections_enabled['warning']:
            warning_html = f'''<div style="background: {colors['warning_bg']}; border: 1px solid {colors['warning_border']}; border-radius: 6px; padding: 12px; margin: 12px 0;">
    <p style="margin: 0;"><strong>⚠️ Importante:</strong> {self.mensaje_importante.text()}</p>
</div>'''
            sections_html.append(warning_html)
            
        # Evaluation
        if self.sections_enabled['evaluation']:
            criterios_list = '\n'.join([f'<li><strong>{crit.strip()}</strong></li>' 
                                       for crit in self.criterios.text().split(';') if crit.strip()])
            
            evaluation_html = f'''<h3 style="color: {colors['primary']}; margin: 16px 0 8px 0;">📋 Sistema de Evaluación</h3>
<table style="width: 100%; border-collapse: collapse;" role="presentation">
    <tbody>
      <tr>
        <td style="vertical-align: top; padding: 8px; border: 1px solid #eee; background: #f8f9fa;">
          <h4 style="margin: 0 0 6px 0; color: {colors['primary']};">Evaluación Formativa</h4>
          <p style="margin: 6px 0;"><strong>Formato:</strong> {self.formato_formativa.text()} preguntas GIFT</p>
          <p style="margin: 6px 0;"><strong>Propósito:</strong> Retroalimentación inmediata</p>
          <p style="margin: 6px 0;"><strong>Disponibilidad:</strong> Práctica ilimitada</p>
        </td>
        {self.evaluaciones_adicionales.toPlainText()}
      </tr>
    </tbody>
</table>
<div style="background: {colors['concepts_bg']}; border: 1px solid {colors['concepts_border']}; border-radius: 6px; padding: 12px; margin: 12px 0;">
    <h4 style="margin: 0 0 6px 0;">Criterios de Evaluación</h4>
    <ul style="margin: 0 0 0 16px; padding: 0;">
      {criterios_list}
    </ul>
</div>'''
            sections_html.append(evaluation_html)
            
        # Closing
        if self.sections_enabled['closing']:
            closing_html = f'''<div style="text-align: center; margin-top: 20px; padding: 12px; background: #f8f9fa; border: 1px solid #eee; border-radius: 6px;">
    <h4 style="margin: 0 0 6px 0;">{self.titulo_cierre.text()}</h4>
    <p style="margin: 0;">{self.mensaje_cierre.text()}</p>
</div>'''
            sections_html.append(closing_html)
        
        # Generar HTML final para Moodle (solo el div principal)
        moodle_html = f'''<div style="max-width: 900px; margin: 0 auto; padding: 16px; background: #ffffff; color: #333; font-family: Arial,Helvetica,sans-serif; line-height: 1.5; border: 1px solid #ddd; border-radius: 6px;">
  
{''.join(sections_html)}
  
</div>'''
        
        # Para vista previa, agregar wrapper HTML
        preview_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Vista Previa</title>
    <style>body {{ margin: 0; padding: 20px; background: #f5f5f5; }}</style>
</head>
<body>
{moodle_html}
</body>
</html>'''
        
        self.web_view.setHtml(preview_html)
        self.current_html = moodle_html  # Solo el div para Moodle
        
    def collect_all_data(self):
        """Recopila todos los datos del formulario"""
        return {
            "titulo_modulo": self.titulo_modulo.text(),
            "subtitulo": self.subtitulo.text(),
            "descripcion_general": self.descripcion_general.toPlainText(),
            "objetivos": self.objetivos.text(),
            "modalidades": self.modalidades.text(),
            "titulo_interactivo": self.titulo_interactivo.text(),
            "descripcion_interactivo": self.descripcion_interactivo.text(),
            "contenido_interactivo": self.contenido_interactivo.toPlainText(),
            "key_info_items": [
                {
                    "titulo": item['titulo'].text(),
                    "contenido": item['contenido'].toPlainText()
                }
                for item in self.key_info_items
            ],
            "practical_items": [
                {
                    "actividad": item['actividad'].text(),
                    "enfoque": item['enfoque'].text(),
                    "recursos": item['recursos'].text()
                }
                for item in self.practical_items
            ],
            "duracion_practica": self.duracion_practica.text(),
            "modalidad_practica": self.modalidad_practica.text(),
            "concepts_items": [
                {
                    "titulo": item['titulo'].text(),
                    "descripcion": item['descripcion'].text()
                }
                for item in self.concepts_items
            ],
            "mensaje_importante": self.mensaje_importante.text(),
            "formato_formativa": self.formato_formativa.text(),
            "evaluaciones_adicionales": self.evaluaciones_adicionales.toPlainText(),
            "criterios": self.criterios.text(),
            "titulo_cierre": self.titulo_cierre.text(),
            "mensaje_cierre": self.mensaje_cierre.text(),
            "sections_enabled": self.sections_enabled.copy(),
            "current_palette": self.current_palette
        }
        
    def load_json(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Cargar Configuración JSON", 
            "", 
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Cargar datos básicos
                self.titulo_modulo.setText(data.get('titulo_modulo', ''))
                self.subtitulo.setText(data.get('subtitulo', ''))
                self.descripcion_general.setPlainText(data.get('descripcion_general', ''))
                self.objetivos.setText(data.get('objetivos', ''))
                self.modalidades.setText(data.get('modalidades', ''))
                
                # Cargar contenido interactivo
                self.titulo_interactivo.setText(data.get('titulo_interactivo', ''))
                self.descripcion_interactivo.setText(data.get('descripcion_interactivo', ''))
                self.contenido_interactivo.setPlainText(data.get('contenido_interactivo', ''))
                
                # Cargar datos prácticos
                self.duracion_practica.setText(data.get('duracion_practica', ''))
                self.modalidad_practica.setText(data.get('modalidad_practica', ''))
                
                # Cargar evaluación
                self.formato_formativa.setText(data.get('formato_formativa', ''))
                self.evaluaciones_adicionales.setPlainText(data.get('evaluaciones_adicionales', ''))
                self.criterios.setText(data.get('criterios', ''))
                
                # Cargar otros
                self.mensaje_importante.setText(data.get('mensaje_importante', ''))
                self.titulo_cierre.setText(data.get('titulo_cierre', ''))
                self.mensaje_cierre.setText(data.get('mensaje_cierre', ''))
                
                # Cargar paleta
                if data.get('current_palette') in self.color_palettes:
                    self.color_combo.setCurrentText(data.get('current_palette'))
                    self.current_palette = data.get('current_palette')
                
                # Cargar estados de secciones
                sections_enabled = data.get('sections_enabled', {})
                for key, value in sections_enabled.items():
                    if key in self.sections_enabled:
                        self.sections_enabled[key] = value
                
                # Actualizar checkboxes
                self.header_enabled.setChecked(self.sections_enabled.get('header', True))
                self.general_enabled.setChecked(self.sections_enabled.get('general', True))
                self.interactive_enabled.setChecked(self.sections_enabled.get('interactive', False))
                self.key_info_enabled.setChecked(self.sections_enabled.get('key_info', True))
                self.practical_enabled.setChecked(self.sections_enabled.get('practical', False))
                self.concepts_enabled.setChecked(self.sections_enabled.get('concepts', True))
                self.warning_enabled.setChecked(self.sections_enabled.get('warning', False))
                self.evaluation_enabled.setChecked(self.sections_enabled.get('evaluation', True))
                self.closing_enabled.setChecked(self.sections_enabled.get('closing', True))
                
                # Limpiar items dinámicos existentes
                for item in self.key_info_items:
                    item['widget'].deleteLater()
                self.key_info_items.clear()
                
                for item in self.practical_items:
                    item['widget'].deleteLater()
                self.practical_items.clear()
                
                for item in self.concepts_items:
                    item['widget'].deleteLater()
                self.concepts_items.clear()
                
                # Cargar items dinámicos
                for item_data in data.get('key_info_items', []):
                    self.add_key_info_item(item_data.get('titulo', ''), item_data.get('contenido', ''))
                
                for item_data in data.get('practical_items', []):
                    self.add_practical_item(
                        item_data.get('actividad', ''),
                        item_data.get('enfoque', ''),
                        item_data.get('recursos', '')
                    )
                
                for item_data in data.get('concepts_items', []):
                    self.add_concept_item(item_data.get('titulo', ''), item_data.get('descripcion', ''))
                
                self.update_preview()
                QMessageBox.information(self, "Éxito", "Configuración cargada correctamente!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar el archivo: {str(e)}")
    
    def save_json(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar Configuración JSON", 
            "modulo_config.json", 
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                data = self.collect_all_data()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "Éxito", f"Configuración guardada en: {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar el archivo: {str(e)}")
    
    def copy_prompt(self):
        """Copia al portapapeles un prompt para que un LLM genere el JSON"""
        prompt = f'''# Prompt para Generar Módulo Académico

Genera un JSON completo para un módulo académico con la siguiente estructura. Completa todos los campos con contenido específico y coherente para el tema solicitado.

**TEMA DEL MÓDULO:** [INSERTAR TEMA AQUÍ]

**ESTRUCTURA JSON REQUERIDA:**

```json
{{
  "titulo_modulo": "Título del módulo específico",
  "subtitulo": "Subtítulo descriptivo del módulo",
  "descripcion_general": "Descripción detallada del módulo y su propósito",
  "objetivos": "Objetivo 1;Objetivo 2;Objetivo 3;Objetivo 4",
  "modalidades": "Modalidad 1;Modalidad 2;Modalidad 3;Modalidad 4;Modalidad 5;Modalidad 6",
  "titulo_interactivo": "Título del contenido interactivo",
  "descripcion_interactivo": "Descripción del contenido interactivo",
  "contenido_interactivo": "<p>HTML del contenido interactivo</p>",
  "key_info_items": [
    {{"titulo": "Sección técnica 1", "contenido": "Contenido técnico detallado"}},
    {{"titulo": "Sección práctica 1", "contenido": "Contenido práctico detallado"}}
  ],
  "practical_items": [
    {{"actividad": "Actividad 1", "enfoque": "Enfoque de la actividad", "recursos": "Recursos necesarios"}},
    {{"actividad": "Actividad 2", "enfoque": "Enfoque de la actividad", "recursos": "Recursos necesarios"}}
  ],
  "duracion_practica": "90 min",
  "modalidad_practica": "Laboratorio",
  "concepts_items": [
    {{"titulo": "Concepto 1", "descripcion": "Explicación del concepto"}},
    {{"titulo": "Concepto 2", "descripcion": "Explicación del concepto"}}
  ],
  "mensaje_importante": "Mensaje importante específico para el módulo",
  "formato_formativa": "20",
  "evaluaciones_adicionales": "<td>HTML de evaluaciones adicionales</td>",
  "criterios": "Criterio 1;Criterio 2;Criterio 3;Criterio 4",
  "titulo_cierre": "Título para la sección de cierre",
  "mensaje_cierre": "Mensaje de cierre específico",
  "sections_enabled": {{
    "header": true,
    "general": true,
    "interactive": true,
    "key_info": true,
    "practical": true,
    "concepts": true,
    "warning": true,
    "evaluation": true,
    "closing": true
  }},
  "current_palette": "Azul Académico"
}}
```

**INSTRUCCIONES:**
1. Adapta TODO el contenido al tema específico solicitado
2. Los objetivos deben seguir taxonomía de Bloom
3. Las modalidades deben ser realistas y variadas
4. Incluye 2-4 items en key_info_items, practical_items y concepts_items
5. El contenido debe ser académicamente riguroso
6. Ajusta las secciones habilitadas según la relevancia para el tema
7. Genera contenido específico, evita generalidades

**Responde ÚNICAMENTE con el JSON válido, sin texto adicional.**'''
        
        clipboard = QApplication.clipboard()
        clipboard.setText(prompt)
        QMessageBox.information(self, "Prompt Copiado", 
                              "El prompt ha sido copiado al portapapeles.\n"
                              "Puedes pegarlo en tu LLM favorito especificando el tema del módulo.")
    
    def save_html(self):
        if not hasattr(self, 'current_html'):
            self.update_preview()
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar HTML para Moodle", 
            "modulo_moodle.html", 
            "HTML Files (*.html)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.current_html)
                
                QMessageBox.information(self, "Éxito", 
                                      f"HTML para Moodle guardado en: {filename}\n\n"
                                      "Puedes copiar y pegar este contenido directamente "
                                      "en el editor HTML de Moodle.")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar el archivo: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Verificar si QWebEngineView está disponible
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        QMessageBox.critical(None, "Error", 
                           "QWebEngineView no está disponible.\n"
                           "Instale: pip install PySide6-WebEngine")
        sys.exit(1)
    
    window = ModuleGeneratorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()