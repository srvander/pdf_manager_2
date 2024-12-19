import tkinter as tk
from CTkListbox import CTkListbox
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os
from custom_widgets import (CustomFrame, 
                            CustomLabel, 
                            CustomButton_A,
                            CustomButton_B)


class MergePDF(CustomFrame):
    """Frame para unir varios archivos PDF en uno solo."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pdf_files = []
        self.preview_images = []
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario. Despliega menú de acciones,
        listbox para mostrar los archivos seleccionados, previsualización de
        la primera página de cada archivo y botones para reordenar y unir."""

        # Frame principal
        main_frame = CustomFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para botones de selección y unión, y label con instrucciones
        button_frame = CustomFrame(main_frame)
        button_frame.pack(fill=tk.X)
        
        CustomButton_A(button_frame, text="ABRIR PDFs", command=self.select_pdfs).pack(side=tk.LEFT, padx=10)
        CustomButton_A(button_frame, text="UNIR PDFs", command=self.merge_pdfs).pack(side=tk.LEFT, padx=10)

        #agregar label con instruccion en la misma linea: indicar que seleccion de pdfs creará nuevo archivo llamado merged_pdf en carpeta de documentos
        CustomLabel(button_frame, text="Al Unir se creará un nuevo archivo 'pdf_merged.pdf'\nen la carpeta de los documentos originales.").pack(side=tk.LEFT, padx=5)
        
        # Frame para la lista de archivos y previsualizaciones
        list_frame = CustomFrame(main_frame)
        list_frame.pack(fill=tk.BOTH, side="top", expand=True, pady=(10, 0))
        
        # Listbox para mostrar los archivos seleccionados
        self.file_listbox = CTkListbox(list_frame, 
                                       multiple_selection=False, 
                                       font=("Montserrat bold", 10),
                                       text_color="black",)
        self.file_listbox.pack(side="left", fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Scrollbar para la listbox
        #scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        #scrollbar.pack(side=tk.LEFT)
        #self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # Frame para botones de reordenamiento
        order_frame = CustomFrame(list_frame)
        order_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        CustomButton_B(order_frame, text="↑", command=self.move_up).pack(fill=tk.X)
        CustomButton_B(order_frame, text="↓", command=self.move_down).pack(fill=tk.X)
        
        # Frame para previsualización
        self.preview_frame = ttk.Frame(main_frame)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        #INSERTAR IMAGEN EN PREVIEW FRAME
        #img = Image.open(self.resource_path("images/pdf_pending.png"))
        img = Image.open("images/pdf_pending.png")
        img = img.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        label = ttk.Label(self.preview_frame, image=img_tk)
        label.image = img_tk
        label.pack(pady=(70,30))

        
        # Botón para volver al menú principal
        CustomButton_A(self, text="VOLVER AL MENÚ", 
                   command=lambda: [self.restore_image(),
                       self.master.show_frame("MainMenu"),
                       self.pdf_files.clear(),
                       self.update_file_list(),
                        ]).pack(pady=10)
    
    #restore image in preview frame
    def restore_image(self):
        img = Image.open("images/pdf_pending.png")
        img = img.resize((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        if self.preview_frame.winfo_children():
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
        label = ttk.Label(self.preview_frame, image=img_tk)
        label.image = img_tk
        label.pack(pady=(70,30))

    def select_pdfs(self):
        """ Abre un cuadro de diálogo para seleccionar uno o varios archivos PDF."""

        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if files:
            self.pdf_files = list(files)
            self.update_file_list()
            self.load_previews()
    
    def update_file_list(self):
        """Actualiza la lista de archivos en la listbox."""

        self.file_listbox.delete(0, tk.END)
        for file in self.pdf_files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def load_previews(self):
        """Carga la previsualización de la primera página de cada archivo PDF."""

        self.preview_images = []
        for file in self.pdf_files:
            try:
                doc = fitz.open(file)
                page = doc.load_page(0)  # Primera página
                pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img_tk = ImageTk.PhotoImage(img)
                self.preview_images.append(img_tk)
                doc.close()
            except Exception as e:
                print(f"Error al cargar la previsualización de {file}: {str(e)}")
                self.preview_images.append(None)
    
    def on_select(self, event):
        """Muestra la previsualización del archivo seleccionado en la listbox."""

        selection = self.file_listbox.curselection()
        if selection is not None:
            index = selection
            self.show_preview(index)
    
    def show_preview(self, index):
        """Muestra la previsualización del archivo en la posición indicada."""

        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        
        if 0 <= index < len(self.preview_images):
            img_tk = self.preview_images[index]
            if img_tk:
                label = ttk.Label(self.preview_frame, image=img_tk)
                label.image = img_tk
                label.pack()
                ttk.Label(self.preview_frame, text=f"Previsualización de: {os.path.basename(self.pdf_files[index])}").pack()
            else:
                ttk.Label(self.preview_frame, text="No se pudo cargar la previsualización").pack()
    
    def move_up(self):
        """Mueve el archivo seleccionado hacia arriba en la lista."""

        selected = self.file_listbox.curselection()
        if selected is not None and selected > 0:
            index = selected
            self.pdf_files[index-1], self.pdf_files[index] = self.pdf_files[index], self.pdf_files[index-1]
            self.preview_images[index-1], self.preview_images[index] = self.preview_images[index], self.preview_images[index-1]
            self.update_file_list()
            self.file_listbox.select(index-1)
            self.file_listbox._parent_canvas.yview_moveto((index-1) / self.file_listbox.size())  # Mantener la visualización del ítem seleccionado
    
    def move_down(self):
        """Mueve el archivo seleccionado hacia abajo en la lista."""

        selected = self.file_listbox.curselection()
        if selected is not None and selected < self.file_listbox.size() - 1:
            index = selected
            self.pdf_files[index], self.pdf_files[index+1] = self.pdf_files[index+1], self.pdf_files[index]
            self.preview_images[index], self.preview_images[index+1] = self.preview_images[index+1], self.preview_images[index]
            self.update_file_list()
            self.file_listbox.select(index+1)
            self.file_listbox._parent_canvas.yview_moveto(index / self.file_listbox.size())  # Mantener la visualización del ítem seleccionado
    
    def merge_pdfs(self):
        """Une los archivos PDF seleccionados en uno solo."""

        if not self.pdf_files or len(self.pdf_files) < 2:
            messagebox.showerror("Error", "Por favor, seleccione al menos dos archivo PDF para unir.")
            return
        
        output_dir = os.path.dirname(self.pdf_files[0])
        
        output_filename = "pdf_merged.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Verificar si el archivo ya existe y ajustar el nombre si es necesario
        counter = 1
        while os.path.exists(output_path):
            output_filename = f"pdf_merged_{counter}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            counter += 1
        
        try:
            pdf_writer = PyPDF2.PdfWriter()
            current_page = 0  # Contador de páginas para ajustar marcadores

            for pdf_file in self.pdf_files:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_writer.append(pdf_reader)
                
                # Extraer y añadir marcadores si existen
                try:
                    outlines = pdf_reader.outline
                    for outline in outlines:
                        if isinstance(outline, list):
                            for sub_outline in outline:
                                if isinstance(sub_outline, PyPDF2.generic.Destination):
                                    pdf_writer.add_outline_item(
                                        title=sub_outline.title,
                                        page=sub_outline.page_number + current_page
                                    )
                        elif isinstance(outline, PyPDF2.generic.Destination):
                            pdf_writer.add_outline_item(
                                title=outline.title,
                                page=outline.page_number + current_page
                            )
                except AttributeError:
                    # No hay marcadores en este PDF
                    pass

                current_page += len(pdf_reader.pages)

            with open(output_path, 'wb') as out_file:
                pdf_writer.write(out_file)
            
            messagebox.showinfo("Éxito", f"PDFs unidos exitosamente.\nArchivo guardado como: {output_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al unir los PDFs: {str(e)}")

    #def resource_path(self, relative_path):
    #    try:
    #        base_path = sys._MEIPASS
    #    except Exception:
    #        base_path = os.path.abspath(".")
    #
    #    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    print('hello, CGR!')