"""
Sistema de tooltips mejorado que evita que se queden pegados
"""

import tkinter as tk

class ToolTip:
    """
    Tooltip mejorado que se comporta correctamente
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)  # Cerrar en click
        self.widget.bind("<FocusOut>", self.on_leave)     # Cerrar al perder foco

    def on_enter(self, event=None):
        """Mostrar tooltip al entrar"""
        if self.tooltip_window:
            return

        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Configurar tooltip
        self.tooltip_window.configure(bg='lightyellow')

        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background='lightyellow',
            foreground='black',
            relief='solid',
            borderwidth=1,
            wraplength=300,
            justify='left',
            font=('Arial', 9)
        )
        label.pack()

        # Auto-cerrar después de 5 segundos para evitar que se quede pegado
        self.widget.after(5000, self.force_close)

    def on_leave(self, event=None):
        """Ocultar tooltip al salir"""
        self.close_tooltip()

    def force_close(self):
        """Forzar cierre del tooltip"""
        self.close_tooltip()

    def close_tooltip(self):
        """Cerrar tooltip si existe"""
        if self.tooltip_window:
            try:
                self.tooltip_window.destroy()
            except:
                pass
            finally:
                self.tooltip_window = None

def add_tooltip(widget, text):
    """
    Función helper para agregar tooltip a un widget
    """
    return ToolTip(widget, text)
