import tkinter
import os


class ModalWindow:
    def __init__(self):
        self.width = 200
        self.height = 100
        self.top = tkinter.Toplevel()
        self.start_pos_x = int((self.top.winfo_screenwidth() / 2) - (self.width / 2))
        self.start_pos_y = int((self.top.winfo_screenheight() / 2.5) - (self.height / 2))
        self.top.title("Warning!")
        self.top.geometry('{0}x{1}+{2}+{3}'.format(self.width, self.height,
                                                   self.start_pos_x, self.start_pos_y))
        self.top.maxsize(self.width, self.height)
        self.top.resizable(0, 0)
        if os.name == 'nt':
            self.top.attributes('-toolwindow', 1)

        self.msg = tkinter.Message(self.top, text="This is does't text file!", justify='left', width=190)
        self.msg.pack(side='top', fill='both', expand=True)

        self.button = tkinter.Button(self.top, text="Close", command=self.top.destroy)
        self.button.pack(side='top', expand=True)

    def show(self):
        self.top.mainloop()