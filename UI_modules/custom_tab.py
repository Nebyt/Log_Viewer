from modules.loader import Tail
import tkinter
from tkinter import ttk
from tkinter import BooleanVar, StringVar
import threading
import time
from modules.list_of_tab import list_of_tab
import logging
from UI_modules.window_settings import WindowSetting


class Tab:
    def __init__(self, main_space, file_path=''):
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
        self.tags_dict = {'error': [], 'warn': [], 'debug': [], 'info': []}
        self.need_check = {'error': False, 'warn': False, 'debug': False, 'info': False}
        self.standart_word = ('error', 'warn', 'debug', 'info')
        self.input_word = StringVar()
        self.all_visible_text = ''

        # создаем на вкладке объект документа, который читаем
        self.document = Tail(file_path)

        # объект вкладка
        self.page = ttk.Frame(main_space)

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

        self.error_checkbox = tkinter.Checkbutton(self.bottom_frame, text='Error', bd=4,
                                                  variable=self.error_state,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  font="TextFont 11",
                                                  command=self.__highlight_error_starter)
        self.error_checkbox.pack(side='left')
        self.warn_checkbox = tkinter.Checkbutton(self.bottom_frame, text='Warn', bd=4,
                                                 variable=self.warn_state,
                                                 onvalue=True,
                                                 offvalue=False,
                                                 font="TextFont 11",
                                                 command=self.__highlight_warn_starter)
        self.warn_checkbox.pack(side='left')
        self.debug_checkbox = tkinter.Checkbutton(self.bottom_frame, text='Debug', bd=4,
                                                  variable=self.debug_state,
                                                  onvalue=True,
                                                  offvalue=False,
                                                  font="TextFont 11",
                                                  command=self.__highlight_debug_starter)
        self.debug_checkbox.pack(side='left')
        self.info_checkbox = tkinter.Checkbutton(self.bottom_frame, text='Info', bd=4,
                                                 variable=self.info_state,
                                                 onvalue=True,
                                                 offvalue=False,
                                                 font="TextFont 11",
                                                 command=self.__highlight_info_starter)
        self.info_checkbox.pack(side='left')
        self.input_field = tkinter.Entry(self.bottom_frame, bd=4, textvariable=self.input_word, width=20)
        self.input_field.pack(side='right')
        self.word_highlight_checkbox = tkinter.Checkbutton(self.bottom_frame, text='Highlight word', bd=4,
                                                           variable=self.word_highlight_state,
                                                           onvalue=True,
                                                           offvalue=False,
                                                           font="TextFont 11",
                                                           command=self.__highlight_word_starter)
        self.word_highlight_checkbox.pack(side='right')
        #self.word_filter_checkbox = tkinter.Checkbutton(self.bottom_frame, text='Filter by word', bd=4,
        #                                                variable=self.word_filter_state,
        #                                                onvalue=True,
        #                                                offvalue=False,
        #                                                font="TextFont 11",
        #                                                command=self.__highlight_word_starter)
        #self.word_filter_checkbox.pack(side='right')

        self.txt.pack(side='top', fill='both', expand=True)
        self.scroll.pack(side='right', fill=tkinter.Y)

        # тэги для выделения слов
        self.txt.tag_config("error", background="red", foreground="yellow")
        self.txt.tag_config("warn", background="yellow", foreground="dodger blue")
        self.txt.tag_config("debug", background="blue", foreground="white")
        self.txt.tag_config("info", background="green2", foreground="blue")
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

        # поток для выделения ERROR
        self.thread_highlight_error = threading.Thread(target=self.__highlight_error,
                                                       args=['error',self.search_err_index],
                                                       daemon=True,
                                                       name='highlight_error')
        # поток для выделения WARN
        self.thread_highlight_warn = threading.Thread(target=self.__highlight_warn,
                                                      args=['warn', self.search_warn_index],
                                                      daemon=True,
                                                      name='highlight_warn')
        # поток для выделения DEBUG
        self.thread_highlight_debug = threading.Thread(target=self.__highlight_debug,
                                                       args=['debug', self.search_debug_index],
                                                       daemon=True,
                                                       name='highlight_debug')
        # поток для выделения INFO
        self.thread_highlight_info = threading.Thread(target=self.__highlight_info,
                                                      args=['info', self.search_info_index],
                                                      daemon=True,
                                                      name='highlight_info')
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
        self.__name, self.__file_fmt = tab_name_expect.split('.')
        self.__all_tabs = list_of_tab.get_all_tab()
        self.__count = 1
        for tab in self.__all_tabs:
            if tab.tab_name == tab_name_expect:
                tab_name_expect = '{0}({1}).{2}'.format(self.__name, self.__count, self.__file_fmt)
                self.__count += 1
        return tab_name_expect

    def update_text(self):
        # Эта функция обновляет текст на вкладке
        self.txt.config(state='normal')
        self.txt.insert(tkinter.END, self.document.get_lines())
        self.txt.config(state='disabled')

    def __shows_the_last_string(self):
        # На постоянке крутиться проверка для перехода к концу отображаемого
        while True:
            while self.__end:
                self.txt.see(tkinter.END)
                time.sleep(1)
            time.sleep(1)

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

    def __search_error(self, word, start_index):
        # Поиск первой позиции ERROR от заданной первой позиции
        # Возращаем позицию первого символа и последнего
        pos = self.txt.search(word, start_index, tkinter.END, nocase=True)
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
        # Поиск первой позиции WARN от заданной первой позиции
        # Возращаем позицию первого символа и последнего
        pos = self.txt.search(word, start_index, tkinter.END, nocase=True)
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
        # Поиск первой позиции DEBUG от заданной первой позиции
        # Возращаем позицию первого символа и последнего
        pos = self.txt.search(word, start_index, tkinter.END, nocase=True)
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
        # Поиск первой позиции INFO от заданной первой позиции
        # Возращаем позицию первого символа и последнего
        pos = self.txt.search(word, start_index, tkinter.END, nocase=True)
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
                self.tags_dict[word] = [pos]
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __highlight_error_starter(self):
        # Запуск потока для поиска и выделения слова ERROR
        if not self.thread_highlight_error.isAlive():
            self.thread_highlight_error.start()
            logging.debug('Start thread to watch ERROR of file %s', self.__tab_name_expect)

    def __highlight_warn_starter(self):
        # Запуск потока для поиска и выделения слова WARN
        if not self.thread_highlight_warn.isAlive():
            self.thread_highlight_warn.start()
            logging.debug('Start thread to watch WARNING of file %s', self.__tab_name_expect)

    def __highlight_debug_starter(self):
        # Запуск потока для поиска и выделения слова DEBUG
        if not self.thread_highlight_debug.isAlive():
            self.thread_highlight_debug.start()
            logging.debug('Start thread to watch DEBUG of file %s', self.__tab_name_expect)

    def __highlight_info_starter(self):
        # Запуск потока для поиска и выделения слова INFO
        if not self.thread_highlight_info.isAlive():
            self.thread_highlight_info.start()
            logging.debug('Start thread to watch INFO of file %s', self.__tab_name_expect)

    def __highlight_word_starter(self):
        # Запуск потока для поиска и выделения заданного слова
        if not self.thread_highlight_word.isAlive():
            self.thread_highlight_word.start()
            logging.debug('Start thread to watch "%s" word in file %s',
                          self.input_word.get().strip(),
                          self.__tab_name_expect)

    def __highlight_error(self, word, start_index):
        # Выделение найденного ERROR
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
        # Выделение найденного WARN
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
        # Выделение найденного DEBUG
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
        # Выделение найденного INFO
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

    def __get_input_text(self):
        # Получаем слово из поля ввода
        input_text = self.input_word.get().strip().lower()
        return input_text

    def __highlight_word(self, start_index):
        # Выделение найденного слова из поля ввода
        next_index = start_index
        while True:
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

    def __unhighlight(self, tag_word):
        # Удаляем тэги
        try:
            if not self.need_check[tag_word]:
                logging.debug('Unhighlight "%s" word in file %s', tag_word, self.__tab_name_expect)
                length_of_word = len(tag_word)
                if tag_word.lower() not in self.standart_word:
                    tag = 'custom'
                else:
                    tag = tag_word
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
        if word not in self.standart_word:
            tag = 'custom'
        else:
            tag = word
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
