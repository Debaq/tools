import json

class FlexibleHTMLGenerator:
    def __init__(self, site_data):
        self.site_data = site_data
        self.load_templates()
        
    def load_templates(self):
        """Cargar plantillas desde archivos JSON"""
        try:
            with open('css_templates.json', 'r', encoding='utf-8') as f:
                self.css_data = json.load(f)
            with open('section_templates.json', 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        except FileNotFoundError as e:
            print(f"Error: No se encontró el archivo {e.filename}")
            self.css_data = {"variables": {}, "base_styles": [], "components": {}}
            self.templates = {"section_templates": {}, "item_templates": {}}
            
    def generate_css(self):
        """Generar CSS dinámico basado en plantillas"""
        css_content = "<style>\n"
        
        # Variables CSS con valores dinámicos
        variables = self.css_data["variables"].copy()
        variables["primary_color"] = self.site_data["general"]["primary_color"]
        variables["secondary_color"] = self.site_data["general"]["secondary_color"]
        
        # Aplicar variables a estilos base
        for style in self.css_data["base_styles"]:
            css_content += style.format(**variables) + "\n"
            
        # Agregar estilos de componentes
        for component_styles in self.css_data["components"].values():
            for style in component_styles:
                css_content += style.format(**variables) + "\n"
                
        css_content += "</style>"
        return css_content
        
    def generate_navigation(self):
        """Generar navegación dinámica"""
        nav_items = []
        nav_template = self.templates.get("navigation_template", "<a href=\"#{section_id}\">{nav_text}</a>")
        
        nav_mapping = {
            "que_es": "¿Qué es?",
            "ejes": "Ejes", 
            "etapas": "Etapas",
            "participa": "Participa",
            "noticias": "Noticias",
            "recursos": "Recursos",
            "contacto": "Contacto"
        }
        
        for section_id, nav_text in nav_mapping.items():
            if self.site_data["sections"].get(section_id, {}).get("enabled", False):
                nav_items.append(nav_template.format(section_id=section_id, nav_text=nav_text))
                
        return "\n        ".join(nav_items)
        
    def generate_items(self, items, template_name):
        """Generar elementos iterativos (cards, timeline, etc.)"""
        if not items:
            return ""

        template = self.templates["item_templates"].get(template_name, "")
        if not template:
            return ""

        items_html = []
        for item in items:
            # Crear copia del item para no modificar el original
            item_copy = item.copy()

            # Formatear dirección para HTML si existe
            if "address" in item_copy:
                item_copy["address"] = item_copy["address"].replace("\n", "<br>")

            # Agregar valores por defecto según el tipo de template
            defaults = {
                "card_basic": {"pill": "Info", "title": "Sin título", "text": "Sin contenido"},
                "card_with_icon": {"icon": "📌", "title": "Sin título", "text": "Sin contenido"},
                "timeline_item": {"title": "Sin título", "text": "Sin contenido"},
                "news_card": {"icon": "📰", "title": "Sin título", "meta": "", "text": "Sin contenido"},
                "resource_card": {"icon": "📄", "title": "Sin título", "text": "Sin contenido"}
            }

            # Aplicar valores por defecto
            if template_name in defaults:
                for key, value in defaults[template_name].items():
                    if key not in item_copy:
                        item_copy[key] = value

            try:
                items_html.append(template.format(**item_copy))
            except KeyError as e:
                print(f"Campo faltante en {template_name}: {e}")
                continue

        return "\n            ".join(items_html)

    def generate_section(self, section_name):
        """Generar una sección específica"""
        section_data = self.site_data["sections"].get(section_name, {})
        if not section_data.get("enabled", False):
            return ""
            
        # Mapeo de secciones a plantillas y configuraciones
        section_mapping = {
            "header": {
                "template": "header",
                "data": {"title": section_data.get("title", ""), "navigation": self.generate_navigation()}
            },
            "hero": {
                "template": "hero", 
                "data": section_data
            },
            "que_es": {
                "template": "section_with_cards",
                "data": {**section_data, "section_id": "que-es", "section_class": "container",
                        "cards": self.generate_items(section_data.get("cards", []), "card_basic")}
            },
            "ejes": {
                "template": "section_with_cards",
                "data": {**section_data, "section_id": "ejes", "section_class": "band",
                        "cards": self.generate_items(section_data.get("cards", []), "card_with_icon")}
            },
            "etapas": {
                "template": "section_with_timeline",
                "data": {**section_data, "section_id": "etapas",
                        "timeline_items": self.generate_items(section_data.get("timeline", []), "timeline_item")}
            },
            "participa": {  # <-- AGREGAR AQUÍ
                "template": "section_with_cards",
                "data": {**section_data, "section_id": "participa", "section_class": "container",
                        "cards": self.generate_items(section_data.get("cards", []), "card_basic")}
            },
            "noticias": {
                "template": "section_with_cards",
                "data": {**section_data, "section_id": "noticias", "section_class": "container",
                        "cards": self.generate_items(section_data.get("news", []), "news_card")}
            },
            "recursos": {
                "template": "section_with_cards", 
                "data": {**section_data, "section_id": "recursos", "section_class": "band",
                        "cards": self.generate_items(section_data.get("resources", []), "resource_card")}
            },
            "contacto": {
                "template": "contact_section",
                "data": {**section_data, "address": section_data.get("address", "").replace("\n", "<br>")}
            },
            "footer": {
                "template": "footer",
                "data": {}
            }
        }
        
        config = section_mapping.get(section_name)
        if not config:
            return ""
            
        template_obj = self.templates["section_templates"].get(config["template"], {})
        template = template_obj.get("template", "") if isinstance(template_obj, dict) else template_obj
        if not template:
            return ""
            
        return template.format(**config["data"])
        
    def generate_html(self):
        """Generar HTML completo"""
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.site_data['general']['title']}</title>
    <meta name="description" content="{self.site_data['general']['description']}">
    {self.generate_css()}
</head>
<body>
    {self.generate_section('header')}
    <main>
        {self.generate_section('hero')}
        {self.generate_section('que_es')}
        {self.generate_section('ejes')}
        {self.generate_section('etapas')}
        {self.generate_section('participa') if self.site_data['sections'].get('participa', {}).get('enabled') else ''}
        {self.generate_section('noticias')}
        {self.generate_section('recursos')}
        {self.generate_section('contacto')}
    </main>
    {self.generate_section('footer')}
    <script>{self.templates.get('javascript', '')}</script>
</body>
</html>"""
        
        return html
