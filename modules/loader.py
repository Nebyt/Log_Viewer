#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import chardet
import logging
import gc


class Tail:
    def __init__(self, path):
        self.__path = path
        self.__tail = 0
        self.__last_change = 0
        self.__log_content = ''
        self.__fmt = ''
        self.new_filter = True
        self.__was_filtered = False

    def __recognize_format(self, path_to_file):
        # Пробуем угадать кодировку файла
        logging.info('Try to recognize file codec')
        self.__string = self.__get_string_to_recognize(path_to_file)
        self.__fmt = chardet.detect(self.__string)['encoding']
        logging.info("File's codec is %s", self.__fmt)

    def __get_string_to_recognize(self, path):
        with open(path, 'rb') as file:
            string_massive = file.read(25000)
        return string_massive

    def get_lines(self):
        # Читаем файл, если файл изменялся после нашего последнего чтения
        if self.__was_filtered:
            self.__tail = 0
            self.__last_change = 0
        file_last_change = os.stat(self.__path).st_mtime
        last_processed_change = self.__last_change
        if not self.__fmt:
            self.__recognize_format(self.__path)
        if file_last_change > last_processed_change:
            text = ''
            try:
                with open(self.__path, 'r', encoding=self.__fmt, errors='replace', buffering=1) as file:
                    file.seek(self.__tail)
                    text = []
                    #text = file.read()
                    for line in file:
                        text.append(line)
                    self.__tail = file.tell()
                    del file
                self.__last_change = file_last_change
                self.__was_filtered = False
                text = ''.join(text)
                return text
            except FileNotFoundError:
                logging.error('File not found!')
            finally:
                del text
                gc.collect()
        else:
            text = ''
            try:
                with open(self.__path, 'r', encoding=self.__fmt, errors='replace', buffering=1) as file:
                    file.seek(self.__tail)
                    text = ''
                    text = file.read(1)
                    if text:
                        text = file.read()
                        self.__tail = file.tell()
                        del file
                    self.__last_change = file_last_change
                    self.__was_filtered = False
                return text
            except FileNotFoundError:
                logging.error('File not found!')
            finally:
                del text
                gc.collect()
        return ''

    def get_chosen_lines(self, word):
        file_last_change = os.stat(self.__path).st_mtime
        last_processed_change = self.__last_change
        if self.new_filter:
            new_text = []
            try:
                self.__tail = 0
                with open(self.__path, 'r', encoding=self.__fmt, errors='replace', buffering=1) as file:
                    file.seek(self.__tail)
                    for line in file:
                        if word in line.lower():
                            new_text.append(line)
                    self.__tail = file.tell()
                self.__last_change = file_last_change
                self.new_filter = False
                self.__was_filtered = True
                new_text = ''.join(new_text)
                return new_text
            except FileNotFoundError:
                logging.error('File not found!')
            finally:
                del new_text
                gc.collect()
        elif file_last_change > last_processed_change:
            new_text = ''
            try:
                with open(self.__path, 'r', encoding=self.__fmt, errors='replace', buffering=1) as file:
                    file.seek(self.__tail)
                    for line in file:
                        if word in line.lower():
                            new_text += line
                    self.__tail = file.tell()
                self.__last_change = file_last_change
                return new_text
            except FileNotFoundError:
                logging.error('File not found!')
            finally:
                del new_text
                gc.collect()
        else:
            new_text = ''
            try:
                with open(self.__path, 'r', encoding=self.__fmt, errors='replace', buffering=1) as file:
                    file.seek(self.__tail)
                    exist_text = file.read(1)
                    if exist_text:
                        for line in file:
                            if word in line.lower():
                                new_text += line
                    self.__tail = file.tell()
                self.__last_change = file_last_change
                return new_text
            except FileNotFoundError:
                logging.error('File not found!')
            finally:
                del new_text
                gc.collect()