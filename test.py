import tkinter as tk
root = tk.Tk()
frame = tk.Frame(root)
frame.pack(fill='both', expand=True)
root.wm_attributes("-alpha", 0.0)
root.mainloop()