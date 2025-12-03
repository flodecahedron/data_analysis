import tkinter as tk
from frontend.ui_home import HomeWindow

def main():
    root = tk.Tk()
    app = HomeWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()