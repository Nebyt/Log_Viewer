#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter
import os


class SearchWindow():
    def __init__(self):
        self.width = 300
        self.height = 50
        self.top = tkinter.Toplevel(padx=1, pady=1, relief='flat')
        self.start_pos_x = int((self.top.winfo_screenwidth() / 2) - (self.width / 2))
        self.start_pos_y = int((self.top.winfo_screenheight() / 2.5) - (self.height / 2))
        self.top.title("Settings")
        self.top.geometry('{0}x{1}+{2}+{3}'.format(self.width, self.height,
                                                   self.start_pos_x, self.start_pos_y))
        self.frame_1 = tkinter.Frame(self.top)
        self.frame_2 = tkinter.Frame(self.top)
        self.button_next = tkinter.Button(self.frame_2, text='Next >>')
        self.button_previous = tkinter.Button(self.frame_2, text='<< Previous')
        self.search_field = tkinter.Entry(self.frame_1)
        self.search_label = tkinter.Label(self.frame_1, text='Find: ')

        self.search_label.pack(side='left', expand=False)
        self.search_field.pack(side='right', fill=tkinter.X, expand=True)
        self.button_next.pack(side='right', fill=tkinter.BOTH, expand=True)
        self.button_previous.pack(side='left', fill=tkinter.BOTH, expand=True)
        self.frame_1.pack(side='top', fill=tkinter.X, expand=True)
        self.frame_2.pack(side='bottom', fill=tkinter.X, expand=True)

        self.top.maxsize(self.width, self.height)
        self.top.resizable(0, 0)
        if os.name == 'nt':
            self.top.attributes('-toolwindow', 1)

    def show(self):
        self.top.focus_set()
        self.top.attributes('-topmost', 'true')
        self.top.mainloop()

    def __next_result(self):
        pass

    def __previous_result(self):
        pass

    def __key_check(self):
        pass

if __name__ == '__main__':
    window = SearchWindow()
    window.show()