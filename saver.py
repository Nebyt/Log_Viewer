import zipfile
from tkinter.filedialog import asksaveasfile, asksaveasfilename
from os.path import basename
from datetime import datetime


class Saver:
    def __init__(self, all_tabs, tab_name=''):
        self.tabs_paths = []
        self.tab_name = tab_name
        self.all_tabs = all_tabs
        self.original_path = ''
        for tab in self.all_tabs:
            self.tabs_paths.append(tab.path_to_file)
        self.path_to_save = ''

    def save_all(self):
        current_moment = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(current_moment)
        self.path_to_save = asksaveasfilename(title='Save archive', initialfile='{}.zip'.format(current_moment),
                                              filetypes=(("ZIP File", "*.zip"), ("All files", "*.*")))
        #TODO added try except to empty path
        with zipfile.ZipFile('{}'.format(self.path_to_save), 'a') as my_zip:
            for path_file in self.tabs_paths:
                my_zip.write(basename(path_file))

    def save_one(self):
        for tab in self.all_tabs:
            if tab.tab_name == self.tab_name:
                self.original_path = tab.path_to_file
        self.path_to_save = asksaveasfilename(title='Save file',
                                              initialfile='{}'.format(self.tab_name),
                                              filetypes=(("Log File", "*.log"),
                                                         ("Text File", "*.txt"),
                                                         ("All files", "*.*")))
        # TODO added try except to empty path
        with open('{}'.format(self.path_to_save), 'a') as save_file:
            save_file.write(self.original_path)

