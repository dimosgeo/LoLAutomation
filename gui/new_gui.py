import time
from utils import utils
from tkinter import Tk, Label
from utils import Spacing, Padding
from lolwidgets import Build, PingLabel, VerticalScrollBar
from PIL import Image, ImageTk
from controller import Controller


class App(Tk):
	def __init__(self, development_mode: int = None):
		Tk.__init__(self)
		# self.dev_mode = development_mode
		self.start = time.time()
		self.controller = Controller(self, mode=development_mode)

		self.title('LOL Assistant')
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.configure(bg=utils.colors['background'])
		self.bind("<Configure>", self.events_handler)
		self.resizable(width=False, height=False)
		self.icon = ImageTk.PhotoImage(Image.open('images/icon.png'))
		self.iconbitmap(default='images/icon.png')
		# self.model = Backend(self.dev_mode)
		self.build = None
		self.scrollbar = None
		self.navigation_images = None

		self.spacing = Spacing(vertical=20, horizontal=20)  # FILE
		self.padding = Padding(top=0, left=20, right=20, bottom=20)  # FILE

		self.screenwidth = self.winfo_screenwidth()
		self.screenheight = self.winfo_screenheight()
		self.height = int(self.screenheight * 0.5)
		self.width = int(self.screenwidth * 0.2)
		alignstr = f'{self.width}x{self.height}+{(self.screenwidth - self.width) // 2}+{(self.screenheight - self.height) // 2}'

		self.geometry(alignstr)
		self.wm_iconphoto(False, self.icon)
		self.status_label = Label(self, text='Waiting for client to open', font=utils.fonts['normal'], bg=self['bg'], foreground='white')
		self.ping = PingLabel(self, background=utils.colors['transparent'], foreground='#3BA55C')

		# self.after(1000, self.get_ping)
		self.controller.start()
		print(f'Start time: {time.time() - self.start}')

	def add_build(self) -> None:
		self.navigation_images = self.controller.get_lane_navigation_icons()
		self.build = Build(self, rune_icons=self.controller.get_runes(), lane_navigation_icons=self.controller.get_lane_navigation_icons(), set_skin_function=self.controller.set_active_skin, swap_spell_function=self.controller.swap_spells, set_client_data_func=self.set_client_data)
		self.width = self.build.width
		self.height = self.build.height
		alignstr = f'{self.width}x{self.height}+{(self.screenwidth - self.width) // 2}+{(self.screenheight - self.height) // 2}'
		self.geometry(alignstr)
		self.scrollbar = VerticalScrollBar(self, width=16, background=utils.colors['background'], child_w=self.build)

	def get_ping(self) -> None:
		self.ping['text'] = self.controller.ping()
		self.ping.place(x=self.winfo_width() - self.ping.width - self.padding.right, y=self.winfo_height() - self.ping.height - self.padding.bottom)
		self.ping.lift()
		self.after(1000, self.get_ping)

	def show_status_label(self):
		self.status_label.place(x=0, y=0, width=self.width, height=self.height)

	def events_handler(self, event) -> None:
		if event.widget == self and (self.winfo_width() != self.width or self.winfo_height() != self.height):
			if self.build is not None and self.build.winfo_ismapped():
				self.build.place(x=0, y=self.padding.top)
			self.ping.place(x=self.winfo_width() - self.ping.width - self.padding.right, y=self.winfo_height() - self.ping.height - self.padding.right)
			if self.scrollbar is not None and self.build.winfo_ismapped():
				self.scrollbar.place()

			self.width = self.winfo_width()
			self.height = self.winfo_height()

	def set_client_data(self, data):
		self.controller.set_client_data(data)

	def load_champion_data(self, build) -> None:
		self.after(0, self.build.set_champion, build)

	def show_data(self) -> None:
		self.build.place(x=0, y=self.padding.top)
		self.scrollbar.place()

	def set_active_skin(self, index: int):
		self.build.select_skin(index)

	def hide_build(self):
		self.build.place_forget()
		self.scrollbar.place_forget()

	def hide_status_label(self) -> None:
		self.status_label.place_forget()

	def set_status_label_text(self, text: str) -> None:
		self.status_label['text'] = text

	def show_skins(self, skins_list) -> None:
		self.build.set_skins(skins_list)

	def on_closing(self) -> None:
		self.controller.close()
		self.controller.join()
		self.destroy()


if __name__ == '__main__':
	app = App()
	app.mainloop()
