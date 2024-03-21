import tkinter as tk
from utils import utils


class DescriptionLabel(tk.Label):
	def __init__(self, parent, *args, **kwargs):
		tk.Label.__init__(self, parent, *args, **kwargs)
		self.font = utils.fonts['normal']
		self['font'] = self.font
	
	def show_description(self, text: str, widget) -> None:
		self['text'] = text
		width = utils.fonts['normal'].measure(text)
		super().place(x=min(widget.winfo_rootx() - self.master.winfo_rootx(), self.master.winfo_width() - width - 5), y=widget.winfo_rooty() - self.master.winfo_rooty() - self.winfo_height())

	def hide_description(self) -> None:
		super().place_forget()
