import sys
import json
import os
import tempfile
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QScrollArea, QGroupBox, QCheckBox, QLineEdit, QTextEdit, QPushButton,
    QLabel, QFormLayout, QListWidget, QTabWidget, QColorDialog, QFileDialog,
    QMessageBox, QToolButton, QSizePolicy, QComboBox
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWebEngineWidgets import QWebEngineView

from html_generator import FlexibleHTMLGenerator


class HTMLEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor Visual HTML (sin servidor) - FIUF UACh")
        self.setGeometry(100, 100, 1400, 800)

        self.temp_dir = tempfile.mkdtemp()
        self.last_export_path = None

        self.load_site_data()
        self.setup_ui()
        self.setup_menu()
        self.update_preview()

    # ---------------------- Carga/guardado ----------------------
    def load_site_data(self):
        try:
            with open('site_structure.json', 'r', encoding='utf-8') as f:
                self.site_data = json.load(f)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", "No se encontró site_structure.json")
            sys.exit(1)

    def save_site_data(self):
        try:
            with open('site_structure.json', 'w', encoding='utf-8') as f:
                json.dump(self.site_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {e}")

    # ---------------------------- UI ----------------------------
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        self.setup_editor_panel(splitter)
        self.setup_preview_panel(splitter)

        splitter.setSizes([580, 820])

    def setup_editor_panel(self, parent):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(560)
        scroll.setMaximumWidth(680)
        parent.addWidget(scroll)

        editor_widget = QWidget()
        scroll.setWidget(editor_widget)
        layout = QVBoxLayout(editor_widget)

        # --- Head config
        self.setup_head_config(layout)

        # --- Configuración general
        self.setup_general_config(layout)

        # --- Secciones (tabs)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.setup_section_tabs()

    def setup_head_config(self, layout):
        head_group = QGroupBox("<head> Configuración")
        form = QFormLayout(head_group)
        head = self.site_data.get('head', {})

        self.head_lang = QLineEdit(head.get('lang', 'es'))
        self.head_title = QLineEdit(head.get('title', self.site_data['general']['title']))
        self.head_desc = QTextEdit(head.get('meta_description', self.site_data['general']['description']))
        self.head_desc.setMaximumHeight(80)
        self.head_robots = QLineEdit(head.get('meta_robots', 'index,follow'))
        self.head_charset = QLineEdit(head.get('charset', 'UTF-8'))
        self.head_favicon = QLineEdit(head.get('favicon_url', ''))
        self.head_no_cache = QCheckBox("Desactivar caché")
        self.head_no_cache.setChecked(head.get('disable_cache', False))

        form.addRow("lang:", self.head_lang)
        form.addRow("title:", self.head_title)
        form.addRow("description:", self.head_desc)
        form.addRow("robots:", self.head_robots)
        form.addRow("charset:", self.head_charset)
        form.addRow("favicon url:", self.head_favicon)
        form.addRow("", self.head_no_cache)

        # Conectar cambios
        for w in [self.head_lang, self.head_title, self.head_robots, self.head_charset, self.head_favicon]:
            w.textChanged.connect(self.on_head_changed)
        self.head_desc.textChanged.connect(self.on_head_changed)
        self.head_no_cache.toggled.connect(self.on_head_changed)

        layout.addWidget(head_group)

    def on_head_changed(self):
        self.site_data.setdefault('head', {})
        self.site_data['head']['lang'] = self.head_lang.text()
        self.site_data['head']['title'] = self.head_title.text()
        self.site_data['head']['meta_description'] = self.head_desc.toPlainText()
        self.site_data['head']['meta_robots'] = self.head_robots.text()
        self.site_data['head']['charset'] = self.head_charset.text()
        self.site_data['head']['favicon_url'] = self.head_favicon.text()
        self.site_data['head']['disable_cache'] = self.head_no_cache.isChecked()
        self.schedule_update()

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
        self.primary_color_btn = QPushButton("Primario")
        self.primary_color_btn.setStyleSheet(
            f"background-color: {self.site_data['general']['primary_color']}; min-height: 28px;"
        )
        self.primary_color_btn.clicked.connect(lambda: self.choose_color('primary_color'))

        self.secondary_color_btn = QPushButton("Secundario")
        self.secondary_color_btn.setStyleSheet(
            f"background-color: {self.site_data['general']['secondary_color']}; min-height: 28px;"
        )
        self.secondary_color_btn.clicked.connect(lambda: self.choose_color('secondary_color'))

        color_layout.addWidget(self.primary_color_btn)
        color_layout.addWidget(self.secondary_color_btn)

        form.addRow("Colores:", color_layout)
        layout.addWidget(general_group)

    def setup_section_tabs(self):
        sections = self.site_data['sections']

        # Header tab
        header_tab = QWidget()
        h_layout = QVBoxLayout(header_tab)
        h_enable = QCheckBox("Activar Header")
        h_enable.setChecked(sections['header'].get('enabled', True))
        h_enable.toggled.connect(lambda c: self.toggle_section('header', c))
        h_layout.addWidget(h_enable)

        h_form = QFormLayout()
        self.header_title = QLineEdit(sections['header'].get('title', ''))
        self.header_logo = QLineEdit(sections['header'].get('logo_url', ''))
        self.header_link = QLineEdit(sections['header'].get('logo_link', 'https://'))

        for w in [self.header_title, self.header_logo, self.header_link]:
            w.textChanged.connect(self.on_header_changed)

        h_form.addRow("Título marca:", self.header_title)
        h_form.addRow("Logo URL:", self.header_logo)
        h_form.addRow("Logo Link:", self.header_link)
        h_layout.addLayout(h_form)
        self.tabs.addTab(header_tab, "Header")

        # Hero tab
        hero_tab = QWidget()
        he_layout = QVBoxLayout(hero_tab)
        he_enable = QCheckBox("Activar Hero")
        he_enable.setChecked(sections['hero'].get('enabled', True))
        he_enable.toggled.connect(lambda c: self.toggle_section('hero', c))
        he_layout.addWidget(he_enable)

        he_form = QFormLayout()
        self.hero_rainbow = QCheckBox("Eyebrow arcoíris (varios con coma)")
        self.hero_rainbow.setChecked(sections['hero'].get('rainbow_eyebrow', False))
        self.hero_rainbow.toggled.connect(self.on_hero_changed)

        self.hero_font_title = QLineEdit(sections['hero'].get('font_title', 'var(--serif)'))
        self.hero_font_body = QLineEdit(sections['hero'].get('font_body', 'var(--sans)'))
        self.hero_font_title.textChanged.connect(self.on_hero_changed)
        self.hero_font_body.textChanged.connect(self.on_hero_changed)

        he_form.addRow("", self.hero_rainbow)
        he_form.addRow("Fuente título:", self.hero_font_title)
        he_form.addRow("Fuente cuerpo:", self.hero_font_body)
        he_layout.addLayout(he_form)

        # Slides list and editor
        slides_group = QGroupBox("Láminas (slides)")
        sg_layout = QVBoxLayout(slides_group)

        self.slides_list = QListWidget()
        self.slides_list.currentRowChanged.connect(self.on_slide_selected)
        sg_layout.addWidget(self.slides_list)

        s_btns = QHBoxLayout()
        s_add = QPushButton("Agregar lámina")
        s_del = QPushButton("Eliminar lámina")
        s_add.clicked.connect(self.add_slide)
        s_del.clicked.connect(self.remove_slide)
        s_btns.addWidget(s_add)
        s_btns.addWidget(s_del)
        sg_layout.addLayout(s_btns)

        # Fields for selected slide
        s_form = QFormLayout()
        self.slide_eyebrow = QLineEdit()
        self.slide_title = QLineEdit()
        self.slide_text = QTextEdit(); self.slide_text.setMaximumHeight(90)

        self.slide_bg_type = QComboBox(); self.slide_bg_type.addItems(["gradient", "image"])
        self.slide_bg_image = QLineEdit()
        self.slide_grad_from = QLineEdit("#004527")
        self.slide_grad_to = QLineEdit("#00693e")

        self.slide_buttons_json = QTextEdit()
        self.slide_buttons_json.setPlaceholderText('[{"style":"primary","label":"Texto","href":"#"}]')
        self.slide_buttons_json.setMaximumHeight(110)

        for w in [self.slide_eyebrow, self.slide_title, self.slide_bg_image, self.slide_grad_from, self.slide_grad_to]:
            w.textChanged.connect(self.on_slide_fields_changed)
        self.slide_text.textChanged.connect(self.on_slide_fields_changed)
        self.slide_bg_type.currentTextChanged.connect(self.on_slide_fields_changed)
        self.slide_buttons_json.textChanged.connect(self.on_slide_fields_changed)

        s_form.addRow("Eyebrow(s):", self.slide_eyebrow)
        s_form.addRow("Título:", self.slide_title)
        s_form.addRow("Texto:", self.slide_text)
        s_form.addRow("Fondo tipo:", self.slide_bg_type)
        s_form.addRow("Fondo imagen URL:", self.slide_bg_image)
        s_form.addRow("Gradiente desde:", self.slide_grad_from)
        s_form.addRow("Gradiente hasta:", self.slide_grad_to)
        s_form.addRow("Botones (JSON):", self.slide_buttons_json)

        sg_layout.addLayout(s_form)
        he_layout.addWidget(slides_group)

        self.tabs.addTab(hero_tab, "Hero")

        # Otras secciones
        for sec in ["que_es", "ejes", "etapas", "participa", "noticias", "recursos", "contacto"]:
            data = sections.get(sec, {})
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            checkbox = QCheckBox(f"Activar {sec}")
            checkbox.setChecked(data.get('enabled', False))
            checkbox.toggled.connect(lambda c, name=sec: self.toggle_section(name, c))
            tab_layout.addWidget(checkbox)
            self.create_section_fields(tab_layout, sec, data)
            tab_layout.addStretch()
            self.tabs.addTab(tab, sec)

        # Populate slides list
        self.refresh_slides_list()

    # --------------------------- Eventos ---------------------------
    def on_header_changed(self):
        h = self.site_data['sections']['header']
        h['title'] = self.header_title.text()
        h['logo_url'] = self.header_logo.text()
        h['logo_link'] = self.header_link.text()
        self.schedule_update()

    def on_hero_changed(self):
        he = self.site_data['sections']['hero']
        he['rainbow_eyebrow'] = self.hero_rainbow.isChecked()
        he['font_title'] = self.hero_font_title.text()
        he['font_body'] = self.hero_font_body.text()
        self.schedule_update()

    # --- Slides ---
    def refresh_slides_list(self):
        self.slides_list.blockSignals(True)
        self.slides_list.clear()
        slides = self.site_data['sections']['hero'].get('slides', [])
        for sl in slides:
            self.slides_list.addItem(sl.get('title', 'Lámina'))
        self.slides_list.blockSignals(False)
        if slides:
            self.slides_list.setCurrentRow(0)
            self.load_slide_fields(0)

    def on_slide_selected(self, idx):
        self.load_slide_fields(idx)

    def load_slide_fields(self, idx):
        slides = self.site_data['sections']['hero'].get('slides', [])
        if idx is None or idx < 0 or idx >= len(slides):
            self.slide_eyebrow.setText("")
            self.slide_title.setText("")
            self.slide_text.setPlainText("")
            self.slide_bg_type.setCurrentText("gradient")
            self.slide_bg_image.setText("")
            self.slide_grad_from.setText("#004527")
            self.slide_grad_to.setText("#00693e")
            self.slide_buttons_json.setPlainText("[]")
            return
        sl = slides[idx]
        self.slide_eyebrow.setText(sl.get('eyebrow',""))
        self.slide_title.setText(sl.get('title',""))
        self.slide_text.setPlainText(sl.get('text',""))
        self.slide_bg_type.setCurrentText(sl.get('bg_type', 'gradient'))
        self.slide_bg_image.setText(sl.get('bg_image_url', ""))
        self.slide_grad_from.setText(sl.get('bg_gradient_from', "#004527"))
        self.slide_grad_to.setText(sl.get('bg_gradient_to', "#00693e"))
        self.slide_buttons_json.setPlainText(json.dumps(sl.get('buttons', []), ensure_ascii=False, indent=2))

    def on_slide_fields_changed(self):
        idx = self.slides_list.currentRow()
        if idx < 0: return
        slides = self.site_data['sections']['hero'].setdefault('slides', [])
        if idx >= len(slides): return
        sl = slides[idx]
        sl['eyebrow'] = self.slide_eyebrow.text()
        sl['title'] = self.slide_title.text()
        sl['text'] = self.slide_text.toPlainText()
        sl['bg_type'] = self.slide_bg_type.currentText()
        sl['bg_image_url'] = self.slide_bg_image.text()
        sl['bg_gradient_from'] = self.slide_grad_from.text()
        sl['bg_gradient_to'] = self.slide_grad_to.text()
        try:
            sl['buttons'] = json.loads(self.slide_buttons_json.toPlainText() or "[]")
        except Exception:
            pass
        self.slides_list.blockSignals(True)
        self.slides_list.item(idx).setText(sl.get('title','Lámina'))
        self.slides_list.blockSignals(False)
        self.schedule_update()

    def add_slide(self):
        slides = self.site_data['sections']['hero'].setdefault('slides', [])
        slides.append({
            "eyebrow": "Nuevo",
            "title": "Nueva lámina",
            "text": "Texto de la lámina",
            "bg_type": "gradient",
            "bg_image_url": "",
            "bg_gradient_from": "#004527",
            "bg_gradient_to": "#00693e",
            "buttons": [{"style":"primary","label":"Más info","href":"#"}]
        })
        self.refresh_slides_list()
        self.schedule_update()

    def remove_slide(self):
        idx = self.slides_list.currentRow()
        slides = self.site_data['sections']['hero'].setdefault('slides', [])
        if 0 <= idx < len(slides):
            del slides[idx]
            self.refresh_slides_list()
            self.schedule_update()

    # --------------------------- Helpers ---------------------------
    def create_section_fields(self, layout, section_name, section_data):
        form = QFormLayout()
        basic_fields = ['eyebrow', 'title', 'description', 'text', 'btn_primary', 'btn_secondary', 'email', 'phone', 'address']
        for field in basic_fields:
            if field in section_data:
                if field in ['description', 'text', 'address']:
                    widget = QTextEdit(section_data[field]); widget.setMaximumHeight(100 if field!='address' else 120)
                else:
                    widget = QLineEdit(section_data[field])
                widget.textChanged.connect(self.on_data_changed)
                form.addRow(f"{field.title()}:", widget)
                setattr(self, f"{section_name}_{field}", widget)
        layout.addLayout(form)
        iterative_fields = ['cards', 'timeline', 'news', 'resources']
        for field in iterative_fields:
            if field in section_data:
                self.create_iterative_section(layout, section_name, field, section_data[field])

    def create_iterative_section(self, layout, section_name, field_name, items):
        group = QGroupBox(field_name.title())
        group_layout = QVBoxLayout(group)
        list_widget = QListWidget()
        self.update_item_list(list_widget, items)
        group_layout.addWidget(list_widget)
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
        list_widget.clear()
        for item in items:
            if isinstance(item, dict):
                title = item.get('title', item.get('pill', 'Item'))
                list_widget.addItem(title)

    def add_item(self, section_name, field_name, list_widget):
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
        current_row = list_widget.currentRow()
        if current_row >= 0:
            del self.site_data['sections'][section_name][field_name][current_row]
            self.update_item_list(list_widget, self.site_data['sections'][section_name][field_name])
            self.schedule_update()

    def toggle_section(self, section_name, enabled):
        self.site_data['sections'][section_name]['enabled'] = enabled
        self.schedule_update()

    def choose_color(self, color_type):
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            self.site_data['general'][color_type] = color_hex
            if color_type == 'primary_color':
                self.primary_color_btn.setStyleSheet(f"background-color: {color_hex}; min-height: 28px;")
            else:
                self.secondary_color_btn.setStyleSheet(f"background-color: {color_hex}; min-height: 28px;")
            self.schedule_update()

    def on_data_changed(self):
        self.site_data['general']['title'] = self.title_edit.text()
        self.site_data['general']['description'] = self.description_edit.toPlainText()
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

    # --------------------------- Preview ---------------------------
    def setup_preview_panel(self, parent):
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)

        controls_bar = QWidget()
        controls_bar.setMaximumHeight(36)
        controls_layout = QHBoxLayout(controls_bar)
        controls_layout.setContentsMargins(6, 6, 6, 6)
        controls_layout.setSpacing(6)

        save_btn = QToolButton(); save_btn.setText("💾 Guardar"); save_btn.setAutoRaise(True); save_btn.clicked.connect(self.save_project)
        refresh_btn = QToolButton(); refresh_btn.setText("🔄 Recargar"); refresh_btn.setAutoRaise(True); refresh_btn.clicked.connect(self.reload_preview)
        open_browser_btn = QToolButton(); open_browser_btn.setText("🌐 Abrir en navegador"); open_browser_btn.setAutoRaise(True); open_browser_btn.clicked.connect(self.open_in_browser)

        controls_layout.addWidget(save_btn)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(open_browser_btn)
        controls_layout.addStretch()
        preview_layout.addWidget(controls_bar, 0)

        self.preview_browser = QWebEngineView()
        self.preview_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(self.preview_browser, 1)

        parent.addWidget(preview_widget)

    def schedule_update(self):
        if not hasattr(self, 'update_timer'):
            self.update_timer = QTimer()
            self.update_timer.setSingleShot(True)
            self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(300)

    def update_preview(self):
        try:
            generator = FlexibleHTMLGenerator(self.site_data)
            html_content = generator.generate_html()
            html_path = os.path.join(self.temp_dir, "index.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.preview_browser.setHtml(html_content)
            self.save_site_data()
        except Exception as e:
            error_html = f"<h1>Error generando HTML:</h1><pre>{e}</pre>"
            self.preview_browser.setHtml(error_html)

    def reload_preview(self):
        self.update_preview()

    def open_in_browser(self):
        html_path = os.path.join(self.temp_dir, "index.html")
        if os.path.exists(html_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(html_path))

    # --------------------------- Menú archivo ---------------------------
    def setup_menu(self):
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

    def save_project(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Proyecto", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.site_data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Éxito", "Proyecto guardado")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al guardar: {e}")

    def load_project(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Cargar Proyecto", "", "JSON Files (*.json)")
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
        filename, _ = QFileDialog.getSaveFileName(self, "Exportar HTML", "", "HTML Files (*.html)")
        if filename:
            try:
                generator = FlexibleHTMLGenerator(self.site_data)
                html_content = generator.generate_html()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                self.last_export_path = filename
                QMessageBox.information(self, "Éxito", "HTML exportado")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar: {e}")

    def refresh_ui(self):
        self.title_edit.setText(self.site_data['general']['title'])
        self.description_edit.setPlainText(self.site_data['general']['description'])
        self.primary_color_btn.setStyleSheet(f"background-color: {self.site_data['general']['primary_color']}; min-height: 28px;")
        self.secondary_color_btn.setStyleSheet(f"background-color: {self.site_data['general']['secondary_color']}; min-height: 28px;")
        self.tabs.clear()
        self.setup_section_tabs()

    def closeEvent(self, event):
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    required_files = ['site_structure.json', 'css_templates.json', 'section_templates.json']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"Error: Faltan archivos necesarios: {', '.join(missing_files)}")
        return 1

    window = HTMLEditor()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
