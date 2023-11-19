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
from PyQt5.QtCore import Qt


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.table_widget = QTableWidget()
        self.setCentralWidget(self.table_widget)

        # Устанавливаем количество строк и столбцов в таблице
        self.table_widget.setRowCount(5)
        self.table_widget.setColumnCount(3)

        # Создаем цикл для добавления чекбоксов в каждую ячейку таблицы
        for row in range(self.table_widget.rowCount()):
            for column in range(self.table_widget.columnCount()):
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                checkbox_item.setCheckState(QtCore.Qt.Unchecked)
                self.table_widget.setItem(row, column, checkbox_item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
