import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import PyPDF2
from PIL import Image
import io
import fitz  # PyMuPDF

class CompressPDF(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pdf_path = None
        self.init_ui()

    def init_ui(self):
        frame = ttk.Frame(self)
        frame.pack(padx=10, pady=10)

        ttk.Button(frame, text="Seleccionar PDF", command=self.select_pdf).pack(pady=5)
        
        ttk.Label(frame, text="Nivel de compresión:").pack(pady=5)
        self.compression_var = tk.StringVar(value="medium")
        ttk.Radiobutton(frame, text="Bajo", variable=self.compression_var, value="low").pack()
        ttk.Radiobutton(frame, text="Medio", variable=self.compression_var, value="medium").pack()
        ttk.Radiobutton(frame, text="Alto", variable=self.compression_var, value="high").pack()

        ttk.Button(frame, text="Comprimir PDF", command=self.compress_pdf).pack(pady=10)

        ttk.Button(frame, text="Volver al Menú Principal", 
                   command=lambda: self.master.show_frame("MainMenu")).pack(pady=10)

    def select_pdf(self):
        self.pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if self.pdf_path:
            messagebox.showinfo("PDF Seleccionado", f"Se ha seleccionado: {self.pdf_path}")

    def compress_pdf(self):
        if not self.pdf_path:
            messagebox.showerror("Error", "Por favor, seleccione un PDF primero.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not output_path:
            return

        compression_level = self.compression_var.get()
        
        try:
            self.compress_pdf_with_pymupdf(self.pdf_path, output_path, compression_level)
            messagebox.showinfo("Éxito", f"PDF comprimido guardado en: {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al comprimir el PDF: {str(e)}")

    def compress_pdf_with_pymupdf(self, input_path, output_path, compression_level):
        if compression_level == "low":
            quality = 90
        elif compression_level == "medium":
            quality = 50
        else:  # high
            quality = 20

        doc = fitz.open(input_path)
        for page in doc:
            for img in page.get_images():
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Comprimir la imagen
                img = Image.open(io.BytesIO(image_bytes))
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="JPEG", quality=quality, optimize=True)
                
                # Reemplazar la imagen en el PDF
                doc.update_stream(xref, img_buffer.getvalue())

        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()

if __name__ == "__main__":
    print('holo')