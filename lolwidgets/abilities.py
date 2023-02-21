import tkinter as tk
from tkinter.font import Font
from PIL import ImageTk, Image
from utils import utils


class AbilitiesTable(tk.Frame):
    def __init__(self, parent, cell_size: float, border_size: float, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.ability_buttons = ['P', 'Q', 'W', 'E', 'R']
        self.cell_size = cell_size
        self.border_size = border_size
        self.width = (self.cell_size + self.border_size) * 19 + self.border_size
        self.height = (self.cell_size + self.border_size) * 5 + self.border_size
        self.table: list = [[tk.Label(self, font=Font(family="Helvetica", size=12, weight="bold"), bg=utils.background_color) for _ in range(19)] for _ in range(5)]
        self.old_order = []

        for index, cell in enumerate(self.table[0][1:], start=1):
            cell['text'] = index
            cell['bg'] = '#808080'

    def set_abilities(self, ability_list) -> None:
        for cell in range(5):
            self.table[cell][0] = AbilityIcon(self, icon=ability_list[cell], size=int(self.cell_size), bd=0)

    def set_ability_order(self, ability_order_list) -> None:
        for lvl, ability in enumerate(self.old_order, start=1):
            self.table[ability][lvl]['text'] = ''
            self.table[ability][lvl]['bg'] = utils.background_color

        for lvl, ability in enumerate(ability_order_list, start=1):
            self.table[ability][lvl]['text'] = self.ability_buttons[ability]
            self.table[ability][lvl]['bg'] = '#008000'

        self.old_order = ability_order_list

    def place(self, x=0, y=0):
        super().place(x=x, y=y, height=(self.cell_size + self.border_size) * 5 + self.border_size, width=(self.cell_size + self.border_size) * 19 + self.border_size)
        y = self.border_size
        for row in self.table:
            x = self.border_size
            for cell in row:
                cell.place(x=x, y=y, width=self.cell_size, height=self.cell_size)
                x += self.cell_size + self.border_size
            y += self.cell_size + self.border_size


class AbilityCell(tk.Frame):
    def __init__(self, parent, size: float, *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.content = tk.Label(self, font=Font(family="Helvetica", size=12), bg=self['bg'])
        self.size = size

    def place(self, x=0, y=0):
        super().place(x=x, y=y, width=self.size, height=self.size)
        if self.content is not None:
            self.content.place(x=0, y=0, width=self.size, height=self.size)


class AbilityIcon(tk.Button):
    def __init__(self, parent: tk.Widget, icon: bytes, size: int, *args, **kwargs) -> None:
        tk.Button.__init__(self, parent, *args, **kwargs)
        self.icon = ImageTk.PhotoImage(Image.open(icon).resize((size, size)))
        self.size = size
        self['image'] = self.icon
