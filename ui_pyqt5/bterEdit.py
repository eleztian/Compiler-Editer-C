from PyQt5.QtCore import (QTimer, Qt)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QLabel, QGridLayout,
                             QWidget)

from ui_pyqt5.edit.textedit import TextEdit

__version__ = "1.0.0"

class BterEdit(QWidget):
    NextId = 1
    filename = ""
    def __init__(self, parent=None):
        super(BterEdit, self).__init__(parent)
        self.filename = 'Unnamed-{0}.txt'.format(
                         BterEdit.NextId)
        BterEdit.NextId += 1
        self.setup_ui()

    def setup_ui(self):
        self.setup_edit(self)

    def setup_edit(self, widget):
        font = QFont()
        self.e_label = QLabel(widget)
        self.e_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.e_label.setWordWrap(True)
        self.e_label.setText("1\n")

        self.LineCount = 1
        self.LineNo = 1
        self.startLine = 1

        font.setPointSize(16)  # 24
        self.e_label.setFont(font)
        self.e_label.setMargin(5)
        self.e_edit = TextEdit(widget)
        self.e_edit.setFont(font)
        g_edit = QGridLayout()
        g_edit.setColumnStretch(0, 2)
        g_edit.setColumnStretch(1, 30)
        g_edit.addWidget(self.e_label, 0, 0)
        g_edit.addWidget(self.e_edit, 0, 1)
        widget.setLayout(g_edit)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateLineNum)
        self.timer.start(100)

    def updateLineNum(self):
        self.startLine = self.e_edit.scrollbar.value() // 24
        h_c = int(self.e_edit.height() / 24.5)
        str_l = ""
        count = self.e_edit.document().blockCount()
        if count < h_c:
            end = count
        else:
            end = h_c
        for i in range(1, end):
            str_l += "%3d\n"%(i + self.startLine)
        str_l += "%3d\n"%(end + self.startLine)
        self.e_label.setText(str_l)


