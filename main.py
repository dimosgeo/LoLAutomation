from gui.new_gui import App
from sys import argv


def main():
	development_mode = 0
	if len(argv) == 2 and argv[1].isnumeric():
		development_mode = int(argv[1])
	app = App(development_mode=development_mode)
	app.mainloop()


if __name__ == '__main__':
	main()
