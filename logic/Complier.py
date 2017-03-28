from PyQt5.QtCore import QThread, pyqtSignal
from logic.Lexer import Lexer
from logic.Syner import Syner


class Complier(QThread):
    def __init__(self, filename):
        self.filename = filename
        self.lexer = Lexer(filename)
        self.syner = Syner()

    def run(self):
        pass
