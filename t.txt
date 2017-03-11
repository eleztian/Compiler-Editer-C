from PyQt5.QtCore import (QFile, QFileInfo, QIODevice,
QTextStream, Qt)
from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QTextEdit)
class TextEdit(QTextEdit):
    NextId = 1
    def __init__(self, filename='', parent=None):
    super(TextEdit, self).__init__(parent)
    self.setAttribute(Qt.WA_DeleteOnClose)
    self.filename = filename
    if not self.filename:
    self.filename = 'Unnamed-{0}.txt'.format(
    TextEdit.NextId)
    TextEdit.NextId += 1
    self.document().setModified(False)
    self.setWindowTitle(QFileInfo(self.filename).fileName())
    def closeEvent(self, event):
    if (self.document().isModified() and
    QMessageBox.question(self,
    'Text Editor - Unsaved Changes',
    'Save unsaved changes in {0}?'.format(self.filename),
    QMessageBox.Yes|QMessageBox.No) ==
    QMessageBox.Yes):
    try:
    self.save()
    except EnvironmentError as e:
    QMessageBox.warning(self,
    'Text Editor -- Save Error',
    'Failed to save {0}: {1}'.format(self.filename, e))
    def isModified(self):
    return self.document().isModified()
    def save(self):
    if self.filename.startswith('Unnamed'):
    filename,filetype = QFileDialog.getSaveFileName(self,
    'Text Editor-- Save File As', self.filename,
    'Text files (*.txt *.*)')
    if not filename:
    return
    self.filename = filename
    self.setWindowTitle(QFileInfo(self.filename).fileName())
    exception = None
    fh = None
    try:
    fh = QFile(self.filename)
    if not fh.open(QIODevice.WriteOnly):
    raise IOError(str(fh.errorString()))
    stream = QTextStream(fh)
    stream.setCodec('UTF-8')
    stream << self.toPlainText()
    self.document().setModified(False)
    except EnvironmentError as e:
    exception = e
    finally:
    if fh is not None:
    fh.close()
    if exception is not None:
    raise exception
    def load(self):
    exception = None
    fh = None
    try:
    fh = QFile(self.filename)
    if not fh.open(QIODevice.ReadOnly):
    raise IOError(str(fh.errorString()))
    stream = QTextStream(fh)
    stream.setCodec('UTF-8')
    self.setPlainText(stream.readAll())
    self.document().setModified(False)
    except EnvironmentError as e:
    exception = e
    finally:
    if fh is not None:
    fh.close()
    if exception is not None:
    raise exception
/home/yrd/eric_workspace/chap09/tabbededitor.pyw
import sys
from PyQt5.QtCore import (QFile, QFileInfo, QSettings,QTimer, Qt, QByteArray)
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,
QMainWindow, QMessageBox, QShortcut, QTabWidget,
QTextEdit)
from PyQt5.QtGui import QIcon,QKeySequence
import textedit
import qrc_resources
__version__ = '1.0.0'
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        fileNewAction = self.createAction('&New', self.fileNew,
        QKeySequence.New, 'filenew', 'Create a text file')
        fileOpenAction = self.createAction('&Open...', self.fileOpen,
        QKeySequence.Open, 'fileopen',
        'Open an existing text file')
        fileSaveAction = self.createAction('&Save', self.fileSave,
        QKeySequence.Save, 'filesave', 'Save the text')
        fileSaveAsAction = self.createAction('Save &As...',
        self.fileSaveAs, icon='filesaveas',
        tip='Save the text using a new filename')
        fileSaveAllAction = self.createAction('Save A&amp;ll',
        self.fileSaveAll, icon='filesave',
        tip='Save all the files')
        fileCloseTabAction = self.createAction('Close &Tab',
        self.fileCloseTab, QKeySequence.Close, 'filequit',
        'Close the active tab')
        fileQuitAction = self.createAction('&Quit', self.close,
        'Ctrl+Q', 'filequit', 'Close the application')
        editCopyAction = self.createAction('&Copy', self.editCopy,
        QKeySequence.Copy, 'editcopy',
        'Copy text to the clipboard')
        editCutAction = self.createAction('Cu&t', self.editCut,
        QKeySequence.Cut, 'editcut',
        'Cut text to the clipboard')
        editPasteAction = self.createAction('&Paste', self.editPaste,
        QKeySequence.Paste, 'editpaste',
        'Paste in the clipboard's text')