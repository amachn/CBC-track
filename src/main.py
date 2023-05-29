from tkinter import ttk
import tkinter as tk

from lib.gui import MainFrame
from lib.plotter import Plotter
from lib.reader import Reader


def main() -> None:
    root = tk.Tk()

    # styling
    root.tk.call('source', 'ttk_theme\\azure.tcl')
    root.tk.call('set_theme', 'dark')
    style = ttk.Style()
    style.configure('Mode.TRadiobutton', font=("Segoe UI", 18))

    # application
    reader = Reader("tracking.xlsx")
    plotter = Plotter(root, reader)

    # elements
    frame = MainFrame(reader, plotter)
    frame.pack(fill='both', expand=True)

    # window sizing
    root.update()
    root.update_idletasks()
    root.state('zoomed')
    # root.resizable(width=False, height=False)
    # root.minsize(root.winfo_width(), root.winfo_height())
    # x_coord = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    # y_coord = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    # root.geometry(f"+{x_coord}+{y_coord - 20}")

    root.mainloop()


if __name__ == "__main__":
    main()
