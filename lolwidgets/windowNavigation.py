import tkinter as tk
from utils import utils

class WindowNavigation(tk.Frame):
	def __init__(self, parent, height=30, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.height = height
		self.parent = parent
		self.navigation_buttons = [NavigationButton(self, height, bd=0, bg= utils.palette[1], activebackground=utils.palette[2]) for i in range(3)]
		self.navigation_buttons[0]['command'] = lambda: self.winfo_toplevel().on_closing()

	def place(self):
		super().place(x=0, y=0, height=self.height, width=self.parent.winfo_width())
		
		for i, button in enumerate(self.navigation_buttons, start=1):
			button.place(x=self.parent.winfo_width() - (button.width) * i - (i-1), y=0, width=button.width, height=button.height)

	def place_forget(self):
		super().place_forget()
		for button in self.navigation_buttons:
			button.place_forget()

class NavigationButton(tk.Button):
	def __init__(self, parent, height=30, width=40, *args, **kwargs) -> None:
		tk.Button.__init__(self, parent, *args, **kwargs)
		self.width = width
		self.height = height