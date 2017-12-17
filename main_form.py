import tkinter
from tkinter.filedialog import askopenfilename
import time
import threading
import os
import mimetypes
from custom_notebook import CustomNotebook
from custom_tab import Tab
from modal_window import ModalWindow


APP_WIDTH_WIN = 750
APP_WIDTH_LINUX = 825
APP_HEIGHT = 400


# список всех вкладок
list_of_tab = []


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
        type_of_file = mimetypes.guess_type(file_path)
        if type_of_file[0]:
            type_of_file = type_of_file[0].split('/')[0]
        if type_of_file == 'text' or not type_of_file[0]:
            list_of_tab.append(Tab(nb, file_path))
        else:
            modal_window = ModalWindow()
            modal_window.show()
    else:
        return


if os.name == 'posix':
    app_width = APP_WIDTH_LINUX
    path_to_icon = ''
else:
    app_width = APP_WIDTH_WIN
    path_to_icon = 'icon.ico'
    path_to_icon = os.path.join(os.getcwd(), path_to_icon)

# здесь начинается описание UI
root = tkinter.Tk()

app_height = APP_HEIGHT
start_pos_x = root.winfo_screenwidth() - int((app_width / 2))
start_pos_y = root.winfo_screenheight() - int((app_height / 2))

m = tkinter.Menu(root)
root.config(menu=m)
m.add_command(label="Open...", command=add_tab)

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
