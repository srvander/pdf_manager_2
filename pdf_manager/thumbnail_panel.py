import customtkinter as ctk  # Replace tkinter and ttk with customtkinter
from PIL import Image, ImageTk
import fitz
from functools import partial

class ThumbnailPanel(ctk.CTkFrame):
    """Panel lateral para mostrar miniaturas de páginas del PDF"""
    
    def __init__(self, master, callback):
        super().__init__(master, fg_color="#F7F7F7")  # Use CTkFrame with custom background
        self.thumbnail_size = (100, 142)  # Proporción A4
        self.thumbnails = []
        self.callback = callback
        self.original_images = []  # Guardará las imágenes originales

        # Canvas para las miniaturas con scrollbar
        self.canvas = ctk.CTkCanvas(self, width=120, bg="#F7F7F7", highlightthickness=0)  # Use CTkCanvas
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)  # Use CTkScrollbar
        self.thumbnail_frame = ctk.CTkFrame(self.canvas, fg_color="#F7F7F7")  # Use CTkFrame inside canvas
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configurar expansión
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Crear ventana en el canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.thumbnail_frame, anchor="nw")
        
        # Bindings
        self.thumbnail_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_mousewheel()

    def create_overlay_image(self, img):
        """Crea una versión de la imagen con overlay azul"""
        overlay = img.copy()
        # Crear una capa azul semitransparente
        blue_layer = Image.new('RGB', overlay.size, (0, 0, 255))
        # Combinar la imagen original con la capa azul
        overlay = Image.blend(overlay, blue_layer, 0.3)
        return overlay
        
    def bind_mousewheel(self):
        """Configura el scroll con la rueda del ratón"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
            
        self.bind("<MouseWheel>", _on_mousewheel)
        self.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.thumbnail_frame.bind("<MouseWheel>", _on_mousewheel)
    
    def _on_frame_configure(self, event=None):
        """Actualiza el scroll region cuando cambia el tamaño del frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Ajusta el ancho del frame interno al canvas"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def clean_thumbnails(self):
        """Elimina las miniaturas existentes"""
        for widget in self.thumbnail_frame.winfo_children():
            widget.destroy()
        self.thumbnails.clear()
        self.original_images.clear()
        #self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
    
    def load_thumbnails(self, pdf_document):
        """Carga las miniaturas del documento PDF"""
        
        if not pdf_document:
            return
            
        # Generar nuevas miniaturas
        for page_num in range(len(pdf_document)):
            try:
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(0.15, 0.15))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.thumbnail(self.thumbnail_size)

                # Crear versión normal y seleccionada de la miniatura
                photo_normal = ImageTk.PhotoImage(img)
                photo_selected = ImageTk.PhotoImage(self.create_overlay_image(img))
                
                # Frame para la miniatura y número de página
                frame = ctk.CTkFrame(self.thumbnail_frame, fg_color="#F7F7F7")  # Use CTkFrame
                frame.pack(pady=5)

                # binding para scroll con rueda del ratón
                frame.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

                
                # Label para la miniatura
                label = ctk.CTkLabel(frame, image=photo_normal, text="")  # Use CTkLabel
                label.image = photo_normal  # Mantener referencia
                label.image_selected = photo_selected  # Mantener referencia
                label.pack()
                
                # Label para el número de página
                page_label = ctk.CTkLabel(frame, text=f"Página {page_num + 1}", text_color="#114580")  # Use CTkLabel
                page_label.pack()
                
                # Binding para click
                label.bind("<Button-1>", partial(self._on_thumbnail_click, page_num))
                page_label.bind("<Button-1>", partial(self._on_thumbnail_click, page_num))

                #binding para scroll con rueda del ratón
                label.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))
                page_label.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

                
                self.thumbnails.append((photo_normal, photo_selected, label))
                
            except Exception as e:
                print(f"Error generando miniatura para página {page_num + 1}: {str(e)}")
    
    def _on_thumbnail_click(self, page_num, event):
        """Maneja el click en una miniatura"""
        if self.callback:
            self.callback(page_num)
    
    def update_selection(self, current_page):
        """Actualiza la selección visual de la página actual"""
        for i, (photo_normal, photo_selected, label) in enumerate(self.thumbnails):
            if i == current_page:
                label.configure(image=photo_selected)
                label.image = photo_selected
            else:
                label.configure(image=photo_normal)
                label.image = photo_normal

    def clear_selection(self):
        """Desselecciona cualquier miniatura seleccionada"""
        for photo_normal, photo_selected, label in self.thumbnails:
            label.configure(image=photo_normal)
            label.image = photo_normal
