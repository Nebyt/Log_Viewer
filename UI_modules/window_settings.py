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
        self.__width = 250
        self.__height = 200
        self.__top = tkinter.Toplevel(padx=1, pady=1)
        self.__aval_fonts = []
        for elem in tkinter.font.families(self.__top):
            if ' ' in elem:
                elem = ''.join(elem.split(' '))
            self.__aval_fonts.append(elem)
        self.__aval_fonts.sort()
        self.__font_size = StringVar()
        self.__spaces = StringVar()
        self.__font_var = StringVar()
        self.__start_pos_x = int((self.__top.winfo_screenwidth() / 2) - (self.__width / 2))
        self.__start_pos_y = int((self.__top.winfo_screenheight() / 2.5) - (self.__height / 2))
        self.__top.title("Settings")
        self.__top.geometry('{0}x{1}+{2}+{3}'.format(self.__width, self.__height,
                                                     self.__start_pos_x, self.__start_pos_y))
        self.__frame_1 = tkinter.Frame(self.__top)
        self.__frame_1.pack(side='top', fill=tkinter.X, expand=True)
        self.__frame_2 = tkinter.Frame(self.__top)
        self.__frame_2.pack(side='top', fill=tkinter.X, expand=True)
        self.__frame_3 = tkinter.Frame(self.__top)
        self.__frame_3.pack(side='top', fill=tkinter.X, expand=True)
        self.__frame_4 = tkinter.Frame(self.__top)
        self.__frame_4.pack(side='bottom', fill=tkinter.X)

        self.__size_label = tkinter.Label(self.__frame_1, text='Font size :')
        self.__font_size.set(WindowSetting.font_size)
        self.__input_size = tkinter.Entry(self.__frame_1, bd=1, width=2, textvariable=self.__font_size)
        self.__input_size.bind('<KeyPress>', self.__key_check)
        self.__size_label.pack(side='left')
        self.__input_size.pack(side='left')

        self.__font_label = tkinter.Label(self.__frame_2, text='Font families :')
        self.__font_var.set(WindowSetting.font_family)
        self.__font_dropdown_menu = ttk.Combobox(self.__frame_2, textvariable=self.__font_var, state='readonly')
        self.__font_dropdown_menu['values'] = self.__aval_fonts
        self.__font_dropdown_menu.config(width=80)
        self.__font_label.pack(side='left')
        self.__font_dropdown_menu.pack(side='left', expand=False)
        self.__font_dropdown_menu.bind('<KeyPress>', self.__sort_by_key)

        self.__spacing_label = tkinter.Label(self.__frame_3, text='Spaces between strings :')
        self.__spaces.set(WindowSetting.spacing_btwn_str)
        self.__input_spacing = tkinter.Entry(self.__frame_3, bd=1, width=2, textvariable=self.__spaces)
        self.__input_spacing.bind('<KeyPress>', self.__key_check)
        self.__spacing_label.pack(side='left')
        self.__input_spacing.pack(side='left')

        self.__top.maxsize(self.__width, self.__height)
        self.__top.resizable(0, 0)
        if os.name == 'nt':
            self.__top.attributes('-toolwindow', 1)

        self.__cancel_btn = tkinter.Button(self.__frame_4, text="Cancel", command=self.__cancel_button)
        self.__cancel_btn.pack(side='right', expand=False)
        self.__save_btn = tkinter.Button(self.__frame_4, text="Save", command=self.__save_button)
        self.__save_btn.pack(side='right', expand=True)

    def show(self):
        self.__top.focus_set()
        self.__top.mainloop()

    def __save_button(self):
        new_font_family = self.__font_dropdown_menu.get()
        new_font_size = self.__input_size.get()
        new_spacing = self.__input_spacing.get()

        WindowSetting.font_family = new_font_family
        WindowSetting.font_size = new_font_size
        WindowSetting.spacing_btwn_str = new_spacing

        for tab in list_of_tab.get_all_tab():
            tab.change_font(new_font_family, new_font_size, new_spacing)
        self.__top.destroy()

    def __cancel_button(self):
        self.__top.destroy()

    def __key_check(self, event):
        count_sym = len(event.widget.get())
        if event.char.isdigit():
            if count_sym < 2:
                pass
            elif event.widget.selection_present():
                pass
            else:
                return 'break'
        elif event.keycode in (8, 37, 39, 8, 46) or event.widget.selection_present():
            if event.char.isdigit():
                pass
            else:
                return 'break'
        else:
            return 'break'

    def __sort_by_key(self, event):
        letter = event.char
        for sym in event.widget['values']:
            if letter.upper() == sym[0].upper():
                event.widget.set(sym)
                break