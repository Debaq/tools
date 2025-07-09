# styles.py - Estilos CSS para MarkNote

def get_main_theme():
    return """
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
            stop:0 #1a0d26, stop:0.5 #2d1b3d, stop:1 #1a0d26);
        color: #e6d7ff;
    }
    QMenuBar {
        background-color: #2d1b3d;
        color: #e6d7ff;
        border-bottom: 2px solid #6a4c93;
        font-size: 14px;
        padding: 4px;
    }
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 16px;
        border-radius: 6px;
        margin: 2px;
    }
    QMenuBar::item:selected {
        background-color: #8a2be2;
        color: white;
    }
    QMenu {
        background-color: #3d2a52;
        border: 2px solid #6a4c93;
        color: #e6d7ff;
        border-radius: 8px;
    }
    QMenu::item:selected {
        background-color: #8a2be2;
        color: white;
    }
    QTextEdit {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #2d1b3d, stop:1 #3d2a52);
        border: 2px solid #6a4c93;
        border-radius: 12px;
        padding: 30px;
        selection-background-color: #8a2be2;
    }
    QLineEdit {
        background-color: #3d2a52;
        border: 2px solid #6a4c93;
        border-radius: 8px;
        padding: 8px 12px;
        color: #e6d7ff;
        font-size: 14px;
    }
    QLineEdit:focus {
        border-color: #bb86fc;
        background-color: #4a3361;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #8a2be2, stop:1 #6a4c93);
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #9932cc, stop:1 #7a5ca3);
    }
    QPushButton:pressed {
        background-color: #6a4c93;
    }
    QComboBox {
        background-color: #3d2a52;
        border: 2px solid #6a4c93;
        border-radius: 6px;
        padding: 6px 12px;
        color: #e6d7ff;
        min-width: 120px;
    }
    QComboBox:hover {
        border-color: #8a2be2;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox::down-arrow {
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #e6d7ff;
    }
    QComboBox QAbstractItemView {
        background-color: #3d2a52;
        border: 2px solid #6a4c93;
        color: #e6d7ff;
        selection-background-color: #8a2be2;
    }
    QSpinBox {
        background-color: #3d2a52;
        border: 2px solid #6a4c93;
        border-radius: 6px;
        padding: 6px;
        color: #e6d7ff;
        min-width: 60px;
    }
    QSpinBox:hover {
        border-color: #8a2be2;
    }
    QLabel {
        color: #e6d7ff;
        font-weight: bold;
    }
    """

def get_dialog_theme():
    return """
    QDialog {
        background-color: #2d1b3d;
        color: #e6d7ff;
    }
    QTextEdit {
        background-color: #3d2a52;
        border: 2px solid #6a4c93;
        border-radius: 8px;
        padding: 8px;
        color: #e6d7ff;
    }
    QLineEdit {
        background-color: #1a1a2e;
        border: 2px solid #6a4c93;
        border-radius: 8px;
        padding: 10px;
        color: #e6d7ff;
        font-family: 'Consolas';
        font-size: 12px;
    }
    QPushButton {
        background-color: #8a2be2;
        border: none;
        padding: 10px 18px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #9932cc;
    }
    """

def get_overlay_style():
    return """
    QFrame {
        background-color: rgba(138, 43, 226, 0.9);
        border: 2px solid #8a2be2;
        border-radius: 12px;
        padding: 12px;
        color: #ffffff;
        font-weight: bold;
        font-size: 13px;
    }
    """

def get_markdown_css(font_family, font_size):
    return f"""
    <style>
    body {{
        font-family: '{font_family}', 'Georgia', serif;
        font-size: {font_size}px;
        line-height: 1.8;
        color: #e6d7ff;
        background-color: transparent;
        margin: 0;
        padding: 20px;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: #bb86fc;
        font-weight: bold;
        margin-top: 24px;
        margin-bottom: 16px;
        font-family: '{font_family}', serif;
    }}
    h1 {{ font-size: {font_size * 1.8}px; border-bottom: 2px solid #6a4c93; padding-bottom: 8px; }}
    h2 {{ font-size: {font_size * 1.5}px; color: #cf6679; }}
    h3 {{ font-size: {font_size * 1.3}px; color: #8a2be2; }}
    h4 {{ font-size: {font_size * 1.1}px; color: #bb86fc; }}
    p {{ margin-bottom: 16px; }}
    strong {{ color: #bb86fc; font-weight: bold; }}
    em {{ color: #cf6679; font-style: italic; }}
    code {{
        background-color: #3d2a52;
        color: #bb86fc;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Consolas', monospace;
        font-size: {font_size * 0.9}px;
    }}
    pre {{
        background-color: #2d1b3d;
        border: 1px solid #6a4c93;
        border-radius: 8px;
        padding: 16px;
        overflow-x: auto;
        font-size: {font_size * 0.85}px;
    }}
    pre code {{
        background-color: transparent;
        padding: 0;
    }}
    ul, ol {{ margin-left: 20px; }}
    li {{ margin-bottom: 8px; }}
    blockquote {{
        border-left: 4px solid #8a2be2;
        margin: 16px 0;
        padding-left: 16px;
        color: #b19cd9;
        font-style: italic;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 16px 0;
    }}
    th, td {{
        border: 1px solid #6a4c93;
        padding: 12px;
        text-align: left;
    }}
    th {{
        background-color: #3d2a52;
        color: #bb86fc;
        font-weight: bold;
    }}
    a {{ color: #bb86fc; text-decoration: underline; }}
    a:hover {{ color: #cf6679; }}
    </style>
    """