import tkinter as tk
from frontend.ui_assign import AssignWindow

class HomeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("NAOS data analysis")
        self.root.iconbitmap("naos.ico")

        frame = tk.Frame(root, padx=40, pady=40)
        frame.pack()

        tk.Label(frame, text="Outil d'aide à l'analyse de données",
                 font=("Arial", 18, "bold")).pack(pady=20)

        tk.Button(frame, text="Commencer",
                  font=("Arial", 14),
                  command=self.open_assign_window).pack(pady=15)

    def open_assign_window(self):
        self.root.destroy()
        root = tk.Tk()
        AssignWindow(root)
        root.mainloop()
