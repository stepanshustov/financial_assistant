import datetime


def now_date_to_int():
    return datetime.now().year * 10000 + datetime.now().month * 100 + datetime.now().day


def now_date():
    return datetime.now().year, datetime.now().month, datetime.now().day


def intDate_to_str(dt: int):
    day = '0' + str(dt % 100)
    month = '0' + str(dt // 100 % 100)
    year = '000' + str(dt // 10000)
    return f"{day[-2:]}.{month[-2:]}.{year[-4:]}"


creat_info_text = """Привет, я Шустов Степан - ученик Яндекс Лицея.
         А так же единственный и неповторимый создатель этого проекта!"""

project_info_text = """Это программа поможет вам учитывать и следить за своими финансами"""

check_char = {':', '.', '-', '+', '=', '?', '!', '_', '*'}  # допустимые символы для логина и пароля
