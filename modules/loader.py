#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import modules.recognize_codec as codec
import logging


class Tail:
    def __init__(self, path):
        self.__path = path
        self.__tail = 0
        self.__last_change = 0
        self.__log_content = ''
        self.__fmt = ''

    def __recognize_format(self, path_to_file):
        # Пробуем угадать кодировку файла
        logging.info('Try to recognize file codec')
        self.__fmt = codec.get_string_to_recognize(path_to_file)
        logging.info("File's codec is %s", self.__fmt)

    def get_lines(self):
        # Читаем файл, если файл изменялся после нашего последнего чтения
        last_processed_change = self.__last_change
        file_last_change = os.stat(self.__path).st_mtime
        if not self.__fmt:
            self.__recognize_format(self.__path)
        if file_last_change > last_processed_change:
            text = ''
            try:
                with open(self.__path, 'r', encoding=self.__fmt, errors='replace') as file:
                    file.seek(self.__tail)
                    text = ''
                    text = file.read()
                    self.__tail = file.tell()
                    self.__last_change = file_last_change
                    del file
                return text
            except FileNotFoundError:
                logging.error('File not found!')
            finally:
                del text
        return ''
