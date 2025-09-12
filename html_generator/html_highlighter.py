from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression
import re

class HTMLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_highlighting_rules()

    def setup_highlighting_rules(self):
        self.highlighting_rules = []

        # HTML Tags
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#0066CC"))  # Azul
        tag_format.setFontWeight(600)
        tag_pattern = QRegularExpression(r"<[!?/]?[a-zA-Z0-9_-]+(?:\s|>|/>)")
        self.highlighting_rules.append((tag_pattern, tag_format))

        # HTML Attributes
        attr_format = QTextCharFormat()
        attr_format.setForeground(QColor("#CC6600"))  # Naranja
        attr_pattern = QRegularExpression(r"\b[a-zA-Z0-9_-]+(?=\s*=)")
        self.highlighting_rules.append((attr_pattern, attr_format))

        # HTML Attribute Values
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#009900"))  # Verde
        value_pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((value_pattern, value_format))

        # CSS Selectors
        css_selector_format = QTextCharFormat()
        css_selector_format.setForeground(QColor("#6F42C1"))  # Púrpura
        css_selector_format.setFontWeight(600)
        css_selector_pattern = QRegularExpression(r"[.#]?[a-zA-Z0-9_-]+(?=\s*\{)|[a-zA-Z0-9_-]+(?=\s*\{)")
        self.highlighting_rules.append((css_selector_pattern, css_selector_format))

        # CSS Properties
        css_property_format = QTextCharFormat()
        css_property_format.setForeground(QColor("#E74C3C"))  # Rojo
        css_property_pattern = QRegularExpression(r"[a-zA-Z-]+(?=\s*:)")
        self.highlighting_rules.append((css_property_pattern, css_property_format))

        # CSS Values
        css_value_format = QTextCharFormat()
        css_value_format.setForeground(QColor("#27AE60"))  # Verde
        css_value_pattern = QRegularExpression(r"(?<=:\s)[^;]+(?=;)")
        self.highlighting_rules.append((css_value_pattern, css_value_format))

        # CSS Units and Numbers
        css_number_format = QTextCharFormat()
        css_number_format.setForeground(QColor("#F39C12"))  # Naranja
        css_number_pattern = QRegularExpression(r"\b\d+(?:\.\d+)?(?:px|em|rem|%|vh|vw|pt|pc|in|cm|mm|ex|ch|fr|s|ms|deg|rad|turn)?\b")
        self.highlighting_rules.append((css_number_pattern, css_number_format))

        # CSS Colors (hex, rgb, rgba, hsl, hsla)
        css_color_format = QTextCharFormat()
        css_color_format.setForeground(QColor("#8E44AD"))  # Púrpura oscuro
        css_color_pattern = QRegularExpression(r"#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|hsla\([^)]+\)")
        self.highlighting_rules.append((css_color_pattern, css_color_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#999999"))  # Gris claro
        comment_format.setFontItalic(True)
        comment_pattern = QRegularExpression(r"<!--.*?-->")
        self.highlighting_rules.append((comment_pattern, comment_format))

        # Doctype
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(QColor("#990099"))  # Púrpura
        doctype_format.setFontWeight(600)
        doctype_pattern = QRegularExpression(r"<!DOCTYPE[^>]*>")
        self.highlighting_rules.append((doctype_pattern, doctype_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = pattern
            iterator = expression.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)