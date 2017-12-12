"""
analysis.py
~~~~~~~~~~~

Various routines to perform standard analysis, and/or visualisation, tasks.
"""

import matplotlib.pyplot as _plt
import matplotlib.collections as _mpl_collections
import descartes as _descartes
import csv as _csv
import collections as _collections
import scipy.stats as _stats
import open_cp.plot as _plot
import numpy as _np

def _add_outline(loaded, ax):
    p = _descartes.PolygonPatch(loaded.geometry, fc="none", ec="black")
    ax.add_patch(p)
    ax.set_aspect(1)

def plot_prediction(loaded, prediction, ax):
    """Visualise a single prediction.

    :param loaded: Instance of :class:`Loader`
    :param prediction: The prediction to plot
    :param ax: `matplotlib` Axis object to draw to.
    """
    _add_outline(loaded, ax)
    m = ax.pcolor(*prediction.mesh_data(), prediction.intensity_matrix, cmap="Greys")
    _plt.colorbar(m, ax=ax)

def _set_standard_limits(loaded, ax):
    xmin, ymin, xmax, ymax = loaded.geometry.bounds
    d = max(xmax - xmin, ymax - ymin) / 20
    ax.set(xlim=[xmin-d, xmax+d], ylim=[ymin-d, ymax+d])

def plot_data_scatter(loaded, ax):
    """Produce a scatter plot of the input data.
    
    :param loaded: Instance of :class:`Loader`
    :param ax: `matplotlib` Axis object to draw to.
    """
    _add_outline(loaded, ax)
    ax.scatter(*loaded.timed_points.coords, marker="x", linewidth=1, color="black", alpha=0.5)
    _set_standard_limits(loaded, ax)

def plot_data_grid(loaded, ax):
    """Produce a plot of masked grid we used.
    
    :param loaded: Instance of :class:`Loader`
    :param ax: `matplotlib` Axis object to draw to.
    """
    _add_outline(loaded, ax)
    pc = _mpl_collections.PatchCollection(_plot.patches_from_grid(loaded.grid),
        facecolors="none", edgecolors="black")
    ax.add_collection(pc)
    _set_standard_limits(loaded, ax)

def _open_text_file(filename):
    need_close = False
    if isinstance(filename, str):
        file = open(filename, "rt", newline="")
        need_close = True
    else:
        file = filename
    try:
        yield file
    finally:
        if need_close:
            file.close()


def hit_counts_to_beta(csv_file):
    """Using the data from the csv_file, return the beta distributed posterior
    given the hit count data.  This gives an indication of the "hit rate" and
    its variance.

    :param csv_file: Filename to load, or file-like object

    :return: Dictionary from prediction name to dictionary from coverage level
      to a :class:`scipy.stats.beta` instance.
    """
    for file in _open_text_file(csv_file):
        reader = _csv.reader(file)
        header = next(reader)
        if header[:4] != ["Predictor", "Start time", "End time" ,"Number events"]:
            raise ValueError("Input file is not from `HitCountSave`")
        coverages = [int(x[:-1]) for x in header[4:]]

        counts = _collections.defaultdict(int)
        hits = _collections.defaultdict(lambda : _collections.defaultdict(int))
        for row in reader:
            name = row[0]
            counts[name] += int(row[3])
            for cov, value in zip(coverages, row[4:]):
                hits[name][cov] += int(value)

        betas = {name : dict() for name in counts}
        for name in counts:
            for cov in coverages:
                a = hits[name][cov]
                b = counts[name] - a
                betas[name][cov] = _stats.beta(a, b)

        return betas

def plot_betas(betas, ax, coverages=None):
    """Plot hit rate curves using the data from :func:`hit_counts_to_beta`.
    Plots the median and +/-34% (roughly a +/- 1 standard deviation) of the
    posterior estimate of the hit-rate probability.

    :param betas: Dict as from :func:`hit_counts_to_beta`.
    :param ax: `matplotlib` Axis object to draw to.
    :param coverages: If not `None`, plot only these coverages.
    """
    if coverages is not None:
        coverages = list(coverages)
    for name, data in betas.items():
        if coverages is None:
            x = _np.sort(list(data))
        else:
            x = _np.sort(coverages)
        y = [data[xx].ppf(0.5) for xx in x]
        ax.plot(x,y,label=name)
        y1 = [data[xx].ppf(0.5 - 0.34) for xx in x]
        y2 = [data[xx].ppf(0.5 + 0.34) for xx in x]
        ax.fill_between(x,y1,y2,alpha=0.5)
    ax.legend()
    ax.set(xlabel="Coverage (%)", ylabel="Hit rate (probability)")

