import customtkinter as ctk

class CustomButton_A(ctk.CTkButton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            font=("Montserrat bold", 10), 
            fg_color="#00c4ff", 
            text_color="white",
            width=100)

class CustomButton_B(ctk.CTkButton):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(font=("Montserrat bold", 10), 
                        fg_color="white", 
                        text_color="#114580",
                        border_color="#00C4FF",
                    border_width=1,
                    hover_color="light blue",
                    width=50)
        
class CustomFrame(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#F7F7F7", bg_color="#F7F7F7")

class CustomLabel(ctk.CTkLabel):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(font=("Montserrat", 10), 
                       fg_color="#F7F7F7",
                       bg_color="#F7F7F7",
                       text_color="#114850")