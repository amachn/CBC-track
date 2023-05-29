from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.markers import MarkerStyle
import numpy as np

import sys
import tkinter as tk

try:
    from .reader import Reader
except ImportError:
    from reader import Reader
    

class Plotter:
    root: tk.Tk
    reader: Reader
    
    canvases: dict[int, FigureCanvasTkAgg]
    
    def __init__(self, root: tk.Tk, reader: Reader) -> None:
        self.root = root
        self.reader = reader
        self._make()

        # test_canvas = self.canvases[0]
        # test_canvas.draw()
        # test_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # tk.mainloop()
        
    def _make(self) -> ...:
        # this fn makes/replaces all canvases stored
        self.canvases = {}
        
        line_df = self.reader.get_lines()
        scatter_df = self.reader.get_scatter()
        
        if len(line_df.columns) > 20:
            sys.exit("ERROR: Cannot have more than 20 graphs due to GUI/performance limitations.")
        
        for i in range(0, len(line_df.columns)):
            # steps: make figure, plot lines on subplot/format subplot, create/store figure in canvas
            # make figure
            fig = Figure(figsize=(5, 4), dpi=100, facecolor='lightgrey')
            
            # collect line data
            # col = line_df.columns[i]
            line_data_unmasked = line_df.iloc[:, i].to_numpy()
            line_dates, line_data = self.reader.mask(line_data_unmasked)
            
            # collect scatter data
            scatter_data: list[tuple[np.ndarray, ...]] = []
            for j in range(0, len(scatter_df.columns)):
                s_dates, s_data = self.reader.interp_by_series(line_data_unmasked, scatter_df.iloc[:, j].to_numpy())
                scatter_data.append((s_dates, s_data))
            
            # plot data
            ax = fig.add_subplot()
            ax.plot(self.reader.to_timestamp(line_dates), line_data, linestyle='-', marker='.')
            
            for s_set in scatter_data:
                ax.scatter(
                    self.reader.to_timestamp(s_set[0]), s_set[1], s=100, c='purple', marker=MarkerStyle('x'), alpha=0.9
                )
            
            # format plotted data
            
            # store figure/canvas
            canvas = FigureCanvasTkAgg(fig, self.root)
            self.canvases[i] = canvas
            # need to set up canvas bindings
    
        
if __name__ == "__main__":
    plotter = Plotter(tk.Tk(), Reader("tracking.xlsx"))
    