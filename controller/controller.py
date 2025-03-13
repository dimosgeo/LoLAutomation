from threading import Thread
from model import Model
from controller import LoLHandler
from typing import Optional, Dict
from utils import StatusType, init_fonts
from time import time
from queue import Queue


class Controller(Thread):
	def __init__(self, view, mode: Optional[int] = None, *args, **kwargs):
		super().__init__(*args, *kwargs)
		self.view = view
		self.queue = Queue(maxsize=10)
		self.lol_handler = LoLHandler(self.queue)
		self.lol_handler.start()
		self.model: Model = Model(mode)
		self.mode: Optional[int] = mode
		init_fonts()
		self.champion_id = -1
		self.champion_skin = -1

	def run(self):
		self.view.show_status_label()
		while True:
			message = self.queue.get()
			status = message.message_type
			if status == StatusType.PROCESS_CLOSED:
				break
			if status == StatusType.GAME_OPENED:
				start = time()
				self.view.set_status_label_text('Waiting for champion pick')
				self.model.init_data()
				self.view.after(0, self.view.add_build)
				self.view.after(0, self.view.show_status_label)
				if self.mode:
					self.champion_id = self.mode
					self.view.load_champion_data(self.get_build())
					print(f'Data load took: {time() - start}')
					self.view.show_data()
				print(f'Initial load took: {time() - start}')
			if status == StatusType.CHAMPION_PICKED:
				champion_id = self.lol_handler.champion_id
				if self.champion_id != champion_id:
					self.champion_id = champion_id
					self.view.load_champion_data(self.get_build())
					self.view.show_data()
			if status == StatusType.CHAMPION_LOCKED:
				self.view.hide_status_label()
				self.view.after(0, self.view.show_skins, self.get_skins())
			if status == StatusType.GAME_CLOSED:
				self.view.set_status_label_text('Waiting for client to open')
				self.view.hide_build()
				self.view.show_status_label()
			if status == StatusType.CHANGED_SKIN:
				self.champion_skin = message.message[0]
				self.view.after(0, self.view.set_active_skin, message.message[0])

	def set_client_data(self, champion):
		return self.model.set_client_data(champion)

	def set_active_skin(self, skin_id):
		return self.model.set_active_skin(skin_id)

	def swap_spells(self):
		return self.model.swap_spells()

	def get_lane_navigation_icons(self) -> Dict[str, Dict[str, str]]:
		return self.model.get_lane_navigation_icons()

	def get_skins(self):
		return self.model.get_skins()

	def get_build(self):
		return self.model.get_build(self.champion_id)

	def get_runes(self):
		return self.model.get_runes()

	def close(self):
		self.lol_handler.loop_stop()
		self.lol_handler.join()

	def ping(self):
		pass
