# ========================================================================
# PARTE 1: 🔧 IMPORTS Y CONFIGURACIÓN INICIAL
# ========================================================================

import sys
import json
import os
import tempfile
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QScrollArea, QGroupBox, QCheckBox, QLineEdit, QTextEdit, QPushButton,
    QLabel, QFormLayout, QListWidget, QTabWidget, QColorDialog, QFileDialog,
    QMessageBox, QToolButton, QSizePolicy, QComboBox, QGridLayout,
    QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices, QColor, QFont
from PySide6.QtWebEngineWidgets import QWebEngineView

from html_generator import FlexibleHTMLGenerator


class ColorButton(QPushButton):
    def __init__(self, color_hex, tooltip_text, parent=None):
        super().__init__(parent)
        self.color_hex = color_hex
        self.setFixedSize(40, 40)
        self.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #ccc; border-radius: 4px;")
        self.setToolTip(tooltip_text)


class HTMLEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor Visual HTML")
        self.setGeometry(100, 100, 1400, 800)

        self.temp_dir = tempfile.mkdtemp()
        self.last_export_path = None
        
        # Variables para navegación automática
        self.current_scroll_position = 0
        self.pending_section_scroll = None

        self.load_site_data()

        self.color_buttons = {}
        self.color_inputs = {}
        self.css_variables = {}
        self.load_css_variables()  

        self.setup_ui()
        self.setup_menu()
        self.update_preview()

# ========================================================================
# PARTE 2: 💾 GESTIÓN DE DATOS
# ========================================================================

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

# ========================================================================
# PARTE 3: 🏗️ CONFIGURACIÓN DE UI PRINCIPAL
# ========================================================================

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

        # --- Configuración general unificada
        self.setup_general_config(layout)

        # --- Secciones (tabs)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.setup_section_tabs()

    def setup_preview_panel(self, parent):
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)

        # Barra de controles
        controls_bar = QWidget()
        controls_bar.setMaximumHeight(36)
        controls_layout = QHBoxLayout(controls_bar)
        controls_layout.setContentsMargins(6, 6, 6, 6)
        controls_layout.setSpacing(6)

        save_btn = QToolButton(); save_btn.setText("💾 Guardar"); save_btn.setAutoRaise(True); save_btn.clicked.connect(self.save_project)
        refresh_btn = QToolButton(); refresh_btn.setText("🔄 Recargar"); refresh_btn.setAutoRaise(True); refresh_btn.clicked.connect(self.reload_preview)
        open_browser_btn = QToolButton(); open_browser_btn.setText("🌐 Abrir en navegador"); open_browser_btn.setAutoRaise(True); open_browser_btn.clicked.connect(self.open_in_browser)
        
        # NUEVO: Botón para vista móvil
        self.mobile_view_btn = QToolButton()
        self.mobile_view_btn.setText("📱 Vista Móvil")
        self.mobile_view_btn.setAutoRaise(True)
        self.mobile_view_btn.setCheckable(True)
        self.mobile_view_btn.clicked.connect(self.toggle_mobile_view)
        self.is_mobile_view = False

        controls_layout.addWidget(save_btn)
        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(open_browser_btn)
        controls_layout.addWidget(self.mobile_view_btn)
        controls_layout.addStretch()
        preview_layout.addWidget(controls_bar, 0)

        # NUEVO: Tabs para Visor y Código HTML
        self.preview_tabs = QTabWidget()
        preview_layout.addWidget(self.preview_tabs, 1)

        # Tab 1: Visor
        viewer_widget = QWidget()
        viewer_layout = QVBoxLayout(viewer_widget)
        viewer_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_browser = QWebEngineView()
        self.preview_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # NUEVO: Desactivar menú contextual
        self.preview_browser.setContextMenuPolicy(Qt.NoContextMenu)
        viewer_layout.addWidget(self.preview_browser)

        self.preview_tabs.addTab(viewer_widget, "🖥️ Visor")

        # Tab 2: Código HTML
        html_widget = QWidget()
        html_layout = QVBoxLayout(html_widget)
        html_layout.setContentsMargins(8, 8, 8, 8)

        self.html_source_view = QTextEdit()
        self.html_source_view.setReadOnly(True)
        self.html_source_view.setFont(QFont("Consolas", 10))
        html_layout.addWidget(self.html_source_view)

        self.preview_tabs.addTab(html_widget, "📄 Código HTML")

        parent.addWidget(preview_widget)

# ========================================================================
# PARTE 4: ⚙️ CONFIGURACIÓN GENERAL
# ========================================================================

    def setup_general_config(self, layout):
        general_group = QGroupBox("Configuración General")
        general_layout = QVBoxLayout(general_group)
        
        # Crear tabs para la configuración general
        self.general_tabs = QTabWidget()
        general_layout.addWidget(self.general_tabs)
        
        # === FICHA GENERAL ===
        general_tab = QWidget()
        general_form = QFormLayout(general_tab)
        
        # Título del sitio
        self.title_edit = QLineEdit(self.site_data['general']['title'])
        self.title_edit.textChanged.connect(self.on_general_changed)
        general_form.addRow("Título del sitio:", self.title_edit)
        
        # Descripción
        self.description_edit = QTextEdit(self.site_data['general']['description'])
        self.description_edit.setMaximumHeight(80)
        self.description_edit.textChanged.connect(self.on_general_changed)
        general_form.addRow("Descripción:", self.description_edit)
        
        # Idioma
        self.lang_combo = QComboBox()
        languages = [
            ("es", "Español"),
            ("en", "English"),
            ("fr", "Français"),
            ("de", "Deutsch"),
            ("pt", "Português"),
            ("it", "Italiano")
        ]
        for code, name in languages:
            self.lang_combo.addItem(name, code)
        
        current_lang = self.site_data.get('head', {}).get('lang', 'es')
        lang_index = next((i for i, (code, _) in enumerate(languages) if code == current_lang), 0)
        self.lang_combo.setCurrentIndex(lang_index)
        self.lang_combo.currentTextChanged.connect(self.on_general_changed)
        general_form.addRow("Idioma:", self.lang_combo)
        
        self.general_tabs.addTab(general_tab, "General")
        
        # === FICHA META & SEO ===
        meta_tab = QWidget()
        meta_form = QFormLayout(meta_tab)
        
        # Charset
        self.charset_combo = QComboBox()
        charsets = ["UTF-8", "ISO-8859-1", "Windows-1252"]
        self.charset_combo.addItems(charsets)
        current_charset = self.site_data.get('head', {}).get('charset', 'UTF-8')
        if current_charset in charsets:
            self.charset_combo.setCurrentText(current_charset)
        self.charset_combo.currentTextChanged.connect(self.on_general_changed)
        meta_form.addRow("Codificación:", self.charset_combo)
        
        # Keywords
        self.keywords_edit = QLineEdit(self.site_data.get('head', {}).get('meta_keywords', ''))
        self.keywords_edit.setPlaceholderText("ciencia, investigación, universidad, desarrollo")
        self.keywords_edit.textChanged.connect(self.on_general_changed)
        meta_form.addRow("Palabras clave:", self.keywords_edit)
        
        # Author
        self.author_edit = QLineEdit(self.site_data.get('head', {}).get('meta_author', ''))
        self.author_edit.setPlaceholderText("Universidad Austral de Chile")
        self.author_edit.textChanged.connect(self.on_general_changed)
        meta_form.addRow("Autor:", self.author_edit)
        
        # URL Canónica
        self.canonical_edit = QLineEdit(self.site_data.get('head', {}).get('canonical_url', ''))
        self.canonical_edit.setPlaceholderText("https://www.ejemplo.com/")
        self.canonical_edit.textChanged.connect(self.on_general_changed)
        meta_form.addRow("URL Canónica:", self.canonical_edit)
        
        # Robots (checkboxes con tooltips)
        robots_layout = QHBoxLayout()
        self.robots_index = QCheckBox("Indexar")
        self.robots_index.setToolTip("Permite que los motores de búsqueda indexen esta página en sus resultados")
        self.robots_follow = QCheckBox("Seguir enlaces")
        self.robots_follow.setToolTip("Permite que los motores de búsqueda sigan los enlaces de esta página")
        self.robots_noarchive = QCheckBox("No archivar")
        self.robots_noarchive.setToolTip("Impide que los motores de búsqueda guarden una copia en caché de la página")
        
        # Parsear robots actuales
        current_robots = self.site_data.get('head', {}).get('meta_robots', 'index,follow')
        self.robots_index.setChecked('index' in current_robots.lower())
        self.robots_follow.setChecked('follow' in current_robots.lower())
        self.robots_noarchive.setChecked('noarchive' in current_robots.lower())
        
        for cb in [self.robots_index, self.robots_follow, self.robots_noarchive]:
            cb.toggled.connect(self.on_general_changed)
            robots_layout.addWidget(cb)
        
        meta_form.addRow("Robots:", robots_layout)
        
        # Cache
        self.no_cache_cb = QCheckBox("Desactivar caché")
        self.no_cache_cb.setToolTip("Fuerza a los navegadores a recargar la página en cada visita")
        self.no_cache_cb.setChecked(self.site_data.get('head', {}).get('disable_cache', False))
        self.no_cache_cb.toggled.connect(self.on_general_changed)
        meta_form.addRow("", self.no_cache_cb)
        
        self.general_tabs.addTab(meta_tab, "Meta & SEO")
        
        # === FICHA REDES SOCIALES ===
        social_tab = QWidget()
        social_form = QFormLayout(social_tab)
        
        # Open Graph
        og_group = QGroupBox("Open Graph (Facebook, LinkedIn)")
        og_layout = QFormLayout(og_group)
        
        self.og_title = QLineEdit(self.site_data.get('head', {}).get('og_title', ''))
        self.og_title.setPlaceholderText("Título para redes sociales")
        self.og_title.textChanged.connect(self.on_general_changed)
        og_layout.addRow("OG Título:", self.og_title)
        
        self.og_description = QTextEdit(self.site_data.get('head', {}).get('og_description', ''))
        self.og_description.setMaximumHeight(60)
        self.og_description.setPlaceholderText("Descripción para redes sociales")
        self.og_description.textChanged.connect(self.on_general_changed)
        og_layout.addRow("OG Descripción:", self.og_description)
        
        self.og_image = QLineEdit(self.site_data.get('head', {}).get('og_image', ''))
        self.og_image.setPlaceholderText("https://ejemplo.com/imagen.jpg")
        self.og_image.textChanged.connect(self.on_general_changed)
        og_layout.addRow("OG Imagen:", self.og_image)
        
        self.og_type = QComboBox()
        og_types = ["website", "article", "profile", "book"]
        self.og_type.addItems(og_types)
        current_og_type = self.site_data.get('head', {}).get('og_type', 'website')
        if current_og_type in og_types:
            self.og_type.setCurrentText(current_og_type)
        self.og_type.currentTextChanged.connect(self.on_general_changed)
        og_layout.addRow("OG Tipo:", self.og_type)
        
        social_form.addRow("", og_group)
        
        # Twitter Cards
        twitter_group = QGroupBox("Twitter Cards")
        twitter_layout = QFormLayout(twitter_group)
        
        self.twitter_card = QComboBox()
        card_types = ["summary", "summary_large_image", "app", "player"]
        self.twitter_card.addItems(card_types)
        current_twitter_card = self.site_data.get('head', {}).get('twitter_card', 'summary')
        if current_twitter_card in card_types:
            self.twitter_card.setCurrentText(current_twitter_card)
        self.twitter_card.currentTextChanged.connect(self.on_general_changed)
        twitter_layout.addRow("Tipo de tarjeta:", self.twitter_card)
        
        self.twitter_site = QLineEdit(self.site_data.get('head', {}).get('twitter_site', ''))
        self.twitter_site.setPlaceholderText("@usuario_sitio")
        self.twitter_site.textChanged.connect(self.on_general_changed)
        twitter_layout.addRow("Usuario del sitio:", self.twitter_site)
        
        self.twitter_creator = QLineEdit(self.site_data.get('head', {}).get('twitter_creator', ''))
        self.twitter_creator.setPlaceholderText("@usuario_creador")
        self.twitter_creator.textChanged.connect(self.on_general_changed)
        twitter_layout.addRow("Usuario creador:", self.twitter_creator)
        
        social_form.addRow("", twitter_group)
        
        self.general_tabs.addTab(social_tab, "Redes Sociales")
        
        # === FICHA COLORES ===
        colors_tab = QWidget()
        colors_layout = QVBoxLayout(colors_tab)

        colors_info = QLabel("Los colores se aplican automáticamente a los elementos correspondientes del sitio:")
        colors_info.setWordWrap(True)
        colors_info.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        colors_layout.addWidget(colors_info)

        colors_grid = QGridLayout()

        # Definir colores con sus tooltips descriptivos y labels
        color_config = [
            ("primary_color", "Color primario", "Enlaces, botones principales, header, elementos de navegación"),
            ("secondary_color", "Color secundario", "Acentos, elementos destacados, detalles decorativos"),
            ("yellow", "Color amarillo", "Etiquetas (eyebrow) del hero, badges y elementos de énfasis"),
            ("celeste", "Color celeste", "Píldoras (pills) de las tarjetas, tags informativos"),
            ("black", "Color negro", "Texto principal, títulos, contenido general"),
            ("gray_60", "Color gris", "Texto secundario, descripciones, elementos sutiles"),
            ("blue_footer", "Color azul footer", "Fondo del pie de página, elementos del footer"),
        ]

        row = 0
        for color_key, label, description in color_config:
            # valor actual
            if color_key in ["primary_color", "secondary_color"]:
                current_color = self.site_data["general"].get(color_key, "#000000")
            else:
                current_color = self.css_variables.get(color_key, "#000000")

            # label
            color_label = QLabel(label)
            color_label.setStyleSheet("font-weight: bold;")
            colors_grid.addWidget(color_label, row, 0)

            # botón picker
            btn = ColorButton(current_color, description)
            btn.clicked.connect(lambda _=False, key=color_key: self.choose_color(key))
            self.color_buttons[color_key] = btn
            colors_grid.addWidget(btn, row, 1)

            # input de texto (hex)
            edit = QLineEdit(current_color)
            edit.setPlaceholderText("#RRGGBB")
            edit.setMaxLength(9)  # permitir rgba() breve o #RRGGBB
            edit.textEdited.connect(lambda text, key=color_key: self.on_color_text_changed(key, text))
            self.color_inputs[color_key] = edit
            colors_grid.addWidget(edit, row, 2)

            # descripción
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #666; font-size: 12px;")
            colors_grid.addWidget(desc, row, 3)

            row += 1

        colors_layout.addLayout(colors_grid)
        colors_layout.addStretch()

        self.general_tabs.addTab(colors_tab, "Colores")

        
        # === FICHA RECURSOS ===
        resources_tab = QWidget()
        resources_form = QFormLayout(resources_tab)
        
        # Favicon
        self.favicon_edit = QLineEdit(self.site_data.get('head', {}).get('favicon_url', ''))
        self.favicon_edit.setPlaceholderText("https://ejemplo.com/favicon.ico")
        self.favicon_edit.textChanged.connect(self.on_general_changed)
        resources_form.addRow("Favicon URL:", self.favicon_edit)
        
        # Theme Color
        self.theme_color_edit = QLineEdit(self.site_data.get('head', {}).get('theme_color', ''))
        self.theme_color_edit.setPlaceholderText("#00693e")
        self.theme_color_edit.textChanged.connect(self.on_general_changed)
        resources_form.addRow("Color del tema:", self.theme_color_edit)
        
        # Manifest
        self.manifest_edit = QLineEdit(self.site_data.get('head', {}).get('manifest_url', ''))
        self.manifest_edit.setPlaceholderText("/manifest.json")
        self.manifest_edit.textChanged.connect(self.on_general_changed)
        resources_form.addRow("Manifest URL:", self.manifest_edit)
        
        self.general_tabs.addTab(resources_tab, "Recursos")
        
        layout.addWidget(general_group)

    def on_general_changed(self):
        # Actualizar datos generales
        self.site_data['general']['title'] = self.title_edit.text()
        self.site_data['general']['description'] = self.description_edit.toPlainText()
        
        # Actualizar head
        self.site_data.setdefault('head', {})
        
        # Idioma
        lang_data = self.lang_combo.currentData()
        if lang_data:
            self.site_data['head']['lang'] = lang_data
        
        # Charset
        self.site_data['head']['charset'] = self.charset_combo.currentText()
        
        # Meta campos nuevos
        self.site_data['head']['meta_keywords'] = self.keywords_edit.text()
        self.site_data['head']['meta_author'] = self.author_edit.text()
        self.site_data['head']['canonical_url'] = self.canonical_edit.text()
        
        # Favicon
        self.site_data['head']['favicon_url'] = self.favicon_edit.text()
        
        # Theme color y manifest
        self.site_data['head']['theme_color'] = self.theme_color_edit.text()
        self.site_data['head']['manifest_url'] = self.manifest_edit.text()
        
        # Título y descripción (usar el general si no hay específico)
        self.site_data['head']['title'] = self.title_edit.text()
        self.site_data['head']['meta_description'] = self.description_edit.toPlainText()
        
        # Open Graph
        self.site_data['head']['og_title'] = self.og_title.text()
        self.site_data['head']['og_description'] = self.og_description.toPlainText()
        self.site_data['head']['og_image'] = self.og_image.text()
        self.site_data['head']['og_type'] = self.og_type.currentText()
        
        # Twitter Cards
        self.site_data['head']['twitter_card'] = self.twitter_card.currentText()
        self.site_data['head']['twitter_site'] = self.twitter_site.text()
        self.site_data['head']['twitter_creator'] = self.twitter_creator.text()
        
        # Robots
        robots_parts = []
        if self.robots_index.isChecked():
            robots_parts.append('index')
        else:
            robots_parts.append('noindex')
            
        if self.robots_follow.isChecked():
            robots_parts.append('follow')
        else:
            robots_parts.append('nofollow')
            
        if self.robots_noarchive.isChecked():
            robots_parts.append('noarchive')
            
        self.site_data['head']['meta_robots'] = ','.join(robots_parts)
        
        # Cache
        self.site_data['head']['disable_cache'] = self.no_cache_cb.isChecked()
        
        self.schedule_update()

# ========================================================================
# PARTE 5: 📑 CONFIGURACIÓN DE PESTAÑAS DE SECCIONES
# ========================================================================

    def setup_section_tabs(self):
        sections = self.site_data['sections']

        # Header tab - EXPANDIDO CON CONTROLES MEJORADOS
        header_tab = QWidget()
        h_layout = QVBoxLayout(header_tab)
        
        # Activar header
        h_enable = QCheckBox("Activar Header")
        h_enable.setChecked(sections['header'].get('enabled', True))
        h_enable.toggled.connect(lambda c: self.toggle_section('header', c))
        h_layout.addWidget(h_enable)

        # Crear tabs para el header
        header_tabs = QTabWidget()
        h_layout.addWidget(header_tabs)

        # === TAB 1: BÁSICO ===
        basic_tab = QWidget()
        basic_form = QFormLayout(basic_tab)
        
        self.header_title = QLineEdit(sections['header'].get('title', ''))
        self.header_logo = QLineEdit(sections['header'].get('logo_url', ''))
        self.header_link = QLineEdit(sections['header'].get('logo_link', 'https://'))

        for w in [self.header_title, self.header_logo, self.header_link]:
            w.textChanged.connect(self.on_header_changed)

        basic_form.addRow("Título marca:", self.header_title)
        basic_form.addRow("Logo URL:", self.header_logo)
        basic_form.addRow("Logo Link:", self.header_link)
        
        header_tabs.addTab(basic_tab, "Básico")

        # === TAB 2: ESTILO ===
        style_tab = QWidget()
        style_form = QFormLayout(style_tab)
        
        # Color de fondo personalizado - PALETA DE COLORES
        bg_color_layout = QHBoxLayout()
        self.header_bg_color_btn = ColorButton(
            sections['header'].get('bg_color', '#00693e'), 
            "Color de fondo del header"
        )
        self.header_bg_color_btn.clicked.connect(lambda: self.choose_header_color('bg_color'))
        
        self.header_bg_color_text = QLineEdit(sections['header'].get('bg_color', ''))
        self.header_bg_color_text.setPlaceholderText("ej: #00693e, transparent, rgba(0,105,62,0.9)")
        self.header_bg_color_text.textChanged.connect(self.on_header_color_text_changed)
        
        bg_color_layout.addWidget(self.header_bg_color_btn)
        bg_color_layout.addWidget(self.header_bg_color_text)
        style_form.addRow("Color de fondo:", bg_color_layout)
        
        # Transparencia/opacidad - SPINBOX DECIMAL
        self.header_opacity = QDoubleSpinBox()
        self.header_opacity.setRange(0.0, 1.0)
        self.header_opacity.setSingleStep(0.1)
        self.header_opacity.setDecimals(1)
        self.header_opacity.setValue(float(sections['header'].get('opacity', '1.0') or '1.0'))
        self.header_opacity.valueChanged.connect(self.on_header_changed)
        style_form.addRow("Opacidad:", self.header_opacity)
        
        # Altura del header - CHECKBOX AUTO + INPUT
        height_layout = QHBoxLayout()
        self.header_height_auto = QCheckBox("Auto")
        current_height = sections['header'].get('height', '')
        self.header_height_auto.setChecked(not current_height or current_height.lower() == 'auto')
        self.header_height_auto.toggled.connect(self.on_header_height_auto_changed)
        
        self.header_height = QSpinBox()
        self.header_height.setRange(30, 200)
        self.header_height.setSuffix(" px")
        height_value = 72  # valor por defecto
        if current_height and current_height.lower() != 'auto':
            try:
                height_value = int(current_height.replace('px', ''))
            except:
                pass
        self.header_height.setValue(height_value)
        self.header_height.setEnabled(not self.header_height_auto.isChecked())
        self.header_height.valueChanged.connect(self.on_header_changed)
        
        height_layout.addWidget(self.header_height_auto)
        height_layout.addWidget(self.header_height)
        style_form.addRow("Altura:", height_layout)
        
        # Tipo de fuente para título - COMBOBOX
        self.header_font_family = QComboBox()
        font_options = [
            ("", "Predeterminada"),
            ("var(--serif)", "Serif (Elegante)"),
            ("var(--sans)", "Sans-serif (Moderna)"),
            ("Georgia, serif", "Georgia"),
            ("'Times New Roman', serif", "Times New Roman"),
            ("Arial, sans-serif", "Arial"),
            ("'Helvetica Neue', sans-serif", "Helvetica"),
            ("'Segoe UI', sans-serif", "Segoe UI"),
            ("system-ui, sans-serif", "Sistema"),
            ("monospace", "Monospace"),
            ("'Courier New', monospace", "Courier New")
        ]
        
        for value, label in font_options:
            self.header_font_family.addItem(label, value)
        
        current_font = sections['header'].get('font_family', '')
        font_index = next((i for i, (value, _) in enumerate(font_options) if value == current_font), 0)
        self.header_font_family.setCurrentIndex(font_index)
        self.header_font_family.currentIndexChanged.connect(self.on_header_changed)
        style_form.addRow("Fuente título:", self.header_font_family)
        
        header_tabs.addTab(style_tab, "Estilo")

        # === TAB 3: ELEMENTOS ADICIONALES ===
        elements_tab = QWidget()
        elements_form = QFormLayout(elements_tab)
        
        # Botón CTA
        cta_group = QGroupBox("Botón de Llamada a la Acción")
        cta_layout = QFormLayout(cta_group)
        
        self.header_cta_text = QLineEdit(sections['header'].get('cta_text', ''))
        self.header_cta_text.setPlaceholderText("ej: Contactar, Inscribirse")
        self.header_cta_text.textChanged.connect(self.on_header_changed)
        cta_layout.addRow("Texto del botón:", self.header_cta_text)
        
        self.header_cta_link = QLineEdit(sections['header'].get('cta_link', ''))
        self.header_cta_link.setPlaceholderText("ej: #contacto, https://ejemplo.com")
        self.header_cta_link.textChanged.connect(self.on_header_changed)
        cta_layout.addRow("Enlace:", self.header_cta_link)
        
        self.header_cta_style = QComboBox()
        self.header_cta_style.addItems(["primary", "secondary", "outline"])
        current_cta_style = sections['header'].get('cta_style', 'primary')
        if current_cta_style in ["primary", "secondary", "outline"]:
            self.header_cta_style.setCurrentText(current_cta_style)
        self.header_cta_style.currentTextChanged.connect(self.on_header_changed)
        cta_layout.addRow("Estilo:", self.header_cta_style)
        
        elements_form.addRow("", cta_group)
        
        # Información de contacto
        contact_group = QGroupBox("Información de Contacto")
        contact_layout = QFormLayout(contact_group)
        
        self.header_phone = QLineEdit(sections['header'].get('phone', ''))
        self.header_phone.setPlaceholderText("ej: +56 63 221 9999")
        self.header_phone.textChanged.connect(self.on_header_changed)
        contact_layout.addRow("Teléfono:", self.header_phone)
        
        self.header_email = QLineEdit(sections['header'].get('email', ''))
        self.header_email.setPlaceholderText("ej: contacto@ejemplo.com")
        self.header_email.textChanged.connect(self.on_header_changed)
        contact_layout.addRow("Email:", self.header_email)
        
        elements_form.addRow("", contact_group)
        
        # Redes sociales
        social_group = QGroupBox("Redes Sociales")
        social_layout = QFormLayout(social_group)
        
        self.header_facebook = QLineEdit(sections['header'].get('social_facebook', ''))
        self.header_facebook.setPlaceholderText("ej: https://facebook.com/usuario")
        self.header_facebook.textChanged.connect(self.on_header_changed)
        social_layout.addRow("Facebook:", self.header_facebook)
        
        self.header_twitter = QLineEdit(sections['header'].get('social_twitter', ''))
        self.header_twitter.setPlaceholderText("ej: https://twitter.com/usuario")
        self.header_twitter.textChanged.connect(self.on_header_changed)
        social_layout.addRow("Twitter/X:", self.header_twitter)
        
        self.header_instagram = QLineEdit(sections['header'].get('social_instagram', ''))
        self.header_instagram.setPlaceholderText("ej: https://instagram.com/usuario")
        self.header_instagram.textChanged.connect(self.on_header_changed)
        social_layout.addRow("Instagram:", self.header_instagram)
        
        self.header_linkedin = QLineEdit(sections['header'].get('social_linkedin', ''))
        self.header_linkedin.setPlaceholderText("ej: https://linkedin.com/company/empresa")
        self.header_linkedin.textChanged.connect(self.on_header_changed)
        social_layout.addRow("LinkedIn:", self.header_linkedin)
        
        self.header_youtube = QLineEdit(sections['header'].get('social_youtube', ''))
        self.header_youtube.setPlaceholderText("ej: https://youtube.com/c/canal")
        self.header_youtube.textChanged.connect(self.on_header_changed)
        social_layout.addRow("YouTube:", self.header_youtube)
        
        elements_form.addRow("", social_group)
        
        # Selector de idioma
        lang_group = QGroupBox("Selector de Idioma")
        lang_layout = QFormLayout(lang_group)
        
        self.header_show_lang_selector = QCheckBox("Mostrar selector de idioma")
        self.header_show_lang_selector.setChecked(sections['header'].get('show_lang_selector', False))
        self.header_show_lang_selector.toggled.connect(self.on_header_changed)
        lang_layout.addRow("", self.header_show_lang_selector)
        
        self.header_available_langs = QLineEdit(sections['header'].get('available_langs', ''))
        self.header_available_langs.setPlaceholderText("ej: es,en,fr (códigos separados por coma)")
        self.header_available_langs.textChanged.connect(self.on_header_changed)
        lang_layout.addRow("Idiomas disponibles:", self.header_available_langs)
        
        elements_form.addRow("", lang_group)
        
        header_tabs.addTab(elements_tab, "Elementos")

        # === TAB 4: COMPORTAMIENTO ===
        behavior_tab = QWidget()
        behavior_form = QFormLayout(behavior_tab)
        
        # Animaciones
        animation_group = QGroupBox("Animaciones")
        animation_layout = QFormLayout(animation_group)
        
        self.header_entrance_animation = QComboBox()
        animation_options = [
            ("none", "Sin animación"),
            ("slideDown", "Deslizar desde arriba"),
            ("fadeIn", "Aparecer gradualmente"),
            ("slideInLeft", "Deslizar desde izquierda"),
            ("slideInRight", "Deslizar desde derecha")
        ]
        for value, label in animation_options:
            self.header_entrance_animation.addItem(label, value)
        
        current_animation = sections['header'].get('entrance_animation', 'none')
        anim_index = next((i for i, (value, _) in enumerate(animation_options) if value == current_animation), 0)
        self.header_entrance_animation.setCurrentIndex(anim_index)
        self.header_entrance_animation.currentIndexChanged.connect(self.on_header_changed)
        animation_layout.addRow("Animación de entrada:", self.header_entrance_animation)
        
        # Duración de animación - SPINBOX CON SUFIJO
        self.header_animation_duration = QDoubleSpinBox()
        self.header_animation_duration.setRange(0.1, 5.0)
        self.header_animation_duration.setSingleStep(0.1)
        self.header_animation_duration.setDecimals(1)
        self.header_animation_duration.setSuffix(" s")
        current_duration = sections['header'].get('animation_duration', '0.5s')
        duration_value = 0.5
        try:
            duration_value = float(current_duration.replace('s', '').replace('ms', ''))
            if 'ms' in current_duration:
                duration_value = duration_value / 1000
        except:
            pass
        self.header_animation_duration.setValue(duration_value)
        self.header_animation_duration.valueChanged.connect(self.on_header_changed)
        animation_layout.addRow("Duración:", self.header_animation_duration)
        
        behavior_form.addRow("", animation_group)
        
        # Comportamiento en scroll
        scroll_group = QGroupBox("Comportamiento en Scroll")
        scroll_layout = QFormLayout(scroll_group)
        
        self.header_scroll_behavior = QComboBox()
        scroll_options = [
            ("normal", "Normal (sin cambios)"),
            ("hide", "Ocultar al hacer scroll"),
            ("shrink", "Encoger al hacer scroll"),
            ("transparent", "Volver transparente")
        ]
        for value, label in scroll_options:
            self.header_scroll_behavior.addItem(label, value)
        
        current_scroll = sections['header'].get('scroll_behavior', 'normal')
        scroll_index = next((i for i, (value, _) in enumerate(scroll_options) if value == current_scroll), 0)
        self.header_scroll_behavior.setCurrentIndex(scroll_index)
        self.header_scroll_behavior.currentIndexChanged.connect(self.on_header_changed)
        scroll_layout.addRow("Comportamiento:", self.header_scroll_behavior)
        
        # Umbral de scroll - SPINBOX
        self.header_scroll_threshold = QSpinBox()
        self.header_scroll_threshold.setRange(0, 1000)
        self.header_scroll_threshold.setSuffix(" px")
        threshold_value = 100
        try:
            threshold_value = int(sections['header'].get('scroll_threshold', '100'))
        except:
            pass
        self.header_scroll_threshold.setValue(threshold_value)
        self.header_scroll_threshold.valueChanged.connect(self.on_header_changed)
        scroll_layout.addRow("Umbral de scroll:", self.header_scroll_threshold)
        
        self.header_sticky = QCheckBox("Header pegajoso (sticky)")
        self.header_sticky.setChecked(sections['header'].get('sticky', True))
        self.header_sticky.toggled.connect(self.on_header_changed)
        scroll_layout.addRow("", self.header_sticky)
        
        behavior_form.addRow("", scroll_group)
        
        header_tabs.addTab(behavior_tab, "Comportamiento")

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

        # Conectar cambio de pestañas con navegación automática
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Populate slides list
        self.refresh_slides_list()

# ========================================================================
# PARTE 6: 🔧 MANEJADORES DE EVENTOS
# ========================================================================


    def load_css_variables(self):
        """Carga variables desde css_templates.json en self.css_variables"""
        try:
            with open('css_templates.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.css_variables = data.get("variables", {}).copy()
        except Exception:
            self.css_variables = {
                "primary_color": "#00693e",
                "secondary_color": "#c20430",
                "yellow": "#ffc82e",
                "celeste": "#c0ddea",
                "black": "#1d1d1b",
                "gray_60": "#878787",
                "blue_footer": "#4c5da8"
            }

    def save_css_variables(self):
        """Escribe self.css_variables en css_templates.json (manteniendo el resto)."""
        try:
            with open('css_templates.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {"variables": {}, "base_styles": [], "components": {}}

        data.setdefault("variables", {})
        data["variables"].update(self.css_variables)

        try:
            with open('css_templates.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar css_templates.json: {e}")

    def normalize_hex(self, s: str) -> str:
        """Normaliza un color: admite #RGB, #RRGGBB o rgba(); devuelve cadena válida o ''."""
        s = (s or "").strip()
        if not s:
            return ""
        # permitir valores rgba()/transparent tal cual
        if s.lower() == "transparent" or s.lower().startswith("rgba("):
            return s
        if not s.startswith("#"):
            s = "#" + s
        # expandir #RGB a #RRGGBB
        if len(s) == 4 and all(c in "0123456789abcdefABCDEF" for c in s[1:]):
            s = "#" + "".join(ch*2 for ch in s[1:])
        # validar #RRGGBB
        if len(s) == 7 and all(c in "0123456789abcdefABCDEF" for c in s[1:]):
            return s.lower()
        return ""

    def set_color_value(self, key: str, value: str, from_picker: bool = False):
        """Actualiza color en UI + datos; persiste en json cuando aplica; re-render programado."""
        norm = self.normalize_hex(value)
        if not norm:
            return  # ignora hasta que sea válido

        # Actualiza botones e inputs si existen
        btn = self.color_buttons.get(key)
        if btn:
            btn.color_hex = norm
            btn.setStyleSheet(f"background-color: {norm}; border: 1px solid #ccc; border-radius: 4px;")

        edit = self.color_inputs.get(key)
        if edit and edit.text() != norm:
            # Evita loop al tipear
            edit.blockSignals(True)
            edit.setText(norm)
            edit.blockSignals(False)

        # Persistencia:
        if key in ["primary_color", "secondary_color"]:
            self.site_data["general"][key] = norm
            self.save_site_data()  # mantener coherencia con site_structure.json
        else:
            self.css_variables[key] = norm
            self.save_css_variables()

        # Re-render
        self.schedule_update()

    def on_color_text_changed(self, key: str, text: str):
        """Handler cuando el usuario edita el input hex."""
        self.set_color_value(key, text, from_picker=False)

    def choose_color(self, key: str):
        """Abre el selector y sincroniza input y datos."""
        current = None
        if key in ["primary_color", "secondary_color"]:
            current = self.site_data["general"].get(key, "#000000")
        else:
            current = self.css_variables.get(key, "#000000")

        initial = QColor(current if current.startswith("#") else "#000000")
        color = QColorDialog.getColor(initial, self, "Elige un color")
        if color.isValid():
            self.set_color_value(key, color.name(), from_picker=True)


    def choose_header_color(self, color_type):
        """Abrir paleta de colores para el header"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            
            # Actualizar datos
            self.site_data['sections']['header'][color_type] = color_hex
            
            # Actualizar botón visual
            if color_type == 'bg_color':
                self.header_bg_color_btn.setStyleSheet(
                    f"background-color: {color_hex}; border: 1px solid #ccc; border-radius: 4px;"
                )
                self.header_bg_color_btn.color_hex = color_hex
                # Actualizar también el campo de texto
                self.header_bg_color_text.setText(color_hex)
            
            self.schedule_update('header')

    def on_header_color_text_changed(self):
        """Cuando se cambia el texto del color manualmente"""
        color_text = self.header_bg_color_text.text().strip()
        if color_text:
            self.site_data['sections']['header']['bg_color'] = color_text
            # Si es un color hex válido, actualizar el botón
            if color_text.startswith('#') and len(color_text) == 7:
                try:
                    # Validar que es un color hex válido
                    int(color_text[1:], 16)
                    self.header_bg_color_btn.setStyleSheet(
                        f"background-color: {color_text}; border: 1px solid #ccc; border-radius: 4px;"
                    )
                    self.header_bg_color_btn.color_hex = color_text
                except ValueError:
                    pass
        self.schedule_update('header')

    def on_header_height_auto_changed(self, checked):
        """Cuando se cambia el checkbox de altura automática"""
        self.header_height.setEnabled(not checked)
        if checked:
            self.site_data['sections']['header']['height'] = 'auto'
        else:
            self.site_data['sections']['header']['height'] = f"{self.header_height.value()}px"
        self.schedule_update('header')

    def on_header_changed(self):
        h = self.site_data['sections']['header']
        
        # Campos básicos
        h['title'] = self.header_title.text()
        h['logo_url'] = self.header_logo.text()
        h['logo_link'] = self.header_link.text()
        
        # Campos de estilo mejorados
        h['bg_color'] = self.header_bg_color_text.text()
        h['opacity'] = str(self.header_opacity.value())
        
        # Altura (auto o manual)
        if self.header_height_auto.isChecked():
            h['height'] = 'auto'
        else:
            h['height'] = f"{self.header_height.value()}px"
        
        # Fuente (obtener valor del combobox)
        font_data = self.header_font_family.currentData()
        h['font_family'] = font_data if font_data else ''
        
        # CTA
        h['cta_text'] = self.header_cta_text.text()
        h['cta_link'] = self.header_cta_link.text()
        h['cta_style'] = self.header_cta_style.currentText()
        
        # Contacto
        h['phone'] = self.header_phone.text()
        h['email'] = self.header_email.text()
        
        # Redes sociales
        h['social_facebook'] = self.header_facebook.text()
        h['social_twitter'] = self.header_twitter.text()
        h['social_instagram'] = self.header_instagram.text()
        h['social_linkedin'] = self.header_linkedin.text()
        h['social_youtube'] = self.header_youtube.text()
        
        # Selector de idioma
        h['show_lang_selector'] = self.header_show_lang_selector.isChecked()
        h['available_langs'] = self.header_available_langs.text()
        
        # Comportamiento - Animación
        animation_data = self.header_entrance_animation.currentData()
        h['entrance_animation'] = animation_data if animation_data else 'none'
        
        # Comportamiento - Duración (convertir a string con 's')
        h['animation_duration'] = f"{self.header_animation_duration.value()}s"
        
        # Comportamiento - Scroll
        scroll_data = self.header_scroll_behavior.currentData()
        h['scroll_behavior'] = scroll_data if scroll_data else 'normal'
        
        # Comportamiento - Umbral scroll
        h['scroll_threshold'] = str(self.header_scroll_threshold.value())
        
        # Comportamiento - Sticky
        h['sticky'] = self.header_sticky.isChecked()
        
        self.schedule_update('header')

    def on_hero_changed(self):
        he = self.site_data['sections']['hero']
        he['rainbow_eyebrow'] = self.hero_rainbow.isChecked()
        he['font_title'] = self.hero_font_title.text()
        he['font_body'] = self.hero_font_body.text()
        self.schedule_update('hero')

    def toggle_mobile_view(self):
        """Alternar entre vista desktop y móvil"""
        self.is_mobile_view = not self.is_mobile_view
        
        if self.is_mobile_view:
            self.mobile_view_btn.setText("💻 Vista Desktop")
        else:
            self.mobile_view_btn.setText("📱 Vista Móvil")
        
        self.update_mobile_view()

    def update_mobile_view(self):
        """Cambiar el tamaño del viewport para simular dispositivo móvil"""
        if not hasattr(self, 'preview_browser') or not self.preview_browser:
            return
        
        if self.is_mobile_view:
            # Simular viewport móvil (375x667 - iPhone SE)
            self.preview_browser.setMaximumWidth(375)
            self.preview_browser.setMinimumWidth(375)
        else:
            # Restaurar vista desktop
            self.preview_browser.setMaximumWidth(16777215)  # QWIDGETSIZE_MAX
            self.preview_browser.setMinimumWidth(0)

    def show_html_source(self):
        """Mostrar el código HTML en la pestaña correspondiente"""
        try:
            generator = FlexibleHTMLGenerator(self.site_data)
            html_content = generator.generate_html()
            
            # Formatear el HTML para mejor legibilidad
            formatted_html = self.format_html(html_content)
            self.html_source_view.setPlainText(formatted_html)
        except Exception as e:
            self.html_source_view.setPlainText(f"Error generando HTML:\n{str(e)}")

    def format_html(self, html_content):
        """Formatear HTML para mejor legibilidad"""
        try:
            from html import unescape
            import re
            
            # Básico: agregar saltos de línea después de ciertos tags
            html_content = re.sub(r'><', '>\n<', html_content)
            html_content = re.sub(r'</(\w+)>', r'</\1>\n', html_content)
            html_content = re.sub(r'<(\w+[^>]*)>', r'<\1>\n', html_content)
            
            # Limpiar líneas vacías múltiples
            html_content = re.sub(r'\n\s*\n', '\n', html_content)
            
            return html_content.strip()
        except:
            return html_content

    def toggle_section(self, section_name, enabled):
        self.site_data['sections'][section_name]['enabled'] = enabled
        # Mapear nombres internos a nombres de sección para scroll
        section_map = {
            'que_es': 'que_es',
            'header': 'header', 
            'hero': 'hero',
            'ejes': 'ejes',
            'etapas': 'etapas',
            'participa': 'participa',
            'noticias': 'noticias',
            'recursos': 'recursos',
            'contacto': 'contacto'
        }
        target_section = section_map.get(section_name, section_name)
        self.schedule_update(target_section)

    def on_data_changed(self):
        # Actualizar datos desde los campos de sección
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

    # --------------------------- Navegación automática ---------------------------
    def on_tab_changed(self, index):
        """Navegar automáticamente a la sección correspondiente cuando cambia la pestaña"""
        tab_names = ["header", "hero", "que_es", "ejes", "etapas", "participa", "noticias", "recursos", "contacto"]
        if 0 <= index < len(tab_names):
            section_name = tab_names[index]
            self.scroll_to_section(section_name)

    def scroll_to_section(self, section_name):
        """Hacer scroll a una sección específica en el preview"""
        if not hasattr(self, 'preview_browser') or not self.preview_browser:
            return
            
        # Mapeo de nombres de sección a selectores CSS
        section_selectors = {
            "header": "header.site-header",
            "hero": ".hero",
            "que_es": "#que-es",
            "ejes": "#ejes", 
            "etapas": "#etapas",
            "participa": "#participa",
            "noticias": "#noticias",
            "recursos": "#recursos",
            "contacto": "#contacto"
        }
        
        selector = section_selectors.get(section_name)
        if selector:
            # Usar JavaScript para hacer scroll a la sección
            scroll_script = f"""
                (function() {{
                    const targetElement = document.querySelector('{selector}');
                    if (targetElement) {{
                        targetElement.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }}
                }})();
            """
            self.preview_browser.page().runJavaScript(scroll_script)

    def save_scroll_position(self):
        """Guardar la posición actual de scroll"""
        if hasattr(self, 'preview_browser') and self.preview_browser:
            script = "(function() { return window.pageYOffset || document.documentElement.scrollTop; })();"
            self.preview_browser.page().runJavaScript(script, self.on_scroll_position_saved)

    def on_scroll_position_saved(self, position):
        """Callback para cuando se obtiene la posición de scroll"""
        if position is not None:
            self.current_scroll_position = position

    def restore_scroll_position(self):
        """Restaurar la posición de scroll guardada"""
        if hasattr(self, 'pending_section_scroll') and self.pending_section_scroll:
            # Si hay una sección pendiente de mostrar, navegar a ella
            self.scroll_to_section(self.pending_section_scroll)
            self.pending_section_scroll = None
        else:
            # Restaurar posición anterior
            if hasattr(self, 'preview_browser') and self.preview_browser:
                script = f"(function() {{ window.scrollTo(0, {self.current_scroll_position}); }})();"
                self.preview_browser.page().runJavaScript(script)

    def on_preview_loaded(self, success):
        """Callback para cuando el preview termina de cargar"""
        if success:
            # Aplicar vista móvil si está activa
            if hasattr(self, 'is_mobile_view') and self.is_mobile_view:
                QTimer.singleShot(200, self.update_mobile_view)
            
            # Usar un timer pequeño para asegurar que el DOM esté completamente renderizado
            QTimer.singleShot(100, self.restore_scroll_position)

# ========================================================================
# PARTE 7: 🎠 GESTIÓN DE SLIDES
# ========================================================================

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
        self.schedule_update('hero')

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
        self.schedule_update('hero')

    def remove_slide(self):
        idx = self.slides_list.currentRow()
        slides = self.site_data['sections']['hero'].setdefault('slides', [])
        if 0 <= idx < len(slides):
            del slides[idx]
            self.refresh_slides_list()
            self.schedule_update('hero')

# ========================================================================
# PARTE 8: 🧰 MÉTODOS HELPER
# ========================================================================

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
        # Determinar sección objetivo para scroll
        section_map = {'que_es': 'que_es', 'ejes': 'ejes', 'etapas': 'etapas', 'participa': 'participa', 'noticias': 'noticias', 'recursos': 'recursos', 'contacto': 'contacto'}
        target_section = section_map.get(section_name, section_name)
        self.schedule_update(target_section)

    def remove_item(self, section_name, field_name, list_widget):
        current_row = list_widget.currentRow()
        if current_row >= 0:
            del self.site_data['sections'][section_name][field_name][current_row]
            self.update_item_list(list_widget, self.site_data['sections'][section_name][field_name])
            # Determinar sección objetivo para scroll
            section_map = {'que_es': 'que_es', 'ejes': 'ejes', 'etapas': 'etapas', 'participa': 'participa', 'noticias': 'noticias', 'recursos': 'recursos', 'contacto': 'contacto'}
            target_section = section_map.get(section_name, section_name)
            self.schedule_update(target_section)

# ========================================================================
# PARTE 9: 🖥️ GESTIÓN DE PREVIEW
# ========================================================================

    def schedule_update(self, target_section=None):
        """Programar actualización del preview, opcionalmente especificando sección objetivo"""
        # Guardar posición actual antes de actualizar
        self.save_scroll_position()
        
        # Si se especifica una sección objetivo, guardarla
        if target_section:
            self.pending_section_scroll = target_section
            
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
            
            # Manejar loadFinished signal de forma segura
            if hasattr(self.preview_browser, 'loadFinished'):
                self.preview_browser.loadFinished.connect(self.on_preview_loaded)
            
            self.preview_browser.setHtml(html_content)
            
            # NUEVO: Actualizar también la pestaña de código HTML
            self.show_html_source()
            
            self.save_site_data()
        except Exception as e:
            error_html = f"<h1>Error generando HTML:</h1><pre>{e}</pre>"
            self.preview_browser.setHtml(error_html)
            self.html_source_view.setPlainText(f"Error: {str(e)}")

    def reload_preview(self):
        self.update_preview()

    def open_in_browser(self):
        html_path = os.path.join(self.temp_dir, "index.html")
        if os.path.exists(html_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(html_path))

# ========================================================================
# PARTE 10: 🧭 NAVEGACIÓN AUTOMÁTICA (Continuación de Parte 6)
# ========================================================================

# Esta parte ya está incluida en la Parte 6, pero aquí están los métodos adicionales:

# scroll_to_section(), save_scroll_position(), restore_scroll_position() 
# y on_preview_loaded() ya están en la Parte 6

# ========================================================================
# PARTE 11: 📁 GESTIÓN DE ARCHIVOS
# ========================================================================

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

# ========================================================================
# PARTE 12: 🔄 ACTUALIZACIÓN DE UI
# ========================================================================

    def refresh_ui(self):
        # Actualizar campos generales
        self.title_edit.setText(self.site_data['general']['title'])
        self.description_edit.setPlainText(self.site_data['general']['description'])
        
        # Actualizar campos del head
        head_data = self.site_data.get('head', {})
        
        # Meta campos
        self.keywords_edit.setText(head_data.get('meta_keywords', ''))
        self.author_edit.setText(head_data.get('meta_author', ''))
        self.canonical_edit.setText(head_data.get('canonical_url', ''))
        self.theme_color_edit.setText(head_data.get('theme_color', ''))
        self.manifest_edit.setText(head_data.get('manifest_url', ''))
        
        # Open Graph
        self.og_title.setText(head_data.get('og_title', ''))
        self.og_description.setPlainText(head_data.get('og_description', ''))
        self.og_image.setText(head_data.get('og_image', ''))
        
        og_type = head_data.get('og_type', 'website')
        if og_type in ["website", "article", "profile", "book"]:
            self.og_type.setCurrentText(og_type)
        
        # Twitter
        twitter_card = head_data.get('twitter_card', 'summary')
        if twitter_card in ["summary", "summary_large_image", "app", "player"]:
            self.twitter_card.setCurrentText(twitter_card)
        
        self.twitter_site.setText(head_data.get('twitter_site', ''))
        self.twitter_creator.setText(head_data.get('twitter_creator', ''))
        
        # Idioma
        current_lang = head_data.get('lang', 'es')
        languages = [("es", "Español"), ("en", "English"), ("fr", "Français"), ("de", "Deutsch"), ("pt", "Português"), ("it", "Italiano")]
        lang_index = next((i for i, (code, _) in enumerate(languages) if code == current_lang), 0)
        self.lang_combo.setCurrentIndex(lang_index)
        
        # Charset
        charset = head_data.get('charset', 'UTF-8')
        if charset in ["UTF-8", "ISO-8859-1", "Windows-1252"]:
            self.charset_combo.setCurrentText(charset)
        
        # Robots
        current_robots = head_data.get('meta_robots', 'index,follow')
        self.robots_index.setChecked('index' in current_robots.lower())
        self.robots_follow.setChecked('follow' in current_robots.lower())
        self.robots_noarchive.setChecked('noarchive' in current_robots.lower())
        
        # Cache
        self.no_cache_cb.setChecked(head_data.get('disable_cache', False))
        
        # Actualizar paleta de colores
        for color_key, color_btn in self.color_buttons.items():
            if color_key in ['primary_color', 'secondary_color']:
                current_color = self.site_data['general'][color_key]
            else:
                try:
                    with open('css_templates.json', 'r', encoding='utf-8') as f:
                        css_data = json.load(f)
                    current_color = css_data['variables'][color_key]
                except:
                    current_color = "#000000"
            
            color_btn.setStyleSheet(
                f"background-color: {current_color}; border: 1px solid #ccc; border-radius: 4px;"
            )
            color_btn.color_hex = current_color
        
        # Recrear tabs para incluir los nuevos campos del header
        self.tabs.clear()
        self.setup_section_tabs()
        
        # Actualizar campos específicos del header expandido
        self.refresh_ui_header_section()

    def refresh_ui_header_section(self):
        """Actualizar específicamente la sección header con controles mejorados"""
        header_data = self.site_data['sections'].get('header', {})
        
        # Campos básicos
        if hasattr(self, 'header_title'):
            self.header_title.setText(header_data.get('title', ''))
        if hasattr(self, 'header_logo'):
            self.header_logo.setText(header_data.get('logo_url', ''))
        if hasattr(self, 'header_link'):
            self.header_link.setText(header_data.get('logo_link', 'https://'))
        
        # Estilo - Color de fondo
        if hasattr(self, 'header_bg_color_text'):
            bg_color = header_data.get('bg_color', '')
            self.header_bg_color_text.setText(bg_color)
            if hasattr(self, 'header_bg_color_btn') and bg_color:
                if bg_color.startswith('#') and len(bg_color) == 7:
                    self.header_bg_color_btn.setStyleSheet(
                        f"background-color: {bg_color}; border: 1px solid #ccc; border-radius: 4px;"
                    )
                    self.header_bg_color_btn.color_hex = bg_color
        
        # Estilo - Opacidad
        if hasattr(self, 'header_opacity'):
            opacity_value = 1.0
            try:
                opacity_value = float(header_data.get('opacity', '1.0') or '1.0')
            except:
                pass
            self.header_opacity.setValue(opacity_value)
        
        # Estilo - Altura
        if hasattr(self, 'header_height_auto') and hasattr(self, 'header_height'):
            current_height = header_data.get('height', '')
            is_auto = not current_height or current_height.lower() == 'auto'
            self.header_height_auto.setChecked(is_auto)
            self.header_height.setEnabled(not is_auto)
            
            if not is_auto:
                height_value = 72
                try:
                    height_value = int(current_height.replace('px', ''))
                except:
                    pass
                self.header_height.setValue(height_value)
        
        # Estilo - Fuente
        if hasattr(self, 'header_font_family'):
            current_font = header_data.get('font_family', '')
            font_options = [
                ("", "Predeterminada"),
                ("var(--serif)", "Serif (Elegante)"),
                ("var(--sans)", "Sans-serif (Moderna)"),
                ("Georgia, serif", "Georgia"),
                ("'Times New Roman', serif", "Times New Roman"),
                ("Arial, sans-serif", "Arial"),
                ("'Helvetica Neue', sans-serif", "Helvetica"),
                ("'Segoe UI', sans-serif", "Segoe UI"),
                ("system-ui, sans-serif", "Sistema"),
                ("monospace", "Monospace"),
                ("'Courier New', monospace", "Courier New")
            ]
            font_index = next((i for i, (value, _) in enumerate(font_options) if value == current_font), 0)
            self.header_font_family.setCurrentIndex(font_index)
        
        # CTA
        if hasattr(self, 'header_cta_text'):
            self.header_cta_text.setText(header_data.get('cta_text', ''))
        if hasattr(self, 'header_cta_link'):
            self.header_cta_link.setText(header_data.get('cta_link', ''))
        if hasattr(self, 'header_cta_style'):
            cta_style = header_data.get('cta_style', 'primary')
            if cta_style in ["primary", "secondary", "outline"]:
                self.header_cta_style.setCurrentText(cta_style)
        
        # Contacto
        if hasattr(self, 'header_phone'):
            self.header_phone.setText(header_data.get('phone', ''))
        if hasattr(self, 'header_email'):
            self.header_email.setText(header_data.get('email', ''))
        
        # Redes sociales
        if hasattr(self, 'header_facebook'):
            self.header_facebook.setText(header_data.get('social_facebook', ''))
        if hasattr(self, 'header_twitter'):
            self.header_twitter.setText(header_data.get('social_twitter', ''))
        if hasattr(self, 'header_instagram'):
            self.header_instagram.setText(header_data.get('social_instagram', ''))
        if hasattr(self, 'header_linkedin'):
            self.header_linkedin.setText(header_data.get('social_linkedin', ''))
        if hasattr(self, 'header_youtube'):
            self.header_youtube.setText(header_data.get('social_youtube', ''))
        
        # Selector de idioma
        if hasattr(self, 'header_show_lang_selector'):
            self.header_show_lang_selector.setChecked(header_data.get('show_lang_selector', False))
        if hasattr(self, 'header_available_langs'):
            self.header_available_langs.setText(header_data.get('available_langs', ''))
        
        # Comportamiento - Animación
        if hasattr(self, 'header_entrance_animation'):
            animation_options = [
                ("none", "Sin animación"),
                ("slideDown", "Deslizar desde arriba"),
                ("fadeIn", "Aparecer gradualmente"),
                ("slideInLeft", "Deslizar desde izquierda"),
                ("slideInRight", "Deslizar desde derecha")
            ]
            current_animation = header_data.get('entrance_animation', 'none')
            anim_index = next((i for i, (value, _) in enumerate(animation_options) if value == current_animation), 0)
            self.header_entrance_animation.setCurrentIndex(anim_index)
        
        # Comportamiento - Duración animación
        if hasattr(self, 'header_animation_duration'):
            current_duration = header_data.get('animation_duration', '0.5s')
            duration_value = 0.5
            try:
                duration_value = float(current_duration.replace('s', '').replace('ms', ''))
                if 'ms' in current_duration:
                    duration_value = duration_value / 1000
            except:
                pass
            self.header_animation_duration.setValue(duration_value)
        
        # Comportamiento - Scroll
        if hasattr(self, 'header_scroll_behavior'):
            scroll_options = [
                ("normal", "Normal (sin cambios)"),
                ("hide", "Ocultar al hacer scroll"),
                ("shrink", "Encoger al hacer scroll"),
                ("transparent", "Volver transparente")
            ]
            current_scroll = header_data.get('scroll_behavior', 'normal')
            scroll_index = next((i for i, (value, _) in enumerate(scroll_options) if value == current_scroll), 0)
            self.header_scroll_behavior.setCurrentIndex(scroll_index)
        
        # Comportamiento - Umbral scroll
        if hasattr(self, 'header_scroll_threshold'):
            threshold_value = 100
            try:
                threshold_value = int(header_data.get('scroll_threshold', '100'))
            except:
                pass
            self.header_scroll_threshold.setValue(threshold_value)
        
        # Comportamiento - Sticky
        if hasattr(self, 'header_sticky'):
            self.header_sticky.setChecked(header_data.get('sticky', True))

# ========================================================================
# PARTE 13: 🚪 CIERRE Y MAIN
# ========================================================================

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