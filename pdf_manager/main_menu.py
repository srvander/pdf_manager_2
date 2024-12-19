from tkinterdnd2 import TkinterDnD  # Import TkinterDnD
import customtkinter as ctk  # Use customtkinter instead of ttkbootstrap
from visualize_pdf import ViewPDF
from censor_pdf import CensorPDF
from split_pdf import SplitPDF
from merge_pdf import MergePDF
from highlight_pdf import HighlightPDF
from images_to_pdf import ConvertImagesToPDF
from word_to_pdf import WordToPDF  # Import the new module
from build_dossier import BuildDossier  # Import the new module
from PIL import Image, ImageTk
from tkinter import ttk
import ctypes
from custom_widgets import CustomLabel



class PDFApp(TkinterDnD.Tk):  # Inherit from TkinterDnD.Tk
    """Clase principal de la aplicación, instancia de una ventana de TKINTER,
    que contiene los distintos frames y controla
    cuál de ellos se muestra en cada momento."""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")  # Set dark mode
        ctk.set_default_color_theme("blue")  # Set default color theme
        self.title("PDF Manager")
        
        #self.overrideredirect(True)  # Elimina la barra de título
        self.resizable(True, True) 

        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int(screen_width * 1 / 10)
        y_position = int(screen_height * 1 / 10)

        self.geometry(f"+{x_position}+{y_position}")

        self.configure(bg="#F7F7F7")  # Establece el color de fondo principal
        
        self.frames = {}
        self.current_frame = None
        
        self.init_frames()
        self.show_frame("MainMenu")

        # Add a sizegrip widget to the bottom right corner
        #sizegrip = ttk.Sizegrip(self)
        #sizegrip.place(relx=1.0, rely=1.0, anchor="se")
        #sizegrip.bind("<B1-Motion>", lambda event: self.geometry(f"{event.x_root}x{event.y_root}"))
        
    
    def init_frames(self):
        """Inicializa todos los frames que se usarán en la aplicación,
        y se almacenarán en el diccionario self.frames para su fácil acceso."""

        self.frames["MainMenu"] = MainMenu(self)
        self.frames["ViewPDF"] = ViewPDF(self)
        self.frames["EditPDF"] = CensorPDF(self)
        self.frames["SplitPDF"] = SplitPDF(self)
        self.frames["MergePDFs"] = MergePDF(self)
        self.frames["HighlightPDF"] = HighlightPDF(self)
        self.frames["ConvertImagesToPDF"] = ConvertImagesToPDF(self)
        self.frames["WordToPDF"] = WordToPDF(self)  # Add the new frame
        self.frames["BuildDossier"] = BuildDossier(self)  # Add the new frame

    def show_frame(self, frame_name):
        """Muestra el frame indicado, escondiendo el frame actual si es que hay uno.
        Además, ajusta el tamaño de la ventana según el frame mostrado, y actualiza
        algunas teclas de acceso rápido."""

        if self.current_frame:
            self.current_frame.pack_forget()
        

        if frame_name == 'MainMenu': #Evita que los documentos seleccionados en otras opciones cambien de pagina
            self.bind("<Right>", lambda e: None)
            self.bind("<Left>", lambda e: None)
            self.bind_hotkeys()
            

        elif frame_name == 'ViewPDF' or frame_name == 'EditPDF' or frame_name == 'HighlightPDF':
            self.bind("<Right>", lambda e: self.frames[frame_name].next_page())
            self.bind("<Left>", lambda e: self.frames[frame_name].prev_page())
            self.unbind_hotkeys()
        
        else:
            self.unbind_hotkeys()
        
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill=ctk.BOTH, expand=True)

        # Ajustamos el tamaño de la ventana según el frame
        if frame_name == "MainMenu" or frame_name == "ConvertImagesToPDF":
            self.geometry("600x450")  
        elif frame_name == "SplitPDF":
            self.geometry("650x500")
        elif frame_name == 'WordToPDF':
            self.geometry("600x200")
        elif frame_name == "BuildDossier":
            self.geometry("800x600")
        else:
            self.geometry("800x600")
    

    def bind_hotkeys(self):
        self.bind("1", lambda e: self.show_frame("ViewPDF"))
        self.bind("2", lambda e: self.show_frame("EditPDF"))
        self.bind("3", lambda e: self.show_frame("HighlightPDF"))
        self.bind("4", lambda e: self.show_frame("SplitPDF"))
        self.bind("5", lambda e: self.show_frame("MergePDFs"))
        self.bind("7", lambda e: self.show_frame("WordToPDF"))  # Bind hotkey for the new frame
        self.bind("6", lambda e: self.show_frame("ConvertImagesToPDF"))
        self.bind("8", lambda e: self.show_frame("BuildDossier"))  # Bind hotkey for the new frame

    def unbind_hotkeys(self):
        self.unbind("1")
        self.unbind("2")
        self.unbind("3")
        self.unbind("4")
        self.unbind("5")
        self.unbind("6")
        self.unbind("7")
        self.unbind("8")

class MainMenu(ctk.CTkFrame):  # Inherit from customtkinter CTkFrame
    """Frame principal de la aplicación, con botones para acceder a las distintas opciones."""

    def __init__(self, master):
        super().__init__(master, fg_color="#F7F7F7")  # Establece el color de fondo del frame principal
        
       

        img = Image.open("images/PDF Manager-03.png")
        #img = img.resize((200, 200))
        img_tk = ctk.CTkImage(light_image=img, dark_image=img, size=(279,53))
        label = CustomLabel(self, image=img_tk, text='')
        label.image = img_tk
        label.pack(pady=20, padx=(30,0))
        
        # Visualizar PDF button with double size
        view_pdf_button = ctk.CTkButton(self, 
                                     text="Visualizar PDF",
                                     command=lambda: self.master.show_frame("ViewPDF"),
                                     fg_color="#00C4FF",  # Cambiado a #00C4FF
                                     hover_color="dark blue")
        view_pdf_button.pack(pady=10, ipadx=20, ipady=10)

        # Create a frame for the second row of buttons
        second_row_frame = ctk.CTkFrame(self, fg_color="#F7F7F7")  # Cambia bg_color de "transparent" a "#F7F7F7"
        second_row_frame.pack(pady=10
                              )

        # Censurar PDF and Destacar PDF buttons on the same line
        censor_pdf_button = ctk.CTkButton(second_row_frame, 
                                       text="Censurar PDF",
                                       command=lambda: self.master.show_frame("EditPDF"),
                                       fg_color="#00C4FF",  # Cambiado a #00C4FF
                                       hover_color="#006400")  # Reemplazado "dark green" por código hex válido
        censor_pdf_button.pack(side=ctk.LEFT, padx=5, ipadx=15, ipady=5, fill=ctk.X)

        highlight_pdf_button = ctk.CTkButton(second_row_frame, 
                                          text="Destacar PDF",
                                          command=lambda: self.master.show_frame("HighlightPDF"),
                                          fg_color="#00C4FF",  # Cambiado a #00C4FF
                                          hover_color="#FF8C00")  # Reemplazado "dark orange" por código hex válido
        highlight_pdf_button.pack(side=ctk.LEFT, padx=5, ipadx=15, ipady=5, fill=ctk.X)

        # Create a frame for the third row of buttons
        third_row_frame = ctk.CTkFrame(self, fg_color="#F7F7F7")  # Cambia bg_color de "transparent" a "#F7F7F7"
        third_row_frame.pack(pady=10)

        # Dividir PDF and Unir PDFs buttons on the same line
        split_pdf_button = ctk.CTkButton(third_row_frame, 
                                      text="Dividir PDF",
                                      command=lambda: self.master.show_frame("SplitPDF"),
                                      fg_color="#00C4FF",  # Cambiado a #00C4FF
                                      hover_color="#800080")  # Reemplazado "dark purple" por código hex válido
        split_pdf_button.pack(side=ctk.LEFT, padx=5, ipadx=15, ipady=5, fill=ctk.X)

        merge_pdfs_button = ctk.CTkButton(third_row_frame, 
                                       text="Unir PDFs",
                                       command=lambda: self.master.show_frame("MergePDFs"),
                                       fg_color="#00C4FF",  # Cambiado a #00C4FF
                                       hover_color="#008080")  # Reemplazado "dark teal" por código hex válido
        merge_pdfs_button.pack(side=ctk.LEFT, padx=5, ipadx=15, ipady=5, fill=ctk.X)

        # Create a frame for the last row of buttons
        last_row_frame = ctk.CTkFrame(self, fg_color="#F7F7F7")  # Cambia bg_color de "transparent" a "#F7F7F7"
        last_row_frame.pack(pady=10)

        # Add the "Word a PDF" button to the last row frame
        word_to_pdf_button = ctk.CTkButton(last_row_frame, 
                                        text="Word a PDF",
                                        command=lambda: self.master.show_frame("WordToPDF"),
                                        fg_color="#00C4FF",  # Cambiado a #00C4FF
                                        hover_color="#8B0000")  # Reemplazado "dark red" por código hex válido
        word_to_pdf_button.pack(side=ctk.LEFT, padx=5, ipadx=15, ipady=5, fill=ctk.X)

        # Add the "JPG a PDF" button to the last row frame
        images_to_pdf_button = ctk.CTkButton(last_row_frame, 
                                          text="JPG a PDF",
                                          command=lambda: self.master.show_frame("ConvertImagesToPDF"),
                                          fg_color="#00C4FF",  # Cambiado a #00C4FF
                                          hover_color="#FF1493")  # Reemplazado "deep pink" por código hex válido
        images_to_pdf_button.pack(side=ctk.LEFT, padx=5, ipadx=15, ipady=5, fill=ctk.X)

        # Create a new frame for the "Construir Expediente" button
        dossier_row_frame = ctk.CTkFrame(self, fg_color="#F7F7F7")  # Cambia bg_color de "transparent" a "#F7F7F7"
        dossier_row_frame.pack(pady=10)

        # Add the "Construir Expediente" button to the new frame
        build_dossier_button = ctk.CTkButton(dossier_row_frame, 
                                          text="Construir Expediente",
                                          command=lambda: self.master.show_frame("BuildDossier"),
                                          fg_color="#00C4FF",  # Cambiado a #00C4FF
                                          hover_color="#008B8B")  # Reemplazado "dark cyan" por código hex válido
        build_dossier_button.pack(side=ctk.LEFT, padx=5, ipadx=15, ipady=5, fill=ctk.X)

        # añadir label en esquina inferior derecha con el nombre del autor
        author_label = ctk.CTkLabel(self, text="Autor: Cristian Mella Cortés\nCorreo: cmellac@contraloria.cl", font=("Montserrat", 10, "bold"), text_color="#114580")
        author_label.pack(side=ctk.RIGHT, anchor=ctk.SE, pady=10)

if __name__ == "__main__":
    app = PDFApp()
    app.mainloop()
