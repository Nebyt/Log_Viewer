#! /usr/bin/env python
# -*- coding: utf-8 -*-

import zipfile
import os
from tkinter.filedialog import asksaveasfilename
from datetime import datetime
import logging


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
        # получаем текущее время
        current_moment = datetime.now().strftime('%Y%m%d_%H%M%S')
        # получаем путь для сохранения
        self.path_to_save = asksaveasfilename(title='Save archive', initialfile='{}.zip'.format(current_moment),
                                              filetypes=(("ZIP File", "*.zip"), ("All files", "*.*")))
        if self.path_to_save:
            logging.debug('Save all files')
            logging.debug('Path to save %s', self.path_to_save)
            with zipfile.ZipFile(self.path_to_save, 'a', compression=zipfile.ZIP_STORED, allowZip64=True) as my_zip:
                for tab in self.all_tabs:
                    logging.debug('Added file %s to archive', tab.tab_name)
                    self.current_tab_text = tab.get_all_text()
                    tmp_file = tab.tab_name
                    with open(tmp_file, 'w') as file:
                        file.write(self.current_tab_text)
                    my_zip.write(tmp_file)
                    os.remove(tmp_file)
                    tab.clear_memory_text()
            logging.debug('Packing finished')
        else:
            logging.debug('Path to save not set')
            return

    def save_one(self):
        for tab in self.all_tabs:
            if tab.tab_name == self.tab_name:
                tmp_file = tab.tab_name
                self.path_to_save = asksaveasfilename(title='Save file',
                                                      initialfile='{}'.format(tmp_file),
                                                      filetypes=(("Log File", "*.log"),
                                                                 ("Text File", "*.txt"),
                                                                 ("All files", "*.*")))
                if self.path_to_save:
                    self.current_tab_text = tab.get_all_text()
                    logging.debug('Save file %s', tab.tab_name)
                    logging.debug('Path to save %s', self.path_to_save)
                    with open(self.path_to_save, 'w') as file:
                        file.write(self.current_tab_text)
                    logging.debug('File %s saved to %s', tab.tab_name, self.path_to_save)
                    tab.clear_memory_text()
                else:
                    logging.debug('Path to save not set')
                    return
