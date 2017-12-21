import zipfile
import os
from tkinter.filedialog import asksaveasfilename
from datetime import datetime


class Saver:
    def __init__(self, all_tabs, tab_name=''):
        self.tabs_paths = []
        self.tab_name = tab_name
        self.all_tabs = all_tabs
        self.original_path = ''
        self.current_tab_text = ''
        for tab in self.all_tabs:
            self.tabs_paths.append(tab.path_to_file)
        self.path_to_save = ''

    def save_all(self):
        # get current time
        current_moment = datetime.now().strftime('%Y%m%d_%H%M%S')
        # set the save path
        self.path_to_save = asksaveasfilename(title='Save archive', initialfile='{}.zip'.format(current_moment),
                                              filetypes=(("ZIP File", "*.zip"), ("All files", "*.*")))
        if self.path_to_save:
            with zipfile.ZipFile('{}'.format(self.path_to_save),'a',
                                 compression=zipfile.ZIP_STORED,
                                 allowZip64=True) as my_zip:
                for tab in self.all_tabs:
                    self.current_tab_text = tab.get_all_text()
                    tmp_file = tab.tab_name
                    with open(tmp_file, 'w') as file:
                        file.write(self.current_tab_text)
                    my_zip.write(tmp_file)
                    os.remove(tmp_file)
        else:
            return

    def save_one(self):
        for tab in self.all_tabs:
            if tab.tab_name == self.tab_name:
                self.current_tab_text = tab.get_all_text()
                tmp_file = tab.tab_name
                self.path_to_save = asksaveasfilename(title='Save file',
                                                      initialfile='{}'.format(tmp_file),
                                                      filetypes=(("Log File", "*.log"),
                                                                 ("Text File", "*.txt"),
                                                                 ("All files", "*.*")))
                if self.path_to_save:
                    with open(tmp_file, 'w') as file:
                        file.write(self.current_tab_text)
                else:
                    return
