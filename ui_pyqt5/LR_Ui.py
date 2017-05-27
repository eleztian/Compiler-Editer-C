import sys
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import (QApplication, QGridLayout, QTextEdit, QWidget, QFrame,
                             QPushButton, QTableWidget, QLineEdit,  QAbstractItemView,
                             QMessageBox, QTableWidgetItem, QFileDialog)
from logic.LR0 import LR0


class LRUI(QFrame):
    lr_analysis = None
    step_no = 0
    lr_analysis_text = ''

    def __init__(self):
        super(LRUI, self).__init__()
        self.frame_grid = QGridLayout()

        self.lr_op_widget = QWidget()
        self.lr_open_file_btn = QPushButton(self.lr_op_widget, text="Open")
        self.lr_ok_grammar_btn = QPushButton(self.lr_op_widget, text="OK")
        self.lr_items_btn = QPushButton(self.lr_op_widget, text="Items")
        self.lr_table_btn = QPushButton(self.lr_op_widget, text="LR(0)Table")
        self.gird_op = QGridLayout()
        self.gird_op.addWidget(self.lr_open_file_btn, 0, 0)
        self.gird_op.addWidget(self.lr_ok_grammar_btn, 0, 1)
        self.gird_op.addWidget(self.lr_items_btn, 0, 2)
        self.gird_op.addWidget(self.lr_table_btn, 0, 3)
        self.lr_op_widget.setLayout(self.gird_op)

        self.lr_edit_widget = QWidget()
        self.lr_edit_grid = QGridLayout()

        self.lr_edit = QTextEdit(self.lr_edit_widget)

        self.lr_lineEdit = QLineEdit(self.lr_edit_widget, text="Input Statement")
        self.lr_start_btn = QPushButton("Start")
        self.lr_steup_btn = QPushButton("Steup")
        self.lr_clear_btn = QPushButton("Clear")

        self.lr_tables_widget = QWidget()
        self.grid_tables = QGridLayout()
        self.lr_items_table = QTableWidget()
        self.lr_items_table.resizeColumnsToContents()
        self.lr_items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lr_items_table.verticalHeader().setVisible(False)
        self.lr_items_table.setColumnCount(2)
        self.lr_items_table.setHorizontalHeaderLabels(['StateNo', 'Item Set'])

        self.lr_table_table = QTableWidget()
        self.lr_table_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lr_table_table.verticalHeader().setVisible(False)

        self.lr_analysis_table = QTableWidget()
        self.lr_analysis_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lr_analysis_table.verticalHeader().setVisible(False)
        self.lr_analysis_table.setColumnCount(5)
        self.lr_analysis_table.setHorizontalHeaderLabels(['StepNo', 'StateStack', 'SignStack', 'InputString', 'Info'])

        self.set_layout()
        self.set_action()

    def set_layout(self):
        self.lr_edit_grid.addWidget(self.lr_edit, 0, 0, 2, 3)
        self.lr_edit_grid.addWidget(self.lr_lineEdit, 0, 4, 1, 3)
        self.lr_edit_grid.addWidget(self.lr_steup_btn, 1, 4, 1, 1)
        self.lr_edit_grid.addWidget(self.lr_start_btn, 1, 5, 1, 1)
        self.lr_edit_grid.addWidget(self.lr_clear_btn, 1, 6, 1, 1)
        self.lr_edit_widget.setLayout(self.lr_edit_grid)

        self.grid_tables.addWidget(self.lr_items_table, 0, 0)
        self.grid_tables.addWidget(self.lr_table_table, 0, 1)
        self.grid_tables.addWidget(self.lr_analysis_table, 0, 2)
        self.grid_tables.setColumnStretch(0, 2)
        self.grid_tables.setColumnStretch(1, 3)
        self.grid_tables.setColumnStretch(2, 4)
        self.lr_tables_widget.setLayout(self.grid_tables)

        self.frame_grid.addWidget(self.lr_op_widget, 0, 0)
        self.frame_grid.addWidget(self.lr_edit_widget, 1, 0)
        self.frame_grid.addWidget(self.lr_tables_widget, 2, 0)
        self.setLayout(self.frame_grid)

    def set_action(self):
        self.lr_open_file_btn.clicked.connect(self.lr_open_file)
        self.lr_ok_grammar_btn.clicked.connect(self.lr_ok_grammar)
        self.lr_items_btn.clicked.connect(self.lr_items_start)
        self.lr_table_btn.clicked.connect(self.lr_table_start)
        self.lr_start_btn.clicked.connect(self.lr_start_analysis)
        self.lr_steup_btn.clicked.connect(self.lr_steup_analysis)
        self.lr_clear_btn.clicked.connect(self.lr_clear_tables)

    def lr_open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", '',
                                                  "All Files (*);;"
                                                  "C++ Files (*.cpp *.h *.py);;"
                                                  "Txt files (*.txt);;"
                                                  "Python files (*.py);;"
                                                  "HTML-Files (*.htm *.html)")
        if filename:
            try:
                inFile = QFile(filename)
                if inFile.open(QFile.ReadOnly | QFile.Text):
                    text = inFile.readAll()
                    text = str(text, encoding='utf-8')
                    self.lr_edit.setPlainText(text)
                    inFile.close()
                    return True
            except Exception as e:
                QMessageBox.warning(self, "Text Editor -- Save Error",
                                    "Failed to save {0}: {1}".format(self.filename, e))
        return False

    def lr_ok_grammar(self):
        try:
            self.lr_analysis = LR0(text=self.lr_edit.toPlainText())
        except Exception as e:
            print(e)

    def lr_items_start(self):
        try:
            self.lr_analysis.create_dfa()
            list_items = self.lr_analysis.dfa.get_items_show(self.lr_analysis.grammar.grammar_list)
            for index, i in enumerate(list_items):
                try:
                    self.lr_items_table.insertRow(index)
                    self.lr_items_table.setItem(index, 0, QTableWidgetItem(str(index)))
                    self.lr_items_table.setItem(index, 1, QTableWidgetItem(i))
                except Exception as e:
                    print(e)
            self.lr_items_table.resizeColumnsToContents()
        except Exception as e:
            print(e)

    def lr_table_start(self):
        try:
            self.lr_analysis.create_lr0_table()
            action = self.lr_analysis.action
            goto = self.lr_analysis.goto
            h = ['State'] \
                + self.lr_analysis.grammar.terminal_symbol \
                + ['#'] \
                + self.lr_analysis.grammar.non_terminal_symbol
            row_len = len(h)
            col_len = len(self.lr_analysis.dfa.node_list)
            self.lr_table_table.setRowCount(col_len)
            self.lr_table_table.setColumnCount(row_len)
            self.lr_table_table.setHorizontalHeaderLabels(h)
            for i in range(col_len):
                self.lr_table_table.setItem(i, 0, QTableWidgetItem(str(i)))
                dic = action[i]
                t = list(dic.keys())
                print(t)
                try:
                    for v in t:
                        if v != '$':
                            self.lr_table_table.setItem(i, h.index(v), QTableWidgetItem(dic[v]))
                    dic = goto[i]
                    print(goto)
                    t = list(dic.keys())
                    for v in t:
                        if v != '$':
                            self.lr_table_table.setItem(i, h.index(v), QTableWidgetItem(str(dic[v])))
                except Exception as e:
                    print(e)
            self.lr_table_table.resizeColumnsToContents()
        except Exception as e:
            print(e)

    def lr_start_analysis(self):
        while self.lr_steup_analysis():
            pass

    def lr_steup_analysis(self):
        try:
            s = self.lr_lineEdit.text()
            if s != self.lr_analysis.analysis_text:
                self.lr_clear_tables()
                self.lr_analysis.set_analysis_text(s)
                self.lr_analysis.analysis_init()
            re, isover, info = self.lr_analysis.analysis_lr0()
            if re or isover:
                self.lr_analysis_table.insertRow(self.step_no)
                self.lr_analysis_table.setItem(self.step_no, 0, QTableWidgetItem(str(self.step_no)))
                # self.lr_analysis_table.setItem(self.step_no, 1, QTableWidgetItem(''.join(self.lr_analysis.state_stack.items)))
                # self.lr_analysis_table.setItem(self.step_no, 2, QTableWidgetItem(''.join(self.lr_analysis.sign_stack.items)))
                # self.lr_analysis_table.setItem(self.step_no, 3, QTableWidgetItem(''.join(self.lr_analysis.last_str_stack.items)))
                self.lr_analysis_table.setItem(self.step_no, 1,
                                               QTableWidgetItem(str(self.lr_analysis.state_stack.items)))
                self.lr_analysis_table.setItem(self.step_no, 2,
                                               QTableWidgetItem(str(self.lr_analysis.sign_stack.items)))
                self.lr_analysis_table.setItem(self.step_no, 3,
                                               QTableWidgetItem(str(self.lr_analysis.last_str_stack.items)))
                self.lr_analysis_table.setItem(self.step_no, 4, QTableWidgetItem(info))
                self.step_no += 1
                return re
        except Exception as e:
            return False
            print(e)


    def lr_clear_tables(self):
        pass
        self.lr_analysis_table.clear()
        self.step_no = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("Zhangtian.")
    app.setOrganizationDomain("elezt.cn")
    app.setApplicationName("Complier Editer")
    form = LRUI()
    form.show()
    app.exec_()
