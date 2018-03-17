#! /usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter
from tkinter import font
from tkinter import StringVar
from tkinter import ttk
import os
from modules.list_of_tab import list_of_tab
from tkinter.colorchooser import askcolor
import logging
import json


class WindowSetting:
    font_family = ''
    font_size = None
    spacing_btwn_str = None
    font_color = ''
    background_color = ''
    directory = os.path.join(os.path.expandvars('%Appdata%'), 'pyLogViewer')
    file_conf = 'pyLogViewer.json'
    file_directory = os.path.join(directory, file_conf)

    def __init__(self):
        self.read_setting()
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
        self.__font_color = StringVar()
        self.__font_color.set(WindowSetting.font_color)
        self.__background_color = StringVar()
        self.__background_color.set(WindowSetting.background_color)
        self.__start_pos_x = int((self.__top.winfo_screenwidth() / 2) - (self.__width / 2))
        self.__start_pos_y = int((self.__top.winfo_screenheight() / 2.5) - (self.__height / 2))
        self.__top.title("Settings")
        self.__top.geometry('{0}x{1}+{2}+{3}'.format(self.__width, self.__height,
                                                     self.__start_pos_x, self.__start_pos_y))
        self.__top.maxsize(self.__width, self.__height)
        self.__top.resizable(0, 0)
        if os.name == 'nt':
            self.__top.attributes('-toolwindow', 'true')
        self.__top.attributes('-topmost', 'true')

        self.__frame_1 = tkinter.Frame(self.__top)
        self.__frame_1.pack(side='top', fill=tkinter.X, expand=True)
        self.__frame_2 = tkinter.Frame(self.__top)
        self.__frame_2.pack(side='top', fill=tkinter.X, expand=True)
        self.__frame_3 = tkinter.Frame(self.__top)
        self.__frame_3.pack(side='top', fill=tkinter.X, expand=True)
        self.__frame_4 = tkinter.Frame(self.__top)
        self.__frame_4.pack(side='top', fill=tkinter.X, expand=True)
        self.__frame_5 = tkinter.Frame(self.__top)
        self.__frame_5.pack(side='top', fill=tkinter.X, expand=True)
        self.__frame_6 = tkinter.Frame(self.__top)
        self.__frame_6.pack(side='bottom', fill=tkinter.X)

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

        self.__font_color_label = tkinter.Label(self.__frame_4, text="Font's color :")
        self.__font_color_panel = tkinter.Button(self.__frame_4,
                                                 width=2,
                                                 height=1,
                                                 background=WindowSetting.font_color,
                                                 command=self.__choose_color_font)

        self.__font_color_label.pack(side='left')
        self.__font_color_panel.pack(side='left')

        self.__background_label = tkinter.Label(self.__frame_4, text="Background's color :")
        self.__background_color_panel = tkinter.Button(self.__frame_4,
                                                 width=2,
                                                 height=1,
                                                 background=WindowSetting.background_color,
                                                 command=self.__choose_color_background)

        self.__background_color_panel.pack(side='right')
        self.__background_label.pack(side='right')

        self.__cancel_btn = tkinter.Button(self.__frame_6, text="Cancel", command=self.__cancel_button)
        self.__cancel_btn.pack(side='right', expand=False)
        self.__save_btn = tkinter.Button(self.__frame_6, text="Save", command=self.__save_button)
        self.__save_btn.pack(side='right', expand=True)

    def show(self):
        self.__top.focus_set()
        self.__top.mainloop()
        logging.info('Window of setting is showed')

    def read_setting(self):
        try:
            with open(WindowSetting.file_directory, 'r') as file:
                setting_info = json.load(file)
            WindowSetting.font_family = setting_info['font_family']
            WindowSetting.font_size = setting_info['font_size']
            WindowSetting.spacing_btwn_str = setting_info['spacing']
            WindowSetting.font_color = setting_info['font_color']
            WindowSetting.background_color = setting_info['background_color']
        except FileNotFoundError:
            logging.warning('File not found {0}'.format(WindowSetting.file_directory))
            if not os.path.exists(WindowSetting.directory):
                os.makedirs(WindowSetting.directory)
                with open(WindowSetting.file_directory, 'w') as file:
                    json_obj = json.dumps({'font_family': 'TextFont',
                                           'font_size': 12,
                                           'spacing': 2,
                                           'font_color': 'white',
                                           'background_color': 'grey'})
                    file.write(json_obj)
            logging.info('File of settings is created')
            WindowSetting.font_family = 'TextFont'
            WindowSetting.font_size = 12
            WindowSetting.spacing_btwn_str = 2
            WindowSetting.font_color = 'white'
            WindowSetting.background_color = 'gray'
        except PermissionError:
            logging.warning('Not have permission to {0}'.format(WindowSetting.file_directory))

    def __save_setting(self):
        try:
            with open(WindowSetting.file_directory, 'w') as file:
                json_obj = json.dumps({'font_family': WindowSetting.font_family,
                                       'font_size': WindowSetting.font_size,
                                       'spacing': WindowSetting.spacing_btwn_str,
                                       'font_color': WindowSetting.font_color,
                                       'background_color': WindowSetting.background_color})
                file.write(json_obj)
        except FileNotFoundError:
            logging.warning('File not found {0}'.format(WindowSetting.file_directory))
            if not os.path.exists(WindowSetting.directory):
                with open(WindowSetting.file_directory, 'w') as file:
                    json_obj = json.dumps({'font_family': WindowSetting.font_family,
                                           'font_size': WindowSetting.font_size,
                                           'spacing': WindowSetting.spacing_btwn_str,
                                           'font_color': WindowSetting.font_color,
                                           'background_color': WindowSetting.background_color})
                    file.write(json_obj)
            logging.warning('File not found {0}'.format(WindowSetting.file_directory))
        except PermissionError:
            logging.warning('Not have permission to {0}'.format(WindowSetting.file_directory))

    def __choose_color_font(self):
        font_color = askcolor()
        if font_color[1]:
            print(font_color)
            self.__font_color.set(font_color[1])
            self.__font_color_panel.config(background=font_color[1])
        self.__top.focus_set()

    def __choose_color_background(self):
        background_color = askcolor()
        if background_color[1]:
            print(background_color)
            self.__background_color.set(background_color[1])
            self.__background_color_panel.config(background=background_color[1])
        self.__top.focus_set()

    def __save_button(self):
        new_font_family = self.__font_dropdown_menu.get()
        new_font_size = self.__input_size.get()
        new_spacing = self.__input_spacing.get()
        new_font_color = self.__font_color.get()
        new_background_color = self.__background_color.get()

        WindowSetting.font_family = new_font_family
        WindowSetting.font_size = new_font_size
        WindowSetting.spacing_btwn_str = new_spacing
        WindowSetting.font_color = new_font_color
        WindowSetting.background_color = new_background_color


        for tab in list_of_tab.get_all_tab():
            tab.change_font(new_font_family, new_font_size, new_spacing, new_font_color, new_background_color)
        self.__save_setting()
        logging.info('Save change of font')
        self.__top.destroy()

    def __cancel_button(self):
        self.__top.destroy()
        logging.info("Close setting's window without saving")

    def __key_check(self, event):
        count_sym = len(event.widget.get())
        # print('keycode', event.keycode, '|','keysym', event.keysym, '|', 'char', event.char)
        if event.char.isdigit():
            if count_sym < 2:
                pass
            elif event.widget.selection_present():
                pass
            else:
                return 'break'
        elif event.keycode in (8, 37, 39, 46) or event.widget.selection_present():
            if event.char.isdigit():
                pass
            elif event.keycode in (8, 37, 39, 46):
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

if __name__ == '__main__':
    window = WindowSetting()
    window.show()