#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Window utilities - Redimensionado automático de ventanas
"""

import tkinter as tk
from tkinter import ttk

class AutoResizeWindow:
    """Mixin class para agregar redimensionado automático a cualquier ventana"""
    
    def __init__(self, window, padding=20, min_padding=10):
        self.window = window
        self.padding = padding
        self.min_padding = min_padding
        self.auto_resize_enabled = True
        self.last_size = (0, 0)
        
        # Configurar ventana como redimensionable
        self.window.resizable(True, True)
        
        # Programar check inicial
        self.window.after(100, self.auto_resize)
        
        # Bind a eventos que pueden cambiar el tamaño
        self.window.bind('<Map>', lambda e: self.schedule_resize())
        self.window.bind('<Configure>', lambda e: self.on_configure(e))
    
    def schedule_resize(self, delay=50):
        """Programar redimensionado con delay para evitar spam"""
        if hasattr(self, '_resize_job'):
            self.window.after_cancel(self._resize_job)
        self._resize_job = self.window.after(delay, self.auto_resize)
    
    def on_configure(self, event):
        """Manejar eventos de configuración"""
        # Solo procesar eventos de la ventana principal, no de widgets hijos
        if event.widget == self.window:
            # Si el usuario redimensionó manualmente, actualizar mínimos
            if self.auto_resize_enabled:
                self.window.after(100, self.update_minimum_size)
    
    def auto_resize(self):
        """Redimensionar ventana automáticamente al contenido"""
        if not self.auto_resize_enabled:
            return
        
        try:
            # Forzar actualización de layout
            self.window.update_idletasks()
            
            # Obtener tamaño requerido por los widgets
            req_width = self.window.winfo_reqwidth()
            req_height = self.window.winfo_reqheight()
            
            # Agregar padding
            final_width = req_width + self.padding
            final_height = req_height + self.padding
            
            # Obtener tamaño actual
            current_width = self.window.winfo_width()
            current_height = self.window.winfo_height()
            
            # Solo redimensionar si hay un cambio significativo
            if (abs(current_width - final_width) > 10 or 
                abs(current_height - final_height) > 10):
                
                # Mantener la ventana centrada si es nueva
                if current_width <= 1 or current_height <= 1:
                    self.center_window(final_width, final_height)
                else:
                    # Solo cambiar tamaño, mantener posición
                    x = self.window.winfo_x()
                    y = self.window.winfo_y()
                    self.window.geometry(f"{final_width}x{final_height}+{x}+{y}")
            
            # Actualizar tamaño mínimo
            self.update_minimum_size()
            
            self.last_size = (final_width, final_height)
            
        except tk.TclError:
            # La ventana puede haber sido destruida
            pass
    
    def update_minimum_size(self):
        """Actualizar el tamaño mínimo de la ventana"""
        try:
            self.window.update_idletasks()
            
            # Calcular tamaño mínimo basado en contenido
            min_width = self.window.winfo_reqwidth() + self.min_padding
            min_height = self.window.winfo_reqheight() + self.min_padding
            
            # Establecer tamaño mínimo
            self.window.minsize(min_width, min_height)
            
        except tk.TclError:
            pass
    
    def center_window(self, width=None, height=None):
        """Centrar ventana en pantalla"""
        try:
            if width is None or height is None:
                self.window.update_idletasks()
                width = self.window.winfo_reqwidth() + self.padding
                height = self.window.winfo_reqheight() + self.padding
            
            # Obtener dimensiones de pantalla
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            
            # Calcular posición centrada
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            
            # Asegurar que la ventana no salga de la pantalla
            x = max(0, min(x, screen_width - width))
            y = max(0, min(y, screen_height - height))
            
            self.window.geometry(f"{width}x{height}+{x}+{y}")
            
        except tk.TclError:
            pass
    
    def disable_auto_resize(self):
        """Deshabilitar redimensionado automático"""
        self.auto_resize_enabled = False
    
    def enable_auto_resize(self):
        """Habilitar redimensionado automático"""
        self.auto_resize_enabled = True
        self.schedule_resize()
    
    def force_resize(self):
        """Forzar redimensionado inmediato"""
        self.auto_resize()

# Funciones de conveniencia
def make_auto_resizable(window, padding=20, min_padding=10):
    """Hacer que una ventana sea auto-redimensionable"""
    return AutoResizeWindow(window, padding, min_padding)

def setup_responsive_grid(widget, rows=None, cols=None):
    """Configurar grid responsive para un widget"""
    if rows is None:
        # Auto-detectar número de filas
        slaves = widget.grid_slaves()
        if slaves:
            rows = max(slave.grid_info()['row'] for slave in slaves) + 1
        else:
            rows = 1
    
    if cols is None:
        # Auto-detectar número de columnas
        slaves = widget.grid_slaves()
        if slaves:
            cols = max(slave.grid_info()['column'] for slave in slaves) + 1
        else:
            cols = 1
    
    # Configurar weights para que se expandan
    for i in range(rows):
        widget.rowconfigure(i, weight=1)
    for i in range(cols):
        widget.columnconfigure(i, weight=1)

def center_window_on_parent(child, parent):
    """Centrar ventana hija sobre ventana padre"""
    try:
        child.update_idletasks()
        parent.update_idletasks()
        
        # Obtener dimensiones
        child_width = child.winfo_reqwidth()
        child_height = child.winfo_reqheight()
        
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Calcular posición centrada sobre el padre
        x = parent_x + (parent_width // 2) - (child_width // 2)
        y = parent_y + (parent_height // 2) - (child_height // 2)
        
        # Asegurar que esté en pantalla
        screen_width = child.winfo_screenwidth()
        screen_height = child.winfo_screenheight()
        
        x = max(0, min(x, screen_width - child_width))
        y = max(0, min(y, screen_height - child_height))
        
        child.geometry(f"{child_width}x{child_height}+{x}+{y}")
        
    except tk.TclError:
        pass

# Decorador para clases de ventana
def auto_resizable(padding=20, min_padding=10):
    """Decorador para hacer una clase de ventana auto-redimensionable"""
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, window, *args, **kwargs):
            # Llamar al __init__ original
            original_init(self, window, *args, **kwargs)
            
            # Agregar funcionalidad de auto-resize
            self._auto_resizer = AutoResizeWindow(window, padding, min_padding)
            
            # Agregar métodos de conveniencia
            self.auto_resize = self._auto_resizer.auto_resize
            self.center_window = self._auto_resizer.center_window
            self.disable_auto_resize = self._auto_resizer.disable_auto_resize
            self.enable_auto_resize = self._auto_resizer.enable_auto_resize
        
        cls.__init__ = new_init
        return cls
    
    return decorator

# Función para wizard/dialogs
def setup_wizard_window(window, min_width=400, min_height=300):
    """Configurar ventana para wizard con auto-resize"""
    # Hacer auto-redimensionable
    auto_resizer = make_auto_resizable(window, padding=30, min_padding=20)
    
    # Establecer tamaño mínimo absoluto
    window.minsize(min_width, min_height)
    
    # Configurar grid principal
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)
    
    return auto_resizer

# Para testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Auto Resize")
    
    # Hacer la ventana auto-redimensionable
    auto_resizer = make_auto_resizable(root)
    
    frame = ttk.Frame(root, padding="20")
    frame.grid(row=0, column=0, sticky="nsew")
    
    ttk.Label(frame, text="Esta ventana se redimensiona automáticamente").grid(row=0, column=0, pady=10)
    
    def add_button():
        btn = ttk.Button(frame, text=f"Botón {len(frame.winfo_children())}")
        btn.grid(row=len(frame.winfo_children()), column=0, pady=5)
        auto_resizer.schedule_resize()
    
    ttk.Button(frame, text="Agregar botón", command=add_button).grid(row=1, column=0, pady=10)
    
    setup_responsive_grid(root)
    
    root.mainloop()