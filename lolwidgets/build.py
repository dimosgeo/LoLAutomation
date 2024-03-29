import tkinter as tk
from typing import Dict, Any, List, Callable
from utils import utils
from PIL import ImageTk, Image
from lolwidgets.runepage import RuneSheet
from lolwidgets.championcard import ChampionFrame
from lolwidgets.abilities import AbilitiesTable
from lolwidgets.items import ItemBuildFrame
from lolwidgets.skinchooser import SkinChooser
from utils import Spacing


class Build(tk.Frame):
	def __init__(self, parent: tk.Misc, rune_icons: List[bytes], lane_navigation_icons: Dict[str, Dict[str, str]], client_setup_function: Callable[[Dict], None], set_skin_function: Callable[[int], None], swap_spell_function: Callable[[], None], vertical_space: int = 20, horizontal_space: int = 20, ability_cell_size: int = 40, champion_frame_size: int = 110, item_size: float = 64, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.champion = None
		self.spacing = Spacing(vertical=vertical_space, horizontal=horizontal_space)
		self.rune_sheet = RuneSheet(self, rune_icons, vertical_space=15)
		self.abilities = AbilitiesTable(self, cell_size=int((self.rune_sheet.width - ability_cell_size) / 19), border_size=2)
		self.width = int(self.rune_sheet.width + self.abilities.width + self.spacing.horizontal * 3)
		self.champion_frame = ChampionFrame(self, width=self.width, size=champion_frame_size, swap_spell_function=swap_spell_function, background=self['bg'])
		self.data = ControlFrame(self, lane_navigation=lane_navigation_icons, width=self.rune_sheet.width, func=self.select_lane, background=self['bg'])
		
		self.starting_items = ItemBuildFrame(self, title='Starting Items', width=self.rune_sheet.width, height=item_size, title_width=150, background=self['bg'])
		self.full_build = ItemBuildFrame(self, title='Full Build', width=self.rune_sheet.width, height=item_size, title_width=150, background=self['bg'])

		self.height = int(self.champion_frame.height + self.data.height + self.rune_sheet.height + vertical_space)
		self.skins = SkinChooser(self, width=self.abilities.width, height=self.height - self.champion_frame.height - self.abilities.height - self.starting_items.height - self.full_build.height - 5 * self.spacing.vertical, pick_skin=set_skin_function)
		self.previous_selected = ''
		self.setup_client = client_setup_function
	
	def set_champion(self, champion: Dict[str, Any]) -> None:
		self.champion = champion
		self.data.set_lanes(champion['build'].keys())
		self.champion_frame.set_champion(champion['name'], champion['image'])
		self.abilities.set_abilities(champion['abilities'])
		self.select_lane(champion['default_lane'])

	def set_skins(self, skins) -> None:
		self.skins.set_skins(skins)

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

		self.setup_client(self.champion['build'][lane][1])

	def place(self, x=0, y=0) -> None:
		super().place(x=x, y=y, height=self.height, width=self.width)
		y = 0
		self.champion_frame.place(x=0, y=0)
		y += self.champion_frame.height
		self.data.place(x=int(self.spacing.horizontal), y=y)
		y += self.data.height
		self.rune_sheet.place(x=self.spacing.horizontal, y=y)
		x = self.spacing.horizontal * 2 + self.rune_sheet.width
		y = self.champion_frame.height + self.spacing.vertical
		self.abilities.place(x=x, y=y)
		y += self.abilities.height + self.spacing.vertical
		self.starting_items.place(x=x, y=y)
		y += self.starting_items.height + self.spacing.vertical
		self.full_build.place(x=x, y=y)
		y += self.full_build.height + self.spacing.vertical
		self.skins.place(x=x, y=y)

	def place_forget(self) -> None:
		super().place_forget()
		self.rune_sheet.place_forget()
		self.champion_frame.place_forget()
		self.abilities.place_forget()
		self.starting_items.place_forget()
		self.full_build.place_forget()
		self.data.place_forget()

	def select_skin(self, skin_id: int):
		self.skins.select_skin(skin_id)


class ControlFrame(tk.Frame):
	def __init__(self, parent, lane_navigation, width: float, horizontal_spacing: float = 20, func: callable = lambda *args: None, *args, **kwargs) -> None:
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.horizontal_spacing = horizontal_spacing
		self.font = utils.fonts['normal']
		self.height = self.font.metrics('linespace') * 2
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

	def set_values(self, win_rate: float, ban_rate: float, play_rate: float) -> None:
		self.win_rate_value['text'] = f'{win_rate:.2f}%'
		self.ban_rate_value['text'] = f'{ban_rate:.2f}%'
		self.pick_rate_value['text'] = f'{play_rate:.2f}%'

	def set_lanes(self, lane_list) -> None:
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
		self.lane_func = func
		self.height = height
		self.width = 0
		self.horizontal_spacing = horizontal_spacing
		self.button_list = [LaneButton(self, lane=lane, active_icon=lane_navigation[lane]['enabled'], inactive_icon=lane_navigation[lane]['disabled'], size=int(self.height), borderwidth=0, background=self['bg'], activebackground=self['bg'], func=self.toggle_lane) for lane in utils.lanes if lane in lane_navigation]
		self.active_buttons = []
		self.previous_selected = -1

	def select_lane(self, lane: int) -> None:
		if self.previous_selected != -1:
			self.button_list[self.previous_selected].set_active(False)
			self.button_list[self.previous_selected]['bg'] = self['bg']
		self.button_list[utils.lane_indexes[lane]].set_active(True)
		self.button_list[utils.lane_indexes[lane]]['bg'] = utils.colors['widget_highlight']
		self.previous_selected = utils.lane_indexes[lane]

	def toggle_lane(self, lane: int) -> None:
		if self.previous_selected == utils.lane_indexes[lane]:
			return
		self.lane_func(lane)

	def set_active_buttons(self, lanes) -> None:
		self.active_buttons = []
		for lane in lanes:
			self.active_buttons.append(utils.lane_indexes[lane])
		self.active_buttons.sort()
		self.width = (self.height + self.horizontal_spacing) * len(self.active_buttons) - self.horizontal_spacing
	
	def place(self, x: float = 0, y: float = 0) -> None:
		super().place(x=x, y=y, width=(self.height + self.horizontal_spacing) * len(self.active_buttons), height=self.height)
		x = 0
		for i in self.active_buttons:
			self.button_list[i].place(x=x, y=0, height=self.height, width=self.height)
			x += self.height + self.horizontal_spacing


class LaneButton(tk.Button):
	def __init__(self, parent, active_icon, inactive_icon, size: int, lane: str, func: callable = lambda *args: None, *args, **kwargs):
		tk.Button.__init__(self, parent, *args, **kwargs)
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
