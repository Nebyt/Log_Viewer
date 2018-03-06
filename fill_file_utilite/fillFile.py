#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import threading
import os
import random

pressed_key = ''


def press_key():
    global pressed_key
    try:
        import msvcrt
        while True:
            pressed_key = msvcrt.getwch()
            if pressed_key == 'q':
                sys.exit()
            time.sleep(0.5)
    except ImportError:
        pass


th = threading.Thread(target=press_key,name=2)


def fill_file():
    k = 1
    words = []
    crt_drt = os.path.dirname(os.path.realpath(__file__))
    with open('{0}{1}dict.txt'.format(crt_drt, os.sep), 'r') as dictionary:
        words = dictionary.read().split('\n')
    for count in range(11):
        file_path = '{0}{1}{2}'.format(crt_drt, os.sep, 'test_{0}.log'.format(count))
        if not os.path.exists(r'{0}'.format(file_path)):
            while True:
                if pressed_key == 'q':
                    print('Stop the script')
                    sys.exit(0)
                else:
                    w1 = random.choice(words)
                    w2 = random.choice(words)
                    with open('{0}{1}test_{2}.log'.format(crt_drt, os.sep, count), 'a') as file:
                        file.writelines('New string {0} {1} {2} Новая строка {0} {1} {2}\n'.format(k, w1, w2))
                    print('New string {0} {1} {2} Новая строка {0} {1} {2}\n'.format(k, w1, w2))
                    k += 1
                time.sleep(0.0001)
        else:
            pass


def starter():
    th.start()
    fill_file()


starter()