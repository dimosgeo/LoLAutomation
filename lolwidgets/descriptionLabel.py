import tkinter as tk
from tkinter.font import Font

class DescriptionLabel(tk.Label):
	def __init__(self, parent, *args, **kwargs):
		tk.Label.__init__(self, parent, *args, **kwargs)
		self.font = Font(family='Helvetica', size=12)
		self['font'] = self.font
	
	def show_description(self, text: str, button) -> None:
		self['text'] = text
		button = button.widget
		super().place(x=button.winfo_rootx() - self.master.winfo_rootx(), y=button.winfo_rooty() - self.master.winfo_rooty() - self.winfo_height())

	def hide_description(self) -> None:
		super().place_forget()