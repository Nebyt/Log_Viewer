import tkinter
from tkinter.filedialog import askopenfilename
import time
import threading
import os
import mimetypes
from UI_modules.custom_notebook import CustomNotebook
from UI_modules.custom_tab import Tab
from UI_modules.modal_window import ModalWindow
from modules.saver import Saver
from modules.list_of_tab import list_of_tab


APP_WIDTH_WIN = 750
APP_WIDTH_LINUX = 825
APP_HEIGHT = 400


# список всех вкладок
list_of_tab = list_of_tab


# диалоговое окно открытия файла, возвращает путь к файлу
def path_to_file():
    op = askopenfilename(defaultextension='.log',
                         filetypes=(("Log files", ".log"),
                                    ("Text files", ".txt"),
                                    ("All files", ".*")))
    return op


def save_file(tabs=list_of_tab.get_all_tab()):
    tab_name = nb.tab(nb.select(), 'text')
    saver = Saver(tabs, tab_name)
    saver.save_one()


def save_all_file(tabs=list_of_tab.get_all_tab()):
    saver = Saver(tabs)
    saver.save_all()


# обновление информации на всех вкладках
def update_tabs():
    while True:
        for line in list_of_tab.get_all_tab():
            line.update_text()
        time.sleep(1)


# добавление вкладки
def add_tab():
    file_path = path_to_file()
    if file_path:
        type_of_file = mimetypes.guess_type(file_path)

        if type_of_file[0]:
            type_of_file = type_of_file[0].split('/')[0]

        if type_of_file == 'text' or not type_of_file[0]:
            list_of_tab.add_tab(Tab(nb, file_path))
        else:
            file_name = file_path.split('/')[-1]
            modal_window = ModalWindow(file_name)
            modal_window.show()
    else:
        return


if os.name == 'posix':
    app_width = APP_WIDTH_LINUX
    path_to_icon = ''
else:
    app_width = APP_WIDTH_WIN
    path_to_icon = 'icons\icon.ico'
    path_to_icon = os.path.join(os.getcwd(), path_to_icon)

# здесь начинается описание UI
root = tkinter.Tk()

app_height = APP_HEIGHT
start_pos_x = int(root.winfo_screenwidth() / 2) - int((app_width / 2))
start_pos_y = int(root.winfo_screenheight() / 2.5) - int((app_height / 2))

menu_bar = tkinter.Menu(root, tearoff=False)
save_button = tkinter.Menu(root)

root.config(menu=menu_bar)

submenu = tkinter.Menu(menu_bar, tearoff=False)
save_submenu = tkinter.Menu(submenu)

menu_bar.add_cascade(label='File', menu=submenu)
submenu.add_command(label="Open file", command=add_tab)
submenu.add_cascade(label='Save..', menu=save_submenu)
save_submenu.add_command(label='Save active', command=save_file)
save_submenu.add_command(label='Save all...', command=save_all_file)

# Defines and places the notebook widget
nb = CustomNotebook(root)
nb.pack(fill='both', expand='yes')
# здесь заканчивается описание UI


# поток для обновления вкладок
thread_update_tabs = threading.Thread(target=update_tabs, daemon=True, name='update_tabs')
thread_update_tabs.start()

root.title('LogViewer')
root.iconbitmap(path_to_icon)
root.geometry('{0}x{1}'.format(app_width, app_height))
root.minsize(app_width, app_height)
root.geometry('+{0}+{1}'.format(start_pos_x, start_pos_y))
root.mainloop()  # запуск отрисовки UI
