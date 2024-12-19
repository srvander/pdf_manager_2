import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from thumbnail_panel import ThumbnailPanel

class CensorPDF(tk.Frame):
    """Frame para censurar un PDF, permitiendo seleccionar áreas de texto para ocultar."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pdf_document = None
        self.current_page = 0
        self.zoom_levels = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        self.current_zoom_index = 2  # Iniciar en 100%
        self.censure_color = (0, 0, 0)  # Negro por defecto
        self.censure_mode = False
        self.censure_rectangles = []
        self.undo_stack = []
        self.redo_stack = []
        
        self.init_ui()
        
        # Bind de teclas para navegación
        self.master.bind('<Left>', self.prev_page_key)
        self.master.bind('<Right>', self.next_page_key)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario. Despliega menú de acciones, 
        canvas para visualizar y censurar el PDF y barras de desplazamiento."""

        def create_top_frame(self, main_frame):
            """Despliega barra con menú de acciones para censurar y guardar PDF"""

            top_frame = ttk.Frame(main_frame)
            top_frame.pack(fill=tk.X, padx=10, pady=10)
            
            ttk.Button(top_frame, text="Seleccionar PDF", command=self.select_pdf).pack(side=tk.LEFT, padx=5) #(0, 10)
            
            self.prev_btn = ttk.Button(top_frame, text="Anterior", command=self.prev_page, state=tk.DISABLED)
            self.prev_btn.pack(side=tk.LEFT)
            
            self.next_btn = ttk.Button(top_frame, text="Siguiente", command=self.next_page, state=tk.DISABLED)
            self.next_btn.pack(side=tk.LEFT)
            
            ttk.Button(top_frame, text="Zoom -", command=self.zoom_out).pack(side=tk.LEFT, padx=(10, 0))
            
            self.zoom_label = ttk.Label(top_frame, text="100%")
            self.zoom_label.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(top_frame, text="Zoom +", command=self.zoom_in).pack(side=tk.LEFT)
            
            self.censure_btn = ttk.Button(top_frame, text="Activar Censura", command=self.toggle_censure_mode)
            self.censure_btn.pack(side=tk.LEFT, padx=10)
            
            ttk.Button(top_frame, text="Color Censura", command=self.choose_censure_color).pack(side=tk.LEFT)
            
            ttk.Button(top_frame, text="Deshacer", command=self.undo_censure).pack(side=tk.LEFT, padx=(10, 0))
            ttk.Button(top_frame, text="Rehacer", command=self.redo_censure).pack(side=tk.LEFT, padx=(5, 10))
            
            ttk.Button(top_frame, text="Guardar Cambios", command=self.save_changes).pack(side=tk.LEFT)
            
            self.page_label = ttk.Label(top_frame, text="Página: 0 / 0")
            self.page_label.pack(side=tk.RIGHT)
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.create_top_frame()
        self.create_canvas_frame()
        self.create_back_button()
    
    def create_top_frame(self):
        """Despliega barra con menú de acciones para censurar y guardar PDF"""

        top_frame = ttk.Frame()
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(top_frame, text="Seleccionar PDF", command=self.select_pdf).pack(side=tk.LEFT, padx=(0, 10))
        
        self.prev_btn = ttk.Button(top_frame, text="Anterior", command=self.prev_page, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT)
        
        self.next_btn = ttk.Button(top_frame, text="Siguiente", command=self.next_page, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT)
        
        ttk.Button(top_frame, text="Zoom -", command=self.zoom_out).pack(side=tk.LEFT, padx=(10, 0))
        
        self.zoom_label = ttk.Label(top_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(top_frame, text="Zoom +", command=self.zoom_in).pack(side=tk.LEFT)
        
        self.censure_btn = ttk.Button(top_frame, text="Activar Censura", command=self.toggle_censure_mode)
        self.censure_btn.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(top_frame, text="Color Censura", command=self.choose_censure_color).pack(side=tk.LEFT)
        
        ttk.Button(top_frame, text="Deshacer", command=self.undo_censure).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(top_frame, text="Rehacer", command=self.redo_censure).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(top_frame, text="Guardar Cambios", command=self.save_changes).pack(side=tk.LEFT)
        
        self.page_label = ttk.Label(top_frame, text="Página: 0 / 0")
        self.page_label.pack(side=tk.RIGHT)
    
    def create_canvas_frame(self):
        """Despliega canvas para visualizar y censurar el PDF, con barras de desplazamiento."""

        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(fill=tk.X)
        
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        
        self.canvas.bind("<ButtonPress-1>", self.start_rectangle)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.end_rectangle)
    
    def create_back_button(self):
        """Despliega botón para volver al menú principal"""

        ttk.Button(self, text="Volver al Menú Principal", 
                   command=lambda: [self.master.geometry("800x600"), 
                                    self.master.show_frame("MainMenu"),
                                    self.reset_state(),
                                    self.toggle_censure_mode() if self.censure_mode else None,
                                    ]).pack(pady=10)
    
    def on_mousewheel(self, event):
        """Controla el evento de rueda del ratón para hacer scroll en el canvas"""

        if event.num == 5 or event.delta == -120:  # Scroll hacia abajo
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:  # Scroll hacia arriba
            self.canvas.yview_scroll(-1, "units")
    
    def select_pdf(self):
        """Permite seleccionar un archivo PDF para visualizar y censurar"""

        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_document = fitz.open(file_path)
            self.current_page = 0
            self.censure_rectangles.clear()
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.update_page()
            
            self.update_navigation_buttons()
    
    def update_page(self):
        """Actualiza la visualización de la página actual del PDF"""
        
        if self.pdf_document:
            page = self.pdf_document[self.current_page]
            zoom = self.zoom_levels[self.current_zoom_index]
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(img)
            
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(0, 0, pix.width, pix.height))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # Mantener una referencia
            
            self.page_label.config(text=f"Página: {self.current_page + 1} / {len(self.pdf_document)}")
            self.zoom_label.config(text=f"{int(zoom * 100)}%")
            
            self.redraw_censure_rectangles()
    
    def prev_page(self):
        """Muestra la página anterior del PDF, si es que hay una"""

        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()
            self.update_navigation_buttons()
    
    def next_page(self):
        """Muestra la página siguiente del PDF, si es que hay una"""

        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.update_page()
            self.update_navigation_buttons()
    
    def prev_page_key(self, event):
        """vincula la tecla de flecha izquierda para mostrar la página anterior"""

        self.prev_page()
    
    def next_page_key(self, event):
        """vincula la tecla de flecha derecha para mostrar la página siguiente"""

        self.next_page()
    
    def update_navigation_buttons(self):
        """Actualiza el estado de los botones de navegación según la página actual"""

        self.prev_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.pdf_document and self.current_page < len(self.pdf_document) - 1 else tk.DISABLED)
    
    def zoom_in(self):
        """Aumenta el zoom de la página actual, si es posible"""

        if self.current_zoom_index < len(self.zoom_levels) - 1:
            self.current_zoom_index += 1
            self.update_page()
    
    def zoom_out(self):
        """Reduce el zoom de la página actual, si es posible"""

        if self.current_zoom_index > 0:
            self.current_zoom_index -= 1
            self.update_page()
    
    def toggle_censure_mode(self):
        """Activa o desactiva el modo de censura de texto"""

        self.censure_mode = not self.censure_mode
        self.censure_btn.config(text="Desactivar Censura" if self.censure_mode else "Activar Censura")
    
    def choose_censure_color(self):
        """Permite elegir un color para la censura de texto"""
        
        color = colorchooser.askcolor(title="Elegir color de censura")
        if color[1]:
            self.censure_color = tuple(int(x) for x in color[0])
    
    def start_rectangle(self, event):
        """Inicia la selección de un área rectangular para censurar"""

        if self.censure_mode:
            self.start_x = self.canvas.canvasx(event.x)
            self.start_y = self.canvas.canvasy(event.y)
    
    def draw_rectangle(self, event):
        """Dibuja un área rectangular temporal mientras se selecciona"""

        if self.censure_mode:
            cur_x = self.canvas.canvasx(event.x)
            cur_y = self.canvas.canvasy(event.y)
            self.canvas.delete("temp_rectangle")
            self.canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, 
                                         outline="red", tags="temp_rectangle")
    
    def end_rectangle(self, event):
        """Finaliza la selección de un área rectangular para censurar"""

        if self.censure_mode:
            end_x = self.canvas.canvasx(event.x)
            end_y = self.canvas.canvasy(event.y)
            self.canvas.delete("temp_rectangle")
            rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, 
                                                   fill=f"#{self.censure_color[0]:02x}{self.censure_color[1]:02x}{self.censure_color[2]:02x}", 
                                                   outline="")
            zoom = self.zoom_levels[self.current_zoom_index]
            new_rect = {
                "page": self.current_page,
                "rect": fitz.Rect(self.start_x / zoom, self.start_y / zoom, end_x / zoom, end_y / zoom),
                "color": self.censure_color,
                "canvas_id": rect_id
            }
            self.censure_rectangles.append(new_rect)
            self.undo_stack.append(("add", new_rect))
            self.redo_stack.clear()
    
    def redraw_censure_rectangles(self):
        """Redibuja las áreas censuradas en la página actual, para mantenerlas visibles al hacer zoom"""
        
        zoom = self.zoom_levels[self.current_zoom_index]
        for rect in self.censure_rectangles:
            if rect["page"] == self.current_page:
                x0, y0, x1, y1 = rect["rect"]
                rect["canvas_id"] = self.canvas.create_rectangle(
                    x0 * zoom, y0 * zoom, x1 * zoom, y1 * zoom,
                    fill=f"#{rect['color'][0]:02x}{rect['color'][1]:02x}{rect['color'][2]:02x}",
                    outline=""
                )
    
    def undo_censure(self):
        """Deshace la última censura realizada"""

        if self.undo_stack:
            action, rect = self.undo_stack.pop()
            if action == "add":
                self.censure_rectangles.remove(rect)
                self.canvas.delete(rect["canvas_id"])
                #elimina toda la imagen y vuelve a dibujar con todos los rectangulos guardados
                self.canvas.delete("all")
                self.update_page()

            self.redo_stack.append((action, rect))
            
    def redo_censure(self):
        """Rehace la última censura deshecha"""

        if self.redo_stack:
            action, rect = self.redo_stack.pop()
            if action == "add":
                self.censure_rectangles.append(rect)
                self.redraw_censure_rectangles()
            self.undo_stack.append((action, rect))
    
    def save_changes(self):
        """Guarda los cambios realizados en el PDF censurado.
        Crea un nuevo archivo con los cambios y lo guarda en disco."""

        if self.pdf_document:
            for rect in self.censure_rectangles:
                page = self.pdf_document[rect["page"]]
                annot = page.add_redact_annot(rect["rect"])
                page.apply_redactions()
                page.draw_rect(rect["rect"], color=rect["color"], fill=rect["color"])
            
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if save_path:
                try:
                    self.pdf_document.save(save_path)
                    messagebox.showinfo("Guardado", "Los cambios se han guardado correctamente.")
                    self.reset_state()
                    self.master.show_frame("MainMenu")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")
    
    def reset_state(self):
        """Reinicia el estado de la aplicación, eliminando el PDF cargado y las censuras realizadas"""

        self.pdf_document = None
        self.current_page = 0
        self.censure_rectangles.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.canvas.delete("all")
        self.page_label.config(text="Página: 0 / 0")
        self.update_navigation_buttons()

if __name__ == "__main__":
    print('hola, CGR!')
