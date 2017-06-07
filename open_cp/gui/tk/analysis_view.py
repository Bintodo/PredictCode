"""
analysis_view
~~~~~~~~~~~~~

The view for the analysis panel.
"""

import tkinter as tk
import tkinter.ttk as ttk
from . import util
from .. import funcs
from . import mtp
from open_cp.gui.common import CoordType

_text = {
    "data" : "Input data",
    "tasks" : "Analysis tools",
    "filename" : "Input filename: ",
    "rows" : "Number of crime events: ",
    "empty" : "Empty input rows: ",
    "error" : "Rows with input errors: ",
    "plot" : "All input events",
    "timerange" : "Time range of events: ",
    "timerange1" : " to ",
    "coord_type" : "Coordinates are ",
    
}

class AnalysisView(tk.Frame):
    def __init__(self, model, root):
        super().__init__(root)
        self._model = model
        self.grid(sticky=util.NSEW)
        self.master.protocol("WM_DELETE_WINDOW", self.cancel)
        util.centre_window_percentage(self.master, 70, 50)
        self.add_widgets()

    def _info_frame(self, parent):
        info = ttk.Frame(parent)
        text = _text["filename"] + funcs.string_ellipse(self._model.filename, 80)
        ttk.Label(info, text=text).grid(row=0, column=0, sticky=tk.W, padx=3, pady=1)
        row_frame = ttk.Frame(info)
        row_frame.grid(row=1, column=0, sticky=tk.W)
        ttk.Label(row_frame, text=_text["rows"] + str(self._model.num_rows)).grid(row=0, column=0, padx=3, pady=1)
        ttk.Label(row_frame, text=_text["empty"] + str(self._model.num_empty_rows)).grid(row=0, column=1, padx=3, pady=1)
        ttk.Label(row_frame, text=_text["error"] + str(self._model.num_error_rows)).grid(row=0, column=2, padx=3, pady=1)
        text = _text["coord_type"]
        text += CoordType._translation[self._model.coord_type]
        ttk.Label(info, text=text).grid(row=2, column=0, sticky=tk.W)
        return info

    def _plot_frame(self, parent):
        frame = ttk.LabelFrame(parent, text=_text["plot"])
        #canvas = tk.Canvas(frame)
        #canvas.grid()
        #canvas["width"] = 300
        #canvas["height"] = 300
        #canvas.create_text(150, 150, text="TODO: Plot of points here")
        fig, ax = mtp.plt.subplots()
        ax.scatter(self._model.xcoords, self._model.ycoords, marker="+", color="black", alpha=0.2)
        fig.set_size_inches(3, 3)
        fig.tight_layout()
        mtp.figure_to_canvas(fig, frame).grid()
        return frame

    def _data_buttons(self, parent):
        frame = ttk.Frame(parent)
        ttk.Button(frame, text="Select a new input file").grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=2)
        ttk.Button(frame, text="Plot with base map").grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=2)
        return frame

    def _time_range_select(self, parent):
        frame = ttk.Frame(parent)
        text = _text["timerange"]
        text += str(min(self._model.times)) + "\n\t"
        text += _text["timerange1"]
        text += str(max(self._model.times))
        ttk.Label(frame, text=text).grid(row=2, column=0, padx=3, pady=1, sticky=tk.W)

        ttk.Button(frame, text="TODO: Select time ranges here").grid()#row=0, column=0, sticky=tk.NSEW, padx=5, pady=2)
        # https://python-forum.io/Thread-Tkinter-tkinter-calendar-widget
        return frame

    def _analysis_tools(self, frame):
        util.stretchy_columns(frame, [0])
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=tk.EW)
        util.stretchy_columns(button_frame, [0])
        ttk.Button(button_frame, text="Save session").grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=3)
        ttk.Button(button_frame, text="Back to main menu").grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=3)
        pred_frame = ttk.LabelFrame(master=frame, text="Predictions")
        pred_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=3)
        ttk.Label(pred_frame, text="TODO: List of prediction methods / parameters here").grid(row=0,column=0)
        # Just a place-holder...
        c = tk.Canvas(pred_frame)
        c.grid(row=1, column=0)
        c["height"] = 150
        compare_frame = ttk.LabelFrame(frame, text="Comparison methods")
        compare_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=3)
        ttk.Label(compare_frame, text="TODO: List of methods to compare preditions here").grid()
        c = tk.Canvas(compare_frame)
        c.grid(row=1, column=0)
        c["height"] = 150

    def add_widgets(self):
        # TODO: Maybe make column 1 fixed size??
        #self.columnconfigure(0, weight=2)
        #self.columnconfigure(1, weight=10)
        util.stretchy_rows(self, [0])
        
        frame = ttk.LabelFrame(self, text=_text["data"])
        frame.grid(row=0, column=0, sticky=util.NSEW, padx=3, pady=3)
        sub_frame = ttk.Frame(frame)
        sub_frame.grid(row=0, column=0, sticky=tk.N + tk.EW)
        self._info_frame(sub_frame).grid(row=0, column=0)
        self._data_buttons(sub_frame).grid(row=0, column=1)
        sub_frame = ttk.Frame(frame)
        sub_frame.grid(row=1, column=0, sticky=tk.N + tk.EW)
        self._plot_frame(sub_frame).grid(row=0, column=0, sticky=tk.N)
        self._time_range_select(sub_frame).grid(row=0, column=1, sticky=tk.N)

        frame = ttk.LabelFrame(self, text=_text["tasks"])
        frame.grid(row=0, column=1, sticky=util.NSEW, padx=3, pady=3)
        self._analysis_tools(frame)

    def cancel(self):
        # TODO: Eventually, prompt about saving??
        self.destroy()
    