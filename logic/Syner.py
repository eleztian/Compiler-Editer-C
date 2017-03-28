"""
    语法分析(递归下降) LL(1)
"""
from logic.Lexer import Lexer
from logic.complier_s import code, delimiters, s_type, last_keyword_code, error_type, modifier, logic_sign


class Syner(object):
    now_token = None

    def __init__(self, t, sign):
        self.token = t
        self.index = 0
        self.sign_table = sign

    # 获取下一个token值
    def _token_next(self, chooseback=1):
        line, word, co = None, None, None
        if self.index < self.token.__len__():
            line, word, co = self.token[self.index]
            self.index += 1
        else:
            word = None
        if chooseback == 1:
            return word
        else:
            return line, word, co

    def _token_redo(self):
        if self.index > 0:
            self.index -= 1

    def _match(self, c):
        t = self._token_next()
        if t:
            if t == c:
                return True
            else:
                self._token_redo()
                return False
        return False

    # 出错处理
    def _error(self, error_type = ""):
        print("error in ", self.token[self.index - 1], error_type)

    # 定义数据
    def define_id_s(self):
        if self.modifier_s():
            if self.type_s():
                if self.id_s():
                    self.define_id_right_value_or_not()
                    self.define_id_closure()
                else:
                    self._error("no id")
            else:
                self._error('no type')
        else:
            if self.type_s():
                if self.id_s():
                    self.define_id_right_value_or_not()
                    self.define_id_closure()
                else:
                    self._error("no id")
            else:
                return False
        return True

    # 一行里面的多个定义
    def define_id_closure(self):
        if self._match(','):
            if self.id_s():
                self.define_id_right_value_or_not()
                self.define_id_closure()
            else:
                self._error("more ,")
        else:
            if not self._match(';'):
                self._error("no ;")

                # id

    # 验证标识符
    def id_s(self):
        if self.index < self.token.__len__():
            _, _, t = self.token[self.index]
            self.index += 1
            if t == code['id']:
                return True
            else:
                self._token_redo()
        return False

        # 常数

    # 数据定义初始化
    def define_id_right_value_or_not(self):
        if self._match('='):
            if not self.right_value():
                self._error('no value')
                return False
        return True

    # 数据值
    def right_value(self):
        if self.index < self.token.__len__():
            _, _, t = self.token[self.index]
            self.index += 1
            if t == code['id'] or t == code['charRealNum'] or t == code['constNum'] or t == code['string']:
                return True
            else:
                self.index -= 1
        return False

        # 初始化右赋值语句

    # 修饰词
    def modifier_s(self):
        c = self._token_next()
        if c not in modifier:
            self._token_redo()
            return False
        return True

    # 数据类型
    def type_s(self):
        c = self._token_next()
        if c not in s_type:
            self._token_redo()
            return False
        return True

    # 函数声明 <修饰词><类型><函数名>（<函数参数列表>）;
    def fun_declaration_s(self):
        if self.modifier_s():
            flag = 1
        else:
            flag = 0
            if not self.type_s():
                if flag:
                    self._error("no type")
                else:
                    return False  # 没有这个语句
            if not self.id_s():
                self._error("no id")
            if not self._match('('):
                self._error('no (')
            self.fun_declaration_par_s()
            if not self._match(')'):
                self._error('no )')
            if not self._match(';'):
                self._error('no ;')
        return True  # 有这个语句

    # 函数参数列表
    def fun_declaration_par_s(self):
        if self.modifier_s():
            flag = 1
        else:
            flag = 0
        if not self.type_s():
            if flag:
                self._error("no type")
            else:
                return False  # 空
        if not self.id_s():
            self._error("no id")
        self.define_id_right_value_or_not()
        self.fun_declaration_par_closure()
        return True

    # 函数参数 (,<定义>)*
    def fun_declaration_par_closure(self):
        if self._match(','):
            if not self.fun_declaration_par_s():
                self._error("more ,")
                return False
            self.fun_declaration_par_closure()
        return True

    # 函数定义
    def fun_define_s(self):
        if self.modifier_s():
            flag = 1
        else:
            flag = 0
            if not self.type_s():
                if flag:
                    self._error("no type")
                else:
                    return False  # 没有这个语句
            if not self.id_s():
                self._error("no id")
            if not self._match('('):
                self._error('no (')
            self.fun_declaration_par_s()
            if not self._match(')'):
                self._error('no )')
            if not self._match('{'):
                self._error('no {')
            self.fun_block_s()
            if not self._match('}'):
                self._error('no }')
        return True  # 有这个语句

    # 表达式  <表达式> -> <因子> <项>
    def exp_s(self):
        self.yinzi_s()
        self.xiang_s()

    # <因子> -> <因式> <因式递归>
    def yinzi_s(self):
        self.yinshi_s()
        self.yinshi_closure()

    # < 项 > -> + < 因子 > < 项 > | - < 因子 > < 项 > | $
    def xiang_s(self):
        if self._match('+') or self._match('-'):
            self.yinzi_s()
        else:
            pass  # $

    # < 因式 > -> ( < 表达式 > ) | < id > | < 数字 >
    def yinshi_s(self):
        _, w, c = self._token_next(3)
        if c == code['id'] or w.isdigit():
            pass
        else:
            if w == '(':
                self.exp_s()
            else:
                self._error("no (")
            if not self._match(')'):
                self._error('no )')

    # <因式递归> -> * <因式> <因式递归> | / <因式> <因式递归> | $
    def yinshi_closure(self):
        if self._match('*') or self._match('/'):
            self.yinshi_s()
            self.yinshi_closure()

    # < 右值 > -> < 表达式 > | { < 多个数据 >}
    def right_value_s(self):
        if self._match('{'):
            self.many_value_s()
            self._match('}')
        else:
            self.exp_s()

    # <多个数据> -> <数字> <数字闭包>
    def many_value_s(self):
        w = self._token_next()
        if w.isdigit():
            self.many_value_closure()

    # < 数字闭包 > ->, < 数字 > < 数字闭包 > | $
    def many_value_closure(self):
        if self._match(','):
            w = self._token_next()
            if w.isdigit():
                self.many_value_closure()
            else:
                self._error('no number')

    # <赋初值> -> = <右值> | $
    def init_value_s(self):
        if self._match('='):
            self.right_value_s()
        else:
            pass

    # < 声明 > -> < 修饰词 > < 类型 > < id > < 赋初值 >
    def declare_s(self):
        flag = 0
        if self.modifier_s():
            flag = 1
        if self.type_s():
            if flag:
                self._error('no type')
            if self.id_s():
                self.init_value_s()
                self.declare_closure()
            else:
                self._error('no id')
            return True
        return False

    #  <声明闭包> -> , <id>  < 赋初值 > <声明闭包> | $
    def declare_closure(self):
        if self._match(','):
            if self.id_s():
                self.init_value_s()
                self.declare_closure()
            else:
                self._error('more ,')
            return True
        else:
            pass
        return False

    # < 声明语句 > -> < 声明 >;
    def declare_2_s(self):
        if self.declare_s():
            if not self._match(';'):
                self._error(' no ;')
            else:
                return True
        return False

    # < 声明语句闭包 > -> < 声明语句 > < 声明语句闭包 > | $
    def declare_2_closure(self):
        if self.declare_2_s():
            self.declare_2_closure()
        else:
            pass

    # TODO: 函数声明，函数声明闭包，函数定义， 出错处理（直接结束）

    def start(self):
        self.declare_2_closure()
        print("a")

    def scanner(self):
        self.token_len = self.token.__len__()
        state = 1
        while self.index < self.token_len:
            _, word, co = self.token[self.index]
            if word in modifier:
                flag = 0
            else:
                flag = 1
            if word in s_type:
                _, word, co = self.token[self.index]
                while word == '*':
                    state = 3
                if co != code['id']:
                    self._error('no id')
                _, word, co = self.token[self.index]
                if word == ';':
                    pass
                elif word == '[':
                    if not self.right_value():
                        self._error('no value')
                    if not self._match(']'):
                        self._error('no ]')

                elif word == '(':
                    state = 6
                elif word == '=':
                    state = 7
                elif word == ',':
                    state = 8
            else:
                if flag:
                    self._error('more modifier')
                break

            self.index += 1



if __name__ == '__main__':
    lexer = Lexer("testfile.c")
    lexer.run()
    token = lexer.token
    print(token)
    syner = Syner(lexer.token, lexer.sign_table)
    syner.start()
