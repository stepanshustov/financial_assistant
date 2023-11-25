from datetime import datetime
import sqlite3
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


def now_date_to_int():
    return datetime.now().year * 10000 + datetime.now().month * 100 + datetime.now().day


def now_date():
    return datetime.now().year, datetime.now().month, datetime.now().day


def intDate_to_str(dt: int):
    day = '0' + str(dt % 100)
    month = '0' + str(dt // 100 % 100)
    year = '000' + str(dt // 10000)
    return f"{day[-2:]}.{month[-2:]}.{year[-4:]}"
def date_to_int(date: QDateEdit):
    return date.date().year() * 10000 + date.date().month() * 100 + date.date().day()



creat_info_text = """Привет, я Шустов Степан - ученик Яндекс Лицея.
         А так же создатель этого проекта!"""

project_info_text = """Это программа поможет вам учитывать и следить за своими финансами"""

check_char = {':', '.', '-', '+', '=', '?', '!', '_', '*'}  # допустимые символы для логина и пароля

template_html = """
<h2><strong><span style="color: #ff0000;">Расходы</span>.</strong></h2>
<p>&nbsp;</p>
<h3>В период времени:</h3>
<p>&nbsp; &nbsp; С 20.11.2023</p>
<p>&nbsp; &nbsp; По 12.01.2024</p>
<p>&nbsp;</p>
<h3>По категории: <em><span style="background-color: #ffff00;">Продукты питания</span></em></h3>
<p>&nbsp;&nbsp;</p>"""


class Sql_users:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.con = sqlite3.connect(file_name)
        self.cur = self.con.cursor()

    def get_users(self):  # возвращает список всех пользователей
        return self.cur.execute("""SELECT * FROM log_pass""").fetchall()

    def get_user(self, login):  # Возвращает данные для пользователя с данным логином
        mas = self.cur.execute(f"""SELECT * FROM log_pass WHERE login = '{login}'""").fetchall()
        if len(mas):
            return mas[0]
        return False

    def add_user(self, login: str, password: str, balance: float):  # Добавление нового пользователя
        if self.get_user(login):
            return False
        self.cur.execute(
            f"""INSERT INTO log_pass(login, password, balance) VALUES('{login}', '{password}', {balance})""")
        self.cur.execute(f"""
            CREATE TABLE {login + '_income'} (

            id INTEGER PRIMARY KEY NOT NULL,

            title TEXT,

            type INTEGER,

            data INTEGER,

            money NUMERIC)""")

        self.cur.execute(f"""
            CREATE TABLE {login + '_expend'} (

            id INTEGER PRIMARY KEY NOT NULL,

            title TEXT,

            type INTEGER,

            data INTEGER,

            money NUMERIC)""")
        self.con.commit()
        return True

    def get_name_expend_by_id(self, id_: int):  # Название расхода по его id
        return self.cur.execute(f"""SELECT title FROM type_expend WHERE id = {id_}""").fetchall()[0][0]

    def get_name_income_by_id(self, id_: int):  # Название дохода по его id
        return self.cur.execute(f"""SELECT title FROM type_income WHERE id = {id_}""").fetchall()[0][0]

    def get_id_expen_by_name(self, name_: str):  # id дохода по его названию
        return self.cur.execute(f"""SELECT id FROM type_expend WHERE title = '{name_}'""").fetchall()[0][0]

    def get_id_income_by_name(self, name_: str):  # id расхода по его названию
        return self.cur.execute(f"""SELECT id FROM type_income WHERE title = '{name_}'""").fetchall()[0][0]

    def get_all_expend_list(self):  # Возвращает список всех типов расходов
        return self.cur.execute("SELECT * FROM type_expend ORDER BY title").fetchall()

    def get_all_income_list(self):  # Возвращает список всех типов доходов
        return self.cur.execute("SELECT * FROM type_income ORDER BY title").fetchall()

    def get_user_expend_list(self, login: str):  # Возвращает данные о всех расходов для данного пользователя
        return self.cur.execute(f"SELECT * FROM {login + '_expend'}").fetchall()

    def get_user_income_list(self, login: str):  # Возвращает данные о всех доходов для данного пользователя
        return self.cur.execute(f"SELECT * FROM {login + '_income'}").fetchall()

    def add_income(self, login: str, title: str,
                   money: float, type_: int, data: int):  # Добавление дохода для заданного пользователя
        self.cur.execute(f"""INSERT INTO {login + '_income'} (title, money, type, data) 
            VALUES ('{title}', {money}, {type_}, {data})""")
        self.con.commit()

    def add_expend(self, login: str, title: str,
                   money: float, type_: int, data: int):  # Добавление расхода для заданного пользователя
        self.cur.execute(f"""INSERT INTO {login + '_expend'} (title, money, type, data) 
            VALUES ('{title}', {money}, {type_}, {data})""")
        self.con.commit()

    def change_balance(self, login: str, new_balance: float):  # Изменить баланс данному пользователю
        self.cur.execute(f"""UPDATE log_pass
                            SET balance = {new_balance}
                            WHERE login = '{login}'""")
        self.con.commit()

    def delete_income(self, login: str, id_: int):  # Удалить доход по его id
        self.cur.execute(f"""DELETE from {login + '_income'}
                            where id = {id_}""")
        self.con.commit()

    def delete_expend(self, login: str, id_: int):  # Удалить расход по его id
        self.cur.execute(f"""DELETE from {login + '_expend'}
                            where id = {id_}""")
        self.con.commit()
