import time
from utils import utils
from tkinter import Tk, Label
from backend import Backend
from utils import Spacing, Padding
from lolwidgets import Build, PingLabel, VerticalScrollBar
from threading import Thread
from PIL import Image, ImageTk


class App(Tk):
	def __init__(self, development_mode=False):
		Tk.__init__(self)
		self.dev_mode = development_mode
		self.start = time.time()
		self.title('LOL Assistant')
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.configure(bg=utils.colors['background'])
		self.bind("<Configure>", self.events_handler)
		self.resizable(width=False, height=False)
		utils.init_fonts()
		self.icon = ImageTk.PhotoImage(Image.open('images/icon.png'))
		self.iconbitmap(default='images/icon.png')
		self.backend = Backend(self.dev_mode)
		self.build = None
		self.scrollbar = None
		self.navigation_images = None

		self.spacing = Spacing(vertical=20, horizontal=20)
		self.padding = Padding(top=0, left=20, right=20, bottom=20)

		self.screenwidth = self.winfo_screenwidth()
		self.screenheight = self.winfo_screenheight()
		self.height = int(self.screenheight * 0.5)
		self.width = int(self.screenwidth * 0.2)
		alignstr = f'{self.width}x{self.height}+{(self.screenwidth - self.width) // 2}+{(self.screenheight - self.height) // 2}'

		self.geometry(alignstr)
		self.wm_iconphoto(False, self.icon)
		self.status_label = Label(self, text='Waiting for client to open', font=utils.fonts['normal'], bg=self['bg'], foreground='white')
		self.ping = PingLabel(self, font_size=10, background=utils.colors['transparent'], foreground='#3BA55C')

		# self.after(1000, self.get_ping)
		self.lolListener = Thread(target=self.lol_listener, daemon=True)
		self.lolListener.start()
		print(f'Start time: {time.time() - self.start}')

	def add_build(self):
		self.navigation_images = self.backend.get_navigation_icons()
		self.build = Build(self, background=utils.colors['background'], rune_icons=self.backend.get_runes(), lane_navigation_icons=self.backend.navigation_icons['lane_navigation'], client_setup_function=self.backend.set_everything, set_skin_function=self.backend.set_active_skin, swap_spell_function=self.backend.swap_spells)
		self.width = self.build.width
		self.height = self.build.height
		alignstr = f'{self.width}x{self.height}+{(self.screenwidth - self.width) // 2}+{(self.screenheight - self.height) // 2}'
		self.geometry(alignstr)
		self.scrollbar = VerticalScrollBar(self, width=16, background=utils.colors['background'], child_w=self.build)

	def get_ping(self):
		self.ping['text'] = self.backend.ping()
		self.ping.place(x=self.winfo_width() - self.ping.width - self.padding.right, y=self.winfo_height() - self.ping.height - self.padding.bottom)
		self.ping.lift()
		self.after(1000, self.get_ping)

	def lol_listener(self):
		self.show_message_label()
		while True:
			message = self.backend.get_status()
			status = message.message_type
			if status == 'PROCESS_CLOSED':
				break
			if status == 'GAME_OPENED':
				self.status_label['text'] = 'Waiting for champion pick'
				self.add_build()
				self.show_message_label()
				if self.dev_mode:
					self.backend.champion_id = self.dev_mode
					self.load_data()
					self.show_data()
			if status == 'CHAMPION_PICKED':
				self.load_data()
			if status == 'CHAMPION_LOCKED':
				self.status_label.place_forget()
				self.show_data()
				self.show_skins()
			if status == 'GAME_CLOSED':
				self.status_label['text'] = 'Waiting for client to open'
				self.build.place_forget()
				self.scrollbar.place_forget()
				self.show_message_label()
			if status == 'CHANGED_SKIN':
				self.build.select_skin(message.message[0])

	def show_message_label(self):
		self.status_label.place(x=0, y=0, width=self.width, height=self.height)

	def events_handler(self, event):
		if event.widget == self and (self.winfo_width() != self.width or self.winfo_height() != self.height):
			if self.build is not None and self.build.winfo_ismapped():
				self.build.place(x=0, y=self.padding.top)
			self.ping.place(x=self.winfo_width() - self.ping.width - self.padding.right, y=self.winfo_height() - self.ping.height - self.padding.right)
			if self.scrollbar is not None and self.build.winfo_ismapped():
				self.scrollbar.place()

			self.width = self.winfo_width()
			self.height = self.winfo_height()

	def load_data(self):
		self.build.set_champion(self.backend.get_build())

	def show_data(self) -> None:
		self.build.place(x=0, y=self.padding.top)
		self.scrollbar.place()

	def show_skins(self) -> None:
		self.build.set_skins(self.backend.get_skins())

	def on_closing(self):
		self.backend.close()
		self.destroy()


if __name__ == '__main__':
	app = App()
	app.mainloop()
