__encodings = {
    'UTF-8':      'utf-8',
    'WIN-1251':     'windows-1251',
    'KOI8-R':     'koi8-r',
    'IBM866':     'ibm866',
    'ISO-8859-5': 'iso-8859-5',
    'MAC':        'mac',
}

"""
Определение кодировки текста
"""


def __get_codepage(string=None):
    uppercase = 1
    lowercase = 3
    utf_upper = 5
    utf_lower = 7
    code_pages = {}
    for enc in __encodings.keys():
        code_pages[enc] = 0
    if string is not None and len(string) > 0:
        last_simb = 0
        for simb in string:
            simb_ord = simb

            """non-russian characters"""
            if simb_ord < 128 or simb_ord > 256:
                continue

            """UTF-8"""
            if last_simb == 208 and (143 < simb_ord < 176 or simb_ord == 129):
                code_pages['UTF-8'] += (utf_upper * 2)
            if (last_simb == 208 and (simb_ord == 145 or 175 < simb_ord < 192)) \
                or (last_simb == 209 and (127 < simb_ord < 144)):
                code_pages['UTF-8'] += (utf_lower * 2)

            """WIN-1251"""
            if 223 < simb_ord < 256 or simb_ord == 184:
                code_pages['WIN-1251'] += lowercase
            if 191 < simb_ord < 224 or simb_ord == 168:
                code_pages['WIN-1251'] += uppercase

            """KOI8-R"""
            if 191 < simb_ord < 224 or simb_ord == 163:
                code_pages['KOI8-R'] += lowercase
            if 222 < simb_ord < 256 or simb_ord == 179:
                code_pages['KOI8-R'] += uppercase

            """IBM866"""
            if 159 < simb_ord < 176 or 223 < simb_ord < 241:
                code_pages['IBM866'] += lowercase
            if 127 < simb_ord < 160 or simb_ord == 241:
                code_pages['IBM866'] += uppercase

            """ISO-8859-5"""
            if 207 < simb_ord < 240 or simb_ord == 161:
                code_pages['ISO-8859-5'] += lowercase
            if 175 < simb_ord < 208 or simb_ord == 241:
                code_pages['ISO-8859-5'] += uppercase

            """MAC"""
            if 221 < simb_ord < 255:
                code_pages['MAC'] += lowercase
            if 127 < simb_ord < 160:
                code_pages['MAC'] += uppercase

            last_simb = simb_ord

        idx = ''
        maximum = 0
        for item in code_pages:
            if code_pages[item] > maximum:
                maximum = code_pages[item]
                idx = item
        if idx == 'WIN-1251':
            idx = 'windows-1251'
        if not maximum:
            idx = 'ASCII'
        return idx.lower()


def get_string_to_recognize(path):
    with open(path, 'rb') as file:
        string_massive = file.read(25000)
    return __get_codepage(string_massive)
