import sys

from PyQt5.QtCore import QFile, QFileInfo, QSettings, QTimer, Qt, QByteArray
from PyQt5.QtGui import QIcon, QKeySequence, QTextDocumentWriter
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QGridLayout,
                             QMainWindow, QMessageBox, QTabWidget,
                             QWidget, QDockWidget, QTabBar, QListWidget)
from ui_pyqt5.bterEdit import BterEdit
from ui_pyqt5 import textedit_rc
from logic.Lexer import Lexer
from logic.Semanticer import Syner
from ui_pyqt5.Ll1 import Ll1Ui
from ui_pyqt5.LR_Ui import LRUI
from ui_pyqt5.Regual2automata import Regual2autoUI

__version__ = "1.0.0"
rsrcfilename = ":/images/win"


class MainWindow(QMainWindow):
    filename = ""
    docwidget = {}
    step_no = 0
    lexer = None
    syner = None
    pre_analysis = None
    lr_anlysis = None
    regual2auto = None

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowIcon(QIcon(':/images/logo.png'))
        self.setup_ui()
        self.setup_menu()
        self.setting()

    def setup_ui(self):
        w = QWidget()
        self.layout = QGridLayout()
        w.setLayout(self.layout)
        self.setCentralWidget(w)
        self.tab = QTabWidget(w)
        qtabBAR = QTabBar()
        self.tab.setTabBar(qtabBAR)
        # 允许tab点击关闭
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.tab_close)
        self.tab.currentChanged.connect(self.tab_changed)

    def tab_changed(self):
        self.filename = self.tab.currentWidget().filename
        self.set_current_file_name(self.filename)

    def tab_close(self, index):
        self.tab.setCurrentIndex(index)
        dock_name = QFileInfo(self.filename).fileName()
        # 关闭标签
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("The file of {0} has been modified.".format(QFileInfo(self.filename).fileName()))
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec()
        if ret == QMessageBox.Save:
            self.file_save()
            self.tab.removeTab(index)
        elif ret == QMessageBox.Discard:
            self.tab.removeTab(index)
            self.layout.addWidget(self.tab)
        else:
            pass

    def setting(self):
        settings = QSettings()  # 保存用户程序当前状态，下次打开时原样恢复
        if settings.value("MainWindow/Geometry") or settings.value("MainWindow/State"):
            self.restoreGeometry(
                QByteArray(settings.value("MainWindow/Geometry")))
            self.restoreState(
                QByteArray(settings.value("MainWindow/State")))
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)
        self.setWindowTitle("Complier Editer")
        QTimer.singleShot(0, self.load_files)  # 定时触发器

    def setup_edit(self, widget):
        t = BterEdit(widget)
        t.setObjectName("t")
        self.layout.addWidget(self.tab)
        self.tab.addTab(t, t.filename)

        return t

    def setup_menu(self):
        file_new_action = self.create_action("&New", self.file_new,
                                             QKeySequence.New, rsrcfilename + '/filenew.png', "Create a text file")
        file_open_action = self.create_action("&Open...", self.file_open,
                                              QKeySequence.Open, rsrcfilename + '/fileopen.png',
                                              "Open an existing text file")
        file_save_action = self.create_action("&Save", self.file_save,
                                              QKeySequence.Save, rsrcfilename + '/filesave.png', "Save the text")
        file_save_as_action = self.create_action("Save &As...",
                                                 self.file_save_as, icon="filesaveas",
                                                 tip="Save the text using a new filename")
        file_quit_action = self.create_action("&Quit", self.close,
                                              "Ctrl+Q", "filequit", "Close the application")
        edit_copy_action = self.create_action("&Copy", self.edit_copy,
                                              QKeySequence.Copy, rsrcfilename + '/editcopy.png',
                                              "Copy text to the clipboard")
        edit_cut_action = self.create_action("Cu&t", self.edit_cut,
                                             QKeySequence.Cut, rsrcfilename + '/editcut.png',
                                             "Cut text to the clipboard")
        edit_paste_action = self.create_action("&Paste", self.edit_paste,
                                               QKeySequence.Paste, rsrcfilename + '/edipaste.png',
                                               "Paste in the clipboard's text")
        edit_redo_action = self.create_action("&Redo", self.edit_redo,
                                              QKeySequence.Redo, rsrcfilename + '/editredo.png',
                                              "Redo")
        edit_undo_action = self.create_action("&Undo", self.edit_undo,
                                              QKeySequence.Undo, rsrcfilename + '/editundo.png',
                                              "Undo")
        lexical_analysis_action = self.create_action("&Start", self.start_lexer)
        predictive_analysis_action = self.create_action("&LL(1) Analysis", self.predictive_analysis)
        lr_ananlysis_action = self.create_action("&LR(0) Analysis", self.lr_stup)

        regular_nfa_action = self.create_action("&Exp->Autometa", self.regualexp_nfa)

        file_menu = self.menuBar().addMenu("&File")
        self.add_actions(file_menu, (file_new_action, file_open_action,
                                     file_save_action, file_save_as_action,
                                     None, file_quit_action))
        edit_menu = self.menuBar().addMenu("&Edit")
        self.add_actions(edit_menu, (edit_copy_action, edit_cut_action, edit_paste_action,
                                     edit_undo_action, edit_redo_action))
        lexical_analysis_menu = self.menuBar().addMenu("&LexicalAnalysis")
        self.add_actions(lexical_analysis_menu, (lexical_analysis_action, regular_nfa_action))
        syntax_analysis_menu = self.menuBar().addMenu("&SyntaxAnalysis")
        self.add_actions(syntax_analysis_menu, (predictive_analysis_action, lr_ananlysis_action))
        middle_code_menu = self.menuBar().addMenu("&MiddleCode")
        target_code_menu = self.menuBar().addMenu("&TargetCode")
        helpMenu = self.menuBar().addMenu("&Help")

        file_toolbar = self.addToolBar("File")
        file_toolbar.setObjectName("file_toolbar")
        self.add_actions(file_toolbar, (file_new_action, file_open_action, file_save_action))
        edit_toolbar = self.addToolBar("Edit")
        edit_toolbar.setObjectName("edit_toolbar")
        self.add_actions(edit_toolbar,
                         (edit_copy_action, edit_cut_action, edit_paste_action,
                          edit_undo_action, edit_redo_action))

    def create_action(self, text, slot=None, shortcut=None, icon=None, 
                      tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon("{0}".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    @staticmethod
    def add_actions(target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def predictive_analysis(self):
        self.pre_analysis = Ll1Ui()
        self.pre_analysis.show()

    def lr_stup(self):
        self.lr_anlysis = LRUI()
        self.lr_anlysis.show()

    def regualexp_nfa(self):
        self.regual2auto = Regual2autoUI()
        self.regual2auto.show()

    def show_toker_error_sign(self, token, error, sign):
        print(token)
        dock_name = QFileInfo(self.filename).fileName()
        flag = 1
        try:
            self.docwidget[dock_name]["token"].addItem("LineNo\tWord\tCode")
            for i in token:
                self.docwidget[dock_name]["token"].addItem(str(i[0]) + '\t' + i[1] + '\t' + str(i[2]))
            for i in error:
                flag = 0
                self.docwidget[dock_name]["error"].addItem(self.lexer.error_info[self.lexer.error_type[i[0]]] % i)
            self.docwidget[dock_name]["sign"].addItem("Entry\tWord\tLength\tType")
            for index, i in enumerate(sign):
                self.docwidget[dock_name]["sign"].addItem(str(index) + '\t'
                                                          + i[0] + '\t'
                                                          + str(len(i[0])) + '\t'
                                                          + i[1])
        except Exception as e:
            print(e)
        if flag:
            try:
                self.syner = Syner(self.filename)
                self.syner.sinOut.connect(self.show_syner_info)
                self.syner.run()
            except Exception as e:
                print(e)

    def show_syner_info(self, log, error, sign, quaternary):
        dock_name = QFileInfo(self.filename).fileName()
        print('syner finished')
        for i in error:
            self.docwidget[dock_name]["error"].addItem(i)
        for i in log:
            self.docwidget[dock_name]["log"].addItem(i)
        self.docwidget[dock_name]["sign"].clear()
        for index, i in enumerate(sign):
            self.docwidget[dock_name]["sign"].addItem(str(index) + '\t'
                                                          + str(i[0]) + '\t'
                                                          + str(i[1]) + '\t'
                                                          + str(i[2]))
        keys = list(quaternary.keys())
        print(keys)
        try:
            for k in keys:
                print(k)
                self.docwidget[dock_name]['quaternary'].addItem(k + ':')
                li = quaternary[k]
                print(li)
                for index, i in enumerate(li):
                    self.docwidget[dock_name]['quaternary'].addItem('\t'+str(index) +
                                                                    '\t'+str(i[0]) +
                                                                    '\t'+str(i[1]) +
                                                                    '\t'+str(i[2]) +
                                                                    '\t'+str(i[3])
                                                                    )
        except Exception as e:
            print(e)

    def token_list_double_clicked_fun(self, item):
        line_no = int(str(item.text()).split('\t')[0])
        try:
            edit = self.tab.currentWidget().e_edit
            tc = edit.textCursor()
            position = edit.document().findBlockByNumber(line_no - 1).position()
            tc.setPosition(position, tc.KeepAnchor)
            tc.movePosition(tc.NoMove, tc.KeepAnchor)
            tc.select(tc.LineUnderCursor)
            edit.setTextCursor(tc)
            edit.setFocus()
        except Exception as e:
            print(e)

    def error_list_double_clicked_fun(self, item):
        print(str(item.text()).split(" "))
        line_no = int(str(item.text()).split(' ')[3])
        try:
            edit = self.tab.currentWidget().e_edit
            tc = edit.textCursor()
            position = edit.document().findBlockByNumber(line_no - 1).position()
            tc.setPosition(position, tc.KeepAnchor)
            tc.movePosition(tc.NoMove, tc.KeepAnchor)
            tc.select(tc.LineUnderCursor)
            edit.setTextCursor(tc)
            edit.setFocus()
        except Exception as e:
            print(e)

    def start_lexer(self):
        dock_name = QFileInfo(self.filename).fileName()
        token = QListWidget()
        error = QListWidget()
        sign = QListWidget()
        log = QListWidget()
        quaternary = QListWidget()
        self.docwidget[dock_name] = {"token": token, "error": error, "sign": sign, "log": log, 'quaternary': quaternary}
        token.itemDoubleClicked.connect(self.token_list_double_clicked_fun)
        error.itemDoubleClicked.connect(self.error_list_double_clicked_fun)
        self.lexer = Lexer(self.filename)
        try:
            self.lexer.sinOut.connect(self.show_toker_error_sign)
            self.lexer.start()
        except Exception as e:
            print("Start Lexer Error:", e)
        dock_token = QDockWidget(dock_name+"_Token")  # 实例化dockwidget类
        dock_token.setWidget(self.docwidget[dock_name]["token"])  # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        dock_token.setObjectName(dock_name)
        dock_token.setFeatures(dock_token.AllDockWidgetFeatures)  # 设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea, dock_token)  # 设置dockwidget放置在QMainWindow中的位置，并且将dockwidget添加至QMainWindow中

        dock_error = QDockWidget(dock_name+"_Error")
        dock_error.setWidget(self.docwidget[dock_name]["error"])
        dock_error.setObjectName(dock_name)
        dock_error.setFeatures(dock_error.AllDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_error)

        dock_sign = QDockWidget(dock_name+"_sign")
        dock_sign.setWidget(self.docwidget[dock_name]["sign"])
        dock_sign.setObjectName(dock_name)
        dock_sign.setFeatures(dock_sign.AllDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_sign)

        dock_log = QDockWidget(dock_name + "_log")
        dock_log.setWidget(self.docwidget[dock_name]["log"])
        dock_log.setObjectName(dock_name)
        dock_log.setFeatures(dock_log.AllDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_log)

        dock_quaternary = QDockWidget(dock_name + "_quaternary")
        dock_quaternary.setWidget(self.docwidget[dock_name]["quaternary"])
        dock_quaternary.setObjectName(dock_name)
        dock_quaternary.setFeatures(dock_log.AllDockWidgetFeatures)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_quaternary)

        self.tabifyDockWidget(dock_token, dock_error)
        self.tabifyDockWidget(dock_error, dock_sign)
        self.tabifyDockWidget(dock_sign, dock_log)
        self.tabifyDockWidget(dock_log, dock_quaternary)
        print('ui')

    def closeEvent(self, event):
        failures = []
        text_edit = self.tab.currentWidget().e_edit
        if text_edit.isModified():
            try:
                text_edit.save()
            except IOError as e:
                failures.append(str(e))
        if (failures and
            QMessageBox.warning(self, "Text Editor -- Save Error",
                                "Failed to save{0}\nQuit anyway?".format("\n\t".join(failures)),
                                QMessageBox.Yes | QMessageBox.No
                                ) == QMessageBox.No):
            event.ignore()
            return
        settings = QSettings()
        settings.setValue("MainWindow/Geometry",
                          self.saveGeometry())
        settings.setValue("MainWindow/State",
                          self.saveState())
        files = []
        for text_edit in self.mdi.subWindowList():
            text_edit=text_edit.widget()
            if not text_edit.filename.startswith("Unnamed"):
                files.append(text_edit.filename)
        settings.setValue("CurrentFiles", files)
        self.mdi.closeAllSubWindows()

    def load_files(self):
        if len(sys.argv) > 1:
            for filename in sys.argv[1:31]: # Load at most 30 files
                self.filename = filename
                if QFileInfo(filename).isFile():
                    self.load_file(filename)
                    QApplication.processEvents()
        else:
            settings = QSettings()
            # files = settings.value("CurrentFiles").toStringList()
            if settings.value("CurrentFiles"):
                files=settings.value("CurrentFiles")
                for filename in files:
                    filename = filename
                    if QFile.exists(filename):
                        self.load_file(filename)
                        QApplication.processEvents()

    def file_new(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save as...", None,
                                                      "Txt files (*.txt);;"
                                                      "Python files (*.py);;"
                                                      "HTML-Files (*.htm *.html);;"
                                                      "All Files (*)")
            if filename:
                t = BterEdit()
                t.filename = filename
                self.tab.addTab(t, QFileInfo(filename).fileName())
                self.tab.setCurrentWidget(t)
                self.layout.addWidget(self.tab)
        except:
            return False
        return True

    def set_current_file_name(self, fileName=''):
        # self.filename = fileName
        self.tab.currentWidget().e_edit.document().setModified(False)
        if not fileName:
            shownName = 'untitled.txt'
        else:
            shownName = QFileInfo(fileName).fileName()
        self.setWindowTitle(self.tr("%s[*] - %s" % (shownName, "Complier Editer")))
        self.setWindowModified(False)

    def file_open(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", '',
                                                       "All Files (*);;"
                                                       "C++ Files (*.cpp *.h *.py);;"
                                                       "Txt files (*.txt);;"
                                                       "Python files (*.py);;"
                                                       "HTML-Files (*.htm *.html)")
        if filename:
            t = BterEdit()
            t.filename = filename

            self.tab.addTab(t, QFileInfo(filename).fileName())
            self.tab.setCurrentWidget(t)
            self.layout.addWidget(self.tab)
            return self.load_file()
        return False

    def load_file(self):
        if self.filename:
            try:
                inFile = QFile(self.filename)
                if inFile.open(QFile.ReadOnly | QFile.Text):
                    text = inFile.readAll()
                    text = str(text, encoding='utf-8')
                    self.tab.currentWidget().e_edit.setPlainText(text)
                    inFile.close()
            except Exception as e:
                QMessageBox.warning(self, "Text Editor -- Save Error",
                                    "Failed to save {0}: {1}".format(self.filename, e))
                return False
            return True

    def file_save(self):
        print(self.filename)
        if not self.filename:
            return self.file_save_as()
        else:
            writer = QTextDocumentWriter(self.filename)
            success = writer.write(self.tab.currentWidget().e_edit.document())
            if success:
                self.tab.currentWidget().e_edit.document().setModified(False)
                print("save")
                return True
        return False

    def file_save_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save as...", None,
                                            "Txt files (*.txt);;"
                                            "Python files (*.py);;"
                                            "HTML-Files (*.htm *.html);;"
                                            "All Files (*)")
        if filename:
            self.filename = filename
            if self.file_save():
                self.tab.setTabText(self.tab.currentIndex(),QFileInfo(filename).fileName())
        return False

    def edit_copy(self):
        text_edit = self.tab.currentWidget().e_edit
        cursor = text_edit.textCursor()
        text = cursor.selectedText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def edit_cut(self):
        text_edit = self.tab.currentWidget().e_edit
        cursor = text_edit.textCursor()
        text = cursor.selectedText()
        if text:
            cursor.removeSelectedText()
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def edit_paste(self):
        text_edit = self.tab.currentWidget().e_edit
        clipboard = QApplication.clipboard()
        text_edit.insertPlainText(clipboard.text())

    def edit_redo(self):
        self.tab.currentWidget().e_edit.redo()

    def edit_undo(self):
        self.tab.currentWidget().e_edit.undo()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("Zhangtian.")
    app.setOrganizationDomain("elezt.cn")
    app.setApplicationName("Complier Editer")
    form = MainWindow()
    form.resize(1500, 1000)
    form.show()
    app.exec_()

