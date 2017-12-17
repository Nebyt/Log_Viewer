import os
import recognize_codec


class Tail:
    def __init__(self, path):
        self.__path = path
        self.__tail = 0
        self.__last_change = 0
        self.__log_content = ''
        self.__fmt = ''

    def __check_update(self):
        self.__last_change = os.stat(self.__path).st_mtime
        return self.__last_change

    def __recognize_format(self, path_to_file):
        self.__fmt = recognize_codec.get_string_to_recognize(path_to_file)

    def get_lines(self):
        print(self.__fmt)
        if not self.__fmt:
            self.__recognize_format(self.__path)
        if self.__last_change <= self.__check_update():
            with open(r'{0}'.format(self.__path), 'r', encoding='{}'.format(self.__fmt)) as file:
                file.seek(self.__tail)
                self.__log_content = file.read()
                self.__tail = file.tell()
        return self.__log_content


if __name__ == '__main__':
    import time
    test_file = Tail(r'C:\Users\Denis\PycharmProjects\pyLogViewer\test.log')
    for k in range(60):
        print(test_file.get_lines())
        time.sleep(1)
