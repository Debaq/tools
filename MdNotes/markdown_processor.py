# markdown_processor.py - Procesador inteligente de markdown

import re
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass

@dataclass
class MarkdownPattern:
    """Patrón de markdown detectado"""
    type: str  # 'header', 'bold', 'italic', 'code', 'quote', 'list', etc.
    level: int  # Para headers (1-6), para listas (indentación)
    start_marker: str  # Marcador inicial (ej: '##', '**', etc.)
    end_marker: str  # Marcador final (si aplica)
    content: str  # Contenido sin marcadores

class MarkdownProcessor:
    """Procesador inteligente para preservar y detectar formato markdown"""
    
    def __init__(self):
        self.patterns = {
            'header': [
                (r'^(#{1,6})\s+(.+)$', self._process_header),
                (r'^(.+)\n={3,}$', self._process_h1_underline),
                (r'^(.+)\n-{3,}$', self._process_h2_underline),
            ],
            'list': [
                (r'^(\s*)([-*+])\s+(.+)$', self._process_unordered_list),
                (r'^(\s*)(\d+\.)\s+(.+)$', self._process_ordered_list),
            ],
            'quote': [
                (r'^>\s*(.+)$', self._process_quote),
            ],
            'code_block': [
                (r'^```(\w*)\n(.*?)\n```$', self._process_code_block),
            ],
            'inline_formatting': [
                (r'\*\*(.+?)\*\*', self._process_bold),
                (r'\*(.+?)\*', self._process_italic),
                (r'`(.+?)`', self._process_inline_code),
            ]
        }
    
    def detect_markdown_patterns(self, text: str) -> List[MarkdownPattern]:
        """Detectar todos los patrones markdown en el texto"""
        patterns = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detectar headers con underline (necesita línea siguiente)
            if i < len(lines) - 1:
                next_line = lines[i + 1]
                
                # H1 con ===
                if re.match(r'^={3,}$', next_line.strip()):
                    patterns.append(MarkdownPattern(
                        type='header',
                        level=1,
                        start_marker='',
                        end_marker='',
                        content=line.strip()
                    ))
                    i += 2  # Saltar línea de underline
                    continue
                
                # H2 con ---
                elif re.match(r'^-{3,}$', next_line.strip()):
                    patterns.append(MarkdownPattern(
                        type='header',
                        level=2,
                        start_marker='',
                        end_marker='',
                        content=line.strip()
                    ))
                    i += 2  # Saltar línea de underline
                    continue
            
            # Detectar otros patrones línea por línea
            pattern_found = False
            
            for pattern_type, pattern_list in self.patterns.items():
                if pattern_type == 'inline_formatting':
                    continue  # Se procesa después
                    
                for pattern_regex, processor in pattern_list:
                    match = re.match(pattern_regex, line, re.MULTILINE | re.DOTALL)
                    if match:
                        result = processor(match)
                        if result:
                            patterns.append(result)
                            pattern_found = True
                            break
                
                if pattern_found:
                    break
            
            i += 1
        
        return patterns
    
    def _process_header(self, match) -> MarkdownPattern:
        """Procesar header con # sintaxis"""
        markers = match.group(1)
        content = match.group(2)
        return MarkdownPattern(
            type='header',
            level=len(markers),
            start_marker=markers,
            end_marker='',
            content=content
        )
    
    def _process_h1_underline(self, match) -> MarkdownPattern:
        """Procesar H1 con underline ==="""
        content = match.group(1)
        return MarkdownPattern(
            type='header',
            level=1,
            start_marker='',
            end_marker='===',
            content=content
        )
    
    def _process_h2_underline(self, match) -> MarkdownPattern:
        """Procesar H2 con underline ---"""
        content = match.group(1)
        return MarkdownPattern(
            type='header',
            level=2,
            start_marker='',
            end_marker='---',
            content=content
        )
    
    def _process_unordered_list(self, match) -> MarkdownPattern:
        """Procesar lista no ordenada"""
        indent = match.group(1)
        marker = match.group(2)
        content = match.group(3)
        return MarkdownPattern(
            type='list',
            level=len(indent) // 2,  # Nivel basado en indentación
            start_marker=f"{indent}{marker}",
            end_marker='',
            content=content
        )
    
    def _process_ordered_list(self, match) -> MarkdownPattern:
        """Procesar lista ordenada"""
        indent = match.group(1)
        marker = match.group(2)
        content = match.group(3)
        return MarkdownPattern(
            type='ordered_list',
            level=len(indent) // 2,
            start_marker=f"{indent}{marker}",
            end_marker='',
            content=content
        )
    
    def _process_quote(self, match) -> MarkdownPattern:
        """Procesar cita"""
        content = match.group(1)
        return MarkdownPattern(
            type='quote',
            level=1,
            start_marker='>',
            end_marker='',
            content=content
        )
    
    def _process_code_block(self, match) -> MarkdownPattern:
        """Procesar bloque de código"""
        language = match.group(1) or ''
        content = match.group(2)
        return MarkdownPattern(
            type='code_block',
            level=0,
            start_marker=f"```{language}",
            end_marker='```',
            content=content
        )
    
    def _process_bold(self, match) -> MarkdownPattern:
        """Procesar texto en negrita"""
        content = match.group(1)
        return MarkdownPattern(
            type='bold',
            level=0,
            start_marker='**',
            end_marker='**',
            content=content
        )
    
    def _process_italic(self, match) -> MarkdownPattern:
        """Procesar texto en cursiva"""
        content = match.group(1)
        return MarkdownPattern(
            type='italic',
            level=0,
            start_marker='*',
            end_marker='*',
            content=content
        )
    
    def _process_inline_code(self, match) -> MarkdownPattern:
        """Procesar código inline"""
        content = match.group(1)
        return MarkdownPattern(
            type='inline_code',
            level=0,
            start_marker='`',
            end_marker='`',
            content=content
        )
    
    def is_valid_markdown(self, text: str) -> bool:
        """Verificar si el texto contiene markdown válido"""
        patterns = self.detect_markdown_patterns(text)
        return len(patterns) > 0
    
    def extract_main_pattern(self, text: str) -> Optional[MarkdownPattern]:
        """Extraer el patrón principal del texto (el primero/más importante)"""
        patterns = self.detect_markdown_patterns(text)
        
        if not patterns:
            return None
        
        # Prioridad: headers > code_block > quote > list > inline
        priority_order = ['header', 'code_block', 'quote', 'list', 'ordered_list', 'bold', 'italic', 'inline_code']
        
        for priority_type in priority_order:
            for pattern in patterns:
                if pattern.type == priority_type:
                    return pattern
        
        return patterns[0]  # Devolver el primero si no hay prioridades
    
    def smart_update_markdown(self, original_md: str, edited_text: str) -> str:
        """Actualizar markdown preservando formato original o detectando nuevo"""
        
        print(f"🧠 SMART UPDATE:")
        print(f"  Original MD: {repr(original_md)}")
        print(f"  Edited text: {repr(edited_text)}")
        
        # 1. Detectar si el texto editado contiene nuevos patrones MD
        new_pattern = self.extract_main_pattern(edited_text)
        
        if new_pattern:
            print(f"  ✅ Nuevo patrón detectado: {new_pattern.type} - {new_pattern.start_marker}")
            # Hay nuevo markdown, usar tal como está
            result = edited_text
        else:
            # 2. No hay nuevo markdown, preservar formato original
            original_pattern = self.extract_main_pattern(original_md)
            
            if original_pattern:
                print(f"  🔄 Preservando formato original: {original_pattern.type}")
                result = self._preserve_original_format(original_md, original_pattern, edited_text)
            else:
                print(f"  📝 Sin formato, usando texto plano")
                # Ni original ni nuevo tienen formato
                result = edited_text
        
        print(f"  📤 Resultado: {repr(result)}")
        print()
        return result
    
    def _preserve_original_format(self, original_md: str, original_pattern: MarkdownPattern, new_text: str) -> str:
        """Preservar formato original aplicándolo al nuevo texto"""
        
        if original_pattern.type == 'header':
            # Headers: aplicar mismo nivel
            if original_pattern.start_marker:
                return f"{original_pattern.start_marker} {new_text}"
            else:
                # Header con underline
                if original_pattern.end_marker == '===':
                    return f"{new_text}\n{'=' * len(new_text)}"
                elif original_pattern.end_marker == '---':
                    return f"{new_text}\n{'-' * len(new_text)}"
        
        elif original_pattern.type == 'bold':
            return f"**{new_text}**"
        
        elif original_pattern.type == 'italic':
            return f"*{new_text}*"
        
        elif original_pattern.type == 'inline_code':
            return f"`{new_text}`"
        
        elif original_pattern.type == 'quote':
            return f"> {new_text}"
        
        elif original_pattern.type in ['list', 'ordered_list']:
            # Listas: mantener marcador original
            return f"{original_pattern.start_marker} {new_text}"
        
        elif original_pattern.type == 'code_block':
            # Bloques de código: mantener estructura
            lang = original_pattern.start_marker.replace('```', '')
            return f"```{lang}\n{new_text}\n```"
        
        # Si no se puede preservar, devolver texto simple
        return new_text
    
    def analyze_text_changes(self, original_md: str, edited_text: str) -> Dict:
        """Analizar los cambios entre texto original y editado"""
        original_pattern = self.extract_main_pattern(original_md)
        new_pattern = self.extract_main_pattern(edited_text)
        
        analysis = {
            'has_original_format': original_pattern is not None,
            'has_new_format': new_pattern is not None,
            'original_type': original_pattern.type if original_pattern else None,
            'new_type': new_pattern.type if new_pattern else None,
            'format_changed': False,
            'content_changed': False,
            'action': 'preserve'  # 'preserve', 'convert', 'plain'
        }
        
        if original_pattern and new_pattern:
            analysis['format_changed'] = original_pattern.type != new_pattern.type
            analysis['content_changed'] = original_pattern.content != new_pattern.content
            analysis['action'] = 'convert' if analysis['format_changed'] else 'preserve'
        elif new_pattern and not original_pattern:
            analysis['action'] = 'convert'
        elif original_pattern and not new_pattern:
            analysis['action'] = 'preserve'
        else:
            analysis['action'] = 'plain'
        
        return analysis

# Funciones de utilidad para testing
def test_processor():
    """Probar el procesador con varios casos"""
    processor = MarkdownProcessor()
    
    test_cases = [
        ("# Título Original", "Título Modificado"),
        ("## Subtítulo", "## Nuevo Subtítulo"),
        ("**Texto en negrita**", "Texto modificado"),
        ("- Lista item", "Item modificado"),
        ("> Cita importante", "Nueva cita"),
        ("`código inline`", "nuevo código"),
        ("Texto normal", "# Ahora es header"),
        ("# Header", "**Ahora negrita**"),
    ]
    
    print("🧪 PROBANDO PROCESADOR INTELIGENTE:\n")
    
    for i, (original, edited) in enumerate(test_cases, 1):
        print(f"Test {i}:")
        result = processor.smart_update_markdown(original, edited)
        analysis = processor.analyze_text_changes(original, edited)
        print(f"  Análisis: {analysis['action']} ({analysis['original_type']} → {analysis['new_type']})")
        print(f"  {original} + {edited} = {result}")
        print()

if __name__ == "__main__":
    test_processor()