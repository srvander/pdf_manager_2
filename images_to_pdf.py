import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from custom_widgets import (CustomFrame,
                            CustomLabel,
                            CustomButton_A,
                            CustomButton_B)
from PIL import Image, ImageTk
import os
from tkinterdnd2 import DND_FILES  # Import DND_FILES from tkinterdnd2

class ConvertImagesToPDF(CustomFrame):  # Inherit from tk.Frame
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.init_ui()

    def init_ui(self):
        label = CustomLabel(self, text="Convertir Imágenes (jpg, jpeg, png) a PDF")
        label.pack(pady=20)

        select_btn = CustomButton_A(self, text="SELECCIONA IMÁGENES", command=self.select_images)
        select_btn.pack(pady=10, ipadx=20, ipady=5)

        convert_btn = CustomButton_A(self, text="CONVERTIR", command=self.convert_to_pdf)
        convert_btn.pack(pady=10, ipadx=20, ipady=5)

        self.preview_canvas = tk.Canvas(self, height=115, borderwidth=2, relief="solid", bg="#F7F7F7")
        self.preview_frame = CustomFrame(self.preview_canvas)

        self.scrollbar = ctk.CTkScrollbar(self, orientation=tk.HORIZONTAL, command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(xscrollcommand=self.scrollbar.set)

        self.preview_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20)
        self.preview_canvas.create_window((0, 0), window=self.preview_frame, anchor="nw", tags="self.preview_frame")
        self.preview_frame.bind("<Configure>", lambda e: self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all")))

        self.scrollbar.pack(side=tk.TOP, fill=tk.X, padx=20)


        self.drag_drop_label = CustomLabel(self.preview_frame, text="Arrastre y suelte imágenes aquí")
        self.drag_drop_label.pack(padx=200, pady=40)

        bottom_frame = CustomFrame(self)
        bottom_frame.pack(fill=tk.X, padx=29, pady=30)

        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_columnconfigure(2, weight=1)

        move_frame = CustomFrame(bottom_frame)
        move_frame.grid(row=0, column=0, sticky="new", padx=20)

        self.move_up_btn = CustomButton_B(move_frame, text="↑", command=self.move_image_up)
        self.move_up_btn.pack(side=tk.LEFT, padx=10)

        self.move_down_btn = CustomButton_B(move_frame, text="↓", command=self.move_image_down)
        self.move_down_btn.pack(side=tk.LEFT, padx=10)

        back_btn = CustomButton_A(bottom_frame, text="VOLVER AL MENÚ", command=lambda: self.master.show_frame("MainMenu"))
        back_btn.grid(row=0, column=1, sticky="new", padx=30)

        empty_frame = CustomFrame(bottom_frame)
        empty_frame.grid(row=0, column=2,)

        self.master.drop_target_register(DND_FILES)  # Register drop target
        self.master.dnd_bind('<<Drop>>', self.on_drop)  # Bind drop event

        self.selected_image_index = None

        self.image_paths = []

        self.update_move_buttons()

    def on_drop(self, event):
        file_paths = self.master.tk.splitlist(event.data)
        valid_paths = [path for path in file_paths if path.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if valid_paths:
            self.drag_drop_label.pack_forget()  # Hide the drag and drop label
            self.image_paths.extend(valid_paths)
            self.show_image_previews()
        self.update_move_buttons()

    def select_images(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if file_paths:
            self.image_paths = list(file_paths)  # Convert tuple to list
            self.show_image_previews()
        self.update_move_buttons()

    def show_image_previews(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        for index, img_path in enumerate(self.image_paths):
            img = Image.open(img_path)
            img.thumbnail((100, 100))
            img = ImageTk.PhotoImage(img)
            img_label = tk.Label(self.preview_frame, image=img, borderwidth=2, relief="solid")
            img_label.image = img
            img_label.pack(side=tk.LEFT, padx=5)
            img_label.bind("<Button-1>", lambda e, idx=index: self.select_image(idx))
        if not self.image_paths:
            self.drag_drop_label.pack(pady=40)  # Show the drag and drop label if no images
        self.update_move_buttons()

    def select_image(self, index):
        if self.selected_image_index is not None:
            self.preview_frame.winfo_children()[self.selected_image_index].configure(relief="solid")
        self.selected_image_index = index
        self.preview_frame.winfo_children()[index].configure(relief="raised")
        self.update_move_buttons()

    def move_image_up(self):
        if self.selected_image_index is not None and self.selected_image_index > 0:
            self.image_paths.insert(self.selected_image_index - 1, self.image_paths.pop(self.selected_image_index))
            self.selected_image_index -= 1
            self.show_image_previews()
        self.update_move_buttons()

    def move_image_down(self):
        if self.selected_image_index is not None and self.selected_image_index < len(self.image_paths) - 1:
            self.image_paths.insert(self.selected_image_index + 1, self.image_paths.pop(self.selected_image_index))
            self.selected_image_index += 1
            self.show_image_previews()
        self.update_move_buttons()

    def update_move_buttons(self):
        if not self.image_paths or self.selected_image_index is None:
            self.move_up_btn.configure(state=tk.DISABLED)
            self.move_down_btn.configure(state=tk.DISABLED)
        else:
            self.move_up_btn.configure(state=tk.NORMAL if self.selected_image_index > 0 else tk.DISABLED)
            self.move_down_btn.configure(state=tk.NORMAL if self.selected_image_index < len(self.image_paths) - 1 else tk.DISABLED)

    def convert_to_pdf(self):
        if not self.image_paths:
            messagebox.showwarning("Advertencia", "Por favor, seleccione al menos una imagen.")
            return

        images = [Image.open(img_path).convert("RGB") for img_path in self.image_paths]
        save_path = f"{os.path.dirname(self.image_paths[0])}/converted_img.pdf"
        images[0].save(save_path, save_all=True, append_images=images[1:])
        messagebox.showinfo("Éxito", "Las imágenes se han convertido a PDF correctamente.")
        self.image_paths = []
        self.selected_image_index = None
        for widget in self.preview_frame.winfo_children():
            widget.destroy()
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
        self.drag_drop_label = CustomLabel(self.preview_frame, text="Arrastre y suelte imágenes aquí")

        self.drag_drop_label.pack(padx=200, pady=40)  # Show the drag and drop label if no images
        
        self.update_move_buttons()

