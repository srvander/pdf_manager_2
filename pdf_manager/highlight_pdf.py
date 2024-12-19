import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, filedialog, colorchooser, messagebox, simpledialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from thumbnail_panel import ThumbnailPanel
from custom_widgets import (CustomButton_A,
                            CustomButton_B,
                            CustomFrame,
                            CustomLabel)
import tempfile
import shutil
import os


class HighlightPDF(CustomFrame):
    """Frame para destacar áreas de un archivo PDF."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pdf_document = None
        self.current_page = 0
        self.highlights = {}
        self.current_color = (1, 1, 0)  # Yellow default in RGB (0-1 scale)
        self.highlighting_enabled = True
        self.undo_stack = []
        self.redo_stack = []
        self.scale_factor = 1.0
        
        self.create_widgets()
        
    def create_widgets(self):
        """Crea los widgets de la interfaz de usuario."""

        main_frame = CustomFrame(self)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Frame superior para botones
        top_frame = CustomFrame(main_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        CustomButton_A(top_frame, text="ABRIR PDF", command=self.load_pdf).pack(side=tk.LEFT, padx=5)
        self.toggle_button = CustomButton_A(top_frame, text="ACTIVAR DESTACADO", command=self.toggle_highlighting)
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        CustomButton_A(top_frame, text="COLOR", command=self.choose_color).pack(side=tk.LEFT, padx=5)
        self.undo_button = CustomButton_B(top_frame, text="DESHACER", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, padx=5)
        self.redo_button = CustomButton_B(top_frame, text="REHACER", command=self.redo)
        self.redo_button.pack(side=tk.LEFT, padx=5)
        CustomButton_A(top_frame, text="GUARDAR", command=self.save_highlights).pack(side=tk.LEFT, padx=5)
        
        # Botón para agregar marcador
        #bookmark_btn = CustomButton_A(top_frame, text="Agregar Marcador", command=self.add_bookmark)
        #bookmark_btn.pack(side=tk.LEFT, padx=5)

        # Frame central para el canvas y las barras de desplazamiento
        self.pdf_frame = CustomFrame(main_frame)
        self.pdf_frame.pack(expand=True, fill=tk.BOTH, pady=1)
        
        self.canvas = ctk.CTkCanvas(self.pdf_frame, bg='white')
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.v_scrollbar = ctk.CTkScrollbar(self.pdf_frame, orientation=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self.h_scrollbar = ctk.CTkScrollbar(self, orientation=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack( fill=tk.X)
        
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Thumbnail panel
        self.thumbnail_panel = ThumbnailPanel(self.pdf_frame, self.go_to_page)
        self.thumbnail_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame inferior para botones de navegación
        bottom_frame = CustomFrame(self)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.prev_button = CustomButton_B(bottom_frame, text="ANTERIOR", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.page_label = CustomLabel(bottom_frame, text="PÁGINA: 0 / 0")
        self.page_label.pack(side=tk.LEFT, padx=5)
        self.next_button = CustomButton_B(bottom_frame, text="SIGUIENTE", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        CustomButton_A(bottom_frame, text="VOLVER AL MENÚ", 
                   command=lambda: [self.master.geometry("800x600"), 
                                    self.restore_values(),                                    
                                    self.master.show_frame("MainMenu")]).pack(pady=10)
        
        # Set initial state to DISABLED
        self.undo_button.configure(state=tk.DISABLED)
        self.redo_button.configure(state=tk.DISABLED)
        self.prev_button.configure(state=tk.DISABLED)
        self.next_button.configure(state=tk.DISABLED)
        
        # teclas de acceso rápido
        self.canvas.bind("<ButtonPress-1>", self.start_highlight)
        self.canvas.bind("<B1-Motion>", self.drag_highlight)
        self.canvas.bind("<ButtonRelease-1>", self.end_highlight)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux
        self.canvas.bind("<Control-MouseWheel>", self.on_control_mousewheel)  # Windows
        self.canvas.bind("<Control-Button-4>", self.on_control_mousewheel)  # Linux
        self.canvas.bind("<Control-Button-5>", self.on_control_mousewheel)  # Linux

#function to restore all values to default:
    def restore_values(self):
        self.pdf_document = None
        self.current_page = 0
        self.highlights = {}
        self.undo_stack = []
        self.redo_stack = []
        self.scale_factor = 1.0
        self.current_color = (1, 1, 0)
        self.highlighting_enabled = True
        self.toggle_button.configure(text="DESACTIVAR DESTACADO")
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
        self.redo_button.configure(state=tk.DISABLED)
        self.undo_button.configure(state=tk.DISABLED)
        self.prev_button.configure(state=tk.DISABLED)
        self.next_button.configure(state=tk.DISABLED)
        self.thumbnail_panel.clean_thumbnails()
        self.page_label.configure(text="PÁGINA: 0 / 0")

    def on_mousewheel(self, event):
        """Función para hacer scroll en el canvas con la rueda del ratón."""
        if self.pdf_document:
            # Linux (event.num) o Windows (event.delta)
            if event.num == 5 or event.delta == -120:
                self.canvas.yview_scroll(1, "units")
            if event.num == 4 or event.delta == 120:
                self.canvas.yview_scroll(-1, "units")
    
    def on_control_mousewheel(self, event):
        """Función para hacer scroll vertical en el canvas con la rueda del ratón."""


        if self.pdf_document:
            # Respond to Linux (event.num) or Windows (event.delta) wheel event
            if event.num == 5 or event.delta == -120:
                self.canvas.xview_scroll(1, "units")
            if event.num == 4 or event.delta == 120:
                self.canvas.xview_scroll(-1, "units")

    def load_pdf(self):
        """Función que abre un cuadro de diálogo para seleccionar y cargar un PDF"""

        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_document = fitz.open(file_path)
            self.current_page = 0
            self.highlights = {}
            self.undo_stack = []
            self.redo_stack = []
            self.thumbnail_panel.load_thumbnails(self.pdf_document)
            self.display_page()
            # Enable buttons
            self.undo_button.configure(state="normal")
            self.redo_button.configure(state="normal")
            self.prev_button.configure(state="normal")
            self.next_button.configure(state="normal")
    
    def display_page(self):
        """Función que muestra la página actual del PDF en el canvas"""

        if self.pdf_document:
            page = self.pdf_document[self.current_page]
            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.tk_image = ImageTk.PhotoImage(image=img)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))
            
            self.page_label.configure(text=f"Página: {self.current_page + 1} / {len(self.pdf_document)}")
            
            self.scale_factor = 1  # porque se usa fitz.Matrix(1, 1)
            
            # Redibujar destacado
            self.redraw_highlights()
            self.thumbnail_panel.update_selection(self.current_page)
    
    def start_highlight(self, event):
        """Función que inicia el destacado de un área en el PDF"""

        if self.highlighting_enabled:
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
    
    def drag_highlight(self, event):
        """Función que permite arrastrar el área de destacado en el PDF"""

        if self.highlighting_enabled:
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            
            self.canvas.delete("temp_highlight")
            self.canvas.create_rectangle(
                self.start_x, self.start_y, cur_x, cur_y,
                outline=self.rgb_to_hex(self.current_color), 
                fill=self.rgb_to_hex(self.current_color), 
                stipple="gray12",
                tags="temp_highlight"
            )
    
    def end_highlight(self, event):
        """Función que finaliza el destacado de un área en el PDF"""
        if self.highlighting_enabled:
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            
            self.canvas.delete("temp_highlight")
            
            x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
            x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)
            
            if x2 - x1 > 5 and y2 - y1 > 5:  # Minimum size to create highlight
                # Convert canvas coordinates to PDF coordinates
                pdf_x1, pdf_y1 = x1 / self.scale_factor, y1 / self.scale_factor
                pdf_x2, pdf_y2 = x2 / self.scale_factor, y2 / self.scale_factor
                
                highlight = {
                    'x1': pdf_x1, 'y1': pdf_y1, 'x2': pdf_x2, 'y2': pdf_y2, 
                    'color': self.current_color
                }
                self.add_highlight(highlight)
    
    def add_highlight(self, highlight):
        """Función que añade un área destacada al diccionario de highlights"""

        if self.current_page not in self.highlights:
            self.highlights[self.current_page] = []
        
        self.highlights[self.current_page].append(highlight)
        self.undo_stack.append(('add', self.current_page, highlight))
        self.redo_stack.clear()
        self.redraw_highlights()
    
    def remove_highlight(self, page, highlight):
        """Función que elimina un área destacada del diccionario de highlights"""

        if page in self.highlights:
            self.highlights[page].remove(highlight)
            if not self.highlights[page]:
                del self.highlights[page]
        self.redraw_highlights()
    
    def redraw_highlights(self):
        """Función que redibuja todas las áreas destacadas en la página actual"""
        self.canvas.delete("highlight")
        if self.current_page in self.highlights:
            for highlight in self.highlights[self.current_page]:
                self.draw_highlight(highlight)
    
    def draw_highlight(self, highlight):
        """Función que dibuja un área destacada en el canvas"""

        x1 = highlight['x1'] * self.scale_factor
        y1 = highlight['y1'] * self.scale_factor
        x2 = highlight['x2'] * self.scale_factor
        y2 = highlight['y2'] * self.scale_factor
        
        color = self.rgb_to_hex(highlight['color'])
        
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color, fill=color, stipple="gray12", tags="highlight"
        )
    
    def choose_color(self):
        """Función que abre un cuadro de diálogo para seleccionar un color"""

        color = colorchooser.askcolor(color=self.rgb_to_hex(self.current_color))
        if color[0]:  # color[0] es una tupla RGB, color[1] es string hexadecimal
            self.current_color = tuple(c/255 for c in color[0])  # Convierte a escala 0-1
    
    def save_highlights(self):
        """Función que guarda los cambios realizados en el PDF"""

        if not self.pdf_document:
            messagebox.showerror("Error", "No se cargó PDF")
            return
        
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_path:
            for page_num in range(len(self.pdf_document)):
                page = self.pdf_document[page_num]
                if page_num in self.highlights:
                    for highlight in self.highlights[page_num]:
                        rect = fitz.Rect(highlight['x1'], highlight['y1'], highlight['x2'], highlight['y2'])
                        annot = page.add_rect_annot(rect)
                        rgb_color = highlight['color']  # Ya está en rango 0-1
                        annot.set_colors(stroke=rgb_color, fill=rgb_color)
                        annot.set_opacity(0.3)  # Ajusta opacidad, de ser necesario
                        annot.update()
            
            self.pdf_document.save(output_path)
            messagebox.showinfo("Éxito!", f"PDF destacado guardado en {output_path}")
            self.restore_values()
            self.master.geometry("800x600")
            self.master.show_frame("MainMenu")
     
    def choose_color(self):
        """Función que abre un cuadro de diálogo para seleccionar un color"""

        color = colorchooser.askcolor(color=self.rgb_to_hex(self.current_color))
        if color[0]:  # color[0] es tupola RGB, color[1] es string hexadecimal
            self.current_color = tuple(c/255 for c in color[0])  # convierte a escala 0-1

    
    def rgb_to_hex(self, rgb):
        """Función que convierte una tupla RGB en un string hexadecimal"""
        
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
    
    def restore_scrollbars(self):
        """Función que restaura las barras de desplazamiento a su posición inicial"""
        self.canvas.yview_moveto(0)
        self.canvas.xview_moveto(0)
    
    def prev_page(self):
        """Función que muestra la página anterior del PDF, si es que hay una"""

        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.restore_scrollbars()
            self.display_page()
    
    def next_page(self):
        """Función que muestra la página siguiente del PDF, si es que hay una"""

        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.restore_scrollbars()
            self.display_page()
    
    def toggle_highlighting(self):
        """Función que activa o desactiva el destacado de áreas en el PDF"""

        self.highlighting_enabled = not self.highlighting_enabled
        self.toggle_button.configure(text="ACTIVAR DESTACADO" if not self.highlighting_enabled else "DESACTIVAR DESTACADO")
    
    def undo(self):
        """Función que deshace la última acción de destacado"""

        if self.undo_stack:
            action, page, highlight = self.undo_stack.pop()
            if action == 'add':
                self.remove_highlight(page, highlight)
                self.redo_stack.append(('add', page, highlight))
            elif action == 'remove':
                self.add_highlight(highlight)
                self.redo_stack.append(('remove', page, highlight))
    
    def redo(self):
        """Función que rehace la última acción de destacado"""

        if self.redo_stack:
            action, page, highlight = self.redo_stack.pop()
            if action == 'add':
                self.add_highlight(highlight)
            elif action == 'remove':
                self.remove_highlight(page, highlight)

    def go_to_page(self, page_num):
        """Función que navega a una página específica del PDF"""
        if self.pdf_document and 0 <= page_num < len(self.pdf_document):
            self.current_page = page_num
            self.display_page()
            self.thumbnail_panel.update_selection(page_num)

    def add_bookmark(self):
        """Agrega un marcador en la página actual del PDF."""
        if self.pdf_document:
            title = simpledialog.askstring("Agregar Marcador", "Ingrese el título del marcador:")
            if title:
                self.pdf_document.set_toc(self.pdf_document.get_toc() + [[1, title, self.current_page + 1]])

                # Crear una carpeta temporal
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = os.path.join(temp_dir, "temp.pdf")
                    self.pdf_document.save(temp_path)  # Guardar en la carpeta temporal

                    original_path = self.pdf_document.name
                    self.pdf_document.close()

                    # Eliminar el archivo original
                    os.remove(original_path)

                    # Mover el archivo temporal a la ubicación original
                    shutil.move(temp_path, original_path)

                tk.messagebox.showinfo("Marcador Agregado", f"Marcador '{title}' agregado en la página {self.current_page + 1}")

if __name__ == "__main__":
    print('hola tarolas')
