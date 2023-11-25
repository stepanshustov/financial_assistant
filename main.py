import sqlite3
from addition import *  # здесь хранятся дополнительные функции, константы, а так же класс Sql для работы с базой данных
import sys
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
import os
from pyhtml2pdf import converter


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.start_window()
        self.sql = Sql_users("users.sqlite")

    def start_window(self):  # создание главного окна
        uic.loadUi('start_window.ui', self)
        # self.setWindowState(Qt.WindowMaximized)
        self.registr.clicked.connect(self.reg_window)

        self.author.clicked.connect(self.auth_window)
        self.creator_info.clicked.connect(self.out_creat_info)
        self.project_info.clicked.connect(self.out_project_info)

    def reg_window(self):  # окно регистрации
        uic.loadUi("registr_1.ui", self)
        self.out_label.setText(
            f"\tДопустимы только латинские буквы, а так же цифры и простые символы {check_char}")
        self.back_button.clicked.connect(self.start_window)
        self.reg_begin.clicked.connect(self.reg_new_user)

    def reg_new_user(self):  # регистрация нового пользователя
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
            self.main_window(*self.sql.get_user(log))
        else:
            self.out_label.setText(f"""\t Пользователь с таким именем уже существует""")

    def auth_window(self):  # окно авторизации
        uic.loadUi("auth.ui", self)
        # self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        # self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.back_button.clicked.connect(self.start_window)
        self.authButton.clicked.connect(self.auth_user)

    def auth_user(self):
        log = self.login.text()
        pas = self.password.text()
        user = self.sql.get_user(log)
        if user and user[2] == pas:
            self.main_window(*user)
            return
        self.out_label.setText("Неверный логин или пароль")

    def update_table_list(self):  # отображение данных о доходах и расходах в таблицах
        expend_sort = self.sort_expen_comboBox.currentText()  # тип сортировки расходов
        income_sort = self.sort_income_comboBox.currentText()  # тип сортировки доходов
        expend_list = self.sql.get_user_expend_list(self.login)  # список всех расходов
        income_list = self.sql.get_user_income_list(self.login)  # список всех доходов

        # Временной интервал доходов и расходов
        self.expen_date_begin = date_to_int(self.expenDateBegin)
        self.expen_date_end = date_to_int(self.expenDateEnd)
        self.income_date_begin = date_to_int(self.incomeDateBegin)
        self.income_date_end = date_to_int(self.incomeDateEnd)

        expend_list.sort(key=self.sort_dict[expend_sort])
        income_list.sort(key=self.sort_dict[income_sort])

        self.expen_type = self.type_expen_comboBox.currentText()  # тип отображаемых расходов
        if self.expen_type == 'Все':
            self.expen_type = -1
        else:
            self.expen_type = self.sql.get_id_expen_by_name(self.expen_type)

        self.income_type = self.type_income_comboBox.currentText()  # тип отображаемых доходов

        if self.income_type == 'Все':
            self.income_type = -1
        else:
            self.income_type = self.sql.get_id_income_by_name(self.income_type)

        self.s = 0  # сумма всех доходов и расходов с учётом знака
        self.expenWidget.setColumnCount(5)
        self.expenWidget.setHorizontalHeaderLabels(["название", "дата", "сумма", "тип"])
        for el in expend_list:
            if el[3] <= now_date_to_int():
                self.s -= el[4]  # отнимаем сумму расходов
        # Отделяем нужное по дате и типу и создаём список, для таблицы
        self.displayed_list_of_expenses = [el for el in expend_list if
                                           self.expen_date_begin <= el[3] <= self.expen_date_end]
        self.displayed_list_of_expenses = [el for el in self.displayed_list_of_expenses if
                                           el[2] == self.expen_type or self.expen_type == -1]

        self.expenWidget.setRowCount(len(self.displayed_list_of_expenses))

        rez_expen = 0

        for i, string in enumerate(self.displayed_list_of_expenses):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            checkbox_item.setCheckState(QtCore.Qt.Unchecked)  # устанавливаем галочки для удаления расходов
            rez_expen += string[4]
            for j, el in enumerate(
                    (string[1], intDate_to_str(string[3]), string[4], self.sql.get_name_expend_by_id(string[2]))):
                self.expenWidget.setItem(i, j, QTableWidgetItem(str(el)))

            self.expenWidget.setItem(i, 4, checkbox_item)
        self.expenWidget.resizeColumnsToContents()
        self.rez_expen_label.setText(f'Итого: {rez_expen}')

        self.incomeWidget.setColumnCount(5)
        self.incomeWidget.setHorizontalHeaderLabels(["название", "дата", "сумма", "тип"])
        for el in income_list:
            if el[3] <= now_date_to_int():
                self.s += el[4]  # прибавляем сумму доходов
        # Отделяем нужное по дате и типу создаём список, для таблицы
        self.displayed_list_of_incomes = [el for el in income_list if
                                          self.income_date_begin <= el[3] <= self.income_date_end]
        self.displayed_list_of_incomes = [el for el in self.displayed_list_of_incomes if
                                          el[2] == self.income_type or self.income_type == -1]
        self.incomeWidget.setRowCount(len(self.displayed_list_of_incomes))

        rez_income = 0

        for i, string in enumerate(self.displayed_list_of_incomes):
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            checkbox_item.setCheckState(QtCore.Qt.Unchecked)  # устанавливаем галочки для удаления доходов
            rez_income += string[4]
            for j, el in enumerate(
                    (string[1], intDate_to_str(string[3]), string[4], self.sql.get_name_expend_by_id(string[2]))):
                self.incomeWidget.setItem(i, j, QTableWidgetItem(str(el)))

            self.incomeWidget.setItem(i, 4, checkbox_item)
        self.incomeWidget.resizeColumnsToContents()

        self.rez_income_label.setText(f'Итого: {rez_income}')

        self.balanceLabel.setText(f"Ваш текущий баланс: {(self.balance + self.s):.{2}f}")

    def main_window(self, id_, login, password, balance):  # Основное окно программы

        uic.loadUi("main.ui", self)
        self.login = login
        self.password = password
        self.id = id_
        self.balance = balance
        self.sort_dict = {
            "По увеличению даты": lambda x: x[3],
            "По уменьшению даты": lambda x: -1 * x[3],
            "По увеличению суммы": lambda x: x[4],
            "по уменьшению суммы": lambda x: -1 * x[4],
            "По алфавиту": lambda x: x[1]
        }  # Словарь с названиями и функциями сортировки для отображения в таблице
        self.sort_expen_comboBox.addItems(self.sort_dict.keys())
        self.sort_income_comboBox.addItems(self.sort_dict.keys())

        self.addExpenButton.clicked.connect(self.add_expen_dialog_window)  # добавление нового расхода
        self.addIncomeButton.clicked.connect(self.add_income_dialog_window)  # добавление нового дохода

        self.infoButton.clicked.connect(self.addition_menu)
        self.changeBalanceButton.clicked.connect(self.change_balance)

        self.deleteExpenButton.clicked.connect(self.delete_expen)
        self.deleteIncomeButton.clicked.connect(self.delete_income)

        self.expenDateEnd.setDate(QDate(*now_date()))
        self.incomeDateEnd.setDate(QDate(*now_date()))

        self.type_expen_comboBox.addItems(['Все'] + [el[1] for el in self.sql.get_all_expend_list()])
        self.type_income_comboBox.addItems(['Все'] + [el[1] for el in self.sql.get_all_income_list()])

        # Обновление таблицы, при изменении параметров отображения
        self.sort_expen_comboBox.currentTextChanged.connect(self.update_table_list)
        self.sort_income_comboBox.currentTextChanged.connect(self.update_table_list)
        self.expenDateBegin.editingFinished.connect(self.update_table_list)
        self.expenDateEnd.editingFinished.connect(self.update_table_list)
        self.incomeDateBegin.editingFinished.connect(self.update_table_list)
        self.incomeDateEnd.editingFinished.connect(self.update_table_list)
        self.type_expen_comboBox.currentTextChanged.connect(self.update_table_list)
        self.type_income_comboBox.currentTextChanged.connect(self.update_table_list)

        self.save_pdf_pushButton.clicked.connect(self.save_pdf)

        self.update_table_list()

    def save_pdf(self):
        ans_user, ok_pressed = QInputDialog.getItem(
            self, " Выберите вариант", "Что сохранить?",
            ("Только расходы", "Только доходы", "Всё"), 1, False)
        if ok_pressed:
            if ans_user == "Только расходы":
                with open("text.html", 'w', encoding='utf-8') as f_html:
                    print(self.creat_expen_html(), file=f_html)
            elif ans_user == "Только доходы":
                with open("text.html", 'w', encoding='utf-8') as f_html:
                    print(self.creat_income_html(), file=f_html)
            else:
                with open("text.html", 'w', encoding='utf-8') as f_html:
                    print(self.creat_expen_html(), file=f_html)
                    print("<p>&nbsp;</p><p>&nbsp;</p><p>&nbsp;</p>", file=f_html)
                    print(self.creat_income_html(), file=f_html)
            file_out_name = QFileDialog.getSaveFileName(self, "Введите название файла", '', 'PDF (*.pdf)')[0]
            if file_out_name:
                # qd = QDialog(self)
                # qd.setGeometry(500, 500, 300, 300)
                # lab = QLabel(qd)
                # lab.setGeometry(10, 10, 280, 280)
                # lab.setText("Подождите, идёт сохранение файла...")
                # qd.exec()
                path = os.path.abspath('text.html')
                converter.convert(f'file:///{path}', file_out_name)
                # qd.close()

    def creat_expen_html(self):  # Возвращает текст в формате HTML для расходов
        expen_date_begin_str = intDate_to_str(self.expen_date_begin)  # дата начала в виде строки
        expen_date_end_str = intDate_to_str(self.expen_date_end)  # Дата конца в виде строки
        type_expen_str = 'Все'
        if self.expen_type != -1:
            type_expen_str = self.sql.get_name_expend_by_id(self.expen_type)
        html_text = f"""
        <h2><strong><span style="color: #ff0000;">{'Расходы'}</span>.</strong></h2>
        <p>&nbsp;</p>
        <h3>В период времени:</h3>
        <p>&nbsp; &nbsp; С {expen_date_begin_str}</p>
        <p>&nbsp; &nbsp; По {expen_date_end_str}</p>
        <p>&nbsp;</p>
        <h3>По категории: <em><span style="background-color: #ffff00;">{type_expen_str}</span></em></h3>"""
        for i, el in enumerate(self.displayed_list_of_expenses):
            dt_ = intDate_to_str(int(el[3]))
            html_text += f"<p>&nbsp; &nbsp; {i + 1}) {el[1]}&nbsp; &nbsp; {el[4]} руб&nbsp; &nbsp; {dt_}</p>"
        html_text += "<p>&nbsp;&nbsp;</p>"
        return html_text

    def creat_income_html(self):  # Возвращает текст в формате HTML для расходов
        income_date_begin_str = intDate_to_str(self.income_date_begin)  # дата начала в виде строки
        income_date_end_str = intDate_to_str(self.income_date_end)  # Дата конца в виде строки
        type_income_str = 'Все'
        if self.income_type != -1:
            type_income_str = self.sql.get_name_expend_by_id(self.income_type)
        html_text = f"""
        <h2><strong><span style="color: #ff0000;">{'Доходы'}</span>.</strong></h2>
        <p>&nbsp;</p>
        <h3>В период времени:</h3>
        <p>&nbsp; &nbsp; С {income_date_begin_str}</p>
        <p>&nbsp; &nbsp; По {income_date_end_str}</p>
        <p>&nbsp;</p>
        <h3>По категории: <em><span style="background-color: #ffff00;">{type_income_str}</span></em></h3>"""
        for i, el in enumerate(self.displayed_list_of_incomes):
            dt_ = intDate_to_str(int(el[3]))
            html_text += f"<p>&nbsp; &nbsp; {i + 1}) {el[1]}&nbsp; &nbsp; {el[4]} руб&nbsp; &nbsp; {dt_}</p>"
        html_text += "<p>&nbsp;&nbsp;</p>"
        return html_text

    def delete_expen(self):
        for i in range(self.expenWidget.rowCount()):
            if self.expenWidget.item(i, 4).checkState() == Qt.Checked:
                self.sql.delete_expend(self.login, self.displayed_list_of_expenses[i][0])
        self.update_table_list()

    def delete_income(self):
        for i in range(self.incomeWidget.rowCount()):
            if self.incomeWidget.item(i, 4).checkState() == Qt.Checked:
                self.sql.delete_income(self.login, self.displayed_list_of_incomes[i][0])
        self.update_table_list()

    def change_balance(self):
        bal, ok_pressed = QInputDialog.getDouble(
            self, "Введите сумму", "Новое значение",
            self.balance + self.s, 0, 99999999999, 2)
        if ok_pressed:
            self.balance -= self.balance + self.s - bal
            self.balanceLabel.setText(f"Ваш текущий баланс: {(self.balance + self.s):.{2}f}")
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
            self.update_table_list()
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
            self.update_table_list()
            qd.close()

        qd = QDialog(self)
        uic.loadUi("add_.ui", qd)
        dt_now = [datetime.now().year, datetime.now().month, datetime.now().day]
        qd.dateEdit.setDate(QDate(*dt_now))
        type_lst = self.sql.get_all_income_list()  # список с типами доходов
        qd.typeComboBox.addItems([el[1] for el in type_lst])
        qd.pushButton.clicked.connect(fun)
        qd.exec()

    def out_creat_info(self):  # диалоговое окно с выводм информации о создателе проекта
        qd = QDialog(self)
        qd.setGeometry(self.x() + 200, self.y() + 200, 250, 100)
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
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
