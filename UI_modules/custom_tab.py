from modules.loader import Tail
import tkinter
from tkinter import ttk
from tkinter import BooleanVar
import threading
import time
from modules.list_of_tab import list_of_tab
import random


class Tab:
    def __init__(self, main_space, file_path=''):
        self.main_foreground = 'white'
        self.main_background = '#696969'
        self.path_to_file = file_path
        self.error_state = BooleanVar()
        self.warn_state = BooleanVar()
        self.debug_state = BooleanVar()
        self.info_state = BooleanVar()
        self.custom_state = BooleanVar()
        self.__end = 0
        self.search_err_index = '1.0'
        self.search_warn_index = '1.0'
        self.search_debug_index = '1.0'
        self.search_info_index = '1.0'
        self.search_word_index = '1.0'
        self.tags_dict = {'error': [], 'warn': [], 'debug': [], 'info': []}  # добавлять значение в словарь при поиске по слову кастомному
        self.need_check = {'error': False, 'warn': False, 'debug': False, 'info': False}
        self.input_word = None
        self.all_visible_text = ''
        self.document = Tail(file_path)  # создаем на вкладке объект документа, который читаем

        self.page = ttk.Frame(main_space)  # объект вкладка
        self.bottom_frame = ttk.Frame(self.page)
        self.__tab_name_expect = file_path.split('/')[-1]  # имя вкладки,
        # берем последнее значение после разделения по символу /

        self.tab_name = self.__set_tab_name(self.__tab_name_expect)
        self.txt = tkinter.Text(self.page,
                                font="TextFont",
                                spacing3=2,
                                background=self.main_background,
                                foreground=self.main_foreground)  # объект текстовое поле
        self.scroll = tkinter.Scrollbar(self.txt)  # объект скролбарр на текстовое поле

        self.txt.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.txt.yview)  # прикрепляем скроллбар к текстовому полю

        self.bottom_frame.pack(side='bottom', fill=tkinter.X)
        self.error_checkbox = tkinter.Checkbutton(self.bottom_frame, text='error',
                                                  variable=self.error_state,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  command=self.__highlight_error_starter)
        self.error_checkbox.pack(side='left')
        self.warn_checkbox = tkinter.Checkbutton(self.bottom_frame, text='warn',
                                                 variable=self.warn_state,
                                                 onvalue=True,
                                                 offvalue=False,
                                                 command=self.__highlight_warn_starter)
        self.warn_checkbox.pack(side='left')
        self.debug_checkbox = tkinter.Checkbutton(self.bottom_frame, text='debug',
                                                  variable=self.debug_state,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  command=self.__highlight_debug_starter)
        self.debug_checkbox.pack(side='left')
        self.info_checkbox = tkinter.Checkbutton(self.bottom_frame, text='info',
                                                 variable=self.info_state,
                                                 onvalue=True,
                                                 offvalue=False,
                                                 command=self.__highlight_info_starter)
        self.info_checkbox.pack(side='left')

        self.txt.pack(side='top', fill='both', expand=True)  # задаем размещение текстового поле
        self.scroll.pack(side='right', fill=tkinter.Y)  # задаем размещение скроллбара

        self.txt.tag_config("error", background="red", foreground="yellow")
        self.txt.tag_config("warn", background="yellow", foreground="dodger blue")
        self.txt.tag_config("debug", background="blue", foreground="white")
        self.txt.tag_config("info", background="green2", foreground="blue")
        self.txt.tag_config("main", background=self.main_background, foreground=self.main_foreground)

        main_space.add(self.page, text='{}'.format(self.tab_name))  # добавляем вкладку

        self.txt.bind('<End>', self.__watch_tail)  # при нажатии на кнопку END начинается просмотр последних данных
        self.txt.bind('<Double-Button-1>', self.__stop_watch_tail)  # при 2-м клике останавливаем просмотр

        self.txt.insert(tkinter.END, self.document.get_lines())  # вставляем текст из нашего документа
        self.txt.config(state='disabled')  # закрываем возможность редактировать

        self.thread_highlight_error = threading.Thread(target=self.__highlight_error,
                                                     args=['error', self.search_err_index],
                                                     daemon=True,
                                                     name='highlight_error')  # поток для выделения ошибок

        self.thread_highlight_warn = threading.Thread(target=self.__highlight_warn,
                                                     args=['warn', self.search_warn_index],
                                                     daemon=True,
                                                     name='highlight_warn')  # поток для выделения ошибок

        self.thread_highlight_debug = threading.Thread(target=self.__highlight_debug,
                                                     args=['debug', self.search_debug_index],
                                                     daemon=True,
                                                     name='highlight_debug')  # поток для выделения ошибок

        self.thread_highlight_info = threading.Thread(target=self.__highlight_info,
                                                     args=['info', self.search_info_index],
                                                     daemon=True,
                                                     name='highlight_info')  # поток для выделения ошибок

        self.thread_highlight_word = threading.Thread(target=self.__highlight_word,
                                                     args=[self.input_word, self.search_word_index],
                                                     daemon=True,
                                                     name='highlight_word')  # поток для выделения ошибок

        self.thread_show_last_string = threading.Thread(target=self.__shows_the_last_string,
                                                        daemon=True,
                                                        name='watch_tail')  # поток для просмотра последней строки

    def __set_tab_name(self, tab_name_expect):
        self.__name, self.__file_fmt = tab_name_expect.split('.')
        self.__all_tabs = list_of_tab.get_all_tab()
        self.__count = 1
        for tab in self.__all_tabs:
            if tab.tab_name == tab_name_expect:
                tab_name_expect = '{0}({1}).{2}'.format(self.__name, self.__count, self.__file_fmt)
                self.__count += 1
        return tab_name_expect

    def update_text(self):
        """Эта функция должна была обновлять текст на вкладке"""
        self.txt.config(state='normal')
        self.txt.insert(tkinter.END, self.document.get_lines())
        self.txt.config(state='disabled')

    def __shows_the_last_string(self):
        """На постоянке крутиться проверка для перехода к концу"""
        while True:
            while self.__end:
                self.txt.see(tkinter.END)
                time.sleep(1)
            time.sleep(1)

    def __watch_tail(self, event):
        """запуск потока для постоянного просмотра последнего файла"""
        self.__end = 1
        if not self.thread_show_last_string.isAlive():
            self.thread_show_last_string.start()

    def __stop_watch_tail(self, event):
        """останавливаем цикл, который постоянно мониторит последнюю строку"""
        self.__end = 0

    def __search_error(self, word, start_index):
        """Find first position of the word, from start position"""
        pos = self.txt.search(word, start_index, tkinter.END)
        if pos:
            string, sym = pos.split('.')
            new_sym = str(int(sym) + len(word))
            next_start_index = '{0}.{1}'.format(string, new_sym)
            self.search_err_index = next_start_index
            self.tags_dict[word].append(pos)
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __search_warn(self, word, start_index):
        """Find first position of the word, from start position"""
        pos = self.txt.search(word, start_index, tkinter.END)
        if pos:
            string, sym = pos.split('.')
            new_sym = str(int(sym) + len(word))
            next_start_index = '{0}.{1}'.format(string, new_sym)
            self.search_warn_index = next_start_index
            self.tags_dict[word].append(pos)
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __search_debug(self, word, start_index):
        """Find first position of the word, from start position"""
        pos = self.txt.search(word, start_index, tkinter.END)
        if pos:
            string, sym = pos.split('.')
            new_sym = str(int(sym) + len(word))
            next_start_index = '{0}.{1}'.format(string, new_sym)
            self.search_debug_index = next_start_index
            self.tags_dict[word].append(pos)
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __search_info(self, word, start_index):
        """Find first position of the word, from start position"""
        pos = self.txt.search(word, start_index, tkinter.END)
        if pos:
            string, sym = pos.split('.')
            new_sym = str(int(sym) + len(word))
            next_start_index = '{0}.{1}'.format(string, new_sym)
            self.search_info_index = next_start_index
            self.tags_dict[word].append(pos)
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __search_word(self, word, start_index):
        """Find first position of the word, from start position"""
        pos = self.txt.search(word, start_index, tkinter.END)
        if pos:
            string, sym = pos.split('.')
            new_sym = str(int(sym) + len(word))
            next_start_index = '{0}.{1}'.format(string, new_sym)
            self.search_word_index = next_start_index
            self.tags_dict[word].append(pos)
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __highlight_error_starter(self):
        if not self.thread_highlight_error.isAlive():
            self.thread_highlight_error.start()

    def __highlight_warn_starter(self):
        if not self.thread_highlight_warn.isAlive():
            self.thread_highlight_warn.start()

    def __highlight_debug_starter(self):
        if not self.thread_highlight_debug.isAlive():
            self.thread_highlight_debug.start()

    def __highlight_info_starter(self):
        if not self.thread_highlight_info.isAlive():
            self.thread_highlight_info.start()

    def __highlight_word_starter(self):
        if not self.thread_highlight_word.isAlive():
            self.thread_highlight_word.start()

    def __highlight_error(self, word, start_index):
        next_index = start_index
        while True:
            while self.error_state.get():
                if self.need_check[word]:
                    self.__highlight_again(word)
                first_sym, last_sym = self.__search_error(word, start_index=next_index)
                if last_sym:
                    next_index = last_sym
                    self.txt.tag_add(word, first_sym, last_sym)
                else:
                    time.sleep(1)
            self.__unhighlight(word.lower())
            time.sleep(1)

    def __highlight_warn(self, word, start_index):
        next_index = start_index
        while True:
            while self.warn_state.get():
                if self.need_check[word]:
                    self.__highlight_again(word)
                first_sym, last_sym = self.__search_warn(word, start_index=next_index)
                if last_sym:
                    next_index = last_sym
                    self.txt.tag_add(word, first_sym, last_sym)
                else:
                    time.sleep(1)
            self.__unhighlight(word.lower())
            time.sleep(1)

    def __highlight_debug(self, word, start_index):
        next_index = start_index
        while True:
            while self.debug_state.get():
                if self.need_check[word]:
                    self.__highlight_again(word)
                first_sym, last_sym = self.__search_debug(word, start_index=next_index)
                if last_sym:
                    next_index = last_sym
                    self.txt.tag_add(word, first_sym, last_sym)
                else:
                    time.sleep(1)
            self.__unhighlight(word.lower())
            time.sleep(1)

    def __highlight_info(self, word, start_index):
        next_index = start_index
        while True:
            while self.info_state.get():
                if self.need_check[word]:
                    self.__highlight_again(word)
                first_sym, last_sym = self.__search_info(word, start_index=next_index)
                if last_sym:
                    next_index = last_sym
                    self.txt.tag_add(word, first_sym, last_sym)
                else:
                    time.sleep(1)
            self.__unhighlight(word.lower())
            time.sleep(1)

    def __highlight_word(self, word, start_index):
        next_index = start_index
        while True:
            while self.custom_state.get():
                if self.need_check[word]:
                    self.__highlight_again(word)
                first_sym, last_sym = self.__search_word(word, start_index=next_index)
                if last_sym:
                    next_index = last_sym
                    self.txt.tag_add('main', first_sym, last_sym)
                else:
                    time.sleep(1)
            self.__unhighlight(word.lower())
            time.sleep(1)

    def __unhighlight(self, tag_word):
        lenght_of_word = len(tag_word)
        for position in self.tags_dict[tag_word]:
            string, sym = position.split('.')
            last_symbol = str(int(sym) + lenght_of_word)
            last_index = '{0}.{1}'.format(string, last_symbol)
            self.txt.tag_remove(tag_word, position, last_index)
        self.need_check[tag_word] = True

    def __highlight_again(self, word):
        length_of_word = len(word)
        for position in self.tags_dict[word]:
            string, sym = position.split('.')
            last_symbol = str(int(sym) + length_of_word)
            last_index = '{0}.{1}'.format(string, last_symbol)
            self.txt.tag_add(word, position, last_index)
            print(word, position, last_index)
        self.need_check[word] = False

    def get_all_text(self):
        self.all_visible_text = self.txt.get(1.0, tkinter.END)
        return self.all_visible_text
