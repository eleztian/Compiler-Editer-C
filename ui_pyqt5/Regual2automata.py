import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QGridLayout, QWidget, QFrame, QPushButton, QLineEdit, QLabel

from logic.RegularExp import RegularExp


class Regual2autoUI(QFrame):
    def __init__(self, parent=None):
        super(Regual2autoUI, self).__init__(parent=parent)
        self.input_widget = QWidget(self)
        self.image_widget = QWidget(self)
        self.frame_gird = QGridLayout()

        self.nfa_label = QLabel(self.image_widget, text="NFA")
        self.dfa_label = QLabel(self.image_widget, text="DFA")
        self.mfa_label = QLabel(self.image_widget, text="MFA")
        self.image_gird = QGridLayout()

        self.text_input_lineedit = QLineEdit(self.input_widget)
        self.start_btn = QPushButton(self.input_widget, text="Start")
        self.input_gird = QGridLayout()

        self.layout_s()
        self.set_action()

        self.regual_exp = None

    def layout_s(self):
        self.frame_gird.addWidget(self.image_widget, 0, 0)
        self.frame_gird.addWidget(self.input_widget, 1, 0)
        self.frame_gird.setRowStretch(0, 4)
        self.frame_gird.setRowStretch(1, 1)
        self.setLayout(self.frame_gird)

        self.image_gird.addWidget(self.nfa_label, 0, 0)
        self.image_gird.addWidget(self.dfa_label, 1, 0)
        self.image_gird.addWidget(self.mfa_label, 2, 0)
        self.image_gird.setRowStretch(0, 1)
        self.image_gird.setRowStretch(1, 1)
        self.image_gird.setRowStretch(2, 1)
        self.image_widget.setLayout(self.image_gird)

        self.input_gird.addWidget(self.text_input_lineedit, 0, 0)
        self.input_gird.addWidget(self.start_btn, 0, 1)
        self.input_widget.setLayout(self.input_gird)

    def set_action(self):
        self.start_btn.clicked.connect(self.trans_start)

    def trans_start(self):
        try:
            self.regual_exp = RegularExp(self.text_input_lineedit.text())
            self.regual_exp.trans2mfa()
            image = QImage("img/nfa.png").scaled(800, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.nfa_label.setPixmap(QPixmap.fromImage(image))
            image = QImage("img/dfa.png").scaled(800, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.dfa_label.setPixmap(QPixmap.fromImage(image))
            image = QImage("img/mfa.png").scaled(800, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.mfa_label.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            print("exp error：", e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("Zhangtian.")
    app.setOrganizationDomain("elezt.cn")
    app.setApplicationName("Complier Editer")
    form = Regual2autoUI()
    form.show()
    app.exec_()
