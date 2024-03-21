from tkinter import Frame, Button
from lolwidgets.utils import Position


class VerticalScrollBar(Frame):
    def __init__(self, master, child_w, width: float = 16, pivotcolor: str = '#808080', *args, **kargs) -> None:
        Frame.__init__(self, master, *args, **kargs)
        self.width = width
        self.height = 0
        self.scroll_target = child_w
        self.button_height = 0
        self.ratio = 0
        self.button = Button(self, width=self.width, bg=pivotcolor, borderwidth=0)
        self.button_position = Position(x=0, y=0)
        self.child_position = Position(x=0, y=0)
        self.bind('<Button-1>', self.move_button)
        self.bind('<B1-Motion>', self.move_button)
        self.button.bind('<Button-1>', self.move_button)
        self.button.bind('<B1-Motion>', self.move_button)
        self.master.bind('<MouseWheel>', self.move_wheel)

    def place(self):
        self.master.update()
        self.scroll_target.update()
        self.height = self.master.winfo_height()
        self.child_position.x = self.scroll_target.winfo_rootx() - self.master.winfo_rootx()
        self.child_position.y = self.scroll_target.winfo_rooty() - self.master.winfo_rooty()
        self.button_height = min(self.height / self.scroll_target.height, 1) * self.height
        self.ratio = self.scroll_target.height / self.height
        self.button_position.y = - self.child_position.y / self.ratio
        if self.height == self.button_height:
            super().place_forget()
            return
        super().place(x=self.master.winfo_width()-self.width, y=0, height=self.height, width=self.width)
        self.button.place(x=self.button_position.x, y=self.button_position.y, height=self.button_height, width=self.width)

    def move_button(self, e):
        self.button_position.y = min(max(0, e.y_root - self.winfo_rooty() - self.button_height / 2), self.height-self.button_height)
        self.child_position.y = -self.ratio * self.button_position.y
        self.button.place(x=self.button_position.x, y=self.button_position.y, width=self.width)
        self.scroll_target.place(x=self.child_position.x, y=self.child_position.y)

    def move_wheel(self, e):
        if not self.winfo_ismapped():
            return
        change = max(min(e.delta, self.button_position.y), self.button_position.y - self.height + self.button_height)
        self.button_position.y -= change
        self.child_position.y += change * self.ratio
        self.button.place(x=self.button_position.x, y=self.button_position.y, width=self.width)
        self.scroll_target.place(x=self.child_position.x, y=self.child_position.y)
