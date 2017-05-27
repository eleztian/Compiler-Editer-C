import sys
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import (QApplication, QGridLayout, QTextEdit, QWidget, QFrame,
                             QPushButton, QTableWidget, QLineEdit,  QAbstractItemView,
                             QMessageBox, QTableWidgetItem, QFileDialog)
from logic.Forecast import Forecasting


class Ll1Ui(QFrame):
    pre_forecasting = None

    def __init__(self):
        super(Ll1Ui, self).__init__()

        self.pre_op_widget = QWidget(self)

        self.open_file_btn = QPushButton(self.pre_op_widget, text="Open")
        self.ok_grammar_btn = QPushButton(self.pre_op_widget, text="OK")
        self.follow_btn = QPushButton(self.pre_op_widget, text="Fillow")
        self.first_btn = QPushButton(self.pre_op_widget, text="First")
        self.create_pre_table = QPushButton(self.pre_op_widget, text="Create Tabel")
        self.gird_op = QGridLayout()

        self.pre_widget_left = QWidget(self)

        self.gird_w = QGridLayout()
        self.pre_edit = QTextEdit(self.pre_widget_left)
        self.pre_first_table = QTableWidget()
        self.pre_first_table.resizeColumnsToContents()
        self.pre_first_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pre_first_table.setHorizontalHeaderLabels(['First'])
        self.pre_follow_table = QTableWidget()
        self.pre_follow_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pre_follow_table.setHorizontalHeaderLabels(['Fallow'])

        self.pre_widget_right = QWidget(self)

        self.pre_pre_table = QTableWidget()
        self.pre_pre_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pre_pre_table.setHorizontalHeaderLabels(['预测表'])
        self.pre_list = QTableWidget()
        self.pre_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pre_list.verticalHeader().setVisible(False)
        self.pre_list.setColumnCount(4)
        self.pre_list.setHorizontalHeaderLabels(['步骤', '符号栈', '输入串', '所用产生式'])

        self.pre_line_dit = QLineEdit("Input statement")
        self.start_btn = QPushButton("Start")
        self.start_step_btn = QPushButton("Next Step")
        self.clear_all_btn = QPushButton("Clear")
        self.gird_w_r = QGridLayout()


        self.gird_f = QGridLayout()

        self.set_layout()
        self.set_action()

    def set_layout(self):
        self.gird_op.addWidget(self.open_file_btn, 0, 0)
        self.gird_op.addWidget(self.ok_grammar_btn, 0, 1)
        self.gird_op.addWidget(self.first_btn, 0, 2)
        self.gird_op.addWidget(self.follow_btn, 0, 3)
        self.gird_op.addWidget(self.create_pre_table, 0, 4)
        self.pre_op_widget.setLayout(self.gird_op)

        self.gird_w.addWidget(self.pre_edit, 0, 0, 1, 2)
        self.gird_w.addWidget(self.pre_first_table, 1, 0, 1, 2)
        self.gird_w.addWidget(self.pre_follow_table, 2, 0, 1, 2)
        self.pre_widget_left.setLayout(self.gird_w)

        self.gird_w_r.addWidget(self.pre_pre_table, 0, 0, 1, 4)
        self.gird_w_r.addWidget(self.pre_line_dit, 1, 0, 1, 1)
        self.gird_w_r.addWidget(self.start_btn, 1, 1, 1, 1)
        self.gird_w_r.addWidget(self.start_step_btn, 1, 2, 1, 1)
        self.gird_w_r.addWidget(self.clear_all_btn, 1, 3, 1, 1)
        self.gird_w_r.addWidget(self.pre_list, 2, 0, 1, 4)
        self.pre_widget_right.setLayout(self.gird_w_r)

        self.gird_f.addWidget(self.pre_op_widget, 0, 0, 1, 2)
        self.gird_f.addWidget(self.pre_widget_left, 1, 0)
        self.gird_f.addWidget(self.pre_widget_right, 1, 1)
        self.gird_f.setColumnStretch(0, 1)
        self.gird_f.setColumnStretch(1, 1)
        self.setLayout(self.gird_f)

    def set_action(self):
        self.open_file_btn.clicked.connect(self.pre_open_file)
        self.ok_grammar_btn.clicked.connect(self.pre_ok_grammar)
        self.first_btn.clicked.connect(self.pre_first_start)
        self.follow_btn.clicked.connect(self.pre_follow_start)
        self.create_pre_table.clicked.connect(self.pre_create_table)
        self.start_step_btn.clicked.connect(self.pre_start_step)
        self.start_btn.clicked.connect(self.pre_start_all)
        self.clear_all_btn.clicked.connect(self.pre_clear_all)

    def pre_clear_all(self):
        self.pre_list.clear()
        self.pre_forecasting.analysis_init()
        self.result = True

    def pre_start_step(self):
        try:
            if self.pre_forecasting.analysis_text == '':
                s = self.pre_line_dit.text()
                self.pre_forecasting.set_analysis_text(s)
                self.step_no = 0
                self.result = True
            if self.result:
                info_str, self.result = self.pre_forecasting.analysis()
                if info_str:
                    self.pre_list.insertRow(self.step_no)
                    self.pre_list.setItem(self.step_no, 0, QTableWidgetItem(str(self.step_no + 1)))
                    self.pre_list.setItem(self.step_no, 1, QTableWidgetItem(str(self.pre_forecasting.sign_stack)))
                    self.pre_list.setItem(self.step_no, 2, QTableWidgetItem(self.pre_forecasting.analysis_text[
                                                                             self.pre_forecasting.exp_index::]))
                    self.pre_list.setItem(self.step_no, 3, QTableWidgetItem(info_str))
                    self.step_no += 1
            return self.result
        except Exception as e:
            print(e)
        return False

    def pre_start_all(self):
        while self.pre_start_step():
            pass

    def pre_create_table(self):
        try:
            self.pre_forecasting.create_forecasting_table()
            ter_list = self.pre_forecasting.grammar.terminal_symbol + ['#']
            self.pre_pre_table.setColumnCount(len(ter_list))
            self.pre_pre_table.setHorizontalHeaderLabels(ter_list)
            self.pre_pre_table.setVerticalHeaderLabels(self.pre_forecasting.grammar.non_terminal_symbol)
            for y, non in enumerate(self.pre_forecasting.grammar.non_terminal_symbol):
                self.pre_pre_table.insertRow(y)
                for x, ter in enumerate(ter_list):
                    try:
                        gar = self.pre_forecasting.forecast_table[non][ter]
                        self.pre_pre_table.setItem(y, x, QTableWidgetItem(non + '->' + gar))
                    except Exception as e:
                        print(e)
            self.pre_pre_table.resizeColumnsToContents()
            self.pre_pre_table.resizeRowsToContents()
        except Exception as e:
            print(e)

    def pre_first_start(self):
        try:
            self.pre_forecasting.get_first_set()
            ter_list = self.pre_forecasting.grammar.terminal_symbol + ['$']
            self.pre_first_table.setColumnCount(len(ter_list))
            self.pre_first_table.setHorizontalHeaderLabels(ter_list)
            self.pre_first_table.resizeColumnsToContents()
            self.pre_first_table.resizeRowsToContents()
            self.pre_first_table.setVerticalHeaderLabels(self.pre_forecasting.grammar.non_terminal_symbol)
            for y, non in enumerate(self.pre_forecasting.grammar.non_terminal_symbol):
                self.pre_first_table.insertRow(y)
                for x, ter in enumerate(ter_list):
                    t = self.pre_forecasting.first_set[non]
                    if ter in t:
                        self.pre_first_table.setItem(y, x, QTableWidgetItem('1'))
        except Exception as e:
            print(e)

    def pre_follow_start(self):
        try:
            self.pre_forecasting.get_follow_set()
            ter_list = self.pre_forecasting.grammar.terminal_symbol + ['#']
            self.pre_follow_table.setColumnCount(len(ter_list))
            self.pre_follow_table.setHorizontalHeaderLabels(ter_list)
            self.pre_follow_table.resizeColumnsToContents()
            self.pre_follow_table.resizeRowsToContents()
            self.pre_follow_table.setVerticalHeaderLabels(self.pre_forecasting.grammar.non_terminal_symbol)
            for y, non in enumerate(self.pre_forecasting.grammar.non_terminal_symbol):
                self.pre_follow_table.insertRow(y)
                for x, ter in enumerate(ter_list):
                    t = self.pre_forecasting.follow_set[non]
                    if ter in t:
                        self.pre_follow_table.setItem(y, x, QTableWidgetItem('1'))
        except Exception as e:
            print(e)

    def pre_open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", '',
                                                  "All Files (*);;"
                                                  "C++ Files (*.cpp *.h *.py);;"
                                                  "Txt files (*.txt);;"
                                                  "Python files (*.py);;"
                                                  "HTML-Files (*.htm *.html)")

        print(filename)
        if filename:
            try:
                infile = QFile(filename)
                if infile.open(QFile.ReadOnly | QFile.Text):
                    print('read start')
                    text = infile.readAll()
                    text = str(text, encoding='utf-8')
                    print(text)
                    self.pre_edit.setPlainText(text)
                    infile.close()
                    return True
            except Exception as e:
                QMessageBox.warning(self, "Text Editor -- Save Error",
                                    "Failed to save {0}: {1}".format(self.filename, e))
        return False

    def pre_ok_grammar(self):
        try:
            self.pre_forecasting = Forecasting(text=self.pre_edit.toPlainText())

        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("Zhangtian.")
    app.setOrganizationDomain("elezt.cn")
    app.setApplicationName("Complier Editer")
    form = Ll1Ui()
    form.show()
    app.exec_()
