'''
关键字：
    char double enum float int long short signed struct union unsigned void
    for do while continue
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

import re

# 关键字表



class Lexer( object ):
    _key = {
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
        'volatile': 31
    }
    # 符号表
    other_sign = {
        '+', '-', '*', '=', '|', '&', '>', '<'
    }
    token = []
    sign_table = set()

    file_name = ""
    file_con = ""

    ISCHAR = 101
    ISSTRING = 102

    current_line = 0
    current_row = 0

    def __init__(self, filename):
        self.file_name = filename
        self.read_file()

    def read_file(self):
        f = open(self.file_name, "r")
        self.file_con = f.read()
        # # print( f.readline() )
        # print(self.file_con)
        f.close()

    def pre_not_notes(self):
        # ((?<=\n)|^)[ \t]*\/\*.*?\*\/\n?|\/\*.*?\*\/|((?<=\n)|^)[ \t]*\/\/[^\n]*\n|\/\/[^\n]*
        #/\*(.*?)\*/|//(.*?)\n
        p = re.compile(r"((?<=\n)|^)[ \t]*\/\*.*?\*\/\n?|\/\*.*?\*\/|((?<=\n)|^)[ \t]*\/\/[^\n]*\n|\/\/[^\n]*", re.S)
        s = p.sub('', self.file_con)
        print(s)

    def start_with_alpha(self):
        index = self.current_row
        word = ''
        while self.current_row < len(self.file_con):
            self.current_row += 1
            ch = self.file_con[self.current_row]
            if not (ch.isalpha() or ch.isnumeric() or ch == '_'):
                word = self.file_con[index: self.current_row]
                t = 0
                try:
                    t = self._key[word]  # 关键字
                except:
                    t = 100  # 标识符
                self.token.append((word, t))
                self.sign_table.add(word)
                break

    def start_with_multi(self):
        # print(self.current_row, "//  : " + self.file_con[self.current_row])
        self.current_row += 1
        ch = self.file_con[self.current_row]
        if ch == '*':  # /*
            while not (self.file_con[self.current_row] == '*' and self.file_con[self.current_row+1] == '/'):
                self.current_row += 1
        elif ch == '/':  # //
            while self.file_con[self.current_row + 1] is not '\n':
                self.current_row += 1
        else:  # /
            # print("aaa" +self.file_con[self.current_row] )
            word = self.file_con[self.current_row - 1]
            self.token.append((word, 100))
            self.sign_table.add(word)
        self.current_row += 1

    def start_with_number(self):
        index = self.current_row
        while True:
            break

    def start_with_sign_char(self):
        word = self.file_con[self.current_row+1]
        if word is not '\n':
            if self.file_con[self.current_row+2] == '\'':
                self.token.append((self.file_con[self.current_row+1], self.ISCHAR))
                self.sign_table.add(word)
            else:
                pass
                # TODO : 错误 缺少 ’
        else:
            pass
            # TODO: 错误 多余 ‘

    def start_with_sign_string(self):
        pass

    def start_with_sign_other(self):
        pass

    def start_with_sign_pre(self):
        # TODO: 预编译 替换字符串
        index = self.current_row
        while self.file_con[self.current_row] is not ' ':
            self.current_row += 1
        word = self.file_con[index:self.current_row]
        self.token.append((word, self.ISCHAR))
        self.sign_table.add(word)

    def scanner(self):
        self.current_row = 0
        while self.current_row < len(self.file_con):
            ch = self.file_con[self.current_row]
            if ch == ' ':
                self.current_row += 1
            else:
                if ch.isalpha() or ch == '_':  # 关键字 标识符
                    self.start_with_alpha()
                elif ch.isalnum():  # 数字
                    pass
                elif ch == '/':  # 注释 或 除法
                    self.start_with_multi()
                elif ch == '#':  # #
                    pass
                elif ch == '\'':  # 字符
                    self.start_with_sign_char()
                elif ch == '\"':  # 字符串
                    pass
                elif ch in self.other_sign:
                    pass
                else:
                    pass
            self.current_row += 1

    def get_token(self):
        pass


if __name__ == '__main__':
    lexer = Lexer("testfile.c")
    # lexer.pre_not_notes()
    lexer.scanner()
    print(lexer.sign_table)
    print(lexer.token)



