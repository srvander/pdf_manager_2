import tkinter as tk
import customtkinter as ctk  # Replace tkinter with customtkinter
from tkinter import ttk, filedialog, messagebox
from custom_widgets import (CustomButton_A,
                            CustomButton_B,
                            CustomFrame,
                            CustomLabel)
import PyPDF2
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os

class SplitPDF(CustomFrame):
    """Frame para dividir un archivo PDF en varias partes."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pdf_document = None
        self.start_page = tk.StringVar()
        self.end_page = tk.StringVar()
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario. Despliega menú de acciones, entrada para seleccionar el archivo PDF,
        campos para ingresar el rango de páginas, previsualizaciones de las páginas seleccionadas y botones para dividir."""

        # Frame principal
        main_frame = CustomFrame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para selección de archivo
        file_frame = CustomFrame(main_frame)
        file_frame.pack(fill=tk.X)
        
        CustomLabel(file_frame, text="ARCHIVO PDF:" ).pack(side=tk.LEFT)
        self.file_entry = ttk.Entry(file_frame, width=60)
        self.file_entry.pack(side=tk.LEFT, expand=True, padx=10)
        CustomButton_A(file_frame, text="ABRIR PDF", command=self.select_pdf).pack(side=tk.LEFT, fill=tk.BOTH, padx=10)
        
        # Frame para entrada de páginas
        page_frame = CustomFrame(main_frame)
        page_frame.pack(fill=tk.X, pady=(0, 10))
        
        CustomLabel(page_frame, text="PÁGINA INICIAL:").pack(side=tk.LEFT)
        # Replace Entry with Spinbox for start_page
        self.start_page_spinbox = ttk.Spinbox(page_frame, from_=1, to=1, textvariable=self.start_page, width=5)
        self.start_page_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        CustomLabel(page_frame, text="PÁGINA FINAL:").pack(side=tk.LEFT)
        # Replace Entry with Spinbox for end_page
        self.end_page_spinbox = ttk.Spinbox(page_frame, from_=1, to=1, textvariable=self.end_page, width=5)
        self.end_page_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        CustomButton_A(page_frame, text="PREVISUALIZAR", command=self.preview_pages).pack(padx=10)
        
        # Frame para previsualizaciones
        self.preview_frame = CustomFrame(main_frame)
        self.preview_frame.pack(expand=True, side=tk.TOP, padx=10)
        
        # Botón para dividir PDF
        CustomButton_A(main_frame, text="DIVIDIR PDF", command=self.split_pdf).pack(pady=10)
        
        # Botón para volver al menú principal
        CustomButton_A(self, text="VOLVER AL MENÚ", 
                   command=lambda: [
                   self.reset_ui(),
                   self.master.show_frame("MainMenu")],
                   ).pack(pady=10)
    
    def reset_ui(self):
        """Reinicia la interfaz de usuario para permitir una nueva selección de archivo PDF."""

        self.file_entry.delete(0, tk.END)
        self.start_page.set("1")
        self.end_page.set("1")
        self.start_page_spinbox.config(to=1)
        self.end_page_spinbox.config(to=1)
        
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
        
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

            
    def select_pdf(self):
        """Abre un cuadro de diálogo para seleccionar un archivo PDF y carga el documento."""

        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path):
        """Carga el archivo PDF indicado y muestra un mensaje con la cantidad de páginas."""

        try:
            self.pdf_document = fitz.open(file_path)
            total_pages = len(self.pdf_document)
            self.start_page_spinbox.config(to=total_pages)
            self.end_page_spinbox.config(to=total_pages)
            messagebox.showinfo("Información", f"PDF cargado. Total de páginas: {total_pages}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el PDF: {str(e)}")
    
    def preview_pages(self):
        """Muestra previsualizaciones de la primera y última página del rango seleccionado."""

        if not self.pdf_document:
            messagebox.showerror("Error", "Por favor, seleccione un archivo PDF primero.")
            return
        
        try:
            start = int(self.start_page.get()) - 1  # Restamos 1 porque PyMuPDF usa índices base 0
            end = int(self.end_page.get()) - 1
            
            if start < 0 or end >= len(self.pdf_document) or start > end:
                raise ValueError("Rango de páginas inválido")
            
            # Limpiar previsualizaciones anteriores
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
            
            # Mostrar previsualización de la primera y última página
            self.show_preview(start, "Página inicial")
            if start != end:
                self.show_preview(end, "Página final")
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def show_preview(self, page_num, label_text):
        """Muestra la previsualización de la página indicada en el frame correspondiente."""

        page = self.pdf_document[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))  # Escala reducida para previsualización
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_tk = ImageTk.PhotoImage(img)
        
        frame = ttk.Frame(self.preview_frame)
        frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        ttk.Label(frame, text=f"{label_text} (Página {page_num + 1})").pack()
        label = ttk.Label(frame, image=img_tk)
        label.image = img_tk
        label.pack()
    
    def split_pdf(self):
        """Divide el PDF en el rango de páginas indicado y guarda el resultado en un nuevo archivo."""

        if not self.pdf_document:
            messagebox.showerror("Error", "Por favor, seleccione un archivo PDF primero.")
            return
        
        try:
            start = int(self.start_page.get()) - 1
            end = int(self.end_page.get()) - 1
            
            if start < 0 or end >= len(self.pdf_document) or start > end:
                raise ValueError("Rango de páginas inválido")
            
            input_path = self.file_entry.get()
            output_dir = os.path.dirname(input_path)
            output_filename = f"{os.path.splitext(os.path.basename(input_path))[0]}_p{start+1}-{end+1}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            pdf_writer = PyPDF2.PdfWriter()
            with open(input_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(start, end + 1):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            
            messagebox.showinfo("Éxito", f"PDF dividido guardado como:\n{output_path}")
            self.reset_ui()
            self.master.geometry("800x600")
            self.master.show_frame("MainMenu")
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al dividir el PDF:\n{str(e)}")
    
    def on_close(self):
        """Cierra el documento PDF al cerrar el frame."""

        if self.pdf_document:
            self.pdf_document.close()

if __name__ == "__main__":
    print('hello, CGR!')