import customtkinter as ctk  # Replace tkinter and ttk imports
import tkinter as tk
from tkinter import filedialog, simpledialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from thumbnail_panel import ThumbnailPanel
from custom_widgets import CustomButton_A, CustomButton_B

class ViewPDF(ctk.CTkFrame):  # Inherit from customtkinter CTkFrame
    """Frame para una visualización simple de un PDF, 
    con opciones para navegar entre páginas y ajustar el zoom."""
    
    def __init__(self, master):
        super().__init__(master, fg_color="#F7F7F7")
        self.master = master
        self.pdf_document = None
        self.current_page = 0
        self.zoom_levels = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        self.current_zoom_index = 2  # Iniciar en 100%
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario. Despliega menú de acciones, 
        canvas para visualizar el PDF y barras de desplazamiento."""
        
        # Frame superior para botones
        top_frame = ctk.CTkFrame(self, fg_color="#F7F7F7")  # Use CTkFrame
        top_frame.pack(fill=ctk.X, padx=10, pady=10)
        
        # Botón para seleccionar PDF
        select_btn = CustomButton_A(top_frame, text="SELECCIONAR PDF", command=self.select_pdf)
        select_btn.pack(side=ctk.LEFT, padx=(0, 10))
        
    
        
        # Botones de zoom
        self.zoom_out_btn = CustomButton_B(top_frame, text="ZOOM -", 
                                     command=self.zoom_out, state="disabled")
        self.zoom_out_btn.pack(side=ctk.LEFT, padx=10)
        
        self.zoom_label = ctk.CTkLabel(top_frame, 
                                       text="100%",
                                       text_color="#114850",
                                       fg_color="#F7F7F7",
                                       font=("Montserrat bold", 10)
                                       )  # Use CTkLabel
        self.zoom_label.pack(side=ctk.LEFT, padx=5)
        
        self.zoom_in_btn = CustomButton_B(top_frame, text="ZOOM +", command=self.zoom_in, state="disabled")
        self.zoom_in_btn.pack(side=ctk.LEFT, padx=10)   
        
        # Combobox para zoom preestablecido
        #self.zoom_combo = ctk.CTkComboBox(top_frame, values=["50%", "75%", "100%", "125%", "150%", "200%", "Ajustar a página"])
        #elf.zoom_combo.set("100%")
        #self.zoom_combo.pack(side=ctk.LEFT, padx=10)
        #self.zoom_combo.bind("<<ComboboxSelected>>", self.set_zoom)
        #self.zoom_combo.configure(state="readonly")
        
        # Botón para agregar marcador
        #bookmark_btn = CustomButton_A(top_frame, text="Agregar Marcador", command=self.add_bookmark)
        #bookmark_btn.pack(side=ctk.LEFT, padx=(10, 0))
        
        # Frame para el canvas, las barras de desplazamiento y el panel de miniaturas
        content_frame = ctk.CTkFrame(self, fg_color="#F7F7F7")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para mostrar la página del PDF
        self.canvas = tk.Canvas(content_frame, background="#F7F7F7")
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
        
        # Panel de miniaturas
        self.thumbnail_panel = ThumbnailPanel(content_frame, self.on_thumbnail_click)
        self.thumbnail_panel.pack(side=tk.RIGHT, fill=tk.Y)

         # Bottom frame for navigation buttons and page label
        bottom_frame = ctk.CTkFrame(self, fg_color="#F7F7F7")
        bottom_frame.pack(fill=tk.X, padx=5, pady=2)

        # Left frame for navigation buttons and page label
        nav_frame = ctk.CTkFrame(bottom_frame, fg_color="#F7F7F7")
        nav_frame.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.prev_btn = CustomButton_B(nav_frame, 
                            text="ANTERIOR", 
                            command=self.prev_page, 
                            state=tk.DISABLED)
        self.prev_btn.grid(row=0, column=0, padx=1)
        
        self.page_label = ctk.CTkLabel(nav_frame, 
                                       text="0 / 0",
                                       fg_color="#F7F7F7",
                                       font=("Montserrat bold", 10),
                                       text_color="#114850")
        self.page_label.grid(row=0, column=1, padx=3)
        
        self.next_btn = ctk.CTkButton(nav_frame, text="SIGUIENTE", 
                          command=self.next_page, 
                          state=tk.DISABLED,
                          fg_color="white",
                          border_color="#00C4FF",
                          border_width=1,
                          font=("Montserrat bold", 10),
                          hover_color="light blue")

        
        self.next_btn.grid(row=0, column=2, padx=1)

        
        back_btn = CustomButton_A(bottom_frame, text="VOLVER A MENÚ", command=lambda: 
                                  [self.restore_values(), self.master.geometry("800x600"), 
                                   self.master.show_frame("MainMenu")],
                                   )
        back_btn.grid(row=0, column=1, sticky="w")
                
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_columnconfigure(2, weight=1)
        
        
    
    def on_mousewheel(self, event):
        """Controla el evento de rueda del ratón para hacer scroll en el canvas."""

        # Determinar la dirección del scroll
        if event.num == 5 or event.delta == -120:  # Scroll hacia abajo
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:  # Scroll hacia arriba
            self.canvas.yview_scroll(-1, "units")
    
    def select_pdf(self):
        """Abre un cuadro de diálogo para seleccionar un archivo PDF y lo carga."""

        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.pdf_document = fitz.open(file_path)
            self.current_page = 0
            self.thumbnail_panel.load_thumbnails(self.pdf_document)
            self.update_page()
            self.update_navigation_buttons()
            self.zoom_in_btn.configure(state="normal")
            self.zoom_out_btn.configure(state="normal")
    
    def update_page(self):
        """Actualiza la visualización de la página actual del PDF."""

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
            
            self.page_label.configure(
                text=f"PÁGINA: {self.current_page + 1} / {len(self.pdf_document)}")
            self.zoom_label.configure(text=f"{int(zoom * 100)}%")
            self.thumbnail_panel.update_selection(self.current_page)
    
    def restore_scrollbars(self):
        """Restaura las barras de desplazamiento a su posición inicial."""

        self.canvas.yview_moveto(0)
        self.canvas.xview_moveto(0)

    def prev_page(self):
        """Muestra la página anterior del PDF, si es que hay una."""

        if self.current_page and self.current_page > 0:
            self.current_page -= 1
            self.restore_scrollbars()
            self.update_page()
            self.update_navigation_buttons()
    
    def next_page(self):
        """Muestra la página siguiente del PDF, si es que hay una."""

        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.restore_scrollbars()
            self.update_page()
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Actualiza el estado de los botones de navegación según la página actual."""

        self.prev_btn.configure(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED,
                                text_color="grey" if self.current_page == 0 else "#114850")
        self.next_btn.configure(state=tk.NORMAL if self.current_page < len(self.pdf_document) - 1 else tk.DISABLED,
                                text_color="grey" if self.current_page == len(self.pdf_document) - 1 else "#114850")
    
    def zoom_in(self):
        """Aumenta el zoom de la página actual, si es posible."""

        if self.current_zoom_index < len(self.zoom_levels) - 1:
            self.current_zoom_index += 1
            self.update_page()
        
        if self.current_zoom_index == len(self.zoom_levels) - 1:
            self.zoom_in_btn.configure(state="disabled")
        self.zoom_out_btn.configure(state="normal")

        
    
    def zoom_out(self):
        """Reduce el zoom de la página actual, si es posible."""

        if self.current_zoom_index > 0:
            self.current_zoom_index -= 1
            self.update_page()
        
        if self.current_zoom_index == 0:
            self.zoom_out_btn.configure(state="disabled")
        self.zoom_in_btn.configure(state="normal")
    
    def set_zoom(self, event):
        """Establece el zoom de la página actual según la opción seleccionada."""

        selected = self.zoom_combo.get()
        if selected == "Ajustar a página":
            self.fit_to_page()
        else:
            zoom = int(selected.strip('%')) / 100
            self.current_zoom_index = self.zoom_levels.index(zoom)
            self.update_page()
    
    def fit_to_page(self):
        """Ajusta el zoom para que la página actual se ajuste al tamaño del canvas."""

        if self.pdf_document:
            page = self.pdf_document[self.current_page]
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            page_width, page_height = page.rect.width, page.rect.height
            
            width_ratio = canvas_width / page_width
            height_ratio = canvas_height / page_height
            zoom = min(width_ratio, height_ratio)
            
            self.current_zoom_index = min(range(len(self.zoom_levels)), key=lambda i: abs(self.zoom_levels[i] - zoom))
            self.update_page()
    
    def on_thumbnail_click(self, page_num):
        """Maneja el click en una miniatura"""
        self.current_page = page_num
        self.restore_scrollbars()
        self.update_page()
        self.update_navigation_buttons()
    
    def add_bookmark(self):
        """Agrega un marcador en la página actual del PDF."""
        if self.pdf_document:
            title = simpledialog.askstring("Agregar Marcador", "Ingrese el título del marcador:")
            if title:
                self.pdf_document.set_toc(self.pdf_document.get_toc() + [[1, title, self.current_page + 1]])
                self.pdf_document.save(self.pdf_document.name, incremental=True)
                tk.messagebox.showinfo("Marcador Agregado", f"Marcador '{title}' agregado en la página {self.current_page + 1}")

    def restore_values(self):
        self.pdf_document = None
        self.current_page = 0
        self.current_zoom_index = 2
        self.zoom_label.configure(text="100%")
        self.page_label.configure(text="PÁGINA: 0 / 0")
        self.canvas.delete("all")
        self.thumbnail_panel.clean_thumbnails()
        self.canvas.configure(scrollregion=(0,0,0,0)),
        self.zoom_in_btn.configure(state=tk.DISABLED)
        self.zoom_out_btn.configure(state=tk.DISABLED)
        self.prev_btn.configure(state=tk.DISABLED, text_color="grey")
        self.next_btn.configure(state=tk.DISABLED, text_color="grey")

if __name__ == "__main__":
    print('hello, CGR')