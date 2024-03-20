import tkinter as tk
from tkinter.font import Font
from PIL import ImageTk, Image
from utils import utils
from lolwidgets.descriptionLabel import DescriptionLabel


class AbilitiesTable(tk.Frame):
    def __init__(self, parent, cell_size: int, border_size: int, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.ability_buttons = ['P', 'Q', 'W', 'E', 'R']
        self['bg'] = utils.widget_color
        self.cell_size = cell_size
        self.border_size = border_size
        self.width = (self.cell_size + self.border_size) * 19 + self.border_size
        self.height = (self.cell_size + self.border_size) * 5 + self.border_size
        self.table: list = [[tk.Label(self, font=Font(family="Helvetica", size=12, weight="bold"), bg=utils.background_color, fg='white', bd=0) for _ in range(19)] for _ in range(5)]
        self.old_order = []
        self.descriptionLabel = DescriptionLabel(self.winfo_toplevel(), bg='black', foreground='white', anchor='nw')
        self.icons = []

        for index, cell in enumerate(self.table[0][1:], start=1):
            cell['text'] = index
            cell['bg'] = utils.palette[0]

    def set_abilities(self, ability_list) -> None:
        self.icons = []
        for cell in range(5):
            self.table[cell][0].destroy()
            self.table[cell][0] = tk.Label(self, bd=0)
            self.icons.append(ImageTk.PhotoImage(Image.open(ability_list[cell]['icon']).resize((self.cell_size, self.cell_size))))
            self.table[cell][0]['image'] = self.icons[-1]
            self.table[cell][0]['bg'] = utils.background_color
            self.table[cell][0]['bd'] = 0
            
            if ability_list[cell]['name']:
                self.table[cell][0].bind('<Enter>', self.create_lambda(ability_list[cell]['name']))
                self.table[cell][0].bind('<Leave>', lambda *args: self.descriptionLabel.hide_description())

    def create_lambda(self, name):
        return lambda *args: self.descriptionLabel.show_description(name, args[0])

    def set_ability_order(self, ability_order_list) -> None:
        for lvl, ability in enumerate(self.old_order, start=1):
            self.table[ability][lvl]['text'] = ''
            self.table[ability][lvl]['bg'] = utils.background_color

        for lvl, ability in enumerate(ability_order_list, start=1):
            self.table[ability][lvl]['text'] = self.ability_buttons[ability]
            self.table[ability][lvl]['bg'] = '#008000'

        self.old_order = ability_order_list

    def place(self, x=0, y=0):
        super().place(x=x, y=y, height=self.height, width=self.width)
        y = self.border_size

        for row in self.table:
            x = self.border_size
        
            for cell in row:
                cell.place(x=x, y=y, width=self.cell_size, height=self.cell_size)
                x += self.cell_size + self.border_size
        
            y += self.cell_size + self.border_size
