import tkinter as tk
from PIL import Image, ImageTk
from utils import utils

class SkinChooser(tk.Frame):
	def __init__(self, parent, width, height, horizontal_space=5, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.horizontal_spacing = horizontal_space
		self.height = height
		self.width = width
		self['bg'] = utils.palette[0]
		self.skins = dict()
		self.skin_list = []
		self.bind('<MouseWheel>', self.scroll_listener)
		self.scroll = 0
		self.selected_id = -1
		self.image_length = 0

	def place(self, x=0, y=0):
		super().place(x=x, y=y, height=self.height, width=self.width)
		x = self.scroll
		for skin in self.skin_list:
			x += self.horizontal_spacing
			self.skins[skin].place(x=x, y=5)
			x += self.skins[skin].width

	def place_forget(self):
		super().place_forget()
		for skin in self.skin_list:
			self.skins[skin].place_forget()

	def set_skins(self, skins_list):
		for skin in self.skin_list:
			self.skins[skin].place_forget()

		self.skins = dict()
		self.skin_list = []
		self.selected_id = skins_list['selectedSkinId']
		self.image_length = 0

		for skin_id, skin in skins_list['availableSkins'].items():
			self.skins[skin_id] = SkinButton(self, skin_id, self.height - 10, skin, bg='green', bd=0)
			self.skins[skin_id].bind('<MouseWheel>', self.skins[skin_id].scroll)
			self.skin_list.append(skin_id)
			self.image_length += self.skins[skin_id].width
			if self.selected_id == skin_id:
				self.skins[skin_id].pick_skin()

	def clear_pick(self):
		if self.selected_id != -1:
			self.skins[self.selected_id].unpick_skin()
		self.selected_id = -1


	def scroll_listener(self, e):
		self.scroll = max(min(0, self.scroll + e.delta), - (len(self.skins) + 1) * self.horizontal_spacing - self.image_length + self.width)
		x=self.winfo_x()
		y=self.winfo_y()
		self.place_forget()
		self.place(x=x, y=y)

	def select_skin(self, skinid):
		delta = -(self.skin_list.index(skinid) / len(self.skin_list)) * self.image_length - (self.skin_list.index(skinid) * self.horizontal_spacing) - self.horizontal_spacing 
		self.scroll = max(min(0, delta), - (len(self.skins) + 1) * self.horizontal_spacing - self.image_length + self.width)
		x=self.winfo_x()
		y=self.winfo_y()
		self.place_forget()
		self.place(x=x, y=y)
		self.clear_pick()
		self.skins[skinid].pick_skin()


class SkinButton(tk.Button):
	def __init__(self, parent, skin_id, height, image, *args, **kwargs):
		tk.Button.__init__(self, parent, *args, **kwargs)
		self.parent = parent
		self.sid = skin_id
		self['activebackground'] = self['bg']
		self.height = height
		self.icon = Image.open(image)
		w, h = self.icon.size
		self.width = int(w * (self.height / h))
		icon = self.icon.resize((self.width, self.height))
		self.img = ImageTk.PhotoImage(icon)
		self['image'] = self.img
		self['command'] = self.select_skin
	def place(self, x=0, y=0):
		super().place(x=x, y=y, width=self.width, height=self.height)

	def scroll(self, e):
		self.parent.scroll_listener(e)

	def select_skin(self):
		self.winfo_toplevel().backend.set_active_skin(self.sid)
		self.pick_skin()

	def pick_skin(self):
		pil_image = self.icon.resize((self.width-6, self.height-6))
		self.master.clear_pick()
		self.master.selected_id = self.sid
		self.img = ImageTk.PhotoImage(pil_image)
		self['image'] = self.img

	def unpick_skin(self):
		pil_image = self.icon.resize((self.width, self.height))
		self.img = ImageTk.PhotoImage(pil_image)
		self['image'] = self.img
