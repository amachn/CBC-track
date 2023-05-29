import pandas as pd

from tkinter import ttk
import sys
import tkinter as tk

try:
    from .plotter import Plotter
    from .reader import Reader
except ImportError:
    from plotter import Plotter
    from reader import Reader


class CustomText(tk.Text):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pos = 1.0

    def ins(self, chars: str) -> None:
        self.configure(state=tk.NORMAL)
        super().insert(str(self.pos), chars + "\n")
        self.pos += 1.0
        self.configure(state=tk.DISABLED)


class MainFrame(ttk.Frame):
    reader: Reader
    plotter: Plotter
    columns: list[str]
    
    state: tk.IntVar
    graph_state: tk.StringVar
    g_state_binds: dict[str, int]

    mode_frame: tuple[ttk.LabelFrame, list[ttk.Radiobutton], ttk.Separator, ttk.Menubutton]
    display_frame: tuple[ttk.LabelFrame, list[ttk.Widget]]
    tool_frame: tuple[ttk.LabelFrame, list[ttk.Widget]]
    log_frame: tuple[ttk.LabelFrame, CustomText, ttk.Scrollbar]

    def __init__(self, reader: Reader, plotter: Plotter) -> None:
        super().__init__()
        
        self.reader = reader
        self.plotter = plotter
        self.columns = [str(x) for x in self.reader.get_lines().columns]
        
        self.state = tk.IntVar(value=0)
        self.graph_state = tk.StringVar(value=self.columns[0])
        self.g_state_binds = {self.columns[i]: i for i in range(len(self.columns))}
        
        for i in range(0, 11):
            self.rowconfigure(index=i, weight=1)  # allows frame expansion
            self.columnconfigure(index=i, weight=1)
            
        # disallow mode frame and tool frame from expanding
        self.columnconfigure(index=0, weight=0)
        self.rowconfigure(index=10, weight=0)

        self.setup()

    def setup(self) -> None:
        # LAYOUT:
        # |---------------------------------------------------------------------|
        # | Frame 1: | Frame 2:                                                 |
        # | Graphs   | F1 Graphs: Graph/subplot display                         |
        # | Compare  | F1 Compare: Select graphs -> side-by-side display        |
        # | Settings | F1 Settings: File, share mode (compare), debug/info mode |
        # |          |                                                          |
        # |          |                                                          |
        # |  ------  |                                                          |
        # |          |                                                          |
        # | SP MENU  |                                                          |
        # |          |----------------------------------------------------------|
        # |          | Frame 3: NavBar, buttons enabled on F1 graphs/compare    |
        # |---------------------------------------------------------------------|

        # ------------------------------------
        # - Frame 1: UI mode selector, pick between Graphs, Compare, or Settings
        mode_frame = ttk.LabelFrame(self, text='Mode')
        mode_frame.grid(
            row=0, column=0, rowspan=11, sticky=tk.NSEW,
            padx=10, pady=10, ipady=5,
        )

        # -- Frame 1 internal sections
        mode_b_frame = ttk.Frame(mode_frame, padding=(5, 15))
        mode_b_frame.grid(row=0, sticky=tk.NSEW)
        mode_frame.rowconfigure(index=0, weight=1)
        
        mode_separator = ttk.Separator(mode_frame, orient='horizontal')
        mode_separator.grid(row=1, sticky=tk.NSEW)
        
        mode_m_frame = ttk.Frame(mode_frame, padding=(5, 15))
        mode_m_frame.grid(row=2, sticky=tk.NSEW, pady=15)
        mode_frame.rowconfigure(index=2, weight=1)

        # -- Frame 1 buttons
        graph_toggle = ttk.Radiobutton(
            mode_b_frame, text='Graphs', style='Mode.TRadiobutton',
            variable=self.state, value=0, command=self._update_display_frame,
        )
        graph_toggle.pack(anchor=tk.CENTER)  # padx=30, pady=5
        
        compare_toggle = ttk.Radiobutton(
            mode_b_frame, text='Compare', style='Mode.TRadiobutton', 
            variable=self.state, value=1, command=self._update_display_frame,
        )
        compare_toggle.pack(anchor=tk.CENTER)  # padx=30, pady=5
        
        settings_toggle = ttk.Radiobutton(
            mode_b_frame, text='Settings', style='Mode.TRadiobutton', 
            variable=self.state, value=2, command=self._update_display_frame,
        )
        settings_toggle.pack(anchor=tk.CENTER)  # padx=30, pady=5
        
        # -- Frame 1 menu
        graph_menubutton = ttk.OptionMenu(
            mode_m_frame, 
            self.graph_state,
            "",
            *[
                self.columns[i] 
                if len(self.columns[i]) <= 25
                else f"Graph {i+1}"
                for i in range(len(self.columns))
            ],
            command=self._update_display_frame,
        )
        graph_menubutton.pack(anchor=tk.CENTER)
        # graph_menubutton.pack(anchor=tk.CENTER, pady=10)

        # -- Frame 1 reference storing
        self.mode_frame = (
            mode_frame, 
            [graph_toggle, compare_toggle, settings_toggle],
            mode_separator,
            graph_menubutton,
        )

        # ------------------------------------
        # - Frame 2: Primary display, shows graphs, comparative graphs, and settings menu
        display_frame = ttk.LabelFrame(self, text="Display")
        display_frame.grid(
            row=0, column=1, rowspan=10, columnspan=10, sticky=tk.NSEW,
            padx=10, pady=10,
        )
        
        # -- Frame 2 reference storing
        self.display_frame = (display_frame, [])
        
        # -- Frame 2 contents
        self._update_display_frame()

        # ------------------------------------
        # - Frame 3: Toolbar
        tool_frame = ttk.LabelFrame(self, text="Toolbar", padding=(5, 5))
        tool_frame.grid(
            row=10, column=1, columnspan=10, sticky=tk.NSEW,
            padx=10, pady=10,
        )
        
        # -- Frame 3 toolbar buttons
        home_button = ttk.Button(tool_frame, text="Home")
        home_button.pack(anchor=tk.S, side=tk.LEFT)
        
        # -- Frame 3 reference storing
        self.tool_frame = (tool_frame, [home_button])

    def _update_display_frame(self, *args) -> None:
        state = self.state.get()
        graph_state = self.graph_state.get()
        print(state)
        print(graph_state)
        print(self.g_state_binds[graph_state])

        if state == 0:  # graphs tab
            # if not self.selector_frame[0].grid_info():  # if the frame is hidden
            #     # re-adjust display frame and re-add selector frame
            #     dframe.grid(
            #         row=1, column=1, rowspan=7, columnspan=10, sticky=tk.NSEW,
            #         padx=10, pady=10,
            #     )
            #     self.selector_frame[0].grid(
            #         row=0, column=1, columnspan=10, sticky=tk.NSEW,
            #         padx=10, pady=10,
            #     )

            # place the graph down
            ...
        else:  # compare/settings tab
            # if self.selector_frame[0].grid_info():  # if the frame is not hidden
            #     # remove selector frame and re-adjust display frame
            #     self.selector_frame[0].grid_forget()
            #     dframe.grid(
            #         row=0, column=1, rowspan=8, columnspan=10, sticky=tk.NSEW,
            #         padx=10, pady=10,
            #     )
            # place the compare/settings tab
            if state == 1:
                ...
            elif state == 2:
                ...
            else:
                sys.exit(f"ERROR: Mode state went out of bounds @ {self.state.get()}.")
