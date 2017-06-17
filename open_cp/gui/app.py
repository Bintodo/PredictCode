"""
app
~~~

The main application for when running in GUI mode.
"""

import logging
import sys
import os

from open_cp.gui import main_window

from open_cp.gui.tk import main_window_view
from open_cp.gui import locator

def start_logging():
    logger = logging.getLogger("open_cp")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.__stdout__)
    fmt = logging.Formatter("{asctime} {levelname} {name} - {message}", style="{")
    ch.setFormatter(fmt)
    logger.addHandler(ch)

def run():
    start_logging()

    if "win" in sys.platform:
        import ctypes
        myappid = "PredictCode.OpenCP"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    else:
        self._logger.warn("Unexpected flatform: %s.  So visuals might be wrong", sys.platform)


    root = main_window_view.TopWindow()
    locator._make_pool(root)

    #import open_cp.gui.predictors.grid as pred
    #pred.test(root)
    #return

    mw = main_window.MainWindow(root)
    # Quick start jump to analysis...    
    #mw.view.after(50, mw.load_session(os.path.join("..", "Open data sets", "session.json")))
    mw.run()

    # Don't wait for threads...
    os._exit(0)