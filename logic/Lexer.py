'''
关键字：
    char double enum float int long short signed struct union unsigned void
    for do while continue break
    if else goto
    switch case default
    return
    auto extern register static
    const sizeof typdef volatile

标识符：
    由字母或下划线开头 后面有若干字母、数字或下划线组成

常数：
    整数
    实数
运算符：
    算数运算符：
        + - * / % = & | ! && || >> <<
        组合：
    关系运算符：
        > < == != >= <=

界符：
    { } 空格 （）[] , . : " ' // /* */


'''

from PyQt5.QtCore import QThread, pyqtSignal
from logic import complier_s

class Lexer(QThread):

    sinOut = pyqtSignal(list, list, set)

    def __init__(self, filename):
        super(Lexer, self).__init__()
        self.file_name = filename
        self.file_con = ""
        self.file_con_len = 0
        self.current_line = 1
        self.current_row = 0
        self.token = []
        self.error = []
        self.sign_table = set()
        self.read_file()

    def read_file(self):
        with open(self.file_name, "r", encoding='utf8') as f:
            self.file_con = f.read()
        self.file_con_len = len(self.file_con)

    def start_with_alpha(self):
        index = self.current_row
        word = ''
        t = 0
        while self.current_row < self.file_con_len:
            ch = self.file_con[self.current_row]
            if not (ch.isalpha() or ch.isdigit() or ch == '_'):  # 其他字符
                break
            self.current_row += 1
        word = self.file_con[index: self.current_row]
        try:
            t = complier_s.code[word]   # 关键字
        except:
            t = complier_s.code['id']
            self.sign_table.add(word)
        self.token.append((self.current_line, word, t))

        self.current_row -= 1

    def start_with_number(self):
        index = self.current_row
        state = 0
        word = ''

        def get_next_char():
            if (self.current_row+1) < self.file_con_len:
                self.current_row += 1
                return self.file_con[self.current_row]
            return None

        def isnum(_state):
            if _state == 1:
                while _state == 1:
                    c = get_next_char()
                    if c:
                        if c.isdigit():
                            pass
                        elif c == '.':
                            _state = 2
                        elif c == 'e' or c == 'E':
                            _state = 4
                        else:
                            _state = 7
                    else:
                        self.current_row += 1
                        _state = 7
            if _state == 2:
                while _state == 2:
                    c = get_next_char()
                    if c.isdigit():
                        _state = 3
                    else:
                        _state = 11  # . 多余
            if _state == 3:
                while _state == 3:
                    c = get_next_char()
                    if c.isdigit():
                        pass
                    elif (c == 'e') or (c == 'E'):
                        _state = 4
                    else:
                        _state = 7
            if _state == 4:
                while _state == 4:
                    c = get_next_char()
                    if c.isdigit():
                        _state = 6
                    elif (c == '+') or (c == '-'):
                        _state = 5
                    else:
                        _state = 12
            if _state == 5:
                while _state == 5:
                    c = get_next_char()
                    if c.isdigit():
                        _state = 6
                    else:
                        _state = 13
            if _state == 6:
                while _state == 6:
                    c = get_next_char()
                    if not c.isdigit():
                        _state = 7
            if _state == 9:
                while _state == 9:
                    c = get_next_char()
                    if c.isdigit() or ('A' <= c <= 'F') or ('a' <= c <= 'f'):
                        _state = 10
                    else:
                        _state = 14
            if _state == 10:
                while _state == 10:
                    c = get_next_char()
                    if not (c.isdigit() or ('A' <= c <= 'F') or ('a' <= c <= 'f')):
                        _state = 7
            # 错误判断
            if _state == 7:
                return True  # 没有错误
            elif _state == 11:    # TODO: error . 多余
                self.error.append((1, self.current_line, '.'))
                self.current_row -= 1
                pass
            elif _state == 12:    # TODO: error E/e 多余
                self.error.append((1, self.current_line, 'E/e'))
                self.current_row -= 1
                pass
            elif _state == 13:    # TODO: error +/- 多余
                self.error.append((1, self.current_line, '+/-'))
                self.current_row -= 1
                pass
            elif _state == 14:      # TODO: error x/X 多余
                self.error.append((1, self.current_line, 'x/X'))
                self.current_row -= 1
            return False

        if self.file_con[self.current_row] == '0':
            ch = get_next_char()
            if (ch == 'x') or (ch == 'X'):  # 0x 0X
                state = 9
            elif ch.isdigit():
                state = 1
            else:
                state = 7  # 结束
        else:
            state = 1
        isnum(state)
        word = self.file_con[index:self.current_row]
        self.token.append((self.current_line, word, complier_s.code['constNum']))
        self.sign_table.add(word)
        self.current_row -= 1

    def start_with_sign_char(self):
        if (self.current_row+1) < self.file_con_len:
            word = self.file_con[self.current_row+1]  # 超前检测
            if word is not '\n' and self.current_row < self.file_con_len - 2:
                if self.file_con[self.current_row+2] == '\'':  # 超前 2位 检测
                    self.token.append((self.current_line, word, complier_s.code['charRealNum']))
                    self.sign_table.add(word)
                    self.current_row += 2
                else:
                    self.error.append((0, self.current_line, '\''))
                    # TODO : 错误 缺少 ’

            else:
                pass
                self.error.append((1, self.current_line, '\''))
                # TODO: 错误 多余 ‘
        else:
            pass

    def start_with_sign_string(self):
        self.current_row += 1
        index = self.current_row
        flag = 0
        while self.current_row < self.file_con_len:
            if self.file_con[self.current_row] is '\"':
                word = self.file_con[index:self.current_row]
                self.token.append((self.current_line, word, complier_s.code['string']))
                self.sign_table.add(word)
                break
            elif self.file_con[self.current_row] is '\n':
                flag = 1
                break
            else:
                self.current_row += 1
        if flag == 1:
            # TODO: 错误 多余"
            self.error.append((1, self.current_line, '\"'))
            self.current_row = index  # 回到原来位置

    def start_with_sign_multi(self):
        self.current_row += 1
        ch = self.file_con[self.current_row]
        if ch == '*':  # /*
            while self.current_row < self.file_con_len - 1:
                if self.file_con[self.current_row] == '\n':
                    self.current_line += 1
                # 超前检测
                if not (self.file_con[self.current_row] == '*' and self.file_con[self.current_row+1] == '/'):
                    self.current_row += 1
                else:
                    self.current_row += 1
                    break
        elif ch == '/':  # //
            while self.current_row < self.file_con_len - 1:
                if self.file_con[self.current_row + 1] is not '\n':  # 超前检测
                    self.current_row += 1
                else:
                    break
        elif ch == '=':  # /=
            word = self.file_con[self.current_row-1:self.current_row+1]
            self.token.append((self.current_line, word, complier_s.code['/=']))
        else:  # / 除法
            self.current_row -= 1
            word = self.file_con[self.current_row]
            self.token.append((self.current_line, word, complier_s.code['/']))

    def start_with_basic_arithmetic_operator(self):
        ch = self.file_con[self.current_row]
        index = self.current_row

        def next_is_sign(c):
            if self.current_row + 1 < self.file_con_len:
                if self.file_con[self.current_row + 1] == c:
                    self.current_row += 1
                    return True
            return False
        if ch == '%':
            next_is_sign('=')
        elif ch == '!':
            next_is_sign('=')
        elif ch == '=':
            next_is_sign(ch)
        elif (ch == '+') or (ch == '-'):
            if next_is_sign('=') or next_is_sign(ch):
                pass
        elif ch == '*':
            next_is_sign('=')
        elif ch == '|':
            if next_is_sign('=') or next_is_sign("|"):
                pass
        elif ch == '&':
            if next_is_sign('=') or next_is_sign("&"):
                pass
        elif ch == '>':
            if next_is_sign('=') or (next_is_sign(">") and next_is_sign("=")):
                pass
        elif ch == '<':
            if next_is_sign('=') or (next_is_sign('<') and next_is_sign('=')):
                pass
        else:
            return
        word = self.file_con[index:self.current_row + 1]
        self.token.append((self.current_line, word, complier_s.code[word]))

    def start_with_pre(self):
        # TODO: 预编译 替换字符串
        index = self.current_row
        while self.file_con[self.current_row] is not ' ':
            self.current_row += 1
        word = self.file_con[index:self.current_row]
        self.token.append((self.current_line, word, self.ISCHAR))
        self.sign_table.add(word)

    def start_with_delimiter(self):
        word = self.file_con[self.current_row]
        self.token.append((self.current_line, word, complier_s.code[word]))

    def scanner(self):
        self.current_row = 0
        while self.current_row < len(self.file_con):
            ch = self.file_con[self.current_row]
            if not (ch == ' ' or ch == '\t'):
                if ch == '\n' or ch == '\r\n':
                    self.current_line += 1
                elif ch.isalpha() or ch == '_':  # 关键字 标识符
                    self.start_with_alpha()
                elif ch.isdigit():  # 数字
                    self.start_with_number()
                elif ch == '/':  # 注释 或 除法
                    self.start_with_sign_multi()
                elif ch == '#':  # #
                    pass
                elif ch == '\'':  # 字符
                    self.start_with_sign_char()
                elif ch == '\"':  # 字符串
                    self.start_with_sign_string()
                elif ch in complier_s.basic_arithmetic_operator:  # 算数运算符
                    self.start_with_basic_arithmetic_operator()
                elif ch in complier_s.delimiters:
                    self.start_with_delimiter()
                else:
                    self.error.append((2, self.current_line, ch))
                    # TODO: 错误 无法识别的符号
            self.current_row += 1

    def run(self):
        self.scanner()
        try:
         self.sinOut.emit(self.token, self.error, self.sign_table)
        except Exception as e:
            print(e)
        self.quit()

if __name__ == '__main__':
    lexer = Lexer("testfile.c")
    lexer.scanner()
    print(lexer.sign_table)
    print(lexer.token)
    for i in lexer.error:
        print(lexer._error_info[i[0]] % i)
