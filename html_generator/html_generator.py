# ========================================================================
# PARTE 1: 🔧 IMPORTS Y CONFIGURACIÓN INICIAL
# ========================================================================

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

# ========================================================================
# PARTE 2: 📄 GENERACIÓN DE HEAD Y META
# ========================================================================

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

        # Meta adicionales
        meta_keywords = head.get("meta_keywords", "")
        meta_author = head.get("meta_author", "")
        canonical_url = head.get("canonical_url", "")
        theme_color = head.get("theme_color", "")
        manifest_url = head.get("manifest_url", "")

        # Open Graph
        og_title = head.get("og_title", title)
        og_description = head.get("og_description", meta_desc)
        og_image = head.get("og_image", "")
        og_type = head.get("og_type", "website")

        # Twitter Cards
        twitter_card = head.get("twitter_card", "summary")
        twitter_site = head.get("twitter_site", "")
        twitter_creator = head.get("twitter_creator", "")

        # Construir meta tags adicionales
        additional_meta = ""
        
        if meta_keywords:
            additional_meta += f'<meta name="keywords" content="{meta_keywords}">\n    '
        
        if meta_author:
            additional_meta += f'<meta name="author" content="{meta_author}">\n    '
        
        if canonical_url:
            additional_meta += f'<link rel="canonical" href="{canonical_url}">\n    '
        
        if theme_color:
            additional_meta += f'<meta name="theme-color" content="{theme_color}">\n    '
        
        if manifest_url:
            additional_meta += f'<link rel="manifest" href="{manifest_url}">\n    '

        # Open Graph tags
        og_meta = ""
        if og_title:
            og_meta += f'<meta property="og:title" content="{og_title}">\n    '
        if og_description:
            og_meta += f'<meta property="og:description" content="{og_description}">\n    '
        if og_image:
            og_meta += f'<meta property="og:image" content="{og_image}">\n    '
        if og_type:
            og_meta += f'<meta property="og:type" content="{og_type}">\n    '

        # Twitter Cards
        twitter_meta = ""
        if twitter_card:
            twitter_meta += f'<meta name="twitter:card" content="{twitter_card}">\n    '
        if twitter_site:
            twitter_meta += f'<meta name="twitter:site" content="{twitter_site}">\n    '
        if twitter_creator:
            twitter_meta += f'<meta name="twitter:creator" content="{twitter_creator}">\n    '

        head_html = f"""
    <meta charset="{charset}">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="robots" content="{robots}">
    {additional_meta}{og_meta}{twitter_meta}{favicon_link}
    {meta_cache}
    {self.generate_css()}
    """
        return head_html

    def html_lang(self):
        return self.site_data.get("head", {}).get("lang", "es")

# ========================================================================
# PARTE 3: 🎨 GENERACIÓN DE CSS
# ========================================================================

    def generate_css(self):
        css_content = "<style>\n"
        variables = self.css_data["variables"].copy()
        variables["primary_color"] = self.site_data["general"]["primary_color"]
        variables["secondary_color"] = self.site_data["general"]["secondary_color"]

        def fmt_line(s):
            try:
                return s.format(**variables)
            except Exception:
                return s

        # base styles
        for style in self.css_data.get("base_styles", []):
            css_content += fmt_line(style) + "\n"
        # component styles
        for component_styles in self.css_data.get("components", {}).values():
            for style in component_styles:
                css_content += fmt_line(style) + "\n"

        # UX: que el sticky header no tape títulos
        css_content += "section, .container { scroll-margin-top: 84px; }\n"

        # Desescapar llaves literales para que el CSS quede con {} simples
        css_content = css_content.replace("{{", "{").replace("}}", "}")
        css_content += "</style>"
        return css_content

# ========================================================================
# PARTE 4: 🧭 GENERACIÓN DE NAVEGACIÓN
# ========================================================================

    def generate_navigation(self):
        nav_items = []
        nav_template = self.templates.get("navigation_template", "<a href=\"#{section_id}\">{nav_text}</a>")
        entries = [
            ("que_es", "que-es", "¿Qué es?"),
            ("ejes", "ejes", "Ejes"),
            ("etapas", "etapas", "Etapas"),
            ("participa", "participa", "Participa"),
            ("noticias", "noticias", "Noticias"),
            ("recursos", "recursos", "Recursos"),
            ("contacto", "contacto", "Contacto"),
        ]
        for key, dom_id, nav_text in entries:
            if self.site_data["sections"].get(key, {}).get("enabled", False):
                nav_items.append(nav_template.format(section_id=dom_id, nav_text=nav_text))
        return "\n        ".join(nav_items)

# ========================================================================
# PARTE 5: 🏗️ GENERACIÓN DE ITEMS
# ========================================================================

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
            
            # Generar estilos personalizados para cards
            card_styles = []
            if item_copy.get('bg_color'):
                card_styles.append(f"background-color: {item_copy['bg_color']}")
            if item_copy.get('font_title'):
                card_styles.append(f"--card-title-font: {item_copy['font_title']}")
            if item_copy.get('font_text'):
                card_styles.append(f"--card-text-font: {item_copy['font_text']}")
            
            item_copy['card_style'] = "; ".join(card_styles) if card_styles else ""
            
            defaults = {
                "card_basic": {"pill": "Info", "title": "Sin título", "text": "Sin contenido", "card_style": ""},
                "card_with_icon": {"icon": "📌", "title": "Sin título", "text": "Sin contenido", "card_style": ""},
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

# ========================================================================
# PARTE 6: 🎯 HEADER - MÉTODOS HELPER
# ========================================================================

    def header_brand_logo_html(self):
        header_data = self.site_data["sections"].get("header", {})
        logo_url = header_data.get("logo_url", "")
        logo_link = header_data.get("logo_link", "#")
        if not logo_url:
            return '<div class="brand__logo"></div>'
        return f'<a class="brand__logo" href="{logo_link}"><img src="{logo_url}" alt="Logo"></a>'

    def header_custom_styles(self):
        """Genera estilos personalizados para el header"""
        header_data = self.site_data["sections"].get("header", {})
        styles = []
        
        # Color de fondo personalizado
        if header_data.get("bg_color"):
            styles.append(f"background: {header_data['bg_color']}")
        
        # Opacidad
        if header_data.get("opacity"):
            styles.append(f"opacity: {header_data['opacity']}")
        
        # Altura personalizada
        if header_data.get("height"):
            styles.append(f"min-height: {header_data['height']}")
        
        # Sticky o no
        if not header_data.get("sticky", True):
            styles.append("position: relative")
        
        return "; ".join(styles)

    def header_brand_font_style(self):
        """Genera estilos para la fuente del título de marca"""
        header_data = self.site_data["sections"].get("header", {})
        if header_data.get("font_family"):
            return f"font-family: {header_data['font_family']}"
        return ""

    def header_contact_info_html(self):
        """Genera HTML para información de contacto en el header"""
        header_data = self.site_data["sections"].get("header", {})
        contact_items = []
        
        if header_data.get("phone"):
            contact_items.append(f'<a href="tel:{header_data["phone"]}" title="Llamar">📞 {header_data["phone"]}</a>')
        
        if header_data.get("email"):
            contact_items.append(f'<a href="mailto:{header_data["email"]}" title="Enviar email">✉️ {header_data["email"]}</a>')
        
        if contact_items:
            return f'<div class="header-contact">{"".join(contact_items)}</div>'
        return ""

    def header_social_links_html(self):
        """Genera HTML para enlaces de redes sociales en el header"""
        header_data = self.site_data["sections"].get("header", {})
        social_links = []
        
        social_networks = [
            ("social_facebook", "🔗", "Facebook"),
            ("social_twitter", "🐦", "Twitter/X"),
            ("social_instagram", "📷", "Instagram"),
            ("social_linkedin", "💼", "LinkedIn"),
            ("social_youtube", "🎥", "YouTube")
        ]
        
        for key, icon, name in social_networks:
            if header_data.get(key):
                social_links.append(f'<a href="{header_data[key]}" target="_blank" rel="noopener" title="{name}">{icon}</a>')
        
        if social_links:
            return f'<div class="header-social">{"".join(social_links)}</div>'
        return ""

    def header_lang_selector_html(self):
        """Genera HTML para selector de idioma en el header"""
        header_data = self.site_data["sections"].get("header", {})
        
        if not header_data.get("show_lang_selector", False):
            return ""
        
        available_langs = header_data.get("available_langs", "").strip()
        if not available_langs:
            return ""
        
        current_lang = self.site_data.get("head", {}).get("lang", "es")
        lang_codes = [lang.strip() for lang in available_langs.split(",") if lang.strip()]
        
        if len(lang_codes) <= 1:
            return ""
        
        lang_names = {
            "es": "Español",
            "en": "English", 
            "fr": "Français",
            "de": "Deutsch",
            "pt": "Português",
            "it": "Italiano",
            "ca": "Català",
            "eu": "Euskera"
        }
        
        options = []
        for code in lang_codes:
            name = lang_names.get(code, code.upper())
            selected = ' selected' if code == current_lang else ''
            options.append(f'<option value="{code}"{selected}>{name}</option>')
        
        return f'''<div class="header-lang-selector">
            <select onchange="window.location.href='?lang='+this.value">
                {"".join(options)}
            </select>
        </div>'''

    def header_cta_button_html(self):
        """Genera HTML para botón CTA en el header"""
        header_data = self.site_data["sections"].get("header", {})
        
        cta_text = header_data.get("cta_text", "").strip()
        cta_link = header_data.get("cta_link", "").strip()
        
        if not cta_text or not cta_link:
            return ""
        
        cta_style = header_data.get("cta_style", "primary")
        css_class = {
            "primary": "btn btn--primary",
            "secondary": "btn btn--secondary", 
            "outline": "btn btn--outline"
        }.get(cta_style, "btn btn--primary")
        
        return f'<div class="header-cta"><a class="{css_class}" href="{cta_link}">{cta_text}</a></div>'

# ========================================================================
# PARTE 7: 🎠 HERO - MÉTODOS HELPER
# ========================================================================

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

# ========================================================================
# PARTE 8: 📑 GENERACIÓN DE SECCIONES
# ========================================================================

    def generate_section(self, section_name):
        section_data = self.site_data["sections"].get(section_name, {})
        if not section_data.get("enabled", False):
            return ""

        if section_name == "header":
            tpl = self.templates["section_templates"]["header"]["template"]
            return tpl.format(
                title=section_data.get("title",""),
                navigation=self.generate_navigation(),
                brand_logo_html=self.header_brand_logo_html(),
                header_custom_styles=self.header_custom_styles(),
                brand_font_style=self.header_brand_font_style(),
                entrance_animation=section_data.get("entrance_animation", "none"),
                scroll_behavior=section_data.get("scroll_behavior", "normal"),
                scroll_threshold=section_data.get("scroll_threshold", "100"),
                contact_info_html=self.header_contact_info_html(),
                social_links_html=self.header_social_links_html(),
                lang_selector_html=self.header_lang_selector_html(),
                cta_button_html=self.header_cta_button_html()
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

        if section_name == "que_es":
            # Preparar datos con defaults completos
            data = {
                "eyebrow": section_data.get('eyebrow', ''),
                "title": section_data.get('title', ''),
                "description": section_data.get('description', ''),
                "section_id": "que-es",
                "section_class": "container",
                "cards": self.generate_items(section_data.get("cards", []), "card_basic"),
                "section_title_style": f"font-family: {section_data.get('font_title')}" if section_data.get('font_title') else "",
                "section_desc_style": f"font-family: {section_data.get('font_description')}" if section_data.get('font_description') else ""
            }
            
            template_obj = self.templates["section_templates"].get("section_with_cards", {})
            template = template_obj.get("template", "") if isinstance(template_obj, dict) else template_obj
            if not template:
                return ""
            return template.format(**data)

        section_mapping = {
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

# ========================================================================
# PARTE 9: 🌐 GENERACIÓN HTML FINAL
# ========================================================================

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