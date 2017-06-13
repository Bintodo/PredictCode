"""
predictor
~~~~~~~~~

Base classes and utility methods for the GUI side of describing algorithms
which produce predictions.
"""

import inspect as _inspect

class Task():
    """Abstract base class for a computational task which needs to be carried
    out to make a prediction.

    May either be run in this process (e.g. generating a grid) or run off
    process to enable parallelisation.
    
    :param ordering: Higher means run later.  Once all tasks have been
      produced, those with the lowest ordering will run first.
    :param allow_off_process: If true, then run in a separate process in
      parallel.  Default is False, with is optimal for quick tasks.
    """
    def __init__(self, ordering, allow_off_process=False):
        self._ordering = ordering
        self._off_process = allow_off_process

    @property
    def off_process(self):
        """Should we run as a separate process?"""
        return self._off_process

    @property
    def order(self):
        return self._ordering

    def __call__(self):
        raise NotImplementedError()


_TYPE_PREDICTOR = 100

class Predictor():
    """Abstract base class which all prediction methods derive from.
    The actual mechanics of making a prediction should be in the main `open_cp`
    package.  Here we are concerned with GUI issues.

    A predictor may depend upon other predictors (e.g. the user need only
    provide a single algorithm to generate a grid, and all grid-based
    predictors can use it.  The :attr:`name` is used to find suitable partners.
    """
    def __init__(self):
        # Should always be a no-arg constructor
        pass

    @staticmethod
    def describe():
        """Return human readable short description of this predictor."""

    @staticmethod
    def make_view(parent):
        """Construct and return a view object.  This object is the model, and
        the controller may either be another object constructed here, or the
        model."""
        raise NotImplementedError()

    @staticmethod
    def order():
        """An ordinal specifying the order, lowest is "first".  E.g. the generator
        of a grid would be before an actual predictor."""
        raise NotImplementedError()

    @property
    def name(self):
        """Human readable giving the prediction method and perhaps headline
        settings."""
        raise NotImplementedError()

    @property
    def settings_string(self):
        """Human readable giving further settings.  May be `None`."""
        raise NotImplementedError()
    

    def make_tasks(self):
        raise NotImplementedError()


class FindPredictors():
    def __init__(self, start):
        self._predictors = set()
        self._checked = set()
        self._scan_module(start)
        if Predictor in self._predictors:
            self._predictors.remove(Predictor)
        delattr(self, "_checked")
        
    @property
    def predictors(self):
        """Set of classes which (properly) extend predictor.Predictor"""
        return self._predictors
        
    def _scan_module(self, mod):
        if mod in self._checked:
            return
        self._checked.add(mod)
        for name, value in _inspect.getmembers(mod):
            if not name.startswith("_"):
                if _inspect.isclass(value):
                    self._scan_class(value)
                elif _inspect.ismodule(value):
                    self._scan_module(value)
                    
    def _scan_class(self, cla):
        if Predictor in _inspect.getmro(cla):
            self._predictors.add(cla)