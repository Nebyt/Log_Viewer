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
        self.main_space = main_space
        self.previous_key = ''
        self.main_foreground = 'white'
        self.main_background = '#696969'
        self.path_to_file = file_path
        self.error_state = BooleanVar()
        self.warn_state = BooleanVar()
        self.debug_state = BooleanVar()
        self.info_state = BooleanVar()
        self.word_highlight_state = BooleanVar()
        self.word_filter_state = BooleanVar()
        self.__end = 0
        self.search_err_index = '1.0'
        self.search_warn_index = '1.0'
        self.search_debug_index = '1.0'
        self.search_info_index = '1.0'
        self.search_word_index = '1.0'
        self.tags_dict = {}
        self.need_check = {}
        self.standart_word = ('error', 'warn', 'debug', 'info')
        self.input_word = StringVar()
        self.all_visible_text = ''

        # создаем на вкладке объект документа, который читаем
        self.document = Tail(file_path)

        # объект вкладка
        self.page = ttk.Frame(self.main_space)

        # нижняя область для чек боксов
        self.bottom_frame = ttk.Frame(self.page)

        # имя вкладки, берем последнее значение после разделения по символу

        self.__tab_name_expect = file_path.split('/')[-1]
        self.tab_name = self.__set_tab_name(self.__tab_name_expect)
        self.txt = tkinter.Text(self.page,
                                font=('{0} {1}'.format(WindowSetting.font_family, WindowSetting.font_size)),
                                spacing3=WindowSetting.spacing_btwn_str,
                                background=self.main_background,
                                foreground=self.main_foreground,
                                cursor='arrow')
        self.scroll = tkinter.Scrollbar(self.txt)
        self.txt.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.txt.yview, cursor='arrow')
        self.bottom_frame.pack(side='bottom', fill=tkinter.X)

        self.input_field = tkinter.Entry(self.bottom_frame, bd=3, textvariable=self.input_word)
        self.input_field.pack(side='right', fill=tkinter.X, expand=True)
        self.input_field.bind('<KeyPress>', self.__key_check)

        self.word_highlight_checkbox = tkinter.Checkbutton(self.bottom_frame, text='Highlight word', bd=4,
                                                           variable=self.word_highlight_state,
                                                           onvalue=True,
                                                           offvalue=False,
                                                           font="TextFont 11",
                                                           command=self.__highlight_word_starter)
        self.word_highlight_checkbox.pack(side='right')

        self.txt.pack(side='top', fill='both', expand=True)
        self.scroll.pack(side='right', fill=tkinter.Y)

        # тэги для выделения слов
        self.txt.tag_config("custom", background="orange", foreground="black")

        # добавляем вкладку
        main_space.add(self.page, text='{}'.format(self.tab_name))

        # при нажатии на кнопку END начинается просмотр последних данных
        self.txt.bind('<End>', self.__watch_tail)

        # при 2-м клике останавливаем просмотр
        self.txt.bind('<Double-Button-1>', self.__stop_watch_tail)

        # вставляем текст из нашего документа
        self.txt.insert(tkinter.END, self.document.get_lines())
        # закрываем возможность редактировать
        self.txt.config(state='disabled')

        # поток для выделения введенного слова
        self.thread_highlight_word = threading.Thread(target=self.__highlight_word,
                                                      args=[self.search_word_index],
                                                      daemon=True,
                                                      name='highlight_word')
        # поток для просмотра последней строки
        self.thread_show_last_string = threading.Thread(target=self.__shows_the_last_string,
                                                        daemon=True,
                                                        name='watch_tail')

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
        return tab_name_expect

    def update_text(self):
        # Эта функция обновляет текст на вкладке
        try:
            self.txt.config(state='normal')
            self.txt.insert(tkinter.END, self.document.get_lines())
            self.txt.config(state='disabled')
        except tkinter.TclError:
            logging.warning('The tab is already closed')
            pass
        except AttributeError:
            logging.warning('The tab is already closed')
            pass

    def __shows_the_last_string(self):
        # На постоянке крутиться проверка для перехода к концу отображаемого
        while True:
            try:
                while self.__end:
                    try:
                        self.txt.see(tkinter.END)
                        time.sleep(1)
                    except AttributeError:
                        logging.warning('Tab is closed')
                time.sleep(1)
            except AttributeError as err:
                logging.warning('Object and attribute is deleted', err)

    def __watch_tail(self, event):
        # Запуск потока для постоянного просмотра последнего изменения
        self.__end = 1
        if not self.thread_show_last_string.isAlive():
            self.thread_show_last_string.start()
            logging.debug('Start thread to watch tail of file %s', self.__tab_name_expect)

    def __stop_watch_tail(self, event):
        # Меняем триггер просмотра последнего изменения
        self.__end = 0
        logging.debug('Pause thread to watch tail of file %s', self.__tab_name_expect)

    def __search_word(self, word, start_index):
        # Поиск первой позиции слова от заданной первой позиции
        # Возращаем позицию первого символа и последнего
        pos = self.txt.search(word, start_index, tkinter.END, nocase=True)
        if pos:
            string, sym = pos.split('.')
            new_sym = str(int(sym) + len(word))
            next_start_index = '{0}.{1}'.format(string, new_sym)
            self.search_word_index = next_start_index
            try:
                self.tags_dict[word].append(pos)
            except KeyError:
                logging.debug('Add word "{0}" to dictionary of words'.format(word))
                self.tags_dict[word] = [pos]
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __highlight_word_starter(self):
        # Запуск потока для поиска и выделения заданного слова
        if not self.thread_highlight_word.isAlive():
            self.thread_highlight_word.start()
            logging.debug('Start thread to watch "%s" word in file %s',
                          self.input_word.get().strip(),
                          self.__tab_name_expect)

    def __get_input_text(self):
        # Получаем слово из поля ввода
        input_text = self.input_word.get().strip().lower()
        return input_text

    def __highlight_word(self, start_index):
        # Выделение найденного слова из поля ввода
        next_index = start_index
        while True:
            try:
                word = self.__get_input_text()
                while self.word_highlight_state.get():
                    self.input_field.config(state='disabled')
                    if word not in self.need_check.keys():
                        self.need_check[word] = False
                        next_index = '1.0'
                    if self.need_check[word]:
                        self.__highlight_again(word)
                    first_sym, last_sym = self.__search_word(word, start_index=next_index)
                    if last_sym:
                        next_index = last_sym
                        self.txt.tag_add('custom', first_sym, last_sym)
                    else:
                        time.sleep(1)
                self.input_field.config(state='normal')
                self.__unhighlight(word)
                time.sleep(1)
            except AttributeError as err:
                logging.warning('Object and attribute is deleted', err)

    def __unhighlight(self, tag_word):
        # Удаляем тэги
        try:
            if not self.need_check[tag_word]:
                logging.debug('Unhighlight "%s" word in file %s', tag_word, self.__tab_name_expect)
                length_of_word = len(tag_word)
                tag = 'custom'
                for position in self.tags_dict[tag_word]:
                    string, sym = position.split('.')
                    last_symbol = str(int(sym) + length_of_word)
                    last_index = '{0}.{1}'.format(string, last_symbol)
                    self.txt.tag_remove(tag, position, last_index)
                self.need_check[tag_word] = True
        except KeyError:
            return

    def __highlight_again(self, word):
        # Повторная подсветка уже найденных слов
        length_of_word = len(word)
        tag = 'custom'
        for position in self.tags_dict[word]:
            string, sym = position.split('.')
            last_symbol = str(int(sym) + length_of_word)
            last_index = '{0}.{1}'.format(string, last_symbol)
            self.txt.tag_add(tag, position, last_index)
        self.need_check[word] = False

    def get_all_text(self):
        # Возвращем весь текст со вкладки
        self.all_visible_text = self.txt.get(1.0, tkinter.END)
        return self.all_visible_text

    def change_font(self, font, size, spacing):
        self.txt.config(font=('{0} {1}'.format(font, size)), spacing3=int(spacing))

    def clear_memory_text(self):
        self.all_visible_text = ''

    def __key_check(self, event):
        actual_keycode = event.keycode

        try:
            clipboard_text = self.main_space.clipboard_get()
        except tkinter.TclError:
            logging.info('Clipboard is empty')
            clipboard_text = ''
            pass
        len_clipboard_text = len(clipboard_text)
        entry_text = event.widget.get()
        count_sym = len(entry_text)

        if self.previous_key == 17 and actual_keycode == 86:
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
                if self.previous_key == 17 and actual_keycode == 86:
                    event.widget.insert(text_index, clipboard_text)
                    event.widget.icursor(text_index + len_clipboard_text)
                    return 'break'
                else:
                    pass

        elif count_sym < 100:
            self.previous_key = actual_keycode
            pass

        elif actual_keycode in (8, 37, 39, 8, 46) or event.widget.selection_present():
            if count_sym > 100:
                event.widget.delete(100, tkinter.END)
            self.previous_key = actual_keycode
            pass

        elif self.previous_key == 17 and actual_keycode == 65:
            event.widget.select_range(0, tkinter.END)
            event.widget.icursor(tkinter.END)

        elif self.previous_key == 17 and actual_keycode == 67:
            selected_text = event.widget.selection_present()
            self.main_space.clipboard_append(selected_text)

        elif count_sym > 100:
            event.widget.delete(100, tkinter.END)
            self.previous_key = actual_keycode

        else:
            self.previous_key = actual_keycode
            return 'break'

    def clear_tab(self):
        del self.document
        for elem in self.tags_dict:
            self.tags_dict[elem] = None
        del self.tags_dict
        del self.thread_highlight_word
        del self.thread_show_last_string
        self.txt.delete('1.0', tkinter.END)
        del self.txt
        del self.main_foreground
        del self.main_background
        del self.path_to_file
        del self.error_state
        del self.warn_state
        del self.debug_state
        del self.info_state
        del self.word_highlight_state
        del self.word_filter_state
        del self.__end
        del self.search_err_index
        del self.search_warn_index
        del self.search_debug_index
        del self.search_info_index
        del self.search_word_index
        del self.need_check
        del self.standart_word
        del self.input_word
        del self.all_visible_text
        self.page.destroy()
        del self.page
        del self.bottom_frame
        gc.collect()
