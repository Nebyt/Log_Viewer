import zipfile
from tkinter.filedialog import asksaveasfile, asksaveasfilename


class Saver:
    def __init__(self, all_tabs):
        self.tabs_paths = []
        for tab in all_tabs:
            self.tabs_paths.append(tab.path_to_file)
        self.path_to_save = asksaveasfilename(defaultextension='.zip',filetypes=("ZIP file", ".zip"))

    def save_all(self):
        pass

    def save_one(self):
        pass
