import tkinter as tk
from typing import Callable, Any
from PIL import Image, ImageTk
from utils import utils


class SkinChooser(tk.Frame):
	def __init__(self, parent: tk.Misc, width: int, height: int, pick_skin: Callable[[int], None], horizontal_space: int = 5, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.horizontal_spacing = horizontal_space
		self.height = height
		self.width = width
		self['bg'] = utils.colors['background_widget']
		self.skins = dict()
		self.skin_list = []
		self.bind('<MouseWheel>', self.scroll_listener)
		self.scroll = 0
		self.selected_id = -1
		self.image_length = 0
		# self.winfo_toplevel().backend.set_active_skin
		self.pick_skin = pick_skin

	def place(self, x=0, y=0):
		super().place(x=x, y=y, height=self.height, width=self.width)
		self.place_tiles()

	def place_tiles(self):
		x = self.scroll
		for skin in self.skin_list:
			x += self.horizontal_spacing
			self.skins[skin].place(x=x, y=5)
			x += self.skins[skin].width

	def place_forget(self):
		super().place_forget()
		self.place_forget_tiles()

	def place_forget_tiles(self):
		for skin in self.skin_list:
			self.skins[skin].place_forget()

	def set_skins(self, skins_list) -> None:
		self.place_forget_tiles()
		if not len(skins_list):
			return
		self.skins = dict()
		self.skin_list = []
		self.selected_id = skins_list['selectedSkinId']
		self.image_length = 0
		self.scroll = 0

		skin_num = len(skins_list['availableSkins'])
		for skin_id, skin in skins_list['availableSkins'].items():
			self.skins[skin_id] = SkinButton(self, skin_id, self.height - 10, skin, bg='green', bd=0, clear_function=self.clear_pick, scroll_listener=self.scroll_listener, set_skin_function=self.pick_skin)
			if skin_num > 2: 
				self.skins[skin_id].bind('<MouseWheel>', self.skins[skin_id].scroll)
			self.skin_list.append(skin_id)
			self.image_length += self.skins[skin_id].width
			if self.selected_id == skin_id:
				self.skins[skin_id].pick_skin()

	def clear_pick(self) -> None:
		if self.selected_id != -1:
			self.skins[self.selected_id].unpick_skin()
			self.selected_id = -1

	def scroll_listener(self, e) -> None:
		if len(self.skin_list) > 2:
			self.scroll = max(min(0, self.scroll + e.delta), - (len(self.skins) + 1) * self.horizontal_spacing - self.image_length + self.width)
			self.place_forget_tiles()
			self.place_tiles()

	def select_skin(self, skin_id):
		if skin_id not in self.skin_list:
			return
		skin_index = self.skin_list.index(skin_id)
		if skin_index > 2:
			delta = -(skin_index / len(self.skin_list)) * self.image_length - (skin_index * self.horizontal_spacing) + self.horizontal_spacing
			self.scroll = max(min(0., delta), - (len(self.skins) + 1) * self.horizontal_spacing - self.image_length + self.width)
		else:
			self.scroll = 0
		x = self.winfo_x()
		y = self.winfo_y()
		self.place_forget()
		self.place(x=x, y=y)
		self.clear_pick()
		self.skins[skin_id].pick_skin()


class SkinButton(tk.Button):
	def __init__(self, parent: tk.Misc, skin_id: int, height: int, image, clear_function: Callable[[], None], scroll_listener: Callable[[Any], None], set_skin_function: Callable[[int], None], *args, **kwargs):
		tk.Button.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.skin_id = skin_id
		self['activebackground'] = self['bg']
		self.height = int(height)
		icon = Image.open(image)
		w, h = icon.size
		self.width = int(w * (self.height / h))
		self.img = ImageTk.PhotoImage(icon.resize((self.width, self.height)))
		self.active_img = ImageTk.PhotoImage(icon.resize((self.width-6, self.height-6)))
		self['image'] = self.img
		self['command'] = self.pick_skin
		self.clear_skins = clear_function
		self.scroll = lambda e: scroll_listener(e)
		self.select_skin = lambda: set_skin_function(self.skin_id)

	def place(self, x=0, y=0):
		super().place(x=x, y=y, width=self.width, height=self.height)

	# def scroll(self, e):
	# 	self.parent.scroll_listener(e)

	# def select_skin(self):
	# 	self.winfo_toplevel().backend.set_active_skin(self.skin_id)

	def pick_skin(self):
		self.clear_skins()
		self.master.selected_id = self.skin_id
		self['image'] = self.active_img
		self.select_skin()

	def unpick_skin(self):
		self['image'] = self.img
