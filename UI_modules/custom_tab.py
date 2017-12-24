from modules.loader import Tail
import tkinter
from tkinter import ttk
import threading
import time
from modules.list_of_tab import list_of_tab


class Tab:
    def __init__(self, main_space, file_path=''):
        self.path_to_file = file_path
        self.__end = 0
        self.search_index = '1.0'
        self.all_visible_text = ''
        self.document = Tail(file_path)  # создаем на вкладке объект документа, который читаем
        self.page = ttk.Frame(main_space)  # объект вкладка
        self.__tab_name_expect = file_path.split('/')[-1]  # имя вкладки, берем последнее значение после разделения по символу /

        self.tab_name = self.__set_tab_name(self.__tab_name_expect)
        self.txt = tkinter.Text(self.page, font="TextFont", spacing3=2)  # объект текстовое поле
        self.scroll = tkinter.Scrollbar(self.txt)  # объект скролбарр на вкладку

        self.txt.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.txt.yview)  # прикрепляем скроллбар к текстовому полю

        self.txt.pack(side='top', fill='both', expand=True)  # задаем размещение текстового поле
        self.scroll.pack(side='right', fill=tkinter.Y)  # задаем размещение скроллбара

        self.txt.tag_config("red", background="red", foreground="white")

        main_space.add(self.page, text='{}'.format(self.tab_name))  # добавляем вкладку

        self.txt.bind('<End>', self.__watch_tail)  # при нажатии на кнопку END начинается просмотр последних данных
        self.txt.bind('<Double-Button-1>', self.__stop_watch_tail)  # при 2-м клике останавливаем просмотр

        self.txt.insert(tkinter.END, self.document.get_lines())  # вставляем текст из нашего документа
        self.txt.config(state='disabled')  # закрываем возможность редактировать
        self.thread_highlight = threading.Thread(target=self.__highlight_word,
                                                 args=['error', self.search_index],
                                                 daemon=True,
                                                 name='__highlight_red')  # поток для выделения текста
        self.thread_show_last_string = threading.Thread(target=self.__shows_the_last_string,
                                                        daemon=True,
                                                        name='__watch_tail')  # поток для просмотра последней строки
        self.thread_highlight.start()

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

    def __search_word(self, word, start_index):
        """Find first position of the word, from start position"""
        pos = self.txt.search(word, start_index, tkinter.END)
        if pos:
            string, sym = pos.split('.')
            new_sym = str(int(sym) + len(word))
            next_start_index = '{0}.{1}'.format(string, new_sym)
            self.search_index = next_start_index
            return pos, next_start_index
        else:
            next_start_index = ''
            return pos, next_start_index

    def __highlight_word(self, word, start_index):
        next_index = start_index
        while True:
            first_sym, last_sym = self.__search_word(word, start_index=next_index)
            if last_sym:
                next_index = last_sym
                self.txt.tag_add('red', first_sym, last_sym)
            else:
                time.sleep(1)

    def get_all_text(self):
        self.all_visible_text = self.txt.get(1.0, tkinter.END)
        return self.all_visible_text
