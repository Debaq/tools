# markdown_document.py - Sistema de gestión de elementos markdown

import re
import copy
from typing import List, Tuple, Optional

class MarkdownElement:
    """Elemento individual de markdown con su código original"""
    
    def __init__(self, markdown_code: str = ""):
        self.markdown_code = markdown_code  # Solo el código MD original
        self.comments = []  # Lista de comentarios
    
    def get_clean_markdown(self) -> str:
        """Obtener markdown sin comentarios para renderizado"""
        clean = re.sub(r'<!-- COMMENT:.*? -->', '', self.markdown_code)
        return clean.strip()
    
    def add_comment(self, comment: str):
        """Agregar comentario al elemento"""
        self.comments.append(comment)
        self.markdown_code += f" <!-- COMMENT:{comment} -->"
    
    def get_comments(self) -> List[str]:
        """Extraer todos los comentarios del elemento"""
        comments = re.findall(r'<!-- COMMENT:(.*?) -->', self.markdown_code)
        self.comments = comments
        return comments
    
    def update_content(self, new_markdown: str):
        """Actualizar contenido preservando comentarios"""
        # Extraer comentarios actuales
        current_comments = self.get_comments()
        
        # Actualizar código
        self.markdown_code = new_markdown
        
        # Restaurar comentarios
        for comment in current_comments:
            self.markdown_code += f" <!-- COMMENT:{comment} -->"
    
    def is_empty(self) -> bool:
        """Verificar si el elemento está vacío"""
        return not self.get_clean_markdown()
    
    def copy(self):
        """Crear copia del elemento"""
        new_element = MarkdownElement(self.markdown_code)
        new_element.comments = self.comments.copy()
        return new_element
    
    def __repr__(self):
        return f"MarkdownElement('{self.markdown_code[:50]}...')"

class MarkdownDocument:
    """Gestor del documento markdown con historial de cambios"""
    
    def __init__(self):
        self.elements: List[MarkdownElement] = []
        self.history: List[List[MarkdownElement]] = []  # Stack para undo
        self.redo_stack: List[List[MarkdownElement]] = []  # Stack para redo
        self.max_history = 50  # Límite de historial
    
    def save_state(self):
        """Guardar estado actual en el historial"""
        # Crear copia profunda de todos los elementos
        current_state = [element.copy() for element in self.elements]
        self.history.append(current_state)
        
        # Limpiar redo stack cuando se hace una nueva acción
        self.redo_stack.clear()
        
        # Limitar tamaño del historial
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def undo(self) -> bool:
        """Deshacer último cambio"""
        if len(self.history) > 1:  # Mantener al menos un estado
            # Guardar estado actual en redo stack
            current_state = [element.copy() for element in self.elements]
            self.redo_stack.append(current_state)
            
            # Restaurar estado anterior
            self.history.pop()  # Remover estado actual
            previous_state = self.history[-1]  # Obtener estado anterior
            self.elements = [element.copy() for element in previous_state]
            
            return True
        return False
    
    def redo(self) -> bool:
        """Rehacer último cambio deshecho"""
        if self.redo_stack:
            # Guardar estado actual en history
            current_state = [element.copy() for element in self.elements]
            self.history.append(current_state)
            
            # Restaurar estado desde redo stack
            next_state = self.redo_stack.pop()
            self.elements = [element.copy() for element in next_state]
            
            return True
        return False
    
    def load_from_markdown(self, content: str):
        """Cargar documento desde contenido markdown"""
        self.elements.clear()
        self.history.clear()
        self.redo_stack.clear()
        
        # Dividir contenido en elementos lógicos
        # Estrategia: cada bloque separado por líneas vacías es un elemento
        blocks = self._split_into_blocks(content)
        
        for block in blocks:
            if block.strip():  # Solo agregar bloques con contenido
                self.elements.append(MarkdownElement(block.strip()))
            else:
                # Mantener espacios como elementos vacíos para estructura
                self.elements.append(MarkdownElement(""))
        
        # Guardar estado inicial
        self.save_state()
    
    def _split_into_blocks(self, content: str) -> List[str]:
        """Dividir contenido en bloques lógicos sin crear elementos vacíos"""
        lines = content.split('\n')
        blocks = []
        current_block = []
        
        in_code_block = False
        
        for line in lines:
            # Detectar bloques de código
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                current_block.append(line)
                continue
            
            # Si estamos en bloque de código, agregar línea sin procesar
            if in_code_block:
                current_block.append(line)
                continue
            
            # Línea vacía fuera de bloque de código
            if not line.strip():
                if current_block:
                    # Finalizar bloque actual
                    blocks.append('\n'.join(current_block))
                    current_block = []
                # NO crear elemento vacío, solo usar como separador
            else:
                current_block.append(line)
        
        # Agregar último bloque si existe
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def get_element_count(self) -> int:
        """Obtener número de elementos"""
        return len(self.elements)
    
    def get_element(self, index: int) -> Optional[MarkdownElement]:
        """Obtener elemento por índice"""
        if 0 <= index < len(self.elements):
            return self.elements[index]
        return None
    
    def update_element(self, index: int, new_markdown: str):
        """Actualizar elemento específico"""
        if 0 <= index < len(self.elements):
            self.save_state()  # Guardar antes de cambiar
            self.elements[index].update_content(new_markdown)
    
    def insert_element(self, index: int, markdown_code: str = ""):
        """Insertar nuevo elemento en posición específica"""
        self.save_state()
        new_element = MarkdownElement(markdown_code)
        self.elements.insert(index, new_element)
    
    def delete_element(self, index: int):
        """Eliminar elemento"""
        if 0 <= index < len(self.elements) and len(self.elements) > 1:
            self.save_state()
            self.elements.pop(index)
    
    def split_element(self, index: int, split_position: int = -1):
        """Dividir elemento en la posición especificada"""
        if 0 <= index < len(self.elements):
            element = self.elements[index]
            content = element.get_clean_markdown()
            
            if split_position < 0 or split_position >= len(content):
                # División al final: crear elemento vacío después
                self.insert_element(index + 1, "")
            else:
                # División en posición específica
                first_part = content[:split_position].strip()
                second_part = content[split_position:].strip()
                
                self.save_state()
                self.elements[index].update_content(first_part)
                self.insert_element(index + 1, second_part)
    
    def merge_elements(self, index1: int, index2: int):
        """Fusionar dos elementos consecutivos"""
        if (0 <= index1 < len(self.elements) and 
            0 <= index2 < len(self.elements) and 
            abs(index1 - index2) == 1):
            
            self.save_state()
            
            # Obtener contenido de ambos elementos
            content1 = self.elements[min(index1, index2)].get_clean_markdown()
            content2 = self.elements[max(index1, index2)].get_clean_markdown()
            
            # Fusionar contenido
            merged_content = f"{content1}\n{content2}".strip()
            
            # Actualizar primer elemento y eliminar segundo
            self.elements[min(index1, index2)].update_content(merged_content)
            self.elements.pop(max(index1, index2))
    
    def add_comment_to_element(self, index: int, comment: str):
        """Agregar comentario a elemento específico"""
        if 0 <= index < len(self.elements):
            self.save_state()
            self.elements[index].add_comment(comment)
    
    def get_full_markdown(self) -> str:
        """Obtener contenido markdown completo del documento"""
        result = []
        
        for element in self.elements:
            if element.is_empty():
                result.append("")  # Línea vacía solo si el usuario la creó
            else:
                result.append(element.markdown_code)
        
        # Usar doble salto de línea para separar elementos (estándar markdown)
        return '\n\n'.join(result)
    
    def get_elements_for_rendering(self) -> List[str]:
        """Obtener lista de markdown limpio para renderizado"""
        return [element.get_clean_markdown() for element in self.elements]
    
    def get_stats(self) -> dict:
        """Obtener estadísticas del documento"""
        total_elements = len(self.elements)
        non_empty_elements = len([e for e in self.elements if not e.is_empty()])
        total_comments = sum(len(e.get_comments()) for e in self.elements)
        
        return {
            "total_elements": total_elements,
            "content_elements": non_empty_elements,
            "empty_elements": total_elements - non_empty_elements,
            "total_comments": total_comments,
            "history_size": len(self.history),
            "can_undo": len(self.history) > 1,
            "can_redo": len(self.redo_stack) > 0
        }
    
    def debug_print(self):
        """Imprimir estado actual para debug"""
        print("📄 ESTADO DEL DOCUMENTO:")
        print(f"   Elementos: {len(self.elements)}")
        print(f"   Historial: {len(self.history)} estados")
        print(f"   Redo: {len(self.redo_stack)} estados")
        
        for i, element in enumerate(self.elements):
            content_preview = element.markdown_code[:30].replace('\n', '\\n')
            comments_count = len(element.get_comments())
            print(f"   [{i}]: {content_preview}... (comentarios: {comments_count})")
        print()

# Ejemplo de uso
if __name__ == "__main__":
    # Crear documento
    doc = MarkdownDocument()
    
    # Cargar contenido de prueba
    test_content = """# Título Principal

## Subtítulo

Este es un párrafo con **negrita** y *cursiva*.

### Lista

- Elemento 1
- Elemento 2

```python
def ejemplo():
    print("Código")
```

> Cita importante"""
    
    doc.load_from_markdown(test_content)
    doc.debug_print()
    
    # Probar operaciones
    print("🔧 PROBANDO OPERACIONES:")
    
    # Actualizar elemento
    doc.update_element(0, "# Título Modificado")
    print("Después de actualizar elemento 0:")
    doc.debug_print()
    
    # Agregar comentario
    doc.add_comment_to_element(0, "Comentario de prueba")
    print("Después de agregar comentario:")
    doc.debug_print()
    
    # Deshacer
    doc.undo()
    print("Después de deshacer:")
    doc.debug_print()
    
    # Rehacer
    doc.redo()
    print("Después de rehacer:")
    doc.debug_print()
    
    print("📊 ESTADÍSTICAS:")
    stats = doc.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")