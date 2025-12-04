import tkinter as tk

def silent_info(title, message):
    win = tk.Toplevel()
    win.title(title)
    win.resizable(False, False)
    tk.Label(win, text=message, padx=20, pady=10).pack()
    tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=5)
    win.grab_set()  # empêche de cliquer ailleurs
    win.transient()  # fenêtre au-dessus
    win.wait_window()

def silent_warning(title, message):
    win = tk.Toplevel()
    win.title(title)
    win.resizable(False, False)
    tk.Label(win, text=message, padx=20, pady=10, fg="red").pack()
    tk.Button(win, text="OK", command=win.destroy, width=10).pack(pady=5)
    win.grab_set()
    win.transient()
    win.wait_window()
