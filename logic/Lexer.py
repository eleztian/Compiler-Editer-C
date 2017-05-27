"""
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
"""
from logic.ComplierBase import ComplierBase


class Lexer(ComplierBase):
    def __init__(self, filename='', text=''):
        super(Lexer, self).__init__(filename, text)
        self.__current_line = 1
        self.__current_row = 0

    def __start_with_alpha(self):
        index = self.__current_row
        while self.__current_row < self.file_con_len:
            ch = self.file_con[self.__current_row]
            if not (ch.isalpha() or ch.isdigit() or ch == '_'):  # 其他字符
                break
            self.__current_row += 1
        word = self.file_con[index: self.__current_row]
        try:
            t = self.code[word]   # 关键字
        except KeyError:
            t = self.code['id']
            self.sign_table.append((word, 'id'))
        self.token.append((self.__current_line, word, t))

        self.__current_row -= 1

    def __start_with_number(self):
        index = self.__current_row

        def get_next_char():
            if (self.__current_row+1) < self.file_con_len:
                self.__current_row += 1
                return self.file_con[self.__current_row]
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
                        self.__current_row += 1
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
                self.error.append((1, self.__current_line, '.'))
                self.__current_row -= 1
                pass
            elif _state == 12:    # TODO: error E/e 多余
                self.error.append((1, self.__current_line, 'E/e'))
                self.__current_row -= 1
                pass
            elif _state == 13:    # TODO: error +/- 多余
                self.error.append((1, self.__current_line, '+/-'))
                self.__current_row -= 1
                pass
            elif _state == 14:      # TODO: error x/X 多余
                self.error.append((1, self.__current_line, 'x/X'))
                self.__current_row -= 1
            return False

        if self.file_con[self.__current_row] == '0':
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
        word = self.file_con[index:self.__current_row]
        self.token.append((self.__current_line, word, self.code['constNum']))
        self.sign_table.append((word, 'constNum'))
        self.__current_row -= 1

    def __start_with_sign_char(self):
        if (self.__current_row+1) < self.file_con_len:
            word = self.file_con[self.__current_row+1]  # 超前检测
            if word is not '\n' and self.__current_row < self.file_con_len - 2:
                if self.file_con[self.__current_row+2] == '\'':  # 超前 2位 检测
                    self.token.append((self.__current_line, word, self.code['charRealNum']))
                    word = word
                    self.sign_table.append((word, 'char'))
                    self.__current_row += 2
                else:
                    self.error.append((0, self.__current_line, '\''))
                    # TODO : 错误 缺少 ’

            else:
                pass
                self.error.append((1, self.__current_line, '\''))
                # TODO: 错误 多余 ‘
        else:
            pass

    def __start_with_sign_string(self):
        self.__current_row += 1
        index = self.__current_row
        flag = 0
        while self.__current_row < self.file_con_len:
            if self.file_con[self.__current_row] is '\"':
                word = self.file_con[index:self.__current_row]
                self.token.append((self.__current_line, word, self.code['string']))
                word = word
                self.sign_table.append((word, 'string'))
                break
            elif self.file_con[self.__current_row] is '\n':
                flag = 1
                break
            else:
                self.__current_row += 1
        if flag == 1:
            # TODO: 错误 多余"
            self.error.append((1, self.__current_line, '\"'))
            self.__current_row = index  # 回到原来位置

    def __start_with_sign_multi(self):
        self.__current_row += 1
        ch = self.file_con[self.__current_row]
        if ch == '*':  # /*
            while self.__current_row < self.file_con_len - 1:
                if self.file_con[self.__current_row] == '\n':
                    self.__current_line += 1
                # 超前检测
                if not (self.file_con[self.__current_row] == '*' and self.file_con[self.__current_row+1] == '/'):
                    self.__current_row += 1
                else:
                    self.__current_row += 1
                    break
        elif ch == '/':  # //
            while self.__current_row < self.file_con_len - 1:
                if self.file_con[self.__current_row + 1] is not '\n':  # 超前检测
                    self.__current_row += 1
                else:
                    break
        elif ch == '=':  # /=
            word = self.file_con[self.__current_row-1:self.__current_row+1]
            self.token.append((self.__current_line, word, self.code['/=']))
        else:  # / 除法
            self.__current_row -= 1
            word = self.file_con[self.__current_row]
            self.token.append((self.__current_line, word, self.code['/']))

    def __start_with_basic_arithmetic_operator(self):
        ch = self.file_con[self.__current_row]
        index = self.__current_row

        def next_is_sign(c):
            if self.__current_row + 1 < self.file_con_len:
                if self.file_con[self.__current_row + 1] == c:
                    self.__current_row += 1
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
        word = self.file_con[index:self.__current_row + 1]
        self.token.append((self.__current_line, word, self.code[word]))

    def __start_with_pre(self):
        # TODO: 预编译 替换字符串
        index = self.__current_row
        while self.file_con[self.__current_row] is not ' ':
            self.__current_row += 1
        word = self.file_con[index:self.__current_row]
        self.token.append((self.__current_line, word, self.ISCHAR))
        self.sign_table.append((word, 'pre'))

    def __start_with_delimiter(self):
        word = self.file_con[self.__current_row]
        self.token.append((self.__current_line, word, self.code[word]))

    def __scanner(self):
        self.__current_row = 0
        while self.__current_row < len(self.file_con):
            ch = self.file_con[self.__current_row]
            if not (ch == ' ' or ch == '\t'):
                if ch == '\n' or ch == '\r\n':
                    self.__current_line += 1
                elif ch.isalpha() or ch == '_':  # 关键字 标识符
                    self.__start_with_alpha()
                elif ch.isdigit():  # 数字
                    self.__start_with_number()
                elif ch == '/':  # 注释 或 除法
                    self.__start_with_sign_multi()
                elif ch == '#':  # #
                    pass
                elif ch == '\'':  # 字符
                    self.__start_with_sign_char()
                elif ch == '\"':  # 字符串
                    self.__start_with_sign_string()
                elif ch in self.basic_arithmetic_operator:  # 算数运算符
                    self.__start_with_basic_arithmetic_operator()
                elif ch in self.delimiters:
                    self.__start_with_delimiter()
                else:
                    self.error.append((2, self.__current_line, ch))
                    # TODO: 错误 无法识别的符号
            self.__current_row += 1

    def run(self):
        self.__scanner()
        self._exit_message()
        self.quit()

if __name__ == '__main__':
    lexer = Lexer(filename="TestFile/testfile.txt")
    lexer.run()
    print(lexer.sign_table)
    print(lexer.token)
    for i in lexer.error:
        print(lexer.error[i[0]] % i)