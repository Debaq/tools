import json

class FlexibleHTMLGenerator:
    def __init__(self, site_data):
        self.site_data = site_data
        self.load_templates()
        
    def load_templates(self):
        try:
            with open('css_templates.json', 'r', encoding='utf-8') as f:
                self.css_data = json.load(f)
            with open('section_templates.json', 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        except FileNotFoundError as e:
            print(f"Error: No se encontró el archivo {e.filename}")
            self.css_data = {"variables": {}, "base_styles": [], "components": {}}
            self.templates = {"section_templates": {}, "item_templates": {}}
            
    # ------------------------- HEAD / META -------------------------
    def generate_head(self):
        head = self.site_data.get("head", {})
        general = self.site_data.get("general", {})
        title = head.get("title") or general.get("title") or "Sitio"
        meta_desc = head.get("meta_description") or general.get("description", "")
        charset = head.get("charset", "UTF-8")
        robots = head.get("meta_robots", "index,follow")
        favicon = head.get("favicon_url", "")
        no_cache = head.get("disable_cache", False)

        meta_cache = ""
        if no_cache:
            meta_cache = (
                '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
                '<meta http-equiv="Pragma" content="no-cache">'
                '<meta http-equiv="Expires" content="0">'
            )

        favicon_link = f'<link rel="icon" href="{favicon}">' if favicon else ""

        head_html = f"""
    <meta charset="{charset}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="robots" content="{robots}">
    {favicon_link}
    {meta_cache}
    {self.generate_css()}
    """
        return head_html

    def html_lang(self):
        return self.site_data.get("head", {}).get("lang", "es")

    # --------------------------- CSS ---------------------------
    def generate_css(self):
        css_content = "<style>\n"
        variables = self.css_data["variables"].copy()
        variables["primary_color"] = self.site_data["general"]["primary_color"]
        variables["secondary_color"] = self.site_data["general"]["secondary_color"]

        # Solo reemplaza placeholders {primary_color}, etc. y
        # convierte '{{' en '{' (abrir), dejando '}}' tal cual (cierra dos)
        def safe_replace(s: str) -> str:
            s = s.replace('{{', '{')  # aperturas dobles -> literal '{'
            for k, v in variables.items():
                s = s.replace('{'+k+'}', v)  # placeholders
            return s

        for style in self.css_data["base_styles"]:
            css_content += safe_replace(style) + "\n"

        for component_styles in self.css_data["components"].values():
            for style in component_styles:
                css_content += safe_replace(style) + "\n"

        css_content += "</style>"
        return css_content

        
    # ------------------------ NAVIGATION ------------------------
    def generate_navigation(self):
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

    # ------------------------- ITEMS -------------------------
    def generate_items(self, items, template_name):
        if not items:
            return ""
        template = self.templates["item_templates"].get(template_name, "")
        if not template:
            return ""
        items_html = []
        for item in items:
            item_copy = item.copy()
            if "address" in item_copy:
                item_copy["address"] = item_copy["address"].replace("\n", "<br>")
            defaults = {
                "card_basic": {"pill": "Info", "title": "Sin título", "text": "Sin contenido"},
                "card_with_icon": {"icon": "📌", "title": "Sin título", "text": "Sin contenido"},
                "timeline_item": {"title": "Sin título", "text": "Sin contenido"},
                "news_card": {"icon": "📰", "title": "Sin título", "meta": "", "text": "Sin contenido"},
                "resource_card": {"icon": "📄", "title": "Sin título", "text": "Sin contenido"},
                "hero_slide": {"eyebrow_html":"", "title":"Sin título", "text":"","buttons_html":"","hero_bg_style":"","hero_fonts":""}
            }
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

    # ------------------------- SECTIONS -------------------------
    def header_brand_logo_html(self):
        header_data = self.site_data["sections"].get("header", {})
        logo_url = header_data.get("logo_url", "")
        logo_link = header_data.get("logo_link", "#")
        if not logo_url:
            return '<div class="brand__logo"></div>'
        return f'<a class="brand__logo" href="{logo_link}"><img src="{logo_url}" alt="Logo"></a>'

    def split_eyebrows(self, text, rainbow=False):
        if not text:
            return ""
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if not parts:
            return ""
        if rainbow and len(parts) > 1:
            spans = []
            import random
            random.seed(42)
            for p in parts:
                h = random.randint(0, 360)
                span = f'<span class="hero__eyebrow" style="background:hsl({h},85%,70%);">{p}</span>'
                spans.append(span)
            return "".join(spans)
        else:
            return "".join([f'<span class="hero__eyebrow">{p}</span>' for p in parts])

    def hero_bg_style_from_slide(self, slide):
        bg_type = slide.get("bg_type", "gradient")
        if bg_type == "image" and slide.get("bg_image_url"):
            return f'background:url("{slide["bg_image_url"]}") center/cover no-repeat;'
        g1 = slide.get("bg_gradient_from", "#004527")
        g2 = slide.get("bg_gradient_to", "#00693e")
        return f'background:linear-gradient(180deg, {g1}, {g2});'

    def hero_buttons_html(self, buttons):
        if not buttons:
            return ""
        btns = []
        for b in buttons:
            style = b.get("style", "primary")
            label = b.get("label", "Más información")
            href = b.get("href", "#")
            cls = "btn btn--primary" if style == "primary" else "btn btn--secondary"
            btns.append(f'<a class="{cls}" href="{href}">{label}</a>')
        return "".join(btns)

    def hero_fonts_style(self, hero_data):
        ft = hero_data.get("font_title", "var(--serif)")
        fb = hero_data.get("font_body", "var(--sans)")
        return f'--hero-title-font:{ft};--hero-body-font:{fb};'

    def generate_section(self, section_name):
        section_data = self.site_data["sections"].get(section_name, {})
        if not section_data.get("enabled", False):
            return ""

        if section_name == "header":
            tpl = self.templates["section_templates"]["header"]["template"]
            return tpl.format(
                title=section_data.get("title",""),
                navigation=self.generate_navigation(),
                brand_logo_html=self.header_brand_logo_html()
            )

        if section_name == "hero":
            hero = section_data
            slides = hero.get("slides", [])
            rainbow = hero.get("rainbow_eyebrow", False)
            if len(slides) <= 1:
                slide = slides[0] if slides else {}
                eyebrow_html = self.split_eyebrows(slide.get("eyebrow",""), rainbow)
                hero_bg_style = self.hero_bg_style_from_slide(slide)
                buttons_html = self.hero_buttons_html(slide.get("buttons", []))
                hero_fonts = self.hero_fonts_style(hero)
                tpl = self.templates["section_templates"]["hero_single"]["template"]
                return tpl.format(
                    eyebrow_html=eyebrow_html,
                    title=slide.get("title",""),
                    text=slide.get("text",""),
                    buttons_html=buttons_html,
                    hero_bg_style=hero_bg_style,
                    hero_fonts=hero_fonts
                )
            else:
                slide_items = []
                for sl in slides:
                    eyebrow_html = self.split_eyebrows(sl.get("eyebrow",""), rainbow)
                    hero_bg_style = self.hero_bg_style_from_slide(sl)
                    buttons_html = self.hero_buttons_html(sl.get("buttons", []))
                    hero_fonts = self.hero_fonts_style(hero)
                    slide_items.append({
                        "eyebrow_html": eyebrow_html,
                        "title": sl.get("title",""),
                        "text": sl.get("text",""),
                        "buttons_html": buttons_html,
                        "hero_bg_style": hero_bg_style,
                        "hero_fonts": hero_fonts
                    })
                slides_html = self.generate_items(slide_items, "hero_slide")
                dots_html = "".join([f'<button class="dot" onclick="showSlide({i})"></button>' for i in range(len(slides))])
                tpl = self.templates["section_templates"]["hero_carousel"]["template"]
                return tpl.format(slides_html=slides_html, dots_html=dots_html)

        section_mapping = {
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
            "participa": {
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

    # ------------------------- HTML FULL -------------------------
    def generate_html(self):
        head_html = self.generate_head()
        lang = self.html_lang()
        html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
{head_html}
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
