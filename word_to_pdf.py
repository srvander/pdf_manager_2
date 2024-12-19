import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from docx2pdf import convert
import pywintypes
import threading
import os
import customtkinter as ctk
from custom_widgets import (CustomLabel,
                            CustomButton_A,
                            CustomButton_B,
                            CustomFrame)


class WordToPDF(CustomFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        label = CustomLabel(self, text="Selecciona Word para convertir a PDF")
        label.pack(pady=5)

        convert_button = CustomButton_A(self, text="CONVERTIR", command=self.convert_to_pdf)
        convert_button.pack(pady=5)

        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=5)

        back_button = CustomButton_A(self, text="VOLVER AL MENÚ", command=lambda: self.master.show_frame("MainMenu"))
        back_button.pack(pady=5)

    def convert_to_pdf(self):
        word_file = filedialog.askopenfilename(filetypes=[("Word files", "*.docx")])
        if word_file:
            if not word_file.endswith(".docx"):
                messagebox.showerror("Error", "Tipo de archivo inválido. Por favor, selecciona un archivo '.docx'.")
                return

            def run_conversion():
                try:

                    self.progress.start()
                    convert(word_file)
                    self.progress.stop()
                    out_folder = os.path.dirname(word_file)
                    message_box = messagebox.showinfo("Éxito", f"¡Archivo convertido exitosamente! Guardado en: {out_folder}")
                except pywintypes.com_error as e:
                    self.progress.stop()
                    if e.hresult == -2147221005:
                        messagebox.showerror("Precaucion", "Microsoft Word no está instalado. Ejecutando con LibreOffice.")

                        from subprocess import Popen
                        LIBRE_OFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"

                        out_folder = os.path.dirname(word_file)
                        p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir',
                                   out_folder, word_file])
                        print([LIBRE_OFFICE, '--convert-to', 'pdf', word_file])
                        p.communicate()
                    else:
                        messagebox.showerror("Error", f"An error occurred: {e}")
                except Exception as e:
                    self.progress.stop()
                    messagebox.showerror("Error", f"An error occurred: {e}")
                finally:
                    self.progress.stop()

            threading.Thread(target=run_conversion).start()

