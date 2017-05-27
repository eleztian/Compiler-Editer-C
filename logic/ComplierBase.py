from PyQt5.QtCore import QThread, pyqtSignal


class Token(list):
    """
    (LineNo, word, code)
    """
    def __init__(self, seq=()):
        super(Token, self).__init__(seq)
        pass


class SignTable(list):
    """
    (word, type_p, scope, type, others)
    """

    def __init__(self, seq=()):
        super(SignTable, self).__init__(seq)

    def append(self, object_p):
        item = list(object_p)

        t = 5-len(item)
        for i in range(0, t):
            item += ['']
        try:
            self.remove(item)
        except ValueError:
            pass
        super(SignTable, self).append(item)


class Error(list):
    def __init__(self, seq=()):
        super(Error, self).__init__(seq)


class ComplierBase(QThread):
    code = {
        'char': 1,
        'double': 2,
        'enum': 3,
        'float': 4,
        'int': 5,
        'long': 6,
        'short': 7,
        'signed': 8,
        'struct': 9,
        'union': 10,
        'unsigned': 11,
        'void': 12,
        'for': 13,
        'do': 14,
        'while': 15,
        'continue': 16,
        'if': 17,
        'else': 18,
        'goto': 19,
        'switch': 20,
        'case': 21,
        'default': 22,
        'return': 23,
        'auto': 24,
        'extern': 25,
        'register': 26,
        'static': 27,
        'const': 28,
        'sizeof': 29,
        'typdef': 30,
        'volatile': 31,
        'break': 32,  # 关键字
        '+': 33,
        '-': 34,
        '*': 35,
        '/': 36,
        '=': 37,
        '|': 38,
        '&': 39,
        '!': 40,
        '>': 41,
        '<': 42,
        '&&': 43,
        '++': 44,
        '--': 45,
        '+=': 46,
        '-=': 47,
        '*=': 48,
        '/=': 49,
        '==': 50,
        '|=': 51,
        '&=': 52,
        '!=': 53,
        '>=': 54,
        '<=': 55,
        '>>=': 56,
        '<<=': 57,
        '||': 58,
        '%': 59,  # 运算符
        '>>': 60,
        '<<': 61,
        ',': 62,
        '(': 63,
        ')': 64,
        '{': 65,
        '}': 66,
        '[': 67,
        ']': 68,
        ';': 69,
        '//': 70,
        '/*': 71,
        '*/': 72,
        ':': 73,
        '.': 74,
        '\\': 75,  # 界符
        'constNum': 76,
        'charRealNum': 77,
        'string': 78,
        'id': 79
    }  # 内码表
    basic_arithmetic_operator = {
        '+', '-', '*', '=', '|', '&', '>', '<', '!', '%'
    }  # 符号表
    delimiters = {
        ';', ',', ':', '(', ')', '{', '}', '[', ']', '<', '>', '.', '\\'
    }  # 界符表
    error_type = ['miss', 'more', 'no_code', 'no_type', 'no_keyWord']
    error_info = {
        error_type[0]: "错误 %d: 第 %d 行缺少  %s  ;",
        error_type[1]: "错误 %d: 第 %d 行多余  %s  ;",
        error_type[2]: "错误 %d: 第 %d 行不能识别的字符  %s  ;",
        error_type[3]: "错误 %d: 第 %d 行没有 %s 的类型",
        error_type[4]: ""
    }  # 错误信息格式列表
    modifier = ['const', 'static', 'register', 'auto', 'volatile', 'unsigned']
    s_type = ['char', 'int', 'double', 'float', 'short', 'long']
    logic_sign = ['>', '<', '==', '!=', '>=', '<=']
    last_keyword_code = 32
    sinOut = pyqtSignal(Token, Error, SignTable)

    def __init__(self, filename='', text=''):
        super(ComplierBase, self).__init__()
        if filename:
            self.file_name = filename
            self.__load_file()
        elif text:
            self.file_con = text.strip()
        else:
            raise Exception("No Anything to complier")
        self.file_con_len = len(self.file_con)  # 内存长度
        self.token = Token()  # Token表
        self.error = Error()  # 错误信息
        self.sign_table = SignTable()  # 符号表

    # 读取文件内容到 file_con
    def __load_file(self):
        with open(self.file_name, "r", encoding='utf8') as f:
            self.file_con = f.read()

    def run(self):
        pass

    def _exit_message(self):
        try:
            self.sinOut.emit(self.token, self.error, self.sign_table)
        except Exception as e:
            raise e


