"""
util
~~~~

Various utility routines for working with `tkinter`.
"""

import tkinter as tk
import tkinter.font as tkfont
import tkinter.filedialog
import datetime as _datetime

NSEW = tk.N + tk.S + tk.E + tk.W

def screen_size(root):
    """Returns (width, height).
    
    :param root: A valid window object
    """
    # https://stackoverflow.com/questions/3949844
    return (root.winfo_screenwidth(), root.winfo_screenheight())

def centre_window(window, width=None, height=None):
    """Set the window to be of the given size, centred on the screen.
    
    :param width: Width to set the window to.  If `None` then use current
      window width.
    :param height: Height to set the window to.  If `None` then use current
      window height.
    """
    if width is None or height is None:
        window.update_idletasks()
        aw, ah = window.winfo_reqwidth(), window.winfo_reqheight()
        if width is None:
            width = aw
        if height is None:
            height = ah
    w, h = screen_size(window)
    x = (w - width) // 2
    y = (h - height) // 2
    minw, minh = window.minsize()
    minw = min(minw, width)
    minh = min(minh, height)
    window.minsize(minw, minh)
    window.geometry("{}x{}+{}+{}".format(width, height, x, y))

def centre_window_percentage(window, width_percentage, height_percentage):
    """Set the window to be the given percentages of the total screen size,
    cented on the screen."""
    w, h = screen_size(window)
    centre_window(window, w * width_percentage // 100, h * height_percentage // 100)

def stretchy_columns(window, columns):
    """Set all the columns to have a "weight" of 1
    
    :param window: Window like object to call columnconfigure on
    :param columns: Iterable of columns to set
    """
    for i in columns:
        window.columnconfigure(i, weight=1)

def stretchy_rows(window, rows):
    """Set all the rows to have a "weight" of 1
    
    :param window: Window like object to call rowconfigure on
    :param rows: Iterable of rows to set
    """
    for i in rows:
        window.rowconfigure(i, weight=1)

def ask_open_filename(*args, **kwargs):
    """As :func:`tkinter.filedialog.askopenfilename` but filters the returned
    file to be valid or `None`."""
    filename = tkinter.filedialog.askopenfilename(*args, **kwargs)
    if filename is None or filename == "" or len(filename) == 0:
        return None
    return filename

def ask_save_filename(*args, **kwargs):
    """As :func:`tkinter.filedialog.asksaveasfilename` but filters the returned
    file to be valid or `None`."""
    filename = tkinter.filedialog.asksaveasfilename(*args, **kwargs)
    if filename is None or filename == "" or len(filename) == 0:
        return None
    return filename


class Validator():
    """Provide some user-friendly way to validate the contents of a
    `tkinter.Entry` widget.  By default, all entries are valid, so this class
    can also be used as an over-engineered way to get notification of a change.

    :param widget: The widget to bind to
    :param variable: The `tkinter.StringVar` which is bound to the widget.
    :param callback: Optional function-like object to call when the variable changes.
    """
    def __init__(self, widget, variable, callback=None):
        self._widget = widget
        self._variable = variable
        self._callback = callback
        self._old_value = ""
        cmd1 = self._widget.register(self._validate)
        self._widget["validatecommand"] = (cmd1, "%P", "%V")
        self._widget["validate"] = "focus"

    def _reset(self):
        self._variable.set(self._old_value)

    def _validate(self, val, why):
        if why == "focusin":
            self._old_value = self._variable.get()
        elif why == "focusout":
            if not self.validate(val):
                self._widget.after_idle(self._reset)
            elif self._callback is not None:
                self._widget.after_idle(self._callback)
        else:
            raise ValueError("Unexpected event")
        return True

    def validate(self, value):
        """Should check if the value is acceptable, or not.

        :param value: String of the value to check.

        :return: True if the value is acceptable; False otherwise.
        """
        return True


class FloatValidator(Validator):
    """A :class:`Validator` which only accepts values which are empty, or can
    parse to a python `float`.

    :param allow_empty: If True, allow "" as a value; otherwise not.
    """
    def __init__(self, widget, variable, callback=None, allow_empty=False):
        super().__init__(widget, variable, callback)
        self._allow_empty = allow_empty

    def validate(self, value):
        if value == "" and self._allow_empty:
            return True
        try:
            float(value)
        except:
            return False
        return True


class DateTimeValidator(Validator):
    """A :class:`Validator` which only accepts values which parse using the
    given `strptime` string.

    :param format: The `strptime` format string.
    """
    def __init__(self, widget, variable, format, callback=None):
        super().__init__(widget, variable, callback)
        self._format = format

    def validate(self, value):
        try:
            _datetime.datetime.strptime(value, self._format)
        except:
            return False
        return True


def auto_wrap_label(label, padding=0):
    """Add a binding to a :class:`tk.Label` or :class:`ttk.Label` object so
    that when the label is resized, the text wrap length is automatically
    adjusted.

    :param label: The label object to bind to.
    :param padding: The padding to substract from the width; defaults to 0.
    """
    def callback(event):
        event.widget["wraplength"] = event.width - padding
    label.bind("<Configure>", callback)


class TextMeasurer():
    """Simplify measuring the size of text.  I find that this does not work
    terribly well, but it's better than guessing.
    """
    def __init__(self, font=None, scale=1.1, min=30, max=200):
        if font is None:
            font = "TkDefaultFont"#"TkTextFont"
        if isinstance(font, str):
            font = tkfont.nametofont(font)
        self._font = font
        self._scale = scale
        self._minimum = min
        self._maximum = max
        
    @property
    def scale(self):
        """Factor the scale the estimated width by."""
        return self._scale
    
    @scale.setter
    def scale(self, value):
        self._scale = value
        
    @property
    def minimum(self):
        """Cap returned widths to this minimum value."""
        return self._minimum
    
    @minimum.setter
    def minimum(self, value):
        self._minimum = value
        
    @property
    def maximum(self):
        """Cap returned widths to this maximum value."""
        return self._maximum
    
    @maximum.setter
    def maximum(self, value):
        self._maximum = value
        
    def _measure_one(self, text):
        width = self._font.measure(str(text))
        width = int(width * self._scale)
        width = min(self._maximum, max(self._minimum, width))
        return width
        
    def measure(self, text):
        """Return the (very much estimated) width of the text.
        
        :param text: Either a string, or an iterable of strings.
        
        :return: Width of the text, or if passed an iterable, the maximum of
          the widths.
        """
        if isinstance(text, str):
            return self._measure_one(text)
        return max(self._measure_one(t) for t in text)


class ModalWindow(tk.Toplevel):
    """A simple modal window abstract base class.
    
    Ideas from http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
    
    :param parent: The parent window from which to construct the dialog.
    :param title: Title for the modal window.
    """
    def __init__(self, parent, title, no_border = False):
        super().__init__(parent)
        if no_border:
            self.wm_overrideredirect(True)
        self.transient(parent)
        self._parent = parent
        self.title(title)
        self.update_idletasks()
        self.grab_set()
        self.resizable(width=False, height=False)
        self.add_widgets()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind("<Button-1>", self._flash)
        self.bind("<Unmap>", self._minim)

    def _minim(self, event):
        # If we're being minimised then also minimise the parent!
        if self._parent.master is None:
            self._parent.iconify()
        else:
            self._parent.master.iconify()

    def _over_self(self, event):
        over_win = self.winfo_containing(event.x_root, event.y_root)
        # Hopefully, true when the over_win is a child of us
        return str(over_win).startswith(str(self))

    def _flash(self, event):
        if not self._over_self(event):
            # Drag the focus back to us after a brief pause.
            self.after(100, lambda : self.focus_force())

    def _flash_close(self, event):
        if not self._over_self(event):
            self.cancel()

    def close_on_click_away(self):
        """Change behaviour so that the window is `destroy`ed when the user
        clicks off it."""
        self.bind("<Button-1>", self._flash_close)

    def set_size(self, width, height):
        """Set the size of the main window, and centre on the screen."""
        centre_window(self, width, height)
        self.update_idletasks()
        
    def set_size_percentage(self, width, height):
        """Set the size of the main window, as percentages of the screen size,
        and centre on the screen."""
        centre_window_percentage(self, width, height)
        self.update_idletasks()

    def set_to_actual_height(self):
        """Set the window the height required to fit its contents."""
        self.update_idletasks()
        centre_window(self, self.winfo_width(), self.winfo_reqheight())

    def set_to_actual_width(self):
        """Set the window the width required to fit its contents."""
        self.update_idletasks()
        centre_window(self, self.winfo_reqwidth(), self.winfo_height())

    def set_to_actual_size(self):
        """Set the window the size required to fit its contents."""
        self.update_idletasks()
        centre_window(self, self.winfo_reqwidth(), self.winfo_reqheight())

    def add_widgets(self):
        """Override to add widgets."""
        raise NotImplementedError()

    def cancel(self):
        """Override to do something extra on closing the window."""
        self.destroy()


class ListBox(tk.Frame):
    """Friendly version of `tk.ListBox` with vertical scrollbar, sensible
    default options, and a callback on changes.

    Common options are:
      - "width" / "height" : In characters/line respectively
      - "command" : Callback with signature `command(selection)`
    """
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        args = {"selectmode" : tk.MULTIPLE,
            "exportselection" : 0,
            "activestyle" : "dotbox"}
        args.update(kwargs)
        if "command" in args:
            self._command = args["command"]
            del args["command"]
        else:
            self._command = None
        self._box = tk.Listbox(self, **args)
        self._box.grid(row=0, column=0, sticky=tk.NSEW)
        stretchy_columns(self, [0])
        self._yscroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self._yscroll.grid(row=0, column=1, sticky=tk.NS + tk.E)
        self._box["yscrollcommand"] = self._yscroll.set
        self._yscroll["command"] = self._box.yview
        self._closed = False
        if self._command is not None:
            self._old_selection = []
            self._poll()

    def clear_rows(self):
        self._box.delete(0, self.size - 1)

    def add_rows(self, rows):
        """Add one or more rows to the end of the list.

        :param rows: Either a string, or an iterable of strings.
        """
        try:
            for r in rows:
                self._box.insert(tk.END, r)
        except:
            self._box.insert(tk.END, rows)

    @property
    def current_selection(self):
        """A list of the selected rows, with 0 as the first row."""
        return list(self._box.curselection())

    @current_selection.setter
    def current_selection(self, new_selection):
        self._box.selection_clear(0, self.size - 1)
        for r in new_selection:
            self._box.selection_set(r)

    @property
    def size(self):
        return self._box.size()

    def text(self, index):
        """The text of the entry at the index."""
        return self._box.get(index)

    def _poll(self):
        if self._closed:
            return
        sel = self.current_selection
        if sel != self._old_selection:
            self._old_selection = sel
            self._command(sel)
        self.after(250, self._poll)
    
    def destroy(self):
        self._closed = True
        super().destroy()
