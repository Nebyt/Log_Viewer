#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter
import os


class SearchWindow():
    def __init__(self, text):
        self.width = 300
        self.height = 50
        self.text = text
        self.last_search = '1.0'
        self.top = tkinter.Toplevel(padx=1, pady=1, relief='flat')
        self.start_pos_x = int((self.top.winfo_screenwidth() / 2) - (self.width / 2))
        self.start_pos_y = int((self.top.winfo_screenheight() / 2.5) - (self.height / 2))
        self.top.title("Settings")
        self.top.geometry('{0}x{1}+{2}+{3}'.format(self.width, self.height,
                                                   self.start_pos_x, self.start_pos_y))
        self.frame_1 = tkinter.Frame(self.top)
        self.frame_2 = tkinter.Frame(self.top)
        self.button_next = tkinter.Button(self.frame_2, text='Next >>', command=self.__next_result)
        self.button_previous = tkinter.Button(self.frame_2, text='<< Previous', command=self.__previous_result)
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
        self.search_field.focus_set()
        self.top.mainloop()

    def __new_pos(self, pos, word):
        string, sym = pos.split('.')
        new_pos = str(int(sym) + len(word))
        second_pos = '{0}.{1}'.format(string, new_pos)
        return second_pos

    def __next_result(self):
        word = self.search_field.get()
        if self.last_search == '1.0':
            pos = self.text.search(word, self.last_search, tkinter.END, forwards=True, nocase=True)
            second_pos = self.__new_pos(pos, word)
            self.text.tag_add(tkinter.SEL, pos, second_pos)
            self.text.see(pos)
        else:
            next_start_index = self.__new_pos(self.last_search, word)
            pos = self.text.search(word, next_start_index, tkinter.END, forwards=True, nocase=True)
            second_pos = self.__new_pos(pos, word)
            self.text.tag_add(tkinter.SEL, pos, second_pos)
            self.text.see(pos)
        print(pos)
        self.last_search = pos

    def __previous_result(self):
        word = self.search_field.get()
        if self.last_search == '1.0':
            print('This is begin')
        else:
            pos = self.text.search(word, self.last_search, '1.0', backwards=True, nocase=True)
            if not pos:
                self.last_search = '1.0'
            else:
                self.last_search = pos
            print(self.last_search)

    def __key_check(self):

        pass