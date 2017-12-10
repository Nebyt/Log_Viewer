import tkinter
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from loader import Tail
import time
import threading

# список всех вкладок
list_of_tab = []


# объект вкладка
class Tab:
    def __init__(self, main_space, file_path=''):
        self.document = Tail(file_path)  # создаем на вкладке объект документа, который читаем
        self.page = ttk.Frame(main_space)  # объект вкладка
        self.tab_name = file_path.split('/')[-1]  # имя вкладки, берем последнее значение после разделения по символу /

        self.scroll = tkinter.Scrollbar(self.page)  # объект скролбарр на вкладку
        self.txt = tkinter.Text(self.page, font="TextFont", yscrollcommand=self.scroll.set)  # объект текстовое поле

        self.scroll.config(command=self.txt.yview)  # прикрепляем скроллбар к текстовому полю

        self.txt.pack(side='left', fill='both', expand=True)  # задаем размещение текстового поле
        self.scroll.pack(side='right', fill=tkinter.Y)  # задаем размещение скроллбара

        main_space.add(self.page, text='{}'.format(self.tab_name))  # добавляем вкладку

        self.txt.insert(tkinter.END, self.document.get_lines())  # вставляем текст из нашего документа

    def update_text(self):
        """Эта функция должна была обновлять текст на вкладке"""
        self.txt.insert(tkinter.END, self.document.get_lines())


# диалоговое окно открытия файла, возвращает путь к файлу
def path_to_file():
    op = askopenfilename()
    return op


# обновление информации на всех вкладках
def update_tabs():
    while True:
        for line in list_of_tab:
            line.update_text()
        time.sleep(1)


# добавление вкладки
def add_tab():
    file_path = path_to_file()
    if file_path:
        list_of_tab.append(Tab(nb, file_path))
    else:
        return


# здесь начинается описание UI
root = tkinter.Tk()
app_width = int(root.winfo_screenwidth() / 2)
app_height = int(root.winfo_screenheight() / 2)
start_pos_x = int(root.winfo_screenwidth() / 4)
start_pos_y = int(root.winfo_screenheight() / 5)
root.title('LogViewer')
root.geometry('{0}x{1}+{2}+{3}'.format(app_width, app_height, start_pos_x, start_pos_y))

m = tkinter.Menu(root)
root.config(menu=m)
m.add_command(label="Open...", command=add_tab)

# Defines and places the notebook widget
nb = ttk.Notebook(root)
nb.pack(fill='both', expand='yes')
# здесь заканчивается описание UI


thread_update_tabs = threading.Thread(target=update_tabs, daemon=True, name='update_tabs')
thread_update_tabs.start()
root.mainloop()  # запуск отрисовки UI
