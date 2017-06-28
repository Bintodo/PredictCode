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
import open_cp.gui.tk.error_list as error_list
import open_cp.gui.resources as resources
import PIL.ImageTk as ImageTk
import PIL.Image

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
    "askquit" : "Quit to main menu?",
    "long_askquit" : "Quit to the main menu?  Settings will be lost if not saved.",
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
    "ass_count" : "Events in assessment range: {}",
    "sel_ct" : "Select crime types",
    "no_types" : "No crime types",
    "all" : "All",
    "clear" : "Clear",
    "ct_count" : "Events of selected crime type(s): {}",
    "tc" : "Selected data",
    "tcc" : "Overall training data: {}\nOverall assessment data: {}",
    "loadnew" : "Load new input file?",
    "ln_msg" : ("Loading a new input file will replace the data with new data.  " +
                "The new file must be in the same format as the current file!"),
    "ln_pick_msg" : "Select a new CSV file",
    "emsg" :  "Error messages",
    "emsg1" : "From loading saved session",
    "okay" : "Okay",
    "fail_save" : "Failed to save session.\nCause: {}/{}",
    "jsonses" : "JSON session",
    "saveses" : "Please select a session file to save to",
    "saving" :  "Saving file...",
    "loading" :  "Loading file...",
    "ctfail1" : "Crime type selection {} doesn't make sense for input file as we don't have that many selected crime type fields!",
    "ctfail2" : "Crime type selection {} doesn't make sense for input file",
    "ctfail3" : "Number of crimes types is {} which is too many!  No crime types will be considered...",
    "pi_fail1" : "Cannot find a match for a predictor named {}",
    "pi_fail2" : "Multiple matches for a predictor named {}",
    "ci_fail1" : "Cannot find a match for a comparitor named {}",
    "ci_fail2" : "Multiple matches for a comparitor named {}",
    "pickpred" : "Choose a new prediction algorithm",
    "pickcom" : "Choose a new comparator algorithm",
    "cancel" : "Cancel",
    "del_pred" : "Delete this predictor",
    "edit_pred" : "Edit this predictor",
    "add_pred" : "Add new predictor stage",
    "del_comp" : "Delete this comparitor",
    "edit_comp" : "Edit this comparitor",
    "add_comp" : "Add new comparitor stage",
    "run" : "Launch predictors",
    "runbutton" : "Run current analysis",
    "runmsg" : "Messages",
    "runmsgtt" : "Not enough predictors and comparators have been selected to allow an analysis run.  The message here suggest what needs selecting.",
    "runbuttt" : "Click to run an analysis",
    "oldrun" : "Previous analysis",
    "noproj" : "Input data is Longitude/Latitude, so you need to select a projection method.",
    "nogrid" : "Need to select a method of laying a grid over the input data",
    "nopreds" : "Need to select at least one prediction method",
    "nostrat" : "Need to select a prediction requirement in the comparators list",
    "results" : "Analysis run results",
    "r_runat" : "Run @ {} {}",
    "r_runat_tt" : "Click to view analysis results",
    "r_runatsave_tt" : "Save the analysis results to disk.",
    "r_runatsave_tt1" : "Analysis result saved as {}  Click to save again.",
    "r_load" : "Load saved run",
    "r_save" : "Please select a file to save analysis run to",
    "r_save1" : "Saved Analysis File",
    "r_save_fail" : "Failed to save analysis file because: {}/{}",
    "r_load1" : "Please select a file to load old analysis run from",
    "r_load_fail" : "Failed to load old analysis file because: {}",
    "r_remove_tt" : "Forget about this run.  If this run has been saved, it will *not* be deleted from disk.",
    
}

class AnalysisView(tk.Frame):
    def __init__(self, model, controller, root):
        super().__init__(root)
        self._model = model
        self._controller = controller
        self.grid(sticky=util.NSEW)
        self.master.protocol("WM_DELETE_WINDOW", self.cancel)
        util.centre_window_percentage(self.master, 70, 80)
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
        self._plot_widget = None
        self._plot_frame = ttk.LabelFrame(parent, text=_text["plot"])
        return self._plot_frame

    def _data_buttons(self, parent):
        frame = ttk.Frame(parent)
        util.stretchy_columns(frame, [0,1])
        ttk.Button(frame, text=_text["new_input"], command=self._new_input_file
                ).grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=2)
        ttk.Button(frame, text=_text["with_basemap"]).grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=2)
        return frame

    def _new_input_file(self):
        if tkinter.messagebox.askokcancel(_text["loadnew"], _text["ln_msg"], default=tkinter.messagebox.CANCEL):
            filename = util.ask_open_filename(defaultextension=".csv",
                filetypes=[("CSV", "*.csv")], title=_text["ln_pick_msg"])
            if filename is not None:
                self._controller.new_input_file(filename)

    def _format_time_range(self):
        start, end = self._model.time_range_of_data
        fmt = "%Y-%m-%d %H:%M:%S"
        return _text["timerange"] + start.strftime(fmt) + "\n\t" + _text["timerange1"] + end.strftime(fmt)

    def _time_range_select(self, parent):
        frame = ttk.LabelFrame(parent, text=_text["time_select"])
        frame.grid(sticky=tk.NSEW)
        ttk.Label(frame, text=self._format_time_range()).grid(row=0, column=0, padx=3, pady=1, sticky=tk.W)

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

    def update_comparitors_list(self):
        row = self._update_list(self._comparison_frame,
            self._model.comparison_model.objects,
            [_text["del_comp"], _text["edit_comp"], _text["add_comp"]],
            self._controller.comparison_controller )

    def update_predictors_list(self):
        row = self._update_list(self._prediction_frame,
            self._model.analysis_tools_model.objects,
            [_text["del_pred"], _text["edit_pred"], _text["add_pred"]],
            self._controller.tools_controller )

    def _update_list(self, outer_frame, source, texts, controller):
        for w in outer_frame.winfo_children():
            w.destroy()
        
        row = 0
        for index, pred in enumerate(source):
            frame = tk.Frame(outer_frame)
            frame.grid(sticky=tk.NSEW, padx=2, pady=2, row=row, column=0)
            row += 1
            ttk.Label(frame, text=pred.name).grid(row=0, column=0, padx=2, pady=1)
            if pred.settings_string is not None:
                ttk.Label(frame, text=pred.settings_string).grid(row=1, column=0, padx=2, pady=1)

            cmd = lambda i=index : controller.remove(i)
            b = ttk.Button(frame, image=self._close_icon, command=cmd)
            b.grid(row=0, column=1)
            tooltips.ToolTipYellow(b, texts[0])
            cmd = lambda i=index : controller.edit(i)
            b = ttk.Button(frame, image=self._edit_icon, command=cmd)
            b.grid(row=0, column=2)
            tooltips.ToolTipYellow(b, texts[1])

            ttk.Separator(outer_frame).grid(sticky=tk.NSEW, padx=2, pady=1, row=row, column=0)
            row += 1

        ttk.Button(outer_frame, text=texts[2],command=controller.add).grid(
                sticky=tk.NSEW, row=row, padx=5, pady=2)

    def _analysis_tools(self, frame):
        util.stretchy_columns(frame, [0])
        util.stretchy_rows(frame, [1,2])
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, sticky=tk.EW)
        util.stretchy_columns(button_frame, [0])
        ttk.Button(button_frame, text=_text["save"], command=self._save).grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=3)
        ttk.Button(button_frame, text=_text["back"], command=self.cancel).grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=3)

        pred_frame = ttk.LabelFrame(frame, text=_text["preds"])
        pred_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=3)
        util.stretchy_rows_cols(pred_frame, [0], [0])
        f = util.ScrolledFrame(pred_frame)
        f.grid(sticky=tk.NSEW)
        self._prediction_frame = f.frame
        self.update_predictors_list()

        compare_frame = ttk.LabelFrame(frame, text=_text["asses"])
        compare_frame.grid(row=2, column=0, sticky=tk.NSEW, padx=5, pady=3)
        util.stretchy_rows_cols(compare_frame, [0], [0])
        f = util.ScrolledFrame(compare_frame)
        f.grid(sticky=tk.NSEW)
        self._comparison_frame = f.frame
        self.update_comparitors_list()

    def _crime_types_all(self):
        box = self._crime_type_box
        box.current_selection = range(box.size)

    def _crime_types_none(self):
        box = self._crime_type_box
        box.current_selection = []

    def _crime_type_select(self, parent):
        frame = ttk.LabelFrame(parent, text=_text["sel_ct"])
        if self._model.num_crime_type_levels == 0:
            self._crime_type_box = None
            ttk.Label(frame, text=_text["no_types"]).grid()
        else:
            self._crime_type_box = util.ListBox(frame, width=50, height=6,
                    command=self._controller.notify_crime_type_selection)
            self._crime_type_box.add_rows( " / ".join(tup) for tup in self._model.unique_crime_types )
            self._crime_type_box.grid(row=0, column=0, padx=2, pady=2, sticky=tk.NSEW)
            sub_frame = ttk.Frame(frame)
            sub_frame.grid(row=0, column=1, padx=2, pady=2, sticky=tk.NSEW)
            b = ttk.Button(sub_frame, text=_text["all"], command=self._crime_types_all)
            b.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
            b = ttk.Button(sub_frame, text=_text["clear"], command=self._crime_types_none)
            b.grid(row=1, column=0, padx=3, pady=3, sticky=tk.EW)
            self._crime_type_count_label = ttk.Label(sub_frame, wraplength=150)
            self._crime_type_count_label.grid(row=2, column=0, columnspan=2, padx=3, pady=3, sticky=tk.W)
        return frame

    def _total_counts(self, parent):
        frame = ttk.LabelFrame(parent, text=_text["tc"])
        self._total_count_label = ttk.Label(frame)
        self._total_count_label.grid()
        return frame

    def _run_panel(self, parent):
        frame = ttk.Frame(parent)
        self._run_frame = ttk.LabelFrame(frame, text=_text["run"])
        self._run_frame.grid(row=0, column=0, padx=1, pady=1, sticky=tk.NSEW)
        self._result_frame = ttk.LabelFrame(frame, text=_text["results"])
        self._result_frame.grid(row=0, column=1, padx=1, pady=1, sticky=tk.NSEW)
        self.update_run_analysis_results()
        return frame

    @staticmethod
    def _remove_children(widget):
        for w in widget.winfo_children():
            w.destroy()

    def update_run_analysis_results(self):
        self._remove_children(self._result_frame)
        row = 0
        for row, result in enumerate(self._model.analysis_runs):
            frame = ttk.Frame(self._result_frame)
            frame.grid(row=row, column=0, sticky=tk.NSEW)
            button = ttk.Button(frame,
                text = _text["r_runat"].format(
                    result.run_time.strftime(_text["date_format"]),
                    result.run_time.strftime(_text["time_format"]) ),
                command = lambda r=row : self._view_run(r) )
            button.grid(row=0, column=0, padx=1, pady=1, sticky=tk.NSEW)
            tooltips.ToolTipYellow(button, _text["r_runat_tt"])
            save_button = ttk.Button(frame, command = lambda r=row : self._save_run(r) )
            save_button.grid(row=0, column=1, padx=1, pady=1, sticky=tk.NSEW)
            remove_button = ttk.Button(frame, image=self._close_icon, command = lambda r=row : self._remove_run(r) )
            remove_button.grid(row=0, column=2, padx=1, pady=1, sticky=tk.NSEW)
            tooltips.ToolTipYellow(remove_button, _text["r_remove_tt"])
            filename = self._model.analysis_run_filename(row)
            if filename is not None:
                save_button["image"] = self._success_icon
                tooltips.ToolTipYellow(save_button, _text["r_runatsave_tt1"].format(filename))
            else:
                save_button["image"] = self._save_icon
                tooltips.ToolTipYellow(save_button, _text["r_runatsave_tt"])
        ttk.Button(self._result_frame, text=_text["r_load"],
            command=self._load_saved_run).grid(
            row=row + 1, column=0, padx=1, pady=1, sticky=tk.NSEW)

    def _remove_run(self, run):
        self._controller.remove_past_run(run)

    def _view_run(self, run):
        self._controller.view_past_run(run)

    def _save_run(self, run):
        filename = util.ask_save_filename(filetypes = [(_text["r_save1"], "*.pic.xz")],
            title=_text["r_save"],
            defaultextension=".pic.xz")
        if filename is not None:
            self._controller.save_run(run, filename)

    def _load_saved_run(self):
        filename = util.ask_open_filename(filetypes = [(_text["r_save1"], "*.pic.xz")],
            title=_text["r_load1"],
            defaultextension=".pic.xz")
        if filename is not None:
            self._controller.load_saved_run(filename)

    def set_run_messages(self, messages):
        """Set a list of messages giving prerequisits for launching a run, or
        is none, then a run button
        
        :param messages: List of messages; none indicates that a run can start.
        """
        self._remove_children(self._run_frame)
        if len(messages) == 0:
            button = ttk.Button(self._run_frame, text=_text["runbutton"], command=self._run)
            button.grid(sticky=tk.NSEW, row=0, column=0)
            tooltips.ToolTipYellow(button, _text["runbuttt"])
        else:
            labelframe = ttk.LabelFrame(self._run_frame, text=_text["runmsg"])
            labelframe.grid(sticky=tk.NSEW, row=0, column=0)
            for r, text in enumerate(messages):
                ttk.Label(labelframe, text=text).grid(row=r, column=0, padx=1, pady=1, sticky=tk.W)
            tooltips.ToolTipYellow(labelframe, _text["runmsgtt"])
        
    def set_previous_analysis(self):
        labelframe = ttk.LabelFrame(self._run_frame, text=_text["oldrun"])
        labelframe.grid(sticky=tk.NSEW, row=0, column=1)
        
    def _run(self):
        """Launch the analysis."""
        self._controller.run_analysis()

    def _save(self):
        filename = util.ask_save_filename(filetypes = [(_text["jsonses"], "*.json")],
            title=_text["saveses"],
            defaultextension=".json")
        if filename is not None:
            self._controller.save(filename)

    def alert(self, message):
        tkinter.messagebox.showerror("Error", message)

    def _load_resources(self):
        self._close_icon = ImageTk.PhotoImage(resources.close_icon)
        self._edit_icon = ImageTk.PhotoImage(resources.edit_icon)
        self._save_icon = ImageTk.PhotoImage(resources.save_icon)
        self._success_icon = ImageTk.PhotoImage(resources.success_icon)
        self._saved_icon = ImageTk.PhotoImage(PIL.Image.alpha_composite(
                resources.save_icon, resources.success_icon))

    def add_widgets(self):
        self._load_resources()
        # TODO: Maybe make column 1 fixed size??
        #self.columnconfigure(0, weight=2)
        #self.columnconfigure(1, weight=10)
        util.stretchy_rows(self, [0])
        
        frame = ttk.LabelFrame(self, text=_text["data"])
        frame.grid(row=0, column=0, sticky=util.NSEW, padx=3, pady=3)
        sub_frame = ttk.Frame(frame)
        sub_frame.grid(row=0, column=0, sticky=tk.N + tk.EW)
        self._info_frame(sub_frame).grid(row=0, column=0)
        self._data_buttons(sub_frame).grid(row=1, column=0)
        sub_frame = ttk.Frame(frame)
        sub_frame.grid(row=1, column=0, sticky=tk.N + tk.EW)
        self._plot_frame(sub_frame).grid(row=0, column=0, sticky=tk.NSEW, padx=1)
        self._time_range_select(sub_frame).grid(row=0, column=1, sticky=tk.NSEW, padx=1)
        self._crime_type_select(frame).grid(row=2, column=0, sticky=tk.NSEW, padx=1)
        self._total_counts(frame).grid(row=3, column=0, sticky=tk.NSEW, padx=1)
        self._run_panel(frame).grid(row=4, column=0, sticky=tk.NSEW, padx=1)

        frame = ttk.LabelFrame(self, text=_text["tasks"])
        frame.grid(row=0, column=1, sticky=util.NSEW, padx=3, pady=3)
        self._analysis_tools(frame)

    def cancel(self):
        if self._model.session_changed():
            self.destroy()
        else:
            if tkinter.messagebox.askokcancel(_text["askquit"], _text["long_askquit"]):
                self.destroy()

    def refresh_plot(self):
        if self._plot_widget is None:
            self._plot_widget = mtp.CanvasFigure(self._plot_frame, width=250)
            self._plot_widget.grid(sticky=tk.NSEW, padx=2, pady=2)
        def draw():
            fig = mtp.new_figure()
            ax = fig.add_subplot(1,1,1)
            ax.scatter(self._model.xcoords, self._model.ycoords, marker="+", color="black", alpha=0.2)
            fig.set_size_inches(3, 3)
            fig.set_tight_layout(True)
            return fig
        self._plot_widget.set_figure_task(draw)

    def _datetime_from(self, date, time):
        return datetime.datetime(date.year, date.month, date.day, time.hour, time.minute)

    def new_model(self, model):
        self._model = model

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
    
    @property
    def crime_type_selections(self):
        if self._crime_type_box is None:
            return []
        return self._crime_type_box.current_selection

    @crime_type_selections.setter
    def crime_type_selections(self, selections):
        if self._crime_type_box is None:
            raise ValueError()
        self._crime_type_box.current_selection = selections

    def update_time_counts(self, train_count, assess_count):
        self.train_count_label["text"] = _text["train_count"].format(train_count)
        self.assess_count_label["text"] = _text["ass_count"].format(assess_count)

    def update_crime_type_count(self, count):
        self._crime_type_count_label["text"] = _text["ct_count"].format(count)

    def update_total_count(self, train_count, assess_count):
        self._total_count_label["text"] = _text["tcc"].format(train_count, assess_count)

    def show_errors(self, errors):
        el = error_list.ErrorList(self, _text["emsg"], _text["emsg1"], errors, [_text["okay"]])
        el.run()


## Pick Predictions / Comparitors ########################################

class _PickView(util.ModalWindow):
    """Display a modal dialog to choose from an ordered list."""
    def __init__(self, parent, model, controller, title):
        self._model = model
        self._controller = controller
        super().__init__(parent, title)

    def add_widgets(self):
        frame = util.ScrolledFrame(self, mode="v")
        frame.grid(sticky=tk.NSEW)
        frame = frame.frame

        last_order = None
        for index, (name, order) in enumerate(zip(self._model.names(), self._model.orders())):
            if last_order is not None and order != last_order:
                ttk.Separator(frame).grid(sticky=tk.NSEW, pady=3, padx=3)
            last_order = order
            b = ttk.Button(frame, text=name, command=lambda i=index: self._controller.selected(i))
            b.grid(sticky=tk.NSEW, padx=3, pady=3)

        ttk.Separator(frame).grid(sticky=tk.NSEW,pady=5)
        ttk.Button(frame, text=_text["cancel"], command=self.cancel).grid(sticky=tk.NSEW, padx=10, pady=3)

        self.set_to_actual_width()
    

class _EditView(util.ModalWindow):
    def __init__(self, parent, title, resize):
        super().__init__(parent, title, resize=resize)
        self.result = False
    
    def run(self, view):
        util.stretchy_rows_cols(self, [0], [0])
        view.grid(sticky=tk.NSEW, row=0, column=0)
        self.set_to_actual_size()
        self.wait_window(self)

    def add_widgets(self):
        ttk.Separator(self).grid(row=1, column=0, sticky=tk.EW, padx=2, pady=2)
        frame = tk.Frame(self)
        frame.grid(row=2, column=0, sticky=tk.NSEW)
        util.stretchy_columns(frame, [0,1])
        b = ttk.Button(frame, text=_text["okay"], command=self.okay)
        b.grid(row=0, column=0, sticky=tk.EW, padx=5, pady=3)
        b = ttk.Button(frame, text=_text["cancel"], command=self.cancel)
        b.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=3)

    def okay(self):
        self.result = True
        self.cancel()


class PickPredictionView(_PickView):
    def __init__(self, parent, model, controller, ):
        super().__init__(parent, model, controller, _text["pickpred"])


class PredictionEditView(_EditView):
    def __init__(self, parent, title, resize=None):
        super().__init__(parent, title, resize)


class PickComparatorView(_PickView):
    def __init__(self, parent, model, controller, ):
        super().__init__(parent, model, controller, _text["pickcom"])
    

## Utility methods / classes #############################################

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


class Saving(util.ModalWindow):
    """Static "saving..." window"""
    def __init__(self, parent, loading=False):
        title = _text["saving"]
        if loading:
            title = _text["loading"]
        super().__init__(parent, title=title)
        
    def add_widgets(self):
        self.set_size_percentage(30,10)
        util.stretchy_rows_cols(self, [0], [0])
        bar = ttk.Progressbar(self, mode="indeterminate")
        bar.grid(sticky=tk.EW, padx=5)
        bar.start()
