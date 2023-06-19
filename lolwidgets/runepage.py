from utils import utils
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class RuneSheet(tk.Frame):
	def __init__(self, parent: tk.Widget, rune_list: list, categories_size=65, categories_space=20, keystone_size=80, rune_size=60, small_rune_size=50, horizontal_space=5, vertical_space=15, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.categories_space = categories_space
		self.previous_active = [-1, -1]
		self['bg'] = utils.widget_color
		self.bg_label = tk.Label(self, bg=utils.widget_color)
		self.main_categories = RuneHeaderFrame(self, rune_list=rune_list[0], size=categories_size, horizontal_space=horizontal_space, background=utils.widget_color)
		self.secondary_categories = RuneHeaderFrame(self, rune_list=rune_list[0], size=categories_size, horizontal_space=horizontal_space, background=utils.widget_color)
		self.pages = [RuneFrame(self, page, keystone_size=keystone_size, rune_size=rune_size, horizontal_space=horizontal_space, is_primary=True, vertical_space=vertical_space, background=utils.widget_color) for page in rune_list[1:-1]]
		self.small_runes = StatRunes(self, rune_list=rune_list[-1], rune_size=small_rune_size, horizontal_space=15, background=utils.widget_color)
		self.width = self.main_categories.width + self.secondary_categories.width - self.secondary_categories.size + self.categories_space * 3
		self.height = self.secondary_categories.size + self.pages[0].height - keystone_size + self.small_runes.height + categories_space * 1

	def place(self, x=0, y=0):
		super().place(x=x, y=y, width=self.width, height=self.height)
		# self.bg_label.place(x=0, y=0, width=self.width, height=self.height)

	def place_forget(self):
		super().place_forget()
		self.main_categories.place_forget()
		self.secondary_categories.place_forget()
		self.pages.place_forget()
		self.small_runes.place_forget()

	def clear_pages(self):
		if self.previous_active[0] >= 0:
			self.pages[self.previous_active[0]].place_forget()
		if self.previous_active[1] >= 0:
			self.pages[self.previous_active[1]].place_forget()

	def select_main_page(self, index: int):
		page = self.pages[index]
		page.is_primary = True
		page.place(self.main_categories.width / 2 - page.width/2 + self.categories_space, self.main_categories.size + self.categories_space*2)
		self.previous_active[0] = index

	def select_secondary_page(self, runes):
		page = self.pages[runes[0]]
		page.select_runes(runes[1:])
		page.is_primary = False
		page.place((self.secondary_categories.width - page.width) / 2 + self.main_categories.width + 2*self.categories_space, self.secondary_categories.size + self.categories_space*2)
		self.previous_active[1] = runes[0]

	def select_small_runes(self, runes):
		self.small_runes.select_runes(runes)
		self.small_runes.place_forget()
		self.small_runes.place(x=self.main_categories.width + 2 * self.categories_space + (self.secondary_categories.width - self.small_runes.width)/2, y=self.secondary_categories.size + self.pages[self.previous_active[1]].height + 2 * self.categories_space)
	
	def select_runes(self, main_runes, second_runes, small_runes):
		self.main_categories.place_forget()
		self.main_categories.place(x=self.categories_space, y=self.categories_space)
		self.pages[self.previous_active[0]].place_forget()
		self.pages[self.previous_active[1]].place_forget()
		
		self.main_categories.set_active(main_runes[0])
		self.pages[main_runes[0]].select_runes(main_runes[1:])
		self.select_main_page(main_runes[0])

		self.secondary_categories.set_hidden(main_runes[0])
		self.secondary_categories.set_active(second_runes[0])
		self.secondary_categories.place_forget()
		self.secondary_categories.place(x=self.main_categories.width + 2*self.categories_space, y=self.categories_space)

		self.select_secondary_page(second_runes)
		self.select_small_runes(small_runes)
		

class RuneHeaderFrame(tk.Frame):
	def __init__(self, parent, rune_list: list, size: float, horizontal_space, is_primary: bool = False, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.length = len(rune_list)
		self.button_list = []
		self.last_active = 0
		self.size = size
		self.hidden_category = -1
		self.is_primary = is_primary
		self.horizontal_space = horizontal_space
		self.width = self.length * (size + horizontal_space)
		self.button_list = [RuneButton(parent=self, icon=rune, size=self.size, bg=self['bg']) for rune in rune_list]

	def set_active(self, index):
		self.button_list[self.last_active].set_active(False)
		self.button_list[index].set_active(True)
		self.last_active = index

	def set_hidden(self, index: int):
		self.hidden_category = index
		self.width = self.length * (self.size + self.horizontal_space) - self.size

	def place(self, x=0, y=0):
		super().place(x=x, y=y, width=self.width, height=self.size + self.horizontal_space)

		x = (self.width - (self.size + self.horizontal_space) * (self.length - (self.hidden_category != -1)) - self.horizontal_space/2) / 2
		for b, category_button in enumerate(self.button_list):
			if b != self.hidden_category:
				category_button.place(x=x, y=0, height=self.size, width=self.size)
				x += self.size + self.horizontal_space

	def place_forget(self) -> None:
		super().place_forget()
		for button in self.button_list:
			button.place_forget()


class StatRunes(tk.Frame):
	def __init__(self, parent, rune_list, rune_size=40, horizontal_space=5, vertical_space=5, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.rune_size = rune_size
		self.previous_selected = [-1, -1, -1]
		self.horizontal_space = horizontal_space
		self.vertical_space = vertical_space
		self.height = (self.rune_size + self.vertical_space) * len(rune_list)
		rune_num = max((len(row) for row in rune_list))
		self.width = rune_num * self.rune_size + (rune_num + 1) * self.horizontal_space
		self.rune_buttons = [[RuneButton(parent=self, icon=rune, size=self.rune_size, bg=utils.widget_color) for rune in row] for row in rune_list]
	
	def select_runes(self, runes):
		for i, value in enumerate(self.previous_selected):
			if value != -1:
				self.rune_buttons[i][value].set_active(False)
		for i in range(len(runes)):
			self.rune_buttons[i][runes[i]].set_active(True)
		self.previous_selected = runes

	def place(self, x: float = 0, y: float = 0):
		super().place(x=x, y=y, width=self.width, height=self.height)
		
		y = 0
		for row in self.rune_buttons:
			x = (self.width - len(row) * (self.rune_size + self.horizontal_space) + self.horizontal_space) / 2
			for b in row:
				b.place(x=x, y=y, height=self.rune_size, width=self.rune_size)
				x += self.rune_size + self.horizontal_space
					
			y += self.vertical_space + self.rune_size
	
	def place_forget(self) -> None:
		super().place_forget()
		for row in self.rune_buttons:
			for button in row:
				button.place_forget()
		

class RuneFrame(tk.Frame):
	def __init__(self, parent, rune_list, is_primary: bool = True, keystone_size=64, rune_size=64, horizontal_space=5, vertical_space=5, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.rune_buttons = []
		self.is_primary = is_primary
		self.previous_active = [0 for _ in rune_list]
		self.row_sizes = [len(row) for row in rune_list]
		self.length = [max((row for row in self.row_sizes[not self.is_primary:])), max((row for row in self.row_sizes))]
		self.rune_sizes = [rune_size, keystone_size]
		self.horizontal_space = horizontal_space
		self.vertical_space = vertical_space
		self.rune_buttons = [[RuneButton(parent=self, icon=rune, size=keystone_size, bg=self['bg']) for rune in rune_list[0]]] + [[RuneButton(parent=self, icon=rune, size=rune_size, borderwidth=0, bg=self['bg']) for rune in row] for row in rune_list[1:]]
		
	@property
	def width(self) -> float:
		return self.length[self.is_primary] * (self.rune_sizes[self.is_primary] + self.horizontal_space) + self.horizontal_space

	@property
	def height(self) -> float:
		return len(self.rune_buttons[1:]) * self.rune_sizes[0] + (len(self.rune_buttons) + self.is_primary) * self.vertical_space/((not self.is_primary) + 1) + self.rune_sizes[1] * self.is_primary
	
	def select_runes(self, runes: list) -> None:
		for i, row in zip(self.previous_active, self.rune_buttons):
			row[i].set_active(False)
		for i in range(len(runes)):
			if runes[i] != -1:
				self.rune_buttons[i][runes[i]].set_active(True)
		self.previous_active = runes

	def place(self, x: float = 0, y: float = 0) -> None:
		super().place(x=x, y=y, width=self.width, height=self.height)

		y = 0
		for row in self.rune_buttons[not self.is_primary:]:
			size = self.rune_sizes[self.is_primary and y == 0]

			x = (self.width - len(row) * (size + self.horizontal_space) + self.horizontal_space) / 2
			for b in row:
				b.place(x=x, y=y, height=size, width=size)
				x += size + self.horizontal_space				
			y += self.vertical_space / ((not self.is_primary) + 1) + size
	
	def place_forget(self) -> None:
		super().place_forget()
		for row in self.rune_buttons:
			for button in row:
				button.place_forget()


class RuneButton(tk.Button):
	def __init__(self, parent: tk.Widget, icon, size: float, *args, **kwargs):
		tk.Button.__init__(self, parent, *args, **kwargs)
		icon = Image.open(icon).resize((int(size), int(size)))
		self['borderwidth'] = 0
		self.active = False
		self.active_image = ImageTk.PhotoImage(icon)
		self.inactive_image = ImageTk.PhotoImage(utils.grayscale(icon))
		self['activebackground'] = self['bg']
		self.set_active(False)
		# self.bind("<Button-1>", lambda _ : "break", add=True)

	def set_active(self, status: bool) -> None:
		if status:
			self['image'] = self.active_image
		else:
			self['image'] = self.inactive_image
		self.active = status
