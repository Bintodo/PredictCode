"""
analysis_view
~~~~~~~~~~~~~

The view for the analysis panel.
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import datetime
from . import util
from .. import funcs
from . import mtp
from . import tooltips
from . import date_picker
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
    "new_input" : "Select a new input file",
    "with_basemap" : "Plot with base map",
    "save" : "Save session",
    "back" : "Back to main menu",
    "preds" : "Predictions",
    "asses" : "Comparison methods",
    "time_select" : "Select time range",
    "train_time" : "Training data time range",
    "start" : "Start:",
    "start_tt_tt" : "The start date/time of the 'training' data.  Data before this time will be ignored.",
    "end" : "End:",
    "end_tt_tt" : "The end date/time of the 'training' data.  Depending on the prediction algorithm chosen, data after this time will not be used.",
    "assess_time" : "Assessment data time range",
    "date_format" : "%d %b %Y",
    "time_format" : "%H:%M",
    "reset" : "Reset",
    "assess_time" : "Assessment data time range",
    "start_ass_tt" : "The start date/time of the 'assessment' data.",
    "end_ass_tt" : "The end date/time of the 'assessment' data.",
    "train_count" : "Events in training range: {}",
    "ass_count" : "Events in assessment range: {}"
}

class AnalysisView(tk.Frame):
    def __init__(self, model, controller, root):
        super().__init__(root)
        self._model = model
        self._controller = controller
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
        ttk.Label(info, text=text).grid(row=2, column=0, sticky=tk.W, padx=3, pady=1)
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
        ttk.Button(frame, text=_text["new_input"]).grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=2)
        ttk.Button(frame, text=_text["with_basemap"]).grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=2)
        return frame

    def _time_range_select(self, parent):
        frame = ttk.LabelFrame(parent, text=_text["time_select"])
        frame.grid(sticky=tk.NSEW)
        text = _text["timerange"]
        text += str(min(self._model.times)) + "\n\t"
        text += _text["timerange1"]
        text += str(max(self._model.times))
        ttk.Label(frame, text=text).grid(row=0, column=0, padx=3, pady=1, sticky=tk.W)

        training_frame = ttk.LabelFrame(frame, text=_text["train_time"])
        training_frame.grid(row=1, column=0, sticky=tk.EW)
        label = ttk.Label(training_frame, text=_text["start"])
        label.grid(row=0, column=0, padx=2, pady=4, sticky=tk.W)
        tooltips.ToolTipYellow(label, _text["start_tt_tt"])
        label = ttk.Label(training_frame, text=_text["end"])
        label.grid(row=1, column=0, padx=2, pady=4, sticky=tk.W)
        tooltips.ToolTipYellow(label, _text["end_tt_tt"])

        self.training_start_date_entry = DateEntry(training_frame, width=15, command=self._controller.notify_training_start)
        self.training_start_date_entry.grid(row=0, column=1, padx=2, sticky=tk.W)
        self.training_start_time_entry = TimeEntry(training_frame, width=10, command=self._controller.notify_training_start)
        self.training_start_time_entry.grid(row=0, column=2, padx=2, sticky=tk.W)

        self.training_end_date_entry = DateEntry(training_frame, width=15, command=self._controller.notify_training_end)
        self.training_end_date_entry.grid(row=1, column=1, padx=2, sticky=tk.W)
        self.training_end_time_entry = TimeEntry(training_frame, width=10, command=self._controller.notify_training_end)
        self.training_end_time_entry.grid(row=1, column=2, padx=2, sticky=tk.W)

        assess_frame = ttk.LabelFrame(frame, text=_text["assess_time"])
        assess_frame.grid(row=2, column=0, sticky=tk.EW)
        label = ttk.Label(assess_frame, text=_text["start"])
        label.grid(row=0, column=0, padx=2, pady=4, sticky=tk.W)
        tooltips.ToolTipYellow(label, _text["start_ass_tt"])
        label = ttk.Label(assess_frame, text=_text["end"])
        label.grid(row=1, column=0, padx=2, pady=4, sticky=tk.W)
        tooltips.ToolTipYellow(label, _text["end_ass_tt"])

        self.assess_start_date_entry = DateEntry(assess_frame, width=15, command=self._controller.notify_assess_start)
        self.assess_start_date_entry.grid(row=0, column=1, padx=2, sticky=tk.W)
        self.assess_start_time_entry = TimeEntry(assess_frame, width=10, command=self._controller.notify_assess_start)
        self.assess_start_time_entry.grid(row=0, column=2, padx=2, sticky=tk.W)

        self.assess_end_date_entry = DateEntry(assess_frame, width=15, command=self._controller.notify_assess_end)
        self.assess_end_date_entry.grid(row=1, column=1, padx=2, sticky=tk.W)
        self.assess_end_time_entry = TimeEntry(assess_frame, width=10, command=self._controller.notify_assess_end)
        self.assess_end_time_entry.grid(row=1, column=2, padx=2, sticky=tk.W)

        b = ttk.Button(frame, text=_text["reset"], command=self._controller.reset_times)
        b.grid(row=3, column=0, columnspan=1, sticky=tk.EW, padx=3, pady=3)

        self.train_count_label = ttk.Label(frame)
        self.train_count_label.grid(row=4, column=0, sticky=tk.W, padx=3, pady=2)
        self.assess_count_label = ttk.Label(frame)
        self.assess_count_label.grid(row=5, column=0, sticky=tk.W, padx=3, pady=2)

        return frame

    def _analysis_tools(self, frame):
        util.stretchy_columns(frame, [0])
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=tk.EW)
        util.stretchy_columns(button_frame, [0])
        ttk.Button(button_frame, text=_text["save"]).grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=3)
        ttk.Button(button_frame, text=_text["back"], command=self.cancel).grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=3)
        pred_frame = ttk.LabelFrame(master=frame, text=_text["preds"])
        pred_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=3)
        ttk.Label(pred_frame, text="TODO: List of prediction methods / parameters here").grid(row=0,column=0)
        # Just a place-holder...
        c = tk.Canvas(pred_frame)
        c.grid(row=1, column=0)
        c["height"] = 150
        compare_frame = ttk.LabelFrame(frame, text=_text["asses"])
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
        if tkinter.messagebox.askokcancel("Quit to main menu?",
                "Quit to the main menu?  Settings will be lost if not saved."):
            self.destroy()

    def _datetime_from(self, date, time):
        return datetime.datetime(date.year, date.month, date.day, time.hour, time.minute)

    @property
    def training_start(self):
        """Date/Time selected for the start of training data."""
        return self._datetime_from(self.training_start_date_entry.date,
            self.training_start_time_entry.time)

    @training_start.setter
    def training_start(self, dt):
        self.training_start_date_entry.date = dt
        self.training_start_time_entry.time = dt

    @property
    def training_end(self):
        """Date/Time selected for the end of training data."""
        return self._datetime_from(self.training_end_date_entry.date,
            self.training_end_time_entry.time)

    @training_end.setter
    def training_end(self, dt):
        self.training_end_date_entry.date = dt
        self.training_end_time_entry.time = dt

    @property
    def assess_start(self):
        """Date/Time selected for the start of assessment data."""
        return self._datetime_from(self.assess_start_date_entry.date,
            self.assess_start_time_entry.time)

    @assess_start.setter
    def assess_start(self, dt):
        self.assess_start_date_entry.date = dt
        self.assess_start_time_entry.time = dt

    @property
    def assess_end(self):
        """Date/Time selected for the end of assessment data."""
        return self._datetime_from(self.assess_end_date_entry.date,
            self.assess_end_time_entry.time)

    @assess_end.setter
    def assess_end(self, dt):
        self.assess_end_date_entry.date = dt
        self.assess_end_time_entry.time = dt

    def update_time_counts(self, train_count, assess_count):
        self.train_count_label["text"] = _text["train_count"].format(train_count)
        self.assess_count_label["text"] = _text["ass_count"].format(assess_count)


def _find_command(kwargs):
    if "command" in kwargs:
        kwargs = dict(kwargs)
        cmd = kwargs["command"]
        del kwargs["command"]
        return kwargs, cmd
    return kwargs, None

def _add_to_kwargs(kwargs, key, value):
    if key not in kwargs:
        kwargs = dict(kwargs)
        kwargs[key] = value
    return kwargs


class DateEntry(ttk.Entry):
    """Subclass of :class:`ttk.Entry` which opens a date picker which clicked,
    and allows keyboard entry, but validates entry to be a valid date.

    You may set a keyword argument "command" to register a callback on a change.
    """
    def __init__(self, *args, **kwargs):
        kwargs, self._cmd = _find_command(kwargs)
        kwargs = _add_to_kwargs(kwargs, "textvariable", tk.StringVar())
        super().__init__(*args, **kwargs)
        self._data_entry_txt_var = kwargs["textvariable"]
        util.DateTimeValidator(self, self._data_entry_txt_var, _text["date_format"], self._cmd)
        def sett(dt):
            self.date = dt
            self._cmd()
        date_picker.PopUpDatePicker(self.master, self, lambda : self.date, sett)

    @property
    def date(self):
        return datetime.datetime.strptime(self.get(), _text["date_format"])

    @date.setter
    def date(self, new_date):
        self._data_entry_txt_var.set(new_date.strftime(_text["date_format"]))


class TimeEntry(ttk.Entry):
    """Subclass of :class:`ttk.Entry` which validates entry to be a valid time.

    You may set a keyword argument "command" to register a callback on a change.
    """
    def __init__(self, *args, **kwargs):
        kwargs, self._cmd = _find_command(kwargs)
        kwargs = _add_to_kwargs(kwargs, "textvariable", tk.StringVar())
        super().__init__(*args, **kwargs)
        self._data_entry_txt_var = kwargs["textvariable"]
        util.DateTimeValidator(self, self._data_entry_txt_var, _text["time_format"], self._cmd)

    @property
    def time(self):
        return datetime.datetime.strptime(self.get(), _text["time_format"])

    @time.setter
    def time(self, new_time):
        self._data_entry_txt_var.set(new_time.strftime(_text["time_format"]))
