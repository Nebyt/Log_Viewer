#! /usr/bin/env python
# -*- coding: utf-8 -*-

from modules.loader import Tail
import tkinter
import gc
from tkinter import ttk
from tkinter import BooleanVar, StringVar
import threading
import time
from modules.list_of_tab import list_of_tab
import logging
from UI_modules.window_settings import WindowSetting


class Tab:

    def __init__(self, main_space, file_path=''):
        self.__main_space = main_space
        self.__previous_key = ''
        self.__search_panel_enabled = False
        self.path_to_file = file_path
        self.__word_highlight_state = BooleanVar()
        self.__chosen_string_state = BooleanVar()
        self.__end = False
        self.__search_word_index = '1.0'
        self.__tags_dict = {}
        self.__need_check = {}
        self.__input_word = StringVar()
        self.__all_visible_text = ''
        self.__last_search = '1.0'
        self.__previous_len = 0
        self.__first_filter = True
        self.__was_filtered = False
        self.__search_again = False

        # создаем на вкладке объект документа, который читаем
        self.__document = Tail(file_path)

        # объект вкладка
        self.__page = ttk.Frame(self.__main_space)

        # нижняя область для чек боксов
        self.__bottom_frame = ttk.Frame(self.__page)
        self.__highlight_panel = tkinter.Frame(self.__bottom_frame)

        # имя вкладки, берем последнее значение после разделения по символу

        self.__tab_name_expect = self.path_to_file.split('/')[-1]
        self.tab_name = self.__set_tab_name(self.__tab_name_expect)
        self.__txt = tkinter.Text(self.__page,
                                  font=('{0} {1}'.format(WindowSetting.font_family, WindowSetting.font_size)),
                                  spacing3=WindowSetting.spacing_btwn_str,
                                  background=WindowSetting.background_color,
                                  foreground=WindowSetting.font_color,
                                  cursor='arrow')
        self.__txt.focus()
        self.__scroll = tkinter.Scrollbar(self.__txt)
        self.__txt.config(yscrollcommand=self.__scroll.set)
        self.__scroll.config(command=self.__txt.yview, cursor='arrow')
        self.__bottom_frame.pack(side='bottom', fill=tkinter.X)

        self.__highlight_panel.pack(side='bottom', fill=tkinter.X)
        self.__input_field = tkinter.Entry(self.__highlight_panel, bd=3, textvariable=self.__input_word)
        self.__input_field.pack(side='right', fill=tkinter.X, expand=True)
        self.__input_field.bind('<KeyPress>', self.__key_check)

        self.__word_highlight_checkbox = tkinter.Checkbutton(self.__highlight_panel, text='Highlight word', bd=4,
                                                             variable=self.__word_highlight_state,
                                                             onvalue=True,
                                                             offvalue=False,
                                                             font="TextFont 11",
                                                             command=self.__highlight_word_starter)
        self.__word_highlight_checkbox.pack(side='right')

        self.__chosen_string_checkbox = tkinter.Checkbutton(self.__highlight_panel, text='Only string that contains', bd=4,
                                                            variable=self.__chosen_string_state,
                                                            onvalue=True,
                                                            offvalue=False,
                                                            font="TextFont 11")
        self.__chosen_string_checkbox.pack(side='right')

        self.__txt.pack(side='top', fill='both', expand=True)
        self.__scroll.pack(side='right', fill=tkinter.Y)

        # тэги для выделения слов
        self.__txt.tag_config("custom", background="orange", foreground="black")

        # добавляем вкладку
        self.__main_space.add(self.__page, text='{}'.format(self.tab_name))

        # при нажатии на кнопку END начинается просмотр последних данных
        self.__txt.bind('<End>', self.__watch_tail)
        self.__txt.bind('<Control-f>', self.__search_window)

        # при 2-м клике останавливаем просмотр
        self.__txt.bind('<Double-Button-1>', self.__stop_watch_tail)

        # вставляем текст из нашего документа
        self.__txt.insert(tkinter.END, self.__document.get_lines())
        # закрываем возможность редактировать
        self.__txt.config(state='disabled')

        # поток для выделения введенного слова
        self.__thread_highlight_word = threading.Thread(target=self.__highlight_word,
                                                        args=(self.__search_word_index,),
                                                        daemon=True,
                                                        name='highlight_word')
        # поток для просмотра последней строки
        self.__thread_show_last_string = threading.Thread(target=self.__shows_the_last_string,
                                                          daemon=True,
                                                          name='watch_tail')
        logging.info('New tab is created')

    def __set_tab_name(self, tab_name_expect):
        # установка имени вкладки, если вкладка с таким именем уже существет добаляем порядковый номер к названию файла
        self.__name, *self.__file_fmt = tab_name_expect.split('.')
        self.__all_tabs = list_of_tab.get_all_tab()
        self.__count = 1
        if len(self.__file_fmt) > 1:
            file_frmt = '.'.join(self.__file_fmt)
        elif len(self.__file_fmt) == 1:
            file_frmt = self.__file_fmt[0]
        else:
            file_frmt = ''
        for tab in self.__all_tabs:
            if tab.tab_name == tab_name_expect:
                tab_name_expect = '{0}({1}).{2}'.format(self.__name, self.__count, file_frmt)
                self.__count += 1
        logging.info('New tab name is {0}'.format(tab_name_expect))
        return tab_name_expect

    def update_text(self):
        # Эта функция обновляет текст на вкладке
        if self.__chosen_string_state.get():
            self.__chosen_string()
        else:
            if self.__was_filtered:
                highlight_before = self.__word_highlight_state.get()
                word = self.__get_input_text()
                if highlight_before:
                    self.__word_highlight_checkbox.deselect()
                self.__txt.config(state='normal')
                self.__txt.delete('1.0', tkinter.END)
                self.__txt.config(state='disabled')
                if not self.__word_highlight_state.get():
                    self.__input_field.config(state='normal')
                self.__was_filtered = False
                self.__search_word_index = '1.0'
                self.__tags_dict[word] = []
                if highlight_before:
                    self.__search_again = True
                    self.__word_highlight_checkbox.select()
            try:
                self.__first_filter = True
                self.__txt.config(state='normal')
                self.__txt.insert(tkinter.END, self.__document.get_lines())
                self.__txt.config(state='disabled')
            except (tkinter.TclError, AttributeError):
                logging.warning('The tab is already closed')
                pass

    def __shows_the_last_string(self):
        # На постоянке крутиться проверка для перехода к концу отображаемого
        while True:
            try:
                while self.__end:
                    try:
                        self.__txt.see(tkinter.END)
                        time.sleep(1)
                    except AttributeError:
                        logging.warning('Show_the_last_string: Tab is closed')
                        break
                time.sleep(1)
            except AttributeError:
                logging.warning('Show_the_last_string: Object and attribute is deleted')
                break

    def __watch_tail(self, event):
        # Запуск потока для постоянного просмотра последнего изменения
        self.__end = True
        if not self.__thread_show_last_string.isAlive():
            self.__thread_show_last_string.start()
            logging.debug('Start thread to watch tail of file %s', self.__tab_name_expect)

    def __stop_watch_tail(self, event):
        # Меняем триггер просмотра последнего изменения
        self.__end = False
        logging.debug('Pause thread to watch tail of file %s', self.__tab_name_expect)

    def __search_word(self, word, start_index):
        # Поиск первой позиции слова от заданной первой позиции
        # Возращаем позицию первого символа и последнего
        try:
            pos = self.__txt.search(word, start_index, tkinter.END, nocase=True)
        except tkinter.TclError as err:
            logging.warning('Object is deleted', err)
            return
        if pos:
            string, sym = pos.split('.')
            new_sym = str(int(sym) + len(word))
            next_start_index = '{0}.{1}'.format(string, new_sym)
            self.__search_word_index = next_start_index
            try:
                self.__tags_dict[word].append(pos)
            except KeyError:
                logging.debug('Add word "{0}" to dictionary of words'.format(word))
                self.__tags_dict[word] = [pos]
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __highlight_word_starter(self):
        # Запуск потока для поиска и выделения заданного слова
        if not self.__thread_highlight_word.isAlive():
            self.__thread_highlight_word.start()
            logging.debug('Start thread to watch "%s" word in file %s',
                          self.__input_word.get().strip(),
                          self.__tab_name_expect)

    def __get_input_text(self):
        # Получаем слово из поля ввода
        try:
            input_text = self.__input_word.get().strip().lower()
            return input_text
        except AttributeError:
            logging.warning('We have some error')

    def __highlight_word(self, start_index):
        # Выделение найденного слова из поля ввода
        next_index = start_index
        while True:
            try:
                word = self.__get_input_text()
                while self.__word_highlight_state.get():
                    try:
                        if self.__search_again:
                            next_index = '1.0'
                        self.__input_field.config(state='disabled')
                        if word not in self.__need_check.keys():
                            self.__need_check[word] = False
                            next_index = '1.0'
                        if self.__need_check[word]:
                            self.__highlight_again(word)
                        first_sym, last_sym = self.__search_word(word, start_index=next_index)
                        self.__search_again = False
                        if last_sym:
                            next_index = last_sym
                            self.__txt.tag_add('custom', first_sym, last_sym)
                        else:
                            time.sleep(1)
                    except tkinter.TclError:
                        logging.warning('Object is deleted')
                        break
                try:
                    if self.__chosen_string_state.get():
                        self.__unhighlight(word)
                    else:
                        self.__input_field.config(state='normal')
                        self.__unhighlight(word)
                    time.sleep(1)
                except tkinter.TclError:
                    logging.warning('Object is deleted')
                    break
            except AttributeError:
                logging.warning('Object and attribute is deleted')
                break

    def __unhighlight(self, tag_word):
        # Удаляем тэги
        try:
            if not self.__need_check[tag_word]:
                logging.debug('Unhighlight "%s" word in file %s', tag_word, self.__tab_name_expect)
                length_of_word = len(tag_word)
                tag = 'custom'
                for position in self.__tags_dict[tag_word]:
                    string, sym = position.split('.')
                    last_symbol = str(int(sym) + length_of_word)
                    last_index = '{0}.{1}'.format(string, last_symbol)
                    self.__txt.tag_remove(tag, position, last_index)
                self.__need_check[tag_word] = True
        except KeyError:
            return

    def __highlight_again(self, word):
        # Повторная подсветка уже найденных слов
        length_of_word = len(word)
        tag = 'custom'
        for position in self.__tags_dict[word]:
            string, sym = position.split('.')
            last_symbol = str(int(sym) + length_of_word)
            last_index = '{0}.{1}'.format(string, last_symbol)
            self.__txt.tag_add(tag, position, last_index)
        self.__need_check[word] = False

    def __chosen_string(self):
        word = self.__get_input_text()
        if self.__first_filter:
            try:
                self.__input_field.config(state='disabled')
                highlight_before = self.__word_highlight_state.get()
                if highlight_before:
                    self.__word_highlight_checkbox.deselect()
                self.__txt.config(state='normal')
                self.__txt.delete('1.0', tkinter.END)
                self.__txt.insert(tkinter.END, self.__document.get_chosen_lines(word))
                self.__txt.config(state='disabled')
                self.__search_word_index = '1.0'
                self.__tags_dict[word] = []
                if highlight_before:
                    self.__search_again = True
                    self.__word_highlight_checkbox.select()
                self.__first_filter = False
                self.__was_filtered = True
            except (tkinter.TclError, AttributeError):
                logging.warning('Chosen_string: The tab is already closed')
                pass
        else:
            try:
                self.__txt.config(state='normal')
                self.__txt.insert(tkinter.END, self.__document.get_chosen_lines(word))
                self.__txt.config(state='disabled')
            except (tkinter.TclError, AttributeError):
                logging.warning('Chosen_string: The tab is already closed')
                pass

    def __search_window(self, event):
        if not self.__search_panel_enabled:
            self.__search_panel = tkinter.Frame(self.__bottom_frame)
            self.__search_label = tkinter.Label(self.__search_panel, text='Find: ')
            self.__search_field = tkinter.Entry(self.__search_panel, bd=3)
            self.__button_previous = tkinter.Button(self.__search_panel,
                                                    text='<< Previous',
                                                    width=14,
                                                    command=self.__previous_result)
            self.__button_next = tkinter.Button(self.__search_panel,
                                                text='Next >>',
                                                width=14,
                                                command=self.__next_result)

            self.__search_panel.pack(side='top', fill=tkinter.X, expand=True)
            self.__search_label.pack(side='left')
            self.__search_field.pack(side='left', fill=tkinter.X, expand=True)
            self.__button_next.pack(side='right')
            self.__button_previous.pack(side='right')
            self.__search_field.bind('<KeyPress>', self.__key_check)

            self.__search_field.focus_set()
            self.__search_panel_enabled = True
            logging.info('Search panel is enabled')
        else:
            self.__search_panel.destroy()
            self.__search_panel_enabled = False
            logging.info('Search panel is closed')

    def __new_pos(self, pos, word):
        string, sym = pos.split('.')
        new_pos = str(int(sym) + len(word))
        second_pos = '{0}.{1}'.format(string, new_pos)
        return second_pos

    def __next_result(self):
        self.__txt.focus_set()
        word = self.__search_field.get()
        if self.__last_search == '1.0':
            pos = self.__txt.search(word, self.__last_search, tkinter.END, forwards=True, nocase=True)
            if pos:
                second_pos = self.__new_pos(pos, word)
                self.__txt.tag_add(tkinter.SEL, pos, second_pos)
                self.__txt.see(pos)
                self.__last_search = pos
            else:
                self.__last_search = '1.0'
        else:
            next_start_index = self.__new_pos(self.__last_search, word)
            pos = self.__txt.search(word, next_start_index, tkinter.END, forwards=True, nocase=True)
            if pos:
                self.__txt.tag_remove(tkinter.SEL, self.__last_search, tkinter.END)
                second_pos = self.__new_pos(pos, word)
                self.__txt.tag_add(tkinter.SEL, pos, second_pos)
                self.__txt.see(pos)
                self.__last_search = pos
            else:
                pos = self.__last_search
        logging.info('Next_result: Word {0} start on position {1}'.format(self.__last_search, word))

    def __previous_result(self):
        self.__txt.focus_set()
        word = self.__search_field.get()
        if self.__last_search == '1.0':
            logging.info('Previous_result: Search returned in the beginning')
        else:
            self.__txt.tag_remove(tkinter.SEL, self.__last_search, tkinter.END)
            pos = self.__txt.search(word, self.__last_search, '1.0', backwards=True, nocase=True)
            if not pos:
                self.__last_search = '1.0'
            else:
                self.__last_search = pos
                second_pos = self.__new_pos(pos, word)
                self.__txt.tag_add(tkinter.SEL, pos, second_pos)
                self.__txt.see(pos)
        logging.info('Previous_result: Word {0} start on position {1}'.format(self.__last_search, word))

    def get_all_text(self):
        # Возвращем весь текст со вкладки
        self.__all_visible_text = self.__txt.get(1.0, tkinter.END)
        logging.info('Get all text from the tab')
        return self.__all_visible_text

    def change_font(self, font, size, spacing, font_color, background_color):
        self.__txt.config(font=('{0} {1}'.format(font, size)),
                          spacing3=int(spacing),
                          foreground=font_color,
                          background=background_color)
        logging.info('Set new font = {0}, font size = {1}, spacing between string = {2}, font color {3},'
                     ' background color {4}'.format(font, size, spacing, font_color, background_color))

    def clear_memory_text(self):
        self.__all_visible_text = ''
        logging.debug('Clear text from variable')

    def __key_check(self, event):
        actual_keycode = event.keycode

        try:
            clipboard_text = self.__main_space.clipboard_get()
        except tkinter.TclError:
            logging.error('Key_check: Clipboard is empty')
            clipboard_text = ''
            pass
        len_clipboard_text = len(clipboard_text)
        entry_text = event.widget.get()
        count_sym = len(entry_text)

        if self.__previous_key == 17 and actual_keycode == 86:
            if event.widget.selection_present():
                event.widget.delete('sel.first', 'sel.last')

            entry_text = event.widget.get()
            count_sym = len(entry_text)
            symb_sum = len_clipboard_text + count_sym

            if symb_sum > 100:
                text_index = event.widget.index(tkinter.INSERT)
                dif = 100 - text_index
                if dif < len_clipboard_text:
                    cut_entry = entry_text[:text_index]
                    new_string = cut_entry + clipboard_text
                    new_string = new_string[:100]
                    event.widget.delete(0, tkinter.END)
                    event.widget.insert(0, new_string)
                    event.widget.icursor(tkinter.END)
                    return 'break'
                elif dif >= len_clipboard_text:
                    cut_entry_1 = entry_text[:text_index]
                    cut_entry_2 = entry_text[text_index:]
                    new_string = cut_entry_1 + clipboard_text + cut_entry_2
                    new_string = new_string[:100]
                    event.widget.delete(0, tkinter.END)
                    event.widget.insert(0, new_string)
                    event.widget.icursor(text_index + len_clipboard_text)
                    return 'break'
            else:
                text_index = event.widget.index(tkinter.INSERT)
                if self.__previous_key == 17 and actual_keycode == 86:
                    event.widget.insert(text_index, clipboard_text)
                    event.widget.icursor(text_index + len_clipboard_text)
                    return 'break'
                else:
                    pass

        elif count_sym < 100:
            self.__previous_key = actual_keycode
            pass

        elif actual_keycode in (8, 37, 39, 46) or event.widget.selection_present():
            if count_sym > 100:
                event.widget.delete(100, tkinter.END)
            self.__previous_key = actual_keycode
            pass

        elif self.__previous_key == 17 and actual_keycode == 65:
            event.widget.select_range(0, tkinter.END)
            event.widget.icursor(tkinter.END)

        elif self.__previous_key == 17 and actual_keycode == 67:
            selected_text = event.widget.selection_present()
            self.__main_space.clipboard_append(selected_text)

        elif count_sym > 100:
            event.widget.delete(100, tkinter.END)
            self.__previous_key = actual_keycode

        else:
            self.__previous_key = actual_keycode
            return 'break'

    def clear_tab(self):
        del self.__thread_highlight_word
        del self.__thread_show_last_string
        del self.__document
        for elem in self.__tags_dict:
            self.__tags_dict[elem] = None
        del self.__tags_dict
        self.__txt.delete('1.0', tkinter.END)
        del self.path_to_file
        del self.__word_highlight_state
        del self.__end
        del self.__search_word_index
        del self.__need_check
        del self.__input_word
        del self.__all_visible_text
        del self.__txt
        del self.__bottom_frame
        self.__page.destroy()
        del self.__page
        gc.collect()
        logging.debug('Delete the tab and all in the tab')
