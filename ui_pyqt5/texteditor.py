import sys

from PyQt5.QtCore import (QFile, QFileInfo, QSettings, QTimer, Qt, QByteArray,QThread)
from PyQt5.QtGui import QIcon, QKeySequence, QTextDocumentWriter,QTextCursor,QTextBlock
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QGridLayout,
                             QMainWindow, QMessageBox, QTextEdit, QTabWidget,
                             QWidget, QDockWidget, QTabBar, QListWidget, QFrame,
                             QPushButton, QTableWidget, QLineEdit, QTableWidgetItem, QAbstractItemView)
from logic.Lexer import Lexer
from logic.Syner_v2 import Syner
from ui_pyqt5.bterEdit import BterEdit
from ui_pyqt5 import  textedit_rc
from logic.complier_s import error_info, error_type
from logic.Forecast_analysis import Forecasting
__version__ = "1.0.0"
rsrcfilename = ":/images/win"


class MainWindow(QMainWindow):
    filename = ""
    docwidget = {}
    step_no = 0

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
        self.setCurrentFileName(self.filename)

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
            self.fileSave()
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
        QTimer.singleShot(0, self.loadFiles)  # 定时触发器

    def setup_edit(self, widget):
        t = BterEdit(widget)
        t.setObjectName("t")
        self.layout.addWidget(self.tab)
        self.tab.addTab(t, t.filename)

        return t

    def setup_menu(self):
        fileNewAction = self.createAction("&New", self.fileNew,
                                          QKeySequence.New, rsrcfilename + '/filenew.png', "Create a text file")
        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                                           QKeySequence.Open, rsrcfilename + '/fileopen.png',
                                           "Open an existing text file")
        fileSaveAction = self.createAction("&Save", self.fileSave,
                                           QKeySequence.Save, rsrcfilename + '/filesave.png', "Save the text")
        fileSaveAsAction = self.createAction("Save &As...",
                                             self.fileSaveAs, icon="filesaveas",
                                             tip="Save the text using a new filename")
        fileQuitAction = self.createAction("&Quit", self.close,
                                           "Ctrl+Q", "filequit", "Close the application")
        editCopyAction = self.createAction("&Copy", self.editCopy,
                                           QKeySequence.Copy, rsrcfilename + '/editcopy.png',
                                           "Copy text to the clipboard")
        editCutAction = self.createAction("Cu&t", self.editCut,
                                          QKeySequence.Cut, rsrcfilename + '/editcut.png',
                                          "Cut text to the clipboard")
        editPasteAction = self.createAction("&Paste", self.editPaste,
                                            QKeySequence.Paste, rsrcfilename + '/editpaste.png',
                                            "Paste in the clipboard's text")
        editRedoAction = self.createAction("&Redo", self.editRedo,
                                           QKeySequence.Redo, rsrcfilename + '/editredo.png',
                                           "Redo")
        editUndoAction = self.createAction("&Undo", self.editUndo,
                                           QKeySequence.Undo, rsrcfilename + '/editundo.png',
                                           "Undo")
        LexicalAnalysisAction = self.createAction("&Start", self.start_lexer)
        predictiveAnalysisAction = self.createAction("&Predictive Analysis", self.predictive_analysis)
        fileMenu = self.menuBar().addMenu("&File")
        self.addActions(fileMenu, (fileNewAction, fileOpenAction,
                                   fileSaveAction, fileSaveAsAction,
                                   None, fileQuitAction))
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (editCopyAction, editCutAction,
                                   editPasteAction, editUndoAction, editRedoAction))
        lexicalAnalysisMenu = self.menuBar().addMenu("&LexicalAnalysis")
        self.addActions(lexicalAnalysisMenu, (LexicalAnalysisAction,))
        syntaxAnalysisMenu = self.menuBar().addMenu("&SyntaxAnalysis")
        self.addActions(syntaxAnalysisMenu, (predictiveAnalysisAction,))
        middleCodeMenu = self.menuBar().addMenu("&MiddleCode")
        targetCodeMenu = self.menuBar().addMenu("&TargetCode")
        helpMenu = self.menuBar().addMenu("&Help")

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolbar")
        self.addActions(fileToolbar, (fileNewAction, fileOpenAction,
                                      fileSaveAction))
        editToolbar = self.addToolBar("Edit")
        editToolbar.setObjectName("EditToolbar")
        self.addActions(editToolbar,
                        (editCopyAction, editCutAction, editPasteAction,
                         editUndoAction, editRedoAction)
                        )

    def createAction(self, text, slot=None, shortcut=None, icon=None,
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

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def CreateDockWidget(self):  # 定义一个createDock方法创建一个dockwidget
        e = QTextEdit()
        name = "test"
        e.setPlainText(self.tab.currentWidget().e_edit.toPlainText())
        dock = QDockWidget(name)  # 实例化dockwidget类
        dock.setWidget(e)  # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        dock.setObjectName(name)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)  # 设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea,
                           dock)  # 设置dockwidget放置在QMainWindow中的位置，并且将dockwidget添加至QMainWindow中

    def predictive_analysis(self):
        self.pre_frame = QFrame()

        self.pre_op_widget = QWidget(self.pre_frame)
        self.open_file_btn = QPushButton(self.pre_op_widget, text="Open")
        self.ok_grammar_btn = QPushButton(self.pre_op_widget, text="OK")
        self.follow_btn = QPushButton(self.pre_op_widget, text="Fillow")
        self.first_btn = QPushButton(self.pre_op_widget, text="First")
        self.create_pre_table = QPushButton(self.pre_op_widget, text="Create Tabel")
        gird_op = QGridLayout()
        gird_op.addWidget(self.open_file_btn, 0, 0)
        gird_op.addWidget(self.ok_grammar_btn, 0, 1)
        gird_op.addWidget(self.first_btn, 0, 2)
        gird_op.addWidget(self.follow_btn, 0, 3)
        gird_op.addWidget(self.create_pre_table, 0, 4)
        self.pre_op_widget.setLayout(gird_op)

        self.pre_widget_left = QWidget(self.pre_frame)

        gird_w = QGridLayout()
        self.pre_edit = QTextEdit(self.pre_widget_left)
        self.pre_first_table = QTableWidget(5, 10)
        self.pre_first_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pre_first_table.setHorizontalHeaderLabels(['First'])
        self.pre_follow_table = QTableWidget(5, 10)
        self.pre_follow_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pre_follow_table.setHorizontalHeaderLabels(['Fallow'])
        gird_w.addWidget(self.pre_edit, 0, 0, 1, 2)
        gird_w.addWidget(self.pre_first_table, 1, 0, 1, 2)
        gird_w.addWidget(self.pre_follow_table, 2, 0, 1, 2)
        self.pre_widget_left.setLayout(gird_w)

        self.pre_widget_right = QWidget(self.pre_frame)
        self.pre_pre_table = QTableWidget(5, 10)
        self.pre_pre_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pre_pre_table.setHorizontalHeaderLabels(['预测表'])
        self.pre_list = QTableWidget()
        self.pre_list = QTableWidget(30, 4)
        self.pre_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.pre_list.verticalHeader().setVisible(False)
        self.pre_list.setHorizontalHeaderLabels(['步骤', '符号栈', '输入串', '所用产生式'])
        self.pre_line_dit = QLineEdit("Input statement")
        self.start_btn = QPushButton("Start")
        self.start_step_btn = QPushButton("Next Step")
        self.clear_all_btn = QPushButton("Clear")
        gird_w_r = QGridLayout()
        gird_w_r.addWidget(self.pre_pre_table, 0, 0, 1, 4)
        gird_w_r.addWidget(self.pre_line_dit, 1, 0, 1, 1)
        gird_w_r.addWidget(self.start_btn, 1, 1, 1, 1)
        gird_w_r.addWidget(self.start_step_btn, 1, 2, 1, 1)
        gird_w_r.addWidget(self.clear_all_btn, 1, 3, 1, 1)
        gird_w_r.addWidget(self.pre_list, 2, 0, 1, 4)
        self.pre_widget_right.setLayout(gird_w_r)

        gird_f = QGridLayout()
        gird_f.addWidget(self.pre_op_widget, 0, 0, 1, 2)
        gird_f.addWidget(self.pre_widget_left, 1, 0)
        gird_f.addWidget(self.pre_widget_right, 1, 1)
        gird_f.setColumnStretch(0, 1)
        gird_f.setColumnStretch(1, 1)
        self.pre_frame.setLayout(gird_f)
        self.pre_frame.show()
        self.predictive_analysis_acdtion()

    def predictive_analysis_acdtion(self):
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
            ter_list = self.pre_forecasting.terminal_symbol + ['#']
            self.pre_pre_table.setHorizontalHeaderLabels(ter_list)
            self.pre_pre_table.setVerticalHeaderLabels(self.pre_forecasting.non_terminal_symbol)
            for y, non in enumerate(self.pre_forecasting.non_terminal_symbol):
                for x, ter in enumerate(ter_list):
                    try:
                        gar = self.pre_forecasting.forecast_table[non][ter]
                        self.pre_pre_table.setItem(y, x, QTableWidgetItem(non + '->' + gar))
                    except:
                        pass
        except Exception as e:
            print(e)

    def pre_first_start(self):
        try:
            self.pre_forecasting.get_first_set()
            ter_list = self.pre_forecasting.terminal_symbol + ['$']
            self.pre_first_table.setHorizontalHeaderLabels(ter_list)
            self.pre_first_table.setVerticalHeaderLabels(self.pre_forecasting.non_terminal_symbol)
            for y, non in enumerate(self.pre_forecasting.non_terminal_symbol):
                for x, ter in enumerate(ter_list):
                    t = self.pre_forecasting.first_set[non]
                    if ter in t:
                        self.pre_first_table.setItem(y, x, QTableWidgetItem('1'))
        except Exception as e:
            print(e)

    def pre_follow_start(self):
        try:
            self.pre_forecasting.get_follow_set()
            ter_list = self.pre_forecasting.terminal_symbol + ['#']
            self.pre_follow_table.setHorizontalHeaderLabels(ter_list)
            self.pre_follow_table.setVerticalHeaderLabels(self.pre_forecasting.non_terminal_symbol)
            for y, non in enumerate(self.pre_forecasting.non_terminal_symbol):
                for x, ter in enumerate(ter_list):
                    t = self.pre_forecasting.follow_set[non]
                    if ter in t:
                        self.pre_follow_table.setItem(y, x, QTableWidgetItem('1'))
        except Exception as e:
            print(e)

    def pre_open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self.pre_frame, "Open File", '',
                                                  "All Files (*);;"
                                                  "C++ Files (*.cpp *.h *.py);;"
                                                  "Txt files (*.txt);;"
                                                  "Python files (*.py);;"
                                                  "HTML-Files (*.htm *.html)")
        print(filename)
        if filename:
            try:
                inFile = QFile(filename)
                if inFile.open(QFile.ReadOnly | QFile.Text):
                    print('read start')
                    text = inFile.readAll()
                    text = str(text, encoding='utf-8')
                    print(text)
                    self.pre_edit.setPlainText(text)
                    inFile.close()
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
                self.docwidget[dock_name]["error"].addItem(error_info[error_type[i[0]]] % i)
            self.docwidget[dock_name]["sign"].addItem("Entry\tWord\tLength")
            for index, i in enumerate(sign):
                self.docwidget[dock_name]["sign"].addItem(str(index) + '\t' + i + '\t' + str(len(i)))
        except Exception as e:
            print(e)
        if flag:
            try:
                self.syner = Syner(token, sign)
                self.syner.SynerOut.connect(self.showSyner_info)
                self.syner.start()
            except Exception as e:
                print(e)

    def showSyner_info(self, log, error):
        dock_name = QFileInfo(self.filename).fileName()
        print('syner finished')
        for i in error:
            self.docwidget[dock_name]["error"].addItem(i)
        for i in log:
            self.docwidget[dock_name]["log"].addItem(i)

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
        self.docwidget[dock_name] = {"token": token, "error": error, "sign": sign, "log": log}
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

        self.tabifyDockWidget(dock_token, dock_error)
        self.tabifyDockWidget(dock_error, dock_sign)
        self.tabifyDockWidget(dock_sign, dock_log)

    def closeEvent(self, event):
        failures = []
        textEdit = self.tab.currentWidget().e_edit
        if textEdit.isModified():
            try:
                textEdit.save()
            except IOError as e:
                failures.append(str(e))
        if (failures and
            QMessageBox.warning(self, "Text Editor -- Save Error",
                    "Failed to save{0}\nQuit anyway?".format("\n\t".join(failures)),
                    QMessageBox.Yes|QMessageBox.No) ==
                    QMessageBox.No):
            event.ignore()
            return
        settings = QSettings()
        settings.setValue("MainWindow/Geometry",
                          self.saveGeometry())
        settings.setValue("MainWindow/State",
                          self.saveState())
        files = []
        for textEdit in self.mdi.subWindowList():
            textEdit=textEdit.widget()
            if not textEdit.filename.startswith("Unnamed"):
                files.append(textEdit.filename)
        settings.setValue("CurrentFiles", files)
        self.mdi.closeAllSubWindows()

    def loadFiles(self):
        if len(sys.argv) > 1:
            for filename in sys.argv[1:31]: # Load at most 30 files
                self.filename = filename
                if QFileInfo(filename).isFile():
                    self.loadFile(filename)
                    QApplication.processEvents()
        else:
            settings = QSettings()
            # files = settings.value("CurrentFiles").toStringList()
            if settings.value("CurrentFiles"):
                files=settings.value("CurrentFiles")
                for filename in files:
                    filename = filename
                    if QFile.exists(filename):
                        self.loadFile(filename)
                        QApplication.processEvents()

    def fileNew(self):
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

    def setCurrentFileName(self, fileName=''):
        # self.filename = fileName
        self.tab.currentWidget().e_edit.document().setModified(False)
        if not fileName:
            shownName = 'untitled.txt'
        else:
            shownName = QFileInfo(fileName).fileName()
        self.setWindowTitle(self.tr("%s[*] - %s" % (shownName, "Complier Editer")))
        self.setWindowModified(False)

    def fileOpen(self):
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
            return self.loadFile()
        return False

    def loadFile(self):
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

    def fileSave(self):
        print(self.filename)
        if not self.filename:
            return self.fileSaveAs()
        else:
            writer = QTextDocumentWriter(self.filename)
            success = writer.write(self.tab.currentWidget().e_edit.document())
            if success:
                self.tab.currentWidget().e_edit.document().setModified(False)
                print("save")
                return True
        return False

    def fileSaveAs(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save as...", None,
                                            "Txt files (*.txt);;"
                                            "Python files (*.py);;"
                                            "HTML-Files (*.htm *.html);;"
                                            "All Files (*)")
        if filename:
            self.filename = filename
            if self.fileSave():
                self.tab.setTabText(self.tab.currentIndex(),QFileInfo(filename).fileName())
        return False

    def editCopy(self):
        textEdit = self.tab.currentWidget().e_edit
        cursor = textEdit.textCursor()
        text = cursor.selectedText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def editCut(self):
        textEdit = self.tab.currentWidget().e_edit
        cursor = textEdit.textCursor()
        text = cursor.selectedText()
        if text:
            cursor.removeSelectedText()
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def editPaste(self):
        textEdit = self.tab.currentWidget().e_edit
        clipboard = QApplication.clipboard()
        textEdit.insertPlainText(clipboard.text())

    def editRedo(self):
        self.tab.currentWidget().e_edit.redo()

    def editUndo(self):
        self.tab.currentWidget().e_edit.undo()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("Zhangtian.")
    app.setOrganizationDomain("elezt.cn")
    app.setApplicationName("Complier Editer")
    form = MainWindow()
    form.show()
    app.exec_()

