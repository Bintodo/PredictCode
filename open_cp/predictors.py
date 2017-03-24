import abc
import math
import numpy as _np

def _round(x):
    return math.floor(x + 0.5)

def _floor(x):
    return int(math.floor(x))


class Predictor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def predict(self, cutoff_time, predict_time):
        pass


class Prediction(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def risk(self, x, y):
        pass

    @abc.abstractclassmethod
    def grid_risk(self, gx, gy):
        pass


class GridPrediction(Prediction):
    """A `Prediction` based on a grid of fixed `xsize` and `ysize`.
    The risk is always computed by finding the grid cell the coordinates
    contained, and then deferring to the abstract `grid_risk` method."""
    
    def __init__(self, xsize, ysize, xoffset = 0, yoffset = 0):
        self.xsize = xsize
        self.ysize = ysize
        self._xoffset = xoffset
        self._yoffset = yoffset
    
    def risk(self, x, y):
        xx = x - self._xoffset
        yy = y - self._yoffset
        return self.grid_risk(_floor(xx / self.xsize), _floor(yy / self.ysize))


class ContinuousPrediction(Prediction):
    def grid_risk(self, gx, gy):
        raise TypeError("Grid sampling not supported")


class GridPredictionArray(GridPrediction):
    def __init__(self, xsize, ysize, matrix, xoffset = 0, yoffset = 0):
        super().__init__(xsize, ysize, xoffset, yoffset)
        self._matrix = matrix

    def grid_risk(self, gx, gy):
        ylim, xlim = self._matrix.shape
        if gx < 0 or gy < 0 or gx >= xlim or gy >= ylim:
            return 0
        return self._matrix[gy][gx]

    @property
    def intensity_matrix(self):
        return self._matrix

    def mesh_data(self):
        """Returns a pair (xcoords, ycoords) which, when paired with
        `intensity_matrix`, is suitable for passing to matplotlib.pcolor or
        pcolormesh.  That is, intensity_matrix[i][j] is the risk intensity in
        the rectangular cell with diagonally opposite vertices
        (xcoords[j], ycoords[i]), (xcoords[j+1], ycoords[i+1])."""
        
        xcoords = _np.arange(self._matrix.shape[1] + 1) * self.xsize + self._xoffset
        ycoords = _np.arange(self._matrix.shape[0] + 1) * self.ysize + self._yoffset
        return (xcoords, ycoords)
    
    def percentile_matrix(self):
        """Returns a matrix of the same shape as `intensity_matrix` but with
        float values giving the percentile of risk, normalised to [0,1].  So
        the cell with the highest risk is assigned 1.0.  Ties are rounded up,
        so if three cells share the highest risk, they are all assigned 1.0."""
        
        data = self._matrix.ravel().copy()
        data.sort()
        return _np.searchsorted(data, self._matrix, side="right") / len(data)

def sample_to_grid(kernel, cell_width, cell_height, width, height, xoffset=0, yoffset=0, samples=50):
    """Stuff

    kernel : Assumed signature array -> array where input array is of shape (2, #points) and
    output array is of shape (#points)
    """

    matrix = _np.empty((height, width))
    for x in range(width):
        for y in range(height):
            xx = (x + _np.random.random(samples)) * cell_width + xoffset
            yy = (y + _np.random.random(samples)) * cell_height + yoffset
            matrix[y][x] = _np.mean(kernel(_np.stack([xx,yy], axis=0)))
    return GridPredictionArray(cell_width, cell_height, matrix, xoffset, yoffset)
