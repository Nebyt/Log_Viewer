import os
import modules.recognize_codec as codec


class Tail:
    def __init__(self, path):
        self.__path = path
        self.__tail = 0
        self.__last_change = 0
        self.__log_content = ''
        self.__fmt = ''

    def __recognize_format(self, path_to_file):
        self.__fmt = codec.get_string_to_recognize(path_to_file)

    def get_lines(self):
        last_processed_change = self.__last_change
        file_last_change = os.stat(self.__path).st_mtime
        if not self.__fmt:
            self.__recognize_format(self.__path)
        if file_last_change > last_processed_change:
            try:
                with open(self.__path, 'r', encoding=self.__fmt, errors='replace') as file:
                    file.seek(self.__tail)
                    text = file.read()
                    self.__tail = file.tell()
                    self.__last_change = file_last_change
                return text
            except FileNotFoundError:
                print('File not found!')
        return ''

