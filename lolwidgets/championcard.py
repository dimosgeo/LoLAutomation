from tkinter import Frame, Button, Widget, Label
from tkinter.font import Font
from lolwidgets.utils import Spacing
from PIL import Image, ImageTk


class ChampionFrame(Frame):
	def __init__(self, parent: Widget, width: float = 0, size: float = 0, backend=None,  name_size: int = 26, spell_size: int = 65, horizontal_spacing: int = 15, *args, **kwargs) -> None:
		Frame.__init__(self, parent, *args, **kwargs)
		self.width = width
		self.spell_size = spell_size
		self.backend = backend
		self.height = size
		self.spacing = Spacing(horizontal=horizontal_spacing)
		self.champion_icon = None
		self.champion_name = Label(self, text='', font=Font(family="Helvetica", size=name_size, weight="bold"), background=self['bg'], foreground='white', anchor='w')
		self.champion_image = Button(self, background=self['bg'], activebackground=self['bg'], bd=0)
		self.summonerSpellsFrame = SummonerSpellFrame(self, backend, size=self.spell_size, background=self['bg'])

	def set_champion(self, name, image):
		self.champion_icon = ImageTk.PhotoImage(Image.open(image).resize((int(self.height), int(self.height))))
		self.champion_image['image'] = self.champion_icon
		self.champion_name['text'] = name
		
	def set_spells(self, spells):
		self.summonerSpellsFrame.set_spells(spells)

	def place(self, x=0, y=0):
		super().place(x=x, y=y, width=self.width, height=self.height + 10)
		self.champion_image.place(x=5, y=5, width=self.height, height=self.height)
		self.champion_name.place(x=self.height + self.spacing.horizontal, y=5, height=self.height, width=340)
		self.summonerSpellsFrame.place(x=self.width - self.summonerSpellsFrame.width, y=(self.height - self.summonerSpellsFrame.height)/2)


class SummonerSpellFrame(Frame):
	def __init__(self, parent, backend, size, horizontal_spacing=25, *args, **kwargs) -> None:
		Frame.__init__(self, parent, *args, **kwargs)
		self.spacing = Spacing(horizontal=horizontal_spacing)
		self.height = size
		self.backend = backend
		self.images = []
		self.spells = [Button(self, bd=0), Button(self, bd=0)]
		self.swap_button_size = 20
		self.swap_image = ImageTk.PhotoImage(Image.open('images/swap_icon.png').resize((self.swap_button_size, self.swap_button_size)))
		self.label_font = Font(family="Helvetica", size=12, weight="bold")
		self.button_labels = [Label(self, text='D', background='black', foreground='white', font=self.label_font), Label(self, text='F', background='black', foreground='white', font=self.label_font)]
		self.swap_button = Button(self, image=self.swap_image, background=self['bg'], activebackground='#292C44', borderwidth=0, command=self.swap_spells)
		self.width = size * 2 + self.spacing.horizontal
		self.primary_spell_f = True

	def set_spells(self, spells):
		self.images = []
		if not self.primary_spell_f:
			spells = spells[::-1]
		for spell, image in zip(self.spells, spells):
			img = ImageTk.PhotoImage(Image.open(image).resize((self.height, self.height)))
			self.images.append(img)
			spell['image'] = img

	def swap_spells(self) -> None:
		if hasattr(self.winfo_toplevel(), 'backend'):
			self.backend.swap_spells()
		self.images = self.images[::-1]
		for spell, image in zip(self.spells, self.images):
			spell['image'] = image
		self.primary_spell_f = not self.primary_spell_f

	def place(self, x=0, y=0) -> None:
		super().place(x=x, y=y, width=self.width, height=self.height)

		self.swap_button.place(x=self.width / 2 - self.swap_button_size / 2, y=self.height / 2 - self.swap_button_size / 2, height=self.swap_button_size, width=self.swap_button_size)
		x = 0
		for spell, letter in zip(self.spells, self.button_labels):
			spell.place(x=x, y=0, height=self.height, width=self.height)
			letter.place(x=x, y=self.height - self.label_font.metrics('linespace'), height=self.label_font.metrics('linespace'), width=self.label_font.measure('D') + 5)
			x = self.height + self.spacing.horizontal
