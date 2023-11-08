from addition import *

import yadisk
import sqlite3
import sys
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pyqtgraph as pg

y_disk = yadisk.YaDisk(token=y_token)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def date_to_int(date: QDateEdit):
    return date.date().year() * 1000 + date.date().month() * 100 + date.date().day()


def intDate_to_str(dt: int):
    day = '0' + str(dt % 100)
    month = '0' + str(dt // 100 % 100)
    year = '000' + str(dt // 10000)
    return f"{day[-2:]}.{month[-2:]}.{year[-4:]}"


class sql:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.con = sqlite3.connect(file_name)
        self.cur = self.con.cursor()

    def get_users(self):  # полностью работает
        return self.cur.execute("""SELECT * FROM log_pass""").fetchall()

    def get_user(self, login):  # полностью работает
        mas = self.cur.execute(f"""SELECT * FROM log_pass WHERE login = '{login}'""").fetchall()
        if len(mas):
            return mas[0]
        return False

    def add_user(self, login: str, password: str, balance: float):
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

    def get_name_expend_by_id(self, id_: int):
        return self.cur.execute(f"""SELECT title FROM type_expend WHERE id = {id_}""").fetchall()[0][0]

    def get_name_income_by_id(self, id_: int):
        return self.cur.execute(f"""SELECT title FROM type_income WHERE id = {id_}""").fetchall()[0][0]

    def get_all_expend_list(self):
        return self.cur.execute("SELECT * FROM type_expend").fetchall()

    def get_user_expend_list(self, login: str):
        return self.cur.execute(f"SELECT * FROM {login + '_expend'}").fetchall()

    def get_user_income_list(self, login: str):
        return self.cur.execute(f"SELECT * FROM {login + '_income'}").fetchall()

    def get_income_list(self):
        return self.cur.execute("SELECT * FROM type_income").fetchall()

    def add_income(self, login: str, title: str, money: float, type_: int, data: int):
        self.cur.execute(f"""INSERT INTO {login + '_income'} (title, money, type, data) 
            VALUES ('{title}', {money}, {type_}, {data})""")
        self.con.commit()

    def add_expend(self, login: str, title: str, money: float, type_: int, data: int):
        self.cur.execute(f"""INSERT INTO {login + '_expend'} (title, money, type, data) 
            VALUES ('{title}', {money}, {type_}, {data})""")
        self.con.commit()

    def change_balance(self, login: str, new_balance: float):
        self.cur.execute(f"""UPDATE log_pass
                            SET balance = {new_balance}
                            WHERE login = '{login}'""")
        self.con.commit()



class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_window()
        self.sql = sql("users.sqlite")

    def main_window(self):  # создание главного окна
        uic.loadUi('main.ui', self)
        # self.setWindowState(Qt.WindowMaximized)
        self.registr.clicked.connect(self.reg_window)

        self.author.clicked.connect(self.auth_window)
        self.creator_info.clicked.connect(self.out_creat_info)
        self.project_info.clicked.connect(self.out_project_info)

    def reg_window(self):  # окно регистрации
        uic.loadUi("registr_1.ui", self)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.out_label.setText(
            f"\tДопустимы только латинские буквы, а так же цифры и простые символы {check_char}")
        self.back_button.clicked.connect(self.main_window)
        self.reg_begin.clicked.connect(self.reg)

    def reg(self):  # регистрация нового пользователя
        log = self.login.text()
        pas = self.password.text()
        bal = self.money.value()
        if log == '' or pas == '':
            self.out_label.setText("\t Вы ввели не все данные")
            return
        # проверка корректности логина и пароля
        for el in log.lower():
            if not ('a' <= el <= 'z' or el in check_char or el.isdigit()):
                self.out_label.setText(f"""\t Логин некорректен
\tДопустимы только латинские буквы, а так же цифры и простые символы {check_char}""")
                return
        for el in pas.lower():
            if not ('a' <= el <= 'z' or el in check_char or el.isdigit()):
                self.out_label.setText(f"""\t Пароль некорректен
\tДопустимы только латинские буквы, а так же цифры и простые символы {check_char}""")
                return

        if self.sql.add_user(log, pas, bal):
            self.fun_no_name(*self.sql.get_user(log))
        else:
            self.out_label.setText(f"""\t Пользователь с таким именем уже существует""")

    def auth_window(self):  # окно авторизации
        uic.loadUi("auth.ui", self)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.back_button.clicked.connect(self.main_window)
        self.authButton.clicked.connect(self.auth)

    def auth(self):
        log = self.login.text()
        pas = self.password.text()
        user = self.sql.get_user(log)
        if user and user[2] == pas:
            self.fun_no_name(*user)
            return
        self.out_label.setText("Неверный логин или пароль")

    def update(self):
        expend_sort = self.sort_expen_comboBox.currentText()
        income_sort = self.sort_income_comboBox.currentText()
        expend_list = self.sql.get_user_expend_list(self.login)
        income_list = self.sql.get_user_income_list(self.login)

        expend_list.sort(key=self.sort_dict[expend_sort])
        income_list.sort(key=self.sort_dict[income_sort])
        self.expenWidget.setRowCount(len(expend_list))
        self.s = 0
        self.expenWidget.setColumnCount(4)
        self.expenWidget.setHorizontalHeaderLabels(["название", "дата", "сумма", "тип"])
        for i, string in enumerate(expend_list):
            self.s -= string[4]  # отнимаем сумму расходов
            for j, el in enumerate(
                    (string[1], intDate_to_str(string[3]), string[4], self.sql.get_name_expend_by_id(string[2]))):
                self.expenWidget.setItem(i, j, QTableWidgetItem(str(el)))
        self.expenWidget.resizeColumnsToContents()

        self.incomeWidget.setRowCount(len(income_list))
        self.incomeWidget.setColumnCount(4)
        self.incomeWidget.setHorizontalHeaderLabels(["название", "дата", "сумма", "тип"])
        for i, string in enumerate(income_list):
            self.s += string[4]  # прибавляем сумму доходов
            for j, el in enumerate(
                    (string[1], intDate_to_str(string[3]), string[4], self.sql.get_name_expend_by_id(string[2]))):
                self.incomeWidget.setItem(i, j, QTableWidgetItem(str(el)))
        self.incomeWidget.resizeColumnsToContents()
        self.balanceLabel.setText(f"Ваш текущий баланс: {self.balance + self.s}")

    def fun_no_name(self, id_, login, password, balance):  #

        uic.loadUi("no_name.ui", self)
        # self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.login = login
        self.password = password
        self.id = id_
        self.balance = balance
        self.sort_dict = {
            "По увеличению даты": lambda x: x[3],
            "По уменьшению даты": lambda x: -1 * x[3],
            "По увеличению суммы": lambda x: x[4],
            "По уменшении суммы": lambda x: -1 * x[4],
            "По алфавиту": lambda x: x[1]
        }
        self.sort_expen_comboBox.addItems(self.sort_dict.keys())
        self.sort_income_comboBox.addItems(self.sort_dict.keys())
        self.addExpenButton.clicked.connect(self.add_expen_dialog_window)
        self.addIncomeButton.clicked.connect(self.add_income_dialog_window)
        self.sort_expen_comboBox.currentTextChanged.connect(self.update)
        self.sort_income_comboBox.currentTextChanged.connect(self.update)
        self.infoButton.clicked.connect(self.addition_menu)
        self.changeBalanceButton.clicked.connect(self.change_balance)
        self.statisticButton.clicked.connect(self.get_statistic_info)
        self.update()

    def get_statistic_info(self):
        qd = QDialog()

        qd.exec()

    def change_balance(self):
        bal, ok_pressed = QInputDialog.getDouble(
            self, "Введите сумму", "Новое значение",
            self.balance + self.s, 0, 99999999999, 2)
        if ok_pressed:
            self.balance -= self.balance + self.s - bal
            self.balanceLabel.setText(f"Ваш текущий баланс: {self.balance + self.s}")
            self.sql.change_balance(self.login, self.balance)

    def addition_menu(self):
        qd = QDialog(self)
        uic.loadUi("addition_dialog.ui", qd)
        qd.exec()

    def add_expen_dialog_window(self):  # диалоговое окно для добавления нового расхода
        def fun():
            name = qd.name.text()
            sm = qd.sum.value()
            date = date_to_int(qd.dateEdit)
            type_name = qd.typeComboBox.currentText()
            id_type = -1
            if not name or not sm or not date or not type_name:
                qd.out_label.setText("Данные некорректны!")
                return

            for el in type_lst:
                if type_name == el[1]:
                    id_type = el[0]
                    break
            self.sql.add_expend(self.login, name, sm, id_type, date)
            self.update()
            qd.close()

        qd = QDialog(self)
        uic.loadUi("add_.ui", qd)
        dt_now = [datetime.now().year, datetime.now().month, datetime.now().day]
        qd.dateEdit.setDate(QDate(*dt_now))
        type_lst = self.sql.get_all_expend_list()  # список с типами расходов
        qd.typeComboBox.addItems([el[1] for el in type_lst])
        qd.pushButton.clicked.connect(fun)
        qd.exec()

    def add_income_dialog_window(self):  # диалоговое окно для добавления нового дохода
        def fun():
            name = qd.name.text()
            sm = qd.sum.value()
            date = date_to_int(qd.dateEdit)
            type_name = qd.typeComboBox.currentText()
            id_type = -1
            if not name or not sm or not date or not type_name:
                qd.out_label.setText("Данные некорректны!")
                return

            for el in type_lst:
                if type_name == el[1]:
                    id_type = el[0]
                    break
            self.sql.add_income(self.login, name, sm, id_type, date)
            self.update()
            qd.close()

        qd = QDialog(self)
        uic.loadUi("add_.ui", qd)
        dt_now = [datetime.now().year, datetime.now().month, datetime.now().day]
        qd.dateEdit.setDate(QDate(*dt_now))
        type_lst = self.sql.get_income_list()  # список с типами доходов
        qd.typeComboBox.addItems([el[1] for el in type_lst])
        qd.pushButton.clicked.connect(fun)
        qd.exec()

    def out_creat_info(self):  # диалоговое окно с выводм информации о создателе проекта
        qd = QDialog(self)
        qd.setGeometry(self.x() + 200, self.y() + 200, 250, 100)
        qd.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        qd.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        label = QLabel(qd)
        label.setText(creat_info_text)
        label.setWordWrap(True)
        label.setGeometry(1, 1, 240, 80)
        qd.exec()

    def out_project_info(self):  # диалоговое окно с выводм информации о проекте
        qd = QDialog(self)
        qd.setGeometry(self.x() + 200, self.y() + 200, 250, 100)
        label = QLabel(qd)
        label.setText(project_info_text)
        label.setWordWrap(True)
        label.setGeometry(1, 1, 240, 80)
        qd.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
