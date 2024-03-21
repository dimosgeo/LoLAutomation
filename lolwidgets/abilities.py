import tkinter as tk
from typing import Callable, List
from PIL import ImageTk, Image
from utils import utils
from lolwidgets.descriptionLabel import DescriptionLabel


class AbilitiesTable(tk.Frame):
    def __init__(self, parent: tk.Misc, cell_size: int, border_size: int, *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.ability_buttons = ['P', 'Q', 'W', 'E', 'R']
        self['bg'] = utils.colors['widget_highlight']
        self.cell_size = cell_size
        self.border_size = border_size
        self.width = (self.cell_size + self.border_size) * 19 + self.border_size
        self.height = (self.cell_size + self.border_size) * 5 + self.border_size
        self.table: list = [[tk.Label(self, font=utils.fonts['normal'], bg=utils.colors['background'], fg='white', bd=0) for _ in range(19)] for _ in range(5)]
        self.old_order = []
        self.descriptionLabel = DescriptionLabel(self.winfo_toplevel(), bg='black', foreground='white', anchor='nw')
        self.icons = []

        for index, cell in enumerate(self.table[0][1:], start=1):
            cell['text'] = index
            cell['bg'] = utils.colors['background_widget']

    def set_abilities(self, ability_list: List) -> None:
        self.icons = []
        for cell in range(5):
            self.table[cell][0].destroy()
            self.table[cell][0] = tk.Label(self, bd=0)
            self.icons.append(ImageTk.PhotoImage(Image.open(ability_list[cell]['icon']).resize((self.cell_size, self.cell_size))))
            self.table[cell][0]['image'] = self.icons[-1]
            self.table[cell][0]['bg'] = utils.colors['background']
            self.table[cell][0]['bd'] = 0
            
            if ability_list[cell]['name']:
                self.table[cell][0].bind('<Enter>', self.create_lambda(ability_list[cell]['name']))
                self.table[cell][0].bind('<Leave>', lambda *args: self.descriptionLabel.hide_description())

    def create_lambda(self, name: str) -> Callable[[str], None]:
        return lambda *args: self.descriptionLabel.show_description(name, args[0].widget)

    def set_ability_order(self, ability_order_list: List[int]) -> None:

        for lvl, ability in enumerate(self.old_order, start=1):
            self.table[ability][lvl]['text'] = ''
            self.table[ability][lvl]['bg'] = utils.colors['background']

        for lvl, ability in enumerate(ability_order_list, start=1):
            self.table[ability][lvl]['text'] = self.ability_buttons[ability]
            self.table[ability][lvl]['bg'] = '#008000'

        self.old_order = ability_order_list

    def place(self, x: int = 0, y: int = 0) -> None:
        super().place(x=x, y=y, height=self.height, width=self.width)
        y = self.border_size

        for row in self.table:
            x = self.border_size
        
            for cell in row:
                cell.place(x=x, y=y, width=self.cell_size, height=self.cell_size)
                x += self.cell_size + self.border_size
        
            y += self.cell_size + self.border_size
