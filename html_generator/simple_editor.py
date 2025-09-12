import sys
import json
import os
import tempfile
import webbrowser
import threading
import http.server
import socketserver
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QSplitter, QScrollArea, QGroupBox,
                               QCheckBox, QLineEdit, QTextEdit, QPushButton,
                               QLabel, QFormLayout, QListWidget, QTabWidget,
                               QColorDialog, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtWebEngineWidgets import QWebEngineView
from html_generator import FlexibleHTMLGenerator



class HTMLEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor Visual HTML - FIUF UACh")
        self.setGeometry(100, 100, 1400, 800)

        # Configurar servidor HTTP
        self.server_port = 8888
        self.server_thread = None
        self.httpd = None
        self.temp_dir = tempfile.mkdtemp()

        self.load_site_data()
        self.setup_ui()
        self.setup_menu()
        self.start_server()
        self.update_preview()
        

    def start_server(self):
        """Iniciar servidor HTTP en hilo separado"""
        def run_server():
            os.chdir(self.temp_dir)
            Handler = http.server.SimpleHTTPRequestHandler
            Handler.log_message = lambda *args: None  # Silenciar logs
            self.httpd = socketserver.TCPServer(("", self.server_port), Handler)
            self.httpd.serve_forever()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        print(f"Servidor HTTP iniciado en puerto {self.server_port}")

    def load_site_data(self):
        """Cargar datos del sitio"""
        try:
            with open('site_structure.json', 'r', encoding='utf-8') as f:
                self.site_data = json.load(f)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "No se encontró site_structure.json")
            sys.exit(1)
            
    def save_site_data(self):
        """Guardar datos del sitio"""
        try:
            with open('site_structure.json', 'w', encoding='utf-8') as f:
                json.dump(self.site_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {e}")
            
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel editor
        self.setup_editor_panel(splitter)
        # Panel preview  
        self.setup_preview_panel(splitter)
        
        splitter.setSizes([500, 900])
        
    def setup_editor_panel(self, parent):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(500)
        scroll.setMaximumWidth(600)
        parent.addWidget(scroll)
        
        editor_widget = QWidget()
        scroll.setWidget(editor_widget)
        layout = QVBoxLayout(editor_widget)
        
        # Configuración general
        self.setup_general_config(layout)
        
        # Tabs para secciones
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        self.setup_section_tabs()
        
    def setup_general_config(self, layout):
        general_group = QGroupBox("Configuración General")
        form = QFormLayout(general_group)
        
        self.title_edit = QLineEdit(self.site_data['general']['title'])
        self.title_edit.textChanged.connect(self.on_data_changed)
        form.addRow("Título:", self.title_edit)
        
        self.description_edit = QTextEdit(self.site_data['general']['description'])
        self.description_edit.setMaximumHeight(80)
        self.description_edit.textChanged.connect(self.on_data_changed)
        form.addRow("Descripción:", self.description_edit)
        
        # Colores
        color_layout = QHBoxLayout()
        
        self.primary_color_btn = QPushButton()
        self.primary_color_btn.setStyleSheet(f"background-color: {self.site_data['general']['primary_color']}; min-height: 30px;")
        self.primary_color_btn.clicked.connect(lambda: self.choose_color('primary_color'))
        
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.setStyleSheet(f"background-color: {self.site_data['general']['secondary_color']}; min-height: 30px;")
        self.secondary_color_btn.clicked.connect(lambda: self.choose_color('secondary_color'))
        
        color_layout.addWidget(QLabel("Primario:"))
        color_layout.addWidget(self.primary_color_btn)
        color_layout.addWidget(QLabel("Secundario:"))
        color_layout.addWidget(self.secondary_color_btn)
        
        form.addRow("Colores:", color_layout)
        layout.addWidget(general_group)
        
    def setup_section_tabs(self):
        """Crear tabs dinámicamente basado en estructura"""
        for section_name, section_data in self.site_data['sections'].items():
            if section_name == 'footer':  # Footer no necesita edición
                continue
                
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            # Checkbox para habilitar/deshabilitar
            checkbox = QCheckBox(f"Activar {section_name.title()}")
            checkbox.setChecked(section_data.get('enabled', False))
            checkbox.toggled.connect(lambda checked, name=section_name: self.toggle_section(name, checked))
            tab_layout.addWidget(checkbox)
            
            # Campos editables
            self.create_section_fields(tab_layout, section_name, section_data)
            
            tab_layout.addStretch()
            self.tabs.addTab(tab, section_name.title())
            
    def create_section_fields(self, layout, section_name, section_data):
        """Crear campos de edición para una sección"""
        form = QFormLayout()
        
        # Campos básicos
        basic_fields = ['eyebrow', 'title', 'description', 'text', 'btn_primary', 'btn_secondary', 'email', 'phone', 'address']
        
        for field in basic_fields:
            if field in section_data:
                if field in ['description', 'text', 'address']:
                    widget = QTextEdit(section_data[field])
                    widget.setMaximumHeight(80)
                else:
                    widget = QLineEdit(section_data[field])
                    
                widget.textChanged.connect(lambda: self.on_data_changed())
                form.addRow(f"{field.title()}:", widget)
                setattr(self, f"{section_name}_{field}", widget)
                
        layout.addLayout(form)
        
        # Elementos iterativos
        iterative_fields = ['cards', 'timeline', 'news', 'resources']
        for field in iterative_fields:
            if field in section_data:
                self.create_iterative_section(layout, section_name, field, section_data[field])
                
    def create_iterative_section(self, layout, section_name, field_name, items):
        """Crear sección para elementos iterativos"""
        group = QGroupBox(field_name.title())
        group_layout = QVBoxLayout(group)
        
        list_widget = QListWidget()
        self.update_item_list(list_widget, items)
        group_layout.addWidget(list_widget)
        
        # Botones
        btn_layout = QHBoxLayout()
        add_btn = QPushButton(f"Agregar {field_name[:-1]}")
        add_btn.clicked.connect(lambda: self.add_item(section_name, field_name, list_widget))
        
        remove_btn = QPushButton(f"Eliminar {field_name[:-1]}")
        remove_btn.clicked.connect(lambda: self.remove_item(section_name, field_name, list_widget))
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        group_layout.addLayout(btn_layout)
        
        layout.addWidget(group)
        setattr(self, f"{section_name}_{field_name}_list", list_widget)
        
    def update_item_list(self, list_widget, items):
        """Actualizar lista de elementos"""
        list_widget.clear()
        for item in items:
            if isinstance(item, dict):
                title = item.get('title', item.get('pill', 'Item'))
                list_widget.addItem(title)
                
    def add_item(self, section_name, field_name, list_widget):
        """Agregar nuevo elemento"""
        # Plantillas por defecto para nuevos elementos
        templates = {
            'cards': {'pill': 'Nueva', 'title': 'Nuevo Título', 'text': 'Nuevo texto'},
            'timeline': {'title': 'Nueva Etapa', 'text': 'Descripción de la etapa'},
            'news': {'icon': '📰', 'title': 'Nueva Noticia', 'meta': 'Fecha', 'text': 'Contenido'},
            'resources': {'icon': '📄', 'title': 'Nuevo Recurso', 'text': 'Descripción'}
        }
        
        new_item = templates.get(field_name, {'title': 'Nuevo Item'})
        self.site_data['sections'][section_name][field_name].append(new_item)
        self.update_item_list(list_widget, self.site_data['sections'][section_name][field_name])
        self.schedule_update()
        
    def remove_item(self, section_name, field_name, list_widget):
        """Eliminar elemento seleccionado"""
        current_row = list_widget.currentRow()
        if current_row >= 0:
            del self.site_data['sections'][section_name][field_name][current_row]
            self.update_item_list(list_widget, self.site_data['sections'][section_name][field_name])
            self.schedule_update()
            
    def toggle_section(self, section_name, enabled):
        """Activar/desactivar sección"""
        self.site_data['sections'][section_name]['enabled'] = enabled
        self.schedule_update()
        
    def choose_color(self, color_type):
        """Selector de color"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            self.site_data['general'][color_type] = color_hex
            
            if color_type == 'primary_color':
                self.primary_color_btn.setStyleSheet(f"background-color: {color_hex}; min-height: 30px;")
            else:
                self.secondary_color_btn.setStyleSheet(f"background-color: {color_hex}; min-height: 30px;")
            
            self.schedule_update()
            
    def on_data_changed(self):
        """Actualizar datos cuando cambian los campos"""
        # Actualizar configuración general
        self.site_data['general']['title'] = self.title_edit.text()
        self.site_data['general']['description'] = self.description_edit.toPlainText()
        
        # Actualizar campos de secciones
        for section_name in self.site_data['sections']:
            section_data = self.site_data['sections'][section_name]
            for field in ['eyebrow', 'title', 'description', 'text', 'btn_primary', 'btn_secondary', 'email', 'phone', 'address']:
                widget = getattr(self, f"{section_name}_{field}", None)
                if widget:
                    if isinstance(widget, QTextEdit):
                        section_data[field] = widget.toPlainText()
                    else:
                        section_data[field] = widget.text()
                        
        self.schedule_update()
        

    def setup_preview_panel(self, parent):
        """Panel de preview con navegador web real"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        # Controles
        controls_layout = QHBoxLayout()

        # Botón refresh
        refresh_btn = QPushButton("🔄 Recargar")
        refresh_btn.clicked.connect(self.reload_preview)
        controls_layout.addWidget(refresh_btn)

        # Botón para abrir en navegador externo
        open_browser_btn = QPushButton("🌐 Abrir en Navegador Externo")
        open_browser_btn.clicked.connect(self.open_in_browser)
        controls_layout.addWidget(open_browser_btn)

        # Label con URL
        self.url_label = QLabel(f"Preview: http://localhost:{self.server_port}/")
        controls_layout.addWidget(self.url_label)
        controls_layout.addStretch()

        preview_layout.addLayout(controls_layout)

        # Vista web
        self.preview_browser = QWebEngineView()
        self.preview_browser.setMinimumWidth(800)
        preview_layout.addWidget(self.preview_browser)

        parent.addWidget(preview_widget)


        
    def setup_menu(self):
        """Configurar menú de la aplicación"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('Archivo')
        
        save_action = file_menu.addAction('Guardar Proyecto')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        
        load_action = file_menu.addAction('Cargar Proyecto')
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_project)
        
        file_menu.addSeparator()
        
        export_action = file_menu.addAction('Exportar HTML')
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.export_html)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction('Salir')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
    def schedule_update(self):
        """Programar actualización del preview"""
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        
        self.update_timer.start(500)
        
    def update_preview(self):
        """Actualizar preview HTML"""
        try:
            generator = FlexibleHTMLGenerator(self.site_data)
            html_content = generator.generate_html()

            # Guardar HTML en directorio temporal
            html_path = os.path.join(self.temp_dir, "index.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Cargar en el navegador
            self.preview_browser.setUrl(QUrl(f"http://localhost:{self.server_port}/"))

            self.save_site_data()  # Auto-guardar
        except Exception as e:
            error_html = f"<h1>Error generando HTML:</h1><pre>{e}</pre>"
            html_path = os.path.join(self.temp_dir, "index.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(error_html)
            self.preview_browser.reload()

            
    def reload_preview(self):
        """Recargar preview manualmente"""
        self.preview_browser.reload()

    def open_in_browser(self):
        """Abrir preview en navegador externo"""
        webbrowser.open(f'http://localhost:{self.server_port}/')

            
    def save_project(self):
        """Guardar proyecto"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar Proyecto", "", "JSON Files (*.json)"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.site_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Éxito", "Proyecto guardado")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar: {e}")
                
    def load_project(self):
        """Cargar proyecto"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Cargar Proyecto", "", "JSON Files (*.json)"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.site_data = json.load(f)
                self.refresh_ui()
                self.update_preview()
                QMessageBox.information(self, "Éxito", "Proyecto cargado")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar: {e}")
                
    def export_html(self):
        """Exportar HTML final"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exportar HTML", "", "HTML Files (*.html)"
        )
        if filename:
            try:
                generator = FlexibleHTMLGenerator(self.site_data)
                html_content = generator.generate_html()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                QMessageBox.information(self, "Éxito", "HTML exportado")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar: {e}")
                
    def refresh_ui(self):
        """Refrescar UI después de cargar proyecto"""
        # Actualizar campos generales
        self.title_edit.setText(self.site_data['general']['title'])
        self.description_edit.setPlainText(self.site_data['general']['description'])
        
        # Actualizar botones de color
        self.primary_color_btn.setStyleSheet(f"background-color: {self.site_data['general']['primary_color']}; min-height: 30px;")
        self.secondary_color_btn.setStyleSheet(f"background-color: {self.site_data['general']['secondary_color']}; min-height: 30px;")
        
        # Recrear tabs
        self.tabs.clear()
        self.setup_section_tabs()

    def closeEvent(self, event):
        """Limpiar al cerrar"""
        if self.httpd:
            self.httpd.shutdown()
        # Limpiar directorio temporal
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Verificar archivos necesarios
    required_files = ['site_structure.json', 'css_templates.json', 'section_templates.json']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Error: Faltan archivos necesarios: {', '.join(missing_files)}")
        print("Asegúrate de tener todos los archivos JSON en el mismo directorio.")
        return 1
        
    window = HTMLEditor()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
