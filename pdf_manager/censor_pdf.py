import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import fitz
from PIL import Image, ImageTk
from thumbnail_panel import ThumbnailPanel
from custom_widgets import CustomButton_A, CustomButton_B, CustomFrame, CustomLabel

class CensorPDF(CustomFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pdf_document = None
        self.current_page = 0
        self.zoom_levels = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        self.current_zoom_index = 2
        self.censure_color = (0, 0, 0)
        self.censure_mode = False
        self.censure_rectangles = []
        self.undo_stack = []
        self.redo_stack = []
        
        self.init_ui()
        
    def init_ui(self):
        main_frame = CustomFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Compact top controls
        top_frame = CustomFrame(main_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Group 1: File and Navigation
        nav_group = CustomFrame(top_frame)
        nav_group.pack(side=tk.LEFT, padx=2)
        
        CustomButton_A(nav_group, text="ABRIR PDF", 
                  command=self.select_pdf).pack(side=tk.LEFT, padx=1)
        
        # Group 2: Zoom controls
        zoom_group = CustomFrame(top_frame)
        zoom_group.pack(side=tk.LEFT, padx=5)
        
        self.zoom_out_button = CustomButton_B(zoom_group, text="- ZOOM", 
                  command=self.zoom_out, state=tk.DISABLED)
        self.zoom_out_button.pack(side=tk.LEFT, padx=1)
        
        self.zoom_label = CustomLabel(zoom_group, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        self.zoom_in_button = CustomButton_B(zoom_group, text="+ ZOOM", 
                  command=self.zoom_in, state=tk.DISABLED)
        self.zoom_in_button.pack(side=tk.LEFT, padx=1)
        
        # Group 3: Censure controls
        censure_group = CustomFrame(top_frame)
        censure_group.pack(side=tk.LEFT, padx=5)
        
        self.censure_btn = CustomButton_A(censure_group, text="ACTIVAR CENSURA", 
                                   command=self.toggle_censure_mode)
        self.censure_btn.pack(side=tk.LEFT, padx=1)
        
        CustomButton_A(censure_group, text="COLOR", 
                  command=self.choose_censure_color).pack(side=tk.LEFT, padx=1)
        
        # Group 4: Edit controls
        edit_group = CustomFrame(top_frame)
        edit_group.pack(side=tk.LEFT, padx=5)
        
        self.undo_button = CustomButton_B(edit_group, text="DESHACER", 
                  command=self.undo_censure, state=tk.DISABLED)
        self.undo_button.pack(side=tk.LEFT, padx=1)
        
        self.redo_button = CustomButton_B(edit_group, text="REHACER", 
                  command=self.redo_censure, state=tk.DISABLED)
        self.redo_button.pack(side=tk.LEFT, padx=1)
        
        CustomButton_A(edit_group, text="GUARDAR", 
                  command=self.save_changes).pack(side=tk.LEFT, padx=5)

        # Content area
        content_frame = CustomFrame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=1)

        # Canvas para mostrar la página del PDF
        self.canvas = ctk.CTkCanvas(content_frame, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Barras de desplazamiento
        self.v_scrollbar = ctk.CTkScrollbar(content_frame, orientation=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.h_scrollbar = ctk.CTkScrollbar(self, orientation=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(fill=tk.X)
        
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        # Configurar el scroll con la rueda del ratón
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        
        # Thumbnail panel
        self.thumbnail_panel = ThumbnailPanel(content_frame, self.go_to_page)
        self.thumbnail_panel.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom frame for navigation buttons and page label
        bottom_frame = CustomFrame(self)
        bottom_frame.pack(fill=tk.X, padx=5, pady=2)

        # Left frame for navigation buttons and page label
        nav_frame = CustomFrame(bottom_frame)
        nav_frame.grid(row=0, column=0, padx=5, pady=2, sticky="nswe")

        self.prev_btn = CustomButton_B(nav_frame, text="ANTERIOR", 
                    command=self.prev_page, state=tk.DISABLED)
        self.prev_btn.grid(row=0, column=0, padx=1)
        
        self.page_label = CustomLabel(nav_frame, text="0 / 0")
        self.page_label.grid(row=0, column=1, padx=3)
        
        self.next_btn = CustomButton_B(nav_frame, text="SIGUIENTE", 
                    command=self.next_page, state=tk.DISABLED)
        self.next_btn.grid(row=0, column=2, padx=1)

        
        CustomButton_A(bottom_frame, text="VOLVER AL MENÚ", 
              command=lambda: [
              # Clean main frame and thumbnail
              self.reset_state(),
              self.page_label.configure(text="PÁGINA: 0 / 0"),
              self.canvas.delete("all"),
              self.thumbnail_panel.clean_thumbnails(),
              self.canvas.configure(scrollregion=(0, 0, 0, 0)),
              self.undo_button.configure(state=tk.DISABLED),
              self.redo_button.configure(state=tk.DISABLED),
              self.zoom_out_button.configure(state=tk.DISABLED),
              self.zoom_in_button.configure(state=tk.DISABLED),
              self.prev_btn.configure(state=tk.DISABLED),
              self.next_btn.configure(state=tk.DISABLED),
              self.master.show_frame("MainMenu")]).grid(row=0, column=1, sticky="w")
        
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_columnconfigure(2, weight=1)

        

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.start_rectangle)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.end_rectangle)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)

        # Bind de teclas para navegación
        self.master.bind('<Left>', self.prev_page_key)
        self.master.bind('<Right>', self.next_page_key)

    def go_to_page(self, page_num):
        if self.pdf_document and 0 <= page_num < len(self.pdf_document):
            self.current_page = page_num
            self.update_page()
            self.thumbnail_panel.update_selection(page_num)

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

            self.thumbnail_panel.load_thumbnails(self.pdf_document)

            self.update_page()
            self.update_navigation_buttons()
            
            # Enable Zoom buttons
            self.zoom_out_button.configure(state=tk.NORMAL)
            self.zoom_in_button.configure(state=tk.NORMAL)
            
            # Enable Undo and Redo buttons when a file is selected
            self.undo_button.configure(state=tk.NORMAL)
            self.redo_button.configure(state=tk.NORMAL)

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
            self.canvas.configure(scrollregion=(0, 0, pix.width, pix.height))
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # Mantener una referencia

            self.page_label.configure(text=f"Página: {self.current_page + 1} / {len(self.pdf_document)}")
            self.zoom_label.configure(text=f"{int(zoom * 100)}%")

            self.redraw_censure_rectangles()
            self.thumbnail_panel.update_selection(self.current_page)

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
        self.thumbnail_panel.clear_selection()
        self.prev_page()

    def next_page_key(self, event):
        """vincula la tecla de flecha derecha para mostrar la página siguiente"""
        self.thumbnail_panel.clear_selection()
        self.next_page()

    def update_navigation_buttons(self):
        """Actualiza el estado de los botones de navegación según la página actual"""

        self.prev_btn.configure(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_btn.configure(state=tk.NORMAL if self.pdf_document and self.current_page < len(self.pdf_document) - 1 else tk.DISABLED)

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
        self.censure_btn.configure(text="Desactivar Censura" if self.censure_mode else "Activar Censura")

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
            
            # Enable undo_button since there is at least one action
            #self.undo_button.configure(state=tk.NORMAL)
            # Disable redo_button because redo stack is cleared
           # self.redo_button.configure(state=tk.DISABLED)

    def redraw_censure_rectangles(self):
        """Redibuja las áreas censuradas en la página actual, para mantenerlas visibles al hacer zoom"""

        zoom = self.zoom_levels[self.current_zoom_index]
        for rect in self.censure_rectangles:
            if (rect["page"] == self.current_page):
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
            
            # Mantener el botón de Deshacer habilitado
            # if not self.undo_stack:
            #     self.undo_button.configure(state=tk.DISABLED)

    def redo_censure(self):
        """Rehace la última censura deshecha"""

        if self.redo_stack:
            action, rect = self.redo_stack.pop()
            if action == "add":
                self.censure_rectangles.append(rect)
                self.redraw_censure_rectangles()
            self.undo_stack.append((action, rect))
            
            # Mantener el botón de Rehacer habilitado

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
        self.page_label.configure(text="PÁGINA: 0 / 0")
        self.thumbnail_panel.clean_thumbnails()
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
        self.update_navigation_buttons()
        
        # Disable Undo and Redo buttons after reset
        self.undo_button.configure(state=tk.DISABLED)
        self.redo_button.configure(state=tk.DISABLED)

if __name__ == "__main__":
    print('hola tarolas')