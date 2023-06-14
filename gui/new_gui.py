import time
from utils import utils
from tkinter import Tk, Label
from tkinter.font import Font
from backend import Backend
from lolwidgets import Spacing, Padding, Build, PingLabel, MyScrollBar
from threading import Thread
from PIL import Image, ImageTk


class App(Tk):
	def __init__(self):
		Tk.__init__(self)
		self.start = time.time()
		self.title('LOL Assistant')
		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		self.configure(bg=utils.background_color)
		self.bind("<Configure>", self.events_handler)
		self.resizable(width=False, height=False)

		self.icon = ImageTk.PhotoImage(Image.open('images/icon.png'))
		self.iconbitmap(default='images/icon.png')
		self.backend = Backend()
		self.build = None
		self.scrollbar = None
		self.navigation_images = None

		self.spacing = Spacing(vertical=20, horizontal=20)
		self.padding = Padding(top=0, left=20, right=20, bottom=20)

		self.screenwidth = self.winfo_screenwidth()
		self.screenheight = self.winfo_screenheight()
		self.height = int(self.screenheight * 0.8)
		self.width = 735
		alignstr = f'{self.width}x{self.height}+{(self.screenwidth - self.width) // 2}+{(self.screenheight - self.height) // 2}'

		self.geometry(alignstr)
		self.wm_iconphoto(False, self.icon)
		self.status_font = Font(family='Helvetica', size=14)
		self.status_label = Label(self, text='Waiting for client to open.', font=self.status_font, bg=self['bg'], foreground='white')
		self.status_label_width = self.status_font.measure(self.status_label['text'])
		self.status_label_height = self.status_font.metrics('linespace')
		self.ping = PingLabel(self, font_size=10, background=utils.background_color, foreground='#3BA55C')

		self.after(1000, self.get_ping)
		self.lolListener = Thread(target=self.lol_listener, daemon=True)
		self.lolListener.start()
		print(f'Start time: {time.time() - self.start}')

	def add_build(self):
		self.navigation_images = self.backend.get_navigation_icons()
		self.build = Build(self, backend=self.backend, background=utils.background_color)
		self.width = self.build.width
		alignstr = f'{self.width}x{self.height}+{(self.screenwidth - self.width) // 2}+{(self.screenheight - self.height) // 2}'
		self.geometry(alignstr)
		self.scrollbar = MyScrollBar(self, width=16, background=utils.background_color, child_w=self.build)

	def get_ping(self):
		self.ping['text'] = self.backend.ping()
		self.ping.place(x=self.winfo_width() - self.ping.width - self.padding.right, y=self.winfo_height() - self.ping.height - self.padding.bottom)
		self.ping.lift()
		self.after(1000, self.get_ping)

	def lol_listener(self):
		self.show_message_label()
		while True:
			status = self.backend.get_status()
			if status == 'PROCESS_CLOSED':
				break
			if status == 'GAME_OPENED':
				self.status_label['text'] = 'Waiting for champion pick.'
				self.add_build()
				self.show_message_label()
				# self.backend.champion_id = 84 # TEST
				# self.load_data() # TEST
			if status == 'CHAMPION_PICKED':
				self.status_label.place_forget()
				self.load_data()
			if status == 'GAME_CLOSED':
				self.status_label['text'] = 'Waiting for client to open.'
				self.build.place_forget()
				self.scrollbar.place_forget()
				self.show_message_label()

	def show_message_label(self):
		self.status_label_width = self.status_font.measure(self.status_label['text'])
		self.status_label.place(x=self.width / 2 - self.status_label_width / 2, y=self.height / 2 - self.status_label_height / 2, width=self.status_label_width, height=self.status_label_height)

	def events_handler(self, event):
		if event.widget == self and (self.winfo_width() != self.width or self.winfo_height() != self.height):
			if self.build is not None and self.build.winfo_ismapped():
				self.build.place(x=0, y=0)
			self.ping.place(x=self.winfo_width() - self.ping.width - self.padding.right, y=self.winfo_height() - self.ping.height - self.padding.right)
			if self.scrollbar is not None and self.build.winfo_ismapped():
				self.scrollbar.place()

			self.width = self.winfo_width()
			self.height = self.winfo_height()

	def load_data(self):
		self.build.set_champion(self.backend.get_build())
		self.build.place(x=0, y=self.padding.top)
		self.scrollbar.place()

	def on_closing(self):
		self.backend.close()
		self.lolListener.join()
		self.destroy()


if __name__ == '__main__':
	app = App()
	app.mainloop()
