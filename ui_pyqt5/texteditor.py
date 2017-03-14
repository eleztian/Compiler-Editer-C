import sys

from PyQt5.QtCore import (QFile, QFileInfo, QSettings, QTimer, Qt, QByteArray)
from PyQt5.QtGui import QIcon, QKeySequence, QTextDocumentWriter
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QGridLayout,
                             QMainWindow, QMessageBox, QTextEdit, QTabWidget,
                             QWidget, QDockWidget, QTabBar)

from ui_pyqt5.bterEdit import BterEdit
from ui_pyqt5 import textedit_rc

__version__ = "1.0.0"

if sys.platform.startswith('darwin'):
    rsrcfilename = ":/images/mac"
else:
    rsrcfilename = ":/images/win"

class MainWindow(QMainWindow):
    filename = ""
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

        e = QTextEdit()
        self.CreateDockWidget("test", e)

    def tab_changed(self):
        self.filename = self.tab.currentWidget().filename
        self.setCurrentFileName(self.filename)

    def tab_close(self):
        # 关闭标签
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("The file of {0} has been modified.".format(QFileInfo(self.filename).fileName()))
        msgBox.setInformativeText("Do you want to save your changes?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec()
        if ret ==  QMessageBox.Save:
            self.fileSave()
        elif ret == QMessageBox.Discard:
            i = self.tab.currentIndex()  # 获取当前处于激活状态的标签
            self.tab.removeTab(i)
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

        fileMenu = self.menuBar().addMenu("&File")
        self.addActions(fileMenu, (fileNewAction, fileOpenAction,
                                   fileSaveAction, fileSaveAsAction,
                                   None, fileQuitAction))
        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (editCopyAction, editCutAction,
                                   editPasteAction, editUndoAction, editRedoAction))
        lexicalAnalysisMenu = self.menuBar().addMenu("&LexicalAnalysis")
        syntaxAnalysisMenu = self.menuBar().addMenu("&SyntaxAnalysis")
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

    def CreateDockWidget(self, name, widget):  # 定义一个createDock方法创建一个dockwidget
        dock = QDockWidget(name)  # 实例化dockwidget类
        dock.setWidget(widget)  # 带入的参数为一个QWidget窗体实例，将该窗体放入dock中
        dock.setObjectName(name)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)  # 设置dockwidget的各类属性
        self.addDockWidget(Qt.RightDockWidgetArea,
                           dock)  # 设置dockwidget放置在QMainWindow中的位置，并且将dockwidget添加至QMainWindow中

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
                                                       "C++ Files (*.cpp *.h *.py);;"
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
            except Exception as e:
                QMessageBox.warning(self, "Text Editor -- Save Error",
                                    "Failed to save {0}: {1}".format(self.filename, e))
                return False
            return True

    def fileSave(self):
        if not self.filename:
            return self.fileSaveAs()
        else:
            writer = QTextDocumentWriter(self.filename)
            success = writer.write(self.tab.currentWidget().e_edit.document())
            if success:
                self.tab.currentWidget().e_edit.document().setModified(False)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("Zhangtian.")
    app.setOrganizationDomain("elezt.cn")
    app.setApplicationName("Complier Editer")
    form = MainWindow()
    form.show()
    app.exec_()