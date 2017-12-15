import os


class Tail:
    def __init__(self, path):
        self.__path = path
        self.__tail = 0
        self.__last_change = 0
        self.__log_content = ''

    def __check_update(self):
        self.__last_change = os.stat(self.__path).st_mtime
        return self.__last_change

    def __recognize_coding(self, path_to_file):
        with open(r'{0}'.format(self.__path), 'rb') as file:
            pass
        pass

    def get_lines(self):
        if self.__last_change <= self.__check_update():
            with open(r'{0}'.format(self.__path), 'r') as file:
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
