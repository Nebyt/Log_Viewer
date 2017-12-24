import time
import sys
import msvcrt
import threading
import os

pressed_key = ''


def press_key():
    while True:
        pressed_key = msvcrt.getwch()
        if pressed_key == 'q':
            sys.exit()
        time.sleep(0.5)


th = threading.Thread(target=press_key,name=2)


def fill_file():
    k = 1
    for count in range(11):
        file_path = '{0}{1}{2}'.format(os.getcwd(), os.sep, 'test_{0}.log'.format(count))
        if not os.path.exists(r'{0}'.format(file_path)):
            while True:
                if pressed_key == 'q':
                    print('Stop the script')
                    sys.exit(0)
                else:
                    with open('test_{0}.log'.format(count), 'a') as file:
                        file.writelines('New string Новая строка {} лога\n'.format(k))
                    print('New string Новая строка {} лог\n'.format(k))
                    k += 1
                time.sleep(1)
        else:
            pass


def starter():
    th.start()
    fill_file()


starter()