import tkinter as tk
from tkinter.font import Font
from PIL import Image, ImageTk


class ItemBuildFrame(tk.Frame):
	def __init__(self, parent, width: float = 0, height: float = 0, horizontal_space: float = 20, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.width = width
		self.height = height
		self.horizontal_space = horizontal_space
		self.item_list = []
		self.image_list = []
		self.count_list = []
		# self.descriptions = []
		self.descriptionLabel = DescriptionLabel(self.winfo_toplevel(), bg='black', foreground='white', anchor='nw')

	def set_items(self, items):
		for item in self.item_list:
			item.destroy()

		self.image_list = []
		self.item_list = []
		for item in items:
			image = ImageTk.PhotoImage(Image.open(item['image']).resize((int(self.height), int(self.height))))
			self.image_list.append(image)
			self.item_list.append(tk.Button(self, image=image, bg=self['bg'], activebackground=self['bg'], bd=0))
			if 'description' in item:
				# self.descriptions.append(item['description'])
				self.item_list[-1].bind('<Enter>', self.create_lambda(item['description']))
				self.item_list[-1].bind('<Leave>', lambda *args: self.descriptionLabel.hide_description())
			# else:
				# self.descriptions.append('')
			if 'count' in item:
				self.count_list.append(NumberLabel(self, item['count']))
			else:
				self.count_list.append(NumberLabel(self))
		
		# x = 0
		# for item in self.item_list:
		# 	item.place(x=x, y=0, height=self.height, width=self.height)
		# 	x += self.height + self.horizontal_space

	def create_lambda(self, description):
		return lambda *args: self.descriptionLabel.show_description(description, args[0])

	def place(self, x=0, y=0):
		super().place(x=x, y=y, height=self.height, width=self.width)
		x = 0
		for item, count in zip(self.item_list, self.count_list):
			item.place(x=x, y=0, height=self.height, width=self.height)
			count.place(x=x + self.height, y=self.height - self.font.metrics('linespace'))
			x += self.height + self.horizontal_space
	
	def place_forget(self) -> None:
		super().place_forget()
		for item in self.item_list:
			item.place_forget()


class NumberLabel(tk.Label):
	def __init__(self, parent, text='', *args, **kwargs):
		tk.Label.__init__(self, parent, *args, **kwargs)
		self.font = Font(family='Helvetica', size=12)
		self['font'] = self.font
		self['text'] = text

	def place(self, x=0, y=0):
		super().place(x=x, y=y)

	def place_forget(self):
		super.place_forget()


class DescriptionLabel(tk.Label):
	def __init__(self, parent, *args, **kwargs):
		tk.Label.__init__(self, parent, *args, **kwargs)
		self.font = Font(family='Helvetica', size=12)
		self['font'] = self.font
	
	def show_description(self, text: str, button) -> None:
		self['text'] = text
		button = button.widget
		super().place(x=button.winfo_rootx() - self.master.winfo_rootx(), y=button.winfo_rooty() - self.master.winfo_rooty() - self.font.metrics('linespace'))

	def hide_description(self) -> None:
		super().place_forget()
