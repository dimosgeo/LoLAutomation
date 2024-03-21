from tkinter import Frame, Button, Label, Misc
from typing import Callable, List
from utils import Spacing
from utils import utils
from PIL import Image, ImageTk


class ChampionFrame(Frame):
	def __init__(self, parent: Misc, width: int = 0, size: int = 0, swap_spell_function: Callable[[], None] = None, name_size: int = 26, spell_size: int = 65, horizontal_spacing: int = 15, *args, **kwargs) -> None:
		Frame.__init__(self, parent, *args, **kwargs)
		self.width = width
		self['bg'] = utils.colors['background_widget']
		self.spell_size = spell_size
		self.height = size
		self.spacing = Spacing(horizontal=horizontal_spacing)
		self.champion_icon = None
		self.champion_size = size - 10
		self.champion_name = Label(self, text='', font=utils.fonts['title'], background=self['bg'], foreground=utils.colors['text'], anchor='w')
		self.champion_image = Button(self, background=self['bg'], activebackground=self['bg'], bd=0)
		self.summonerSpellsFrame = SummonerSpellFrame(self, swap_spell_function, size=self.spell_size, background=self['bg'])

	def set_champion(self, name: str, image: bytes) -> None:
		self.champion_icon = ImageTk.PhotoImage(Image.open(image).resize((int(self.champion_size), int(self.champion_size))))
		self.champion_image['image'] = self.champion_icon
		self.champion_name['text'] = name
		
	def set_spells(self, spells: List[bytes]) -> None:
		self.summonerSpellsFrame.set_spells(spells)

	def place(self, x: int = 0, y: int = 0) -> None:
		super().place(x=x, y=y, width=self.width, height=self.height)
		self.champion_image.place(x=self.spacing.horizontal + 5, y=5, width=self.champion_size, height=self.champion_size)
		self.champion_name.place(x=self.height + self.spacing.horizontal * 2, y=5, height=self.height, width=340)
		self.summonerSpellsFrame.place(x=self.width - self.summonerSpellsFrame.width - self.spacing.horizontal - 5, y=(self.height - self.summonerSpellsFrame.height)//2)


class SummonerSpellFrame(Frame):
	def __init__(self, parent: Misc, swap_spell_function: Callable[[], None], size: int, horizontal_spacing: int = 25, *args, **kwargs) -> None:
		Frame.__init__(self, parent, *args, **kwargs)
		self.spacing = Spacing(horizontal=horizontal_spacing)
		self.height = size
		self.swap_function = swap_spell_function
		self.images = []
		self.spells = [Button(self, bd=0, bg=self['bg'], activebackground=self['bg']) for _ in range(2)]
		self.swap_button_size = 20
		self.swap_image = ImageTk.PhotoImage(Image.open('images/swap_icon.png').resize((self.swap_button_size, self.swap_button_size)))
		self.button_labels = [Label(self, text='D', background='black', foreground='white', font=utils.fonts['normal_bold']), Label(self, text='F', background='black', foreground='white', font=utils.fonts['normal_bold'])]
		self.swap_button = Button(self, image=self.swap_image, background=self['bg'], activebackground=utils.colors['widget_highlight'], borderwidth=0, command=self.swap_spells)
		self.width = size * 2 + self.spacing.horizontal
		self.primary_spell_f = True

	def set_spells(self, spells: List[bytes]) -> None:
		self.images = []
		if not self.primary_spell_f:
			spells = spells[::-1]
		for spell, image in zip(self.spells, spells):
			img = ImageTk.PhotoImage(Image.open(image).resize((self.height, self.height)))
			self.images.append(img)
			spell['image'] = img

	def swap_spells(self) -> None:
		self.swap_function()
		self.images = self.images[::-1]
		for spell, image in zip(self.spells, self.images):
			spell['image'] = image
		self.primary_spell_f = not self.primary_spell_f

	def place(self, x: int = 0, y: int = 0) -> None:
		super().place(x=x, y=y, width=self.width, height=self.height)

		self.swap_button.place(x=self.width / 2 - self.swap_button_size / 2, y=self.height / 2 - self.swap_button_size / 2, height=self.swap_button_size, width=self.swap_button_size)
		x = 0
		for spell, letter in zip(self.spells, self.button_labels):
			spell.place(x=x, y=0, height=self.height, width=self.height)
			letter.place(x=x, y=self.height - utils.fonts['normal_bold'].metrics('linespace'), height=utils.fonts['normal_bold'].metrics('linespace'), width=utils.fonts['normal_bold'].measure('D') + 5)
			x = self.height + self.spacing.horizontal
