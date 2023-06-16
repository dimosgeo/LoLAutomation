import tkinter as tk
from tkinter.font import Font
from utils import utils
from PIL import ImageTk, Image
from lolwidgets.runepage import RuneSheet
from lolwidgets.championcard import ChampionFrame
from lolwidgets.abilities import AbilitiesTable
from lolwidgets.items import ItemBuildFrame
from lolwidgets.utils import *


class Build(tk.Frame):
	def __init__(self, parent, backend, vertical_space: float = 20, horizontal_space: float = 20, ability_cell_size: float = 40, champion_frame_size: float = 100, item_size: float = 64, control_bar_font_size: int = 16, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.champion = None
		self.backend = backend
		self.spacing = Spacing(vertical=vertical_space, horizontal=horizontal_space)
		# self['highlightbackground'] = "white" # REMOVE
		# self['highlightthickness'] = 2 # REMOVE

		self.rune_sheet = RuneSheet(self, self.backend.get_runes(), background=utils.background_color, vertical_space=10, highlightthickness=2)
		self.abilities = AbilitiesTable(self, cell_size=(self.rune_sheet.width - ability_cell_size) / 19, border_size=2)
		self.width = int(self.rune_sheet.width + self.abilities.width + self.spacing.horizontal * 3)
		self.champion_frame = ChampionFrame(self, width=self.width, size=champion_frame_size, backend=self.backend, background=self['bg'])
		self.data = ControlFrame(self, lane_navigation=self.backend.navigation_icons['lane_navigation'], width=self.rune_sheet.width, font_size=control_bar_font_size, func=self.select_lane, background=self['bg'])
		
		self.starting_items = ItemBuildFrame(self, self.rune_sheet.width, height=item_size, background=self['bg'])
		self.full_build = ItemBuildFrame(self, self.rune_sheet.width, height=item_size, background=self['bg'])

		self.height = int(self.champion_frame.height + self.data.height + self.rune_sheet.height + 2 * vertical_space)#+ self.abilities.height + self.starting_items.height + self.full_build.height + 6 * vertical_space
		self.previous_selected = ''
	
	def set_champion(self, champion) -> None:
		self.champion = champion
		self.data.set_lanes(champion['build'].keys())
		self.champion_frame.set_champion(champion['name'], champion['image'])
		self.abilities.set_abilities(champion['abilities'])
		self.select_lane(champion['default_lane'])
	
	def select_lane(self, lane: str) -> None:
		if self.champion is None:
			return
		self.rune_sheet.select_runes(*self.champion['build'][lane][0]['runes'])
		self.champion_frame.set_spells(self.champion['build'][lane][0]['spells'])
		self.abilities.set_ability_order(self.champion['build'][lane][0]['ability_order'])
		self.starting_items.set_items(self.champion['build'][lane][0]['items'][0])
		self.full_build.set_items(self.champion['build'][lane][0]['items'][1])
		self.data.set_values(self.champion['build'][lane][0]['wr'], self.champion['build'][lane][0]['br'], self.champion['build'][lane][0]['pr'])
		self.data.select_lane(lane)
		self.previous_selected = lane

		self.backend.set_everything(self.champion['build'][lane][1])

	def place(self, x=0, y=0) -> None:
		super().place(x=x, y=y, height=self.height, width=self.width)
		y = 0
		self.champion_frame.place(x=0, y=0)
		y += self.champion_frame.height + self.spacing.vertical
		self.data.place(x=self.spacing.horizontal, y=y)
		y += self.data.height
		self.rune_sheet.place(x=self.spacing.horizontal, y=y)

		self.abilities.place(x=self.spacing.horizontal * 2 + self.rune_sheet.width, y=y)
		y += self.abilities.height + self.spacing.vertical
		self.starting_items.place(x=self.spacing.horizontal *2 + self.rune_sheet.width, y=y)
		y += self.starting_items.height + self.spacing.vertical
		self.full_build.place(x=self.spacing.horizontal * 2 + self.rune_sheet.width, y=y)

	def place_forget(self) -> None:
		super().place_forget()
		self.rune_sheet.place_forget()
		self.champion_frame.place_forget()
		self.abilities.place_forget()
		self.starting_items.place_forget()
		self.full_build.place_forget()
		self.data.place_forget()


class ControlFrame(tk.Frame):
	def __init__(self, parent, lane_navigation, width: float, font_size: int, horizontal_spacing: float = 20, func: callable = lambda *args: None, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.horizontal_spacing = horizontal_spacing
		self.font = Font(size=font_size)
		self.height = self.font.metrics('linespace')
		self.width = width

		self.pick_rate = tk.Label(self, text='PR:', font=self.font, background=self['bg'], foreground='white', anchor='w')
		self.pick_rate_value = tk.Label(self, text='100%', font=self.font, background=self['bg'], foreground='white', anchor='w')
		self.win_rate = tk.Label(self, text='WR:', font=self.font, background=self['bg'], foreground='white', anchor='w')
		self.win_rate_value = tk.Label(self, text='100%', font=self.font, background=self['bg'], foreground='white', anchor='w')
		self.ban_rate = tk.Label(self, text='BR:', font=self.font, background=self['bg'], foreground='white', anchor='w')
		self.ban_rate_value = tk.Label(self, text='100%', font=self.font, background=self['bg'], foreground='white', anchor='w')
		self.lane_images = [ImageTk.PhotoImage(Image.open('images/Top.png').resize((self.height, self.height)))]
		self.laneFrame = LaneFrame(self, lane_navigation=lane_navigation, height=self.height, background=self['bg'], func=func)

	def select_lane(self, lane):
		self.laneFrame.select_lane(lane)

	def set_values(self, win_rate, ban_rate, play_rate):
		self.win_rate_value['text'] = f'{win_rate:.2f}%'
		self.ban_rate_value['text'] = f'{ban_rate:.2f}%'
		self.pick_rate_value['text'] = f'{play_rate:.2f}%'

	def set_lanes(self, lane_list):
		self.laneFrame.set_active_buttons(lane_list)

	def place(self, x=0, y=0) -> None:
		super().place(x=x, y=y, height=self.height, width=self.width)

		x = 0
		self.pick_rate.place(x=x, y=0, height=self.height, width=self.font.measure(self.pick_rate['text']) + self.horizontal_spacing // 4)
		x += self.font.measure(self.pick_rate['text']) + self.horizontal_spacing // 2
		self.pick_rate_value.place(x=x, y=0, height=self.height, width=self.font.measure(self.pick_rate_value['text']) + self.horizontal_spacing)
		
		x += self.font.measure(self.pick_rate_value['text']) + self.horizontal_spacing
		self.win_rate.place(x=x, y=0, height=self.height, width=self.font.measure(self.win_rate['text']) + self.horizontal_spacing // 4)
		x += self.font.measure(self.win_rate['text']) + self.horizontal_spacing // 4
		self.win_rate_value.place(x=x, y=0, height=self.height, width=self.font.measure(self.win_rate_value['text']) + self.horizontal_spacing)

		x += self.font.measure(self.win_rate_value['text']) + self.horizontal_spacing
		self.ban_rate.place(x=x, y=0, height=self.height, width=self.font.measure(self.ban_rate['text']) + self.horizontal_spacing // 4)
		x += self.font.measure(self.ban_rate['text']) + self.horizontal_spacing // 4 
		self.ban_rate_value.place(x=x, y=0, height=self.height, width=self.font.measure(self.ban_rate_value['text']) + self.horizontal_spacing)

		x = self.width - self.laneFrame.width
		self.laneFrame.place(x=x, y=0)

	def place_forget(self) -> None:
		super().place_forget()
		self.pick_rate.place_forget()
		self.pick_rate_value.place_forget()
		self.win_rate.place_forget()
		self.win_rate_value.place_forget()
		self.ban_rate.place_forget()
		self.ban_rate_value.place_forget()
		self.laneFrame.place_forget()


class LaneFrame(tk.Frame):
	def __init__(self, parent, lane_navigation, height: float, horizontal_spacing=5, func: callable = lambda *args: None, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.indexes = {'top': 0, 'jungle': 1, 'mid': 2, 'adc': 3, 'support': 4}
		lanes = ['top', 'jungle', 'mid', 'adc', 'support']
		self.lane_func = func
		self.height = height
		self.width = 0
		self.horizontal_spacing = horizontal_spacing
		self.button_list = [LaneButton(self, lane=lane, active_icon=lane_navigation[lane]['enabled'], inactive_icon=lane_navigation[lane]['disabled'], size=int(self.height), borderwidth=0, background=self['bg'], activebackground=self['bg'], func=self.toggle_lane) for lane in lanes]
		self.active_buttons = []
		self.previous_selected = -1

	def select_lane(self, lane):
		if self.previous_selected != -1:
			self.button_list[self.previous_selected].set_active(False)
		self.button_list[self.indexes[lane]].set_active(True)
		self.previous_selected = self.indexes[lane]

	def toggle_lane(self, lane):
		if self.previous_selected == self.indexes[lane]:
			return
		self.lane_func(lane)

	def set_active_buttons(self, lanes):
		self.active_buttons = []
		for lane in lanes:
			self.active_buttons.append(self.indexes[lane])
		self.active_buttons.sort()
		self.width = (self.height + self.horizontal_spacing) * len(self.active_buttons)
	
	def place(self, x: float = 0, y: float = 0) -> None:
		super().place(x=x, y=y, width=(self.height + self.horizontal_spacing) * len(self.active_buttons), height=self.height)
		x = 0
		for i in self.active_buttons:
			self.button_list[i].place(x=x, y=0, height=self.height, width=self.height)
			x += self.height + self.horizontal_spacing


class LaneButton(tk.Button):
	def __init__(self, parent, active_icon, inactive_icon, size: int, lane: str, func: callable = lambda *args: None, *args, **kwargs):
		tk.Button.__init__(self, parent, *args, **kwargs)
		# image = Image.open(icon).resize((size, size))
		self.size = size
		self.lane = lane
		self.is_active = False
		self.active_image = ImageTk.PhotoImage(Image.open(active_icon).resize((size, size)))
		self.inactive_image = ImageTk.PhotoImage(Image.open(inactive_icon).resize((size, size)))
		self.size = size
		self.func = func
		self['image'] = self.inactive_image
		self['command'] = self.callback

	def set_active(self, status: bool) -> None:
		self.is_active = status
		if status:
			self['image'] = self.active_image
		else:
			self['image'] = self.inactive_image

	def callback(self):
		self.func(self.lane)
