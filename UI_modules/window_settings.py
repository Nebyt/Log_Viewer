#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter
from tkinter import font
from tkinter import StringVar
from tkinter import ttk
import os
from modules.list_of_tab import list_of_tab


class WindowSetting:
    font_family = 'TextFont'
    font_size = 12
    spacing_btwn_str = 2

    def __init__(self):
        self.width = 250
        self.height = 200
        self.top = tkinter.Toplevel(padx=1, pady=1)
        self.aval_fonts = []
        for elem in tkinter.font.families(self.top):
            if ' ' in elem:
                elem = ''.join(elem.split(' '))
            self.aval_fonts.append(elem)
        self.aval_fonts.sort()
        self.__font_size = StringVar()
        self.__spaces = StringVar()
        self.__font_var = StringVar()
        self.start_pos_x = int((self.top.winfo_screenwidth() / 2) - (self.width / 2))
        self.start_pos_y = int((self.top.winfo_screenheight() / 2.5) - (self.height / 2))
        self.top.title("Settings")
        self.top.geometry('{0}x{1}+{2}+{3}'.format(self.width, self.height,
                                                   self.start_pos_x, self.start_pos_y))
        self.frame_1 = tkinter.Frame(self.top)
        self.frame_1.pack(side='top', fill=tkinter.X, expand=True)
        self.frame_2 = tkinter.Frame(self.top)
        self.frame_2.pack(side='top', fill=tkinter.X, expand=True)
        self.frame_3 = tkinter.Frame(self.top)
        self.frame_3.pack(side='top', fill=tkinter.X, expand=True)
        self.frame_4 = tkinter.Frame(self.top)
        self.frame_4.pack(side='bottom', fill=tkinter.X)

        self.size_label = tkinter.Label(self.frame_1, text='Font size :')
        self.__font_size.set(WindowSetting.font_size)
        self.input_size = tkinter.Entry(self.frame_1, bd=1, width=2, textvariable=self.__font_size)
        self.input_size.bind('<KeyPress>', self.__key_check)
        self.size_label.pack(side='left')
        self.input_size.pack(side='left')

        self.font_label = tkinter.Label(self.frame_2, text='Font families :')
        self.__font_var.set(WindowSetting.font_family)
        self.font_dropdown_menu = ttk.Combobox(self.frame_2, textvariable=self.__font_var)
        self.font_dropdown_menu['values'] = self.aval_fonts
        self.font_dropdown_menu.config(width=80)
        self.font_label.pack(side='left')
        self.font_dropdown_menu.pack(side='left', expand=False)

        self.spacing_label = tkinter.Label(self.frame_3, text='Spaces between strings :')
        self.__spaces.set(WindowSetting.spacing_btwn_str)
        self.input_spacing = tkinter.Entry(self.frame_3, bd=1, width=2, textvariable=self.__spaces)
        self.input_spacing.bind('<KeyPress>', self.__key_check)
        self.spacing_label.pack(side='left')
        self.input_spacing.pack(side='left')

        self.top.maxsize(self.width, self.height)
        self.top.resizable(0, 0)
        if os.name == 'nt':
            self.top.attributes('-toolwindow', 1)

        self.cancel_btn = tkinter.Button(self.frame_4, text="Cancel", command=self.__cancel_button)
        self.cancel_btn.pack(side='right', expand=False)
        self.save_btn = tkinter.Button(self.frame_4, text="Save", command=self.__save_button)
        self.save_btn.pack(side='right', expand=True)

    def show(self):
        self.top.focus_set()
        self.top.mainloop()

    def __save_button(self):
        new_font_family = self.font_dropdown_menu.get()
        new_font_size = self.input_size.get()
        new_spacing = self.input_spacing.get()

        WindowSetting.font_family = new_font_family
        WindowSetting.font_size = new_font_size
        WindowSetting.spacing_btwn_str = new_spacing

        #TODO add checking for unsupported fonts
        for tab in list_of_tab.get_all_tab():
            tab.change_font(new_font_family, new_font_size, new_spacing)
        self.top.destroy()

    def __cancel_button(self):
        self.top.destroy()

    def __key_check(self, event):
        count_sym = len(event.widget.get())
        if event.char.isdigit():
            if count_sym < 2:
                pass
            elif event.widget.selection_present():
                pass
            else:
                return 'break'
        elif event.keysym in ('BackSpace', 'Left', 'Right', 'Tab', 'Delete') or event.widget.selection_present():
            if event.char.isdigit():
                pass
            else:
                return 'break'
        else:
            return 'break'