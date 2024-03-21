import tkinter as tk
import utils
from lolwidgets.descriptionLabel import DescriptionLabel
from PIL import Image, ImageTk


class ItemBuildFrame(tk.Frame):
	def __init__(self, parent, title='', width: float = 0, height: float = 0, horizontal_space: float = 20, title_width=None, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.width = width
		self.height = height
		self.font = utils.fonts['normal_bold']
		if not title_width:
			self.title_width = self.font.measure(title) + 5
		else:
			self.title_width = title_width
		self.title = tk.Label(self, text=title, font=self.font, anchor='w', bg=self['bg'], fg='white')
		self.horizontal_space = horizontal_space
		self.item_list = []
		self.image_list = []
		self.count_list = []
		self.descriptionLabel = DescriptionLabel(self.winfo_toplevel(), bg='black', foreground='white', anchor='nw')

	def set_items(self, items):
		for item, count in zip(self.item_list, self.count_list):
			item.destroy()
			count.destroy()

		self.image_list = []
		self.item_list = []
		self.count_list = []
		for item in items:
			image = ImageTk.PhotoImage(Image.open(item['image']).resize((int(self.height), int(self.height))))
			self.image_list.append(image)
			self.item_list.append(tk.Button(self, image=image, bg=self['bg'], activebackground=self['bg'], bd=0))
			if 'description' in item:
				self.item_list[-1].bind('<Enter>', self.create_lambda(item['description']))
				self.item_list[-1].bind('<Leave>', lambda *args: self.descriptionLabel.hide_description())

			if 'count' in item:
				self.count_list.append(NumberLabel(self, item['count'], bg='black'))
			else:
				self.count_list.append(NumberLabel(self))

		self.place_children()

	def create_lambda(self, description):
		return lambda *args: self.descriptionLabel.show_description(description, args[0].widget)

	def place(self, x=0, y=0):
		super().place(x=x, y=y, height=self.height, width=self.width)
		self.title.place(x=0, y=0, height=self.height, width=self.title_width)
		self.place_children()

	def place_children(self):
		x = self.title_width + self.horizontal_space
		for item, count in zip(self.item_list, self.count_list):
			item.place(x=x, y=0, height=self.height, width=self.height)
			if count['text'] > 1:
				count.place(x=x + self.height - count.font.metrics('linespace'), y=self.height - count.font.metrics('linespace'))
			x += self.height + self.horizontal_space
	
	def place_forget(self) -> None:
		super().place_forget()
		for count in self.count_list:
			count.place_forget()

		for item in self.item_list:
			item.place_forget()


class NumberLabel(tk.Label):
	def __init__(self, parent, text=1, *args, **kwargs):
		tk.Label.__init__(self, parent, *args, **kwargs)
		self.font = utils.fonts['small_bold']
		self['font'] = self.font
		self['foreground'] = 'white'
		self['text'] = text

	def place(self, x: int = 0, y: int = 0):
		super().place(x=x, y=y, height=self.font.metrics('linespace'), width=self.font.metrics('linespace'))

	def place_forget(self):
		super().place_forget()

	def __repr__(self):
		return str(self['text'])
