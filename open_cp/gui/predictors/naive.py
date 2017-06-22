"""
naive
~~~~~

Very simple-minded prediction techniques.  For testing and benchmarking.
"""

from . import predictor
import open_cp.naive
import tkinter as tk
import tkinter.ttk as ttk
import open_cp.gui.tk.util as util
import open_cp.gui.tk.richtext as richtext

_text = {
    "cg_main" : ("Counting Grid Predictor.\n\n"
            + "All events previous to the prediction time are considered, and for each grid cell, a simple count is made of the events falling in that cell.  This is used to create a 'relative' risk for the cell.\n\n"
            + "There is likely to be a strong dependence on the exact alignment of the grid cells.  Small grid cells are likely to perform badly.  This is a very simple predictor mainly designed for testing.\n\n"
            + "Training Data usage: For each prediction point, all event from the start of the training data range until the prediction point are used.  The 'end' of the training data range is ignored."
            ),
    "kde_main" : ("Scipy Kernel Density Estimator naive predictor.\n\n"
            + "All events previous to the prediction time are considered, and the locations are passed to the `scipy` Gaussian Kernel Density Estimator method, using default settings.  This produces a continuously"
            + "varying 'risk' which is conformed to the grid in the usual way (using random samples to approximately find the average risk across each grid cell).\n\n"
            + "This is a simple predictor mainly designed for testing.\n\n"
            + "Training Data usage: For each prediction point, all event from the start of the training data range until the prediction point are used.  The 'end' of the training data range is ignored."
            ),
}

class CountingGrid(predictor.Predictor):
    def __init__(self, model):
        super().__init__(model)
        pass
    
    @staticmethod
    def describe():
        return "Counting Grid naive predictor"

    @staticmethod
    def order():
        return predictor._TYPE_GRID_PREDICTOR

    def make_view(self, parent):
        return CountingGridView(parent)

    @property
    def name(self):
        return "Counting Grid naive predictor"
        
    @property
    def settings_string(self):
        return None
        
    def to_dict(self):
        return {}
    
    def from_dict(self, data):
        pass
    
    def make_tasks(self):
        return [self.Task()]
        
    class Task(predictor.GridPredictorTask):
        def __call__(self, analysis_model, grid_task, project_task):
            timed_points = self.projected_data(analysis_model, project_task)
            training_start, _, _, _ = analysis_model.time_range
            timed_points = timed_points[timed_points.timestamps >= training_start]
            grid = grid_task(timed_points)
            return CountingGrid.SubTask(timed_points, grid)

    class SubTask(predictor.SingleGridPredictor):
        def __init__(self, timed_points, grid):
            self._timed_points = timed_points
            self.predictor = open_cp.naive.CountingGridKernel(grid.xsize,
                grid.ysize, grid.region())

        def __call__(self, predict_time, length):
            mask = self._timed_points.timestamps < predict_time
            self.predictor.data = self._timed_points[mask]
            return self.predictor.predict()


class CountingGridView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        util.stretchy_rows_cols(self, [0], [0])
        self._text = richtext.RichText(self, height=12, scroll="v")
        self._text.grid(sticky=tk.NSEW)
        self._text.add_text(_text["cg_main"])




class ScipyKDE(predictor.Predictor):
    def __init__(self, model):
        super().__init__(model)
    
    @staticmethod
    def describe():
        return "Scipy Kernel Density Estimator naive predictor"

    @staticmethod
    def order():
        return predictor._TYPE_GRID_PREDICTOR

    @property
    def name(self):
        return "Scipy Kernel Density Estimator naive predictor"
        
    @property
    def settings_string(self):
        return None
        
    def make_view(self, parent):
        return ScipyKDEView(parent)

    def to_dict(self):
        return {}
    
    def from_dict(self, data):
        pass

    def make_tasks(self):
        raise NotImplementedError()
        
        
class ScipyKDEView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        util.stretchy_rows_cols(self, [0], [0])
        self._text = richtext.RichText(self, height=12, scroll="v")
        self._text.grid(sticky=tk.NSEW)
        self._text.add_text(_text["kde_main"])
    