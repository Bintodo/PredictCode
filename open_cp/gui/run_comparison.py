"""
run_comparison
~~~~~~~~~~~~~~

Run the comparisons on an existing set of results.

Currently this is multi-stage:
    
1. Run any "adjustments" on the raw predictions.  For example, clamping them
  to known geometries.
2. ???

"""

from . import run_analysis
import open_cp.gui.tk.run_analysis_view as run_analysis_view
import open_cp.gui.predictors as predictors
from open_cp.gui.common import CoordType
import open_cp.gui.locator as locator
import collections
import logging



class RunComparison():
    """Controller for performing the computational tasks of actually comparing
    predictions.  Compare with :class:`RunAnalysis`.

    :param parent: Parent `tk` widget
    :param controller: The :class:`analyis.Analysis` model.
    :param result: An :class:`PredictionResult` instance giving the prediction
      to run comparisons on.
    """
    def __init__(self, parent, controller, result):
        self.view = run_analysis_view.RunAnalysisView(parent, self, run_analysis_view._text["title2"])
        self.controller = controller
        self.result = result
        self._msg_logger = predictors.get_logger()
        self._logger = logging.getLogger(__name__)

    @property
    def main_model(self):
        """The :class:`analysis.Model` instance"""
        return self.controller.model

    def run(self):
        try:
            self._model = RunComparisonModel(self, self.main_model)
            self._stage1()
        except:
            self._msg_logger.exception(run_analysis_view._text["genfail1"])
            self._logger.exception(run_analysis_view._text["genfail1"])
            self.view.done()
        self.view.wait_window(self.view)

    @staticmethod
    def _chain_dict(dictionary):
        for name, li in dictionary.items():
            for x in li:
                yield (name, x)

    def _stage1(self):
        """Run any "adjustments" necessary."""
        tasks = list(self._chain_dict(self._model.adjust_tasks))
        task = lambda : self._run_adjust_tasks(tasks)
        locator.get("pool").submit(task, self._finished)

    def to_msg_logger(self, msg, *args, level=logging.DEBUG):
        locator.get("pool").submit_gui_task(lambda : 
            self._msg_logger.log(level, msg, *args))


    def _run_adjust_tasks(self, tasks):
        projection_keys = set(pred.key.projection for pred in self.result.results)
        projection_lookup = {key : self._model.get_projector(key)
            for key in projection_keys}
        for key, proj in projection_lookup.items():
            if proj is None:
                self.to_msg_logger("Failed to find current coordinate projector for '%s'",
                    key, level=logging.WARNING)

        preds_by_projection = dict()
        for pred in self.result.results:
            if pred.key.projection not in preds_by_projection:
                preds_by_projection[key] = list()
            preds_by_projection[key].append(pred)

        out = []
        for adjust_name, task in tasks:
            for key, proj in projection_lookup.items():
                self.to_msg_logger(run_analysis_view._text["log14"], adjust_name,
                    key, level=logging.INFO)
                preds = preds_by_projection[key]
                new_preds = task(proj, [p.prediction for p in preds])
                for p, new_pred in zip(preds, new_preds):
                    result = run_analysis.PredictionResult(p, new_pred)
                    out.append((adjust_name, result))
        self.to_msg_logger("Done...")
        return out

    def _finished(self, out=None):
        self.view.done()
        # TODO...

    def cancel(self):
        """Called when we wish to cancel the running tasks"""
        self._logger.warning("Comparison run being cancelled.")
        self._msg_logger.warning(run_analysis_view._text["log10"])
        if hasattr(self, "_off_thread"):
            self._off_thread.cancel()


class RunComparisonModel():
    """The model for running an analysis.  Constructs dicts:
      - :attr:`adjust_tasks` Tasks which "adjust" predictions in some way (e.g.
        restrict to some geometry).
    
    :param controller: :class:`RunComparison` instance
    :param view: :class:`RunAnalysisView` instance
    :param main_model: :class:`analysis.Model` instance
    """
    def __init__(self, controller, main_model):
        self.controller = controller
        self.main_model = main_model
        self._msg_logger = predictors.get_logger()

        self._run_analysis_model = run_analysis.RunAnalysisModel(self, main_model)
        self._build_adjusts()

    def notify_model_message(*args, **kwargs):
        # Ignore as don't want to log from analysis model
        pass

    def _build_adjusts(self):
        self._adjust_tasks = dict()
        for adjust in self.comparators.comparators_of_type(predictors.comparitor.TYPE_ADJUST):
            self._adjust_tasks[adjust.pprint()] = adjust.make_tasks()

    def get_projector(self, key_string):
        """Try to find a projector task given the "name" string.
        
        :return: `None` is not found, or a callable object which performs the
          projection.
        """
        if key_string in self._run_analysis_model.projectors:
            return self._run_analysis_model.projectors[key_string][0]
        return None

    @property
    def comparators(self):
        return self.main_model.comparison_model
    
    @property
    def predictors(self):
        return self.main_model.analysis_tools_model

    @property
    def adjust_tasks(self):
        """A dictionary from `name` to list of :class:`comparitor.AdjustTask`
        instances."""
        return self._adjust_tasks


class TaskKey():
    """Describes the comparison task which was run.  We don't make any
    assumptions about the components of the key (they are currently strings,
    but in future may be richer objects) and don't implement custom hashing
    or equality.
    
    :param adjust: The "adjustment" which was made.
    """
    def __init__(self, adjust):
        self._adjust = adjust
        
    @property
    def adjust(self):
        """The adjustment which was run, or empty-string."""
        if self._adjust is None:
            return ""
        return self._adjust
    
    def __repr__(self):
        return "adjust: {}".format(self.adjust)


class _AdjustTask():
    def __init__(self):
        pass
    
    @property
    def off_thread(self):
        return True
    
    @property
    def key(self):
        pass
        

class _RunnerThreadOne(run_analysis.BaseRunner):
    def __init__(self, tasks, controller):
        super().__init__(controller)
        self._tasks = list(tasks)

    def make_tasks(self):
        return [self.RunPredTask(t.key, t) for t in self._tasks]
