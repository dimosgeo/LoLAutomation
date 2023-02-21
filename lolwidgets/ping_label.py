import tkinter as tk
from tkinter.font import Font


class PingLabel(tk.Label):
    def __init__(self, parent, font_size: int = 10, *args, **kwargs):
        tk.Label.__init__(self, parent, *args, **kwargs)
        self.font = Font(family='Helvetica', size=font_size, weight='bold')
        self['font'] = self.font
        self['text'] = ''
        self.height = self.font.metrics('linespace')

    @property
    def width(self):
        return self.font.measure(self['text'])

    def place(self, x=0, y=0):
        super().place(x=x, y=y, height=self.height, width=self.width)
