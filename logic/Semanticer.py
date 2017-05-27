"""
    语法分析(递归下降) LL(1)
    语义分析（4元式）
"""
from logic.ComplierBase import ComplierBase, Error, SignTable
from logic.Lexer import Lexer
from PyQt5.QtCore import pyqtSignal

# 装饰器 用于记录log信息（语法树）
def show_log_info(info=""):
    def _deco(func):
        def _func(*args, **kw):
            args[0].tab += 2
            s = "{:->" + str(args[0].tab) + "s} match "
            s = s.format(' ') + info
            result = func(*args, **kw)
            if result:
                args[0].log_info.append(s)
            args[0].tab -= 2
            return result
        return _func
    return _deco


class Syner(ComplierBase):
    sinOut = pyqtSignal(list, Error, SignTable, dict)

    def __init__(self, filename='', text=''):
        super(Syner, self).__init__(filename, text)
        lexer = Lexer(filename, text)
        try:
            lexer.run()
        except Exception as e:
            print('lxer run', e)

        self.token = lexer.token
        self.index = 0
        self.error = lexer.error
        self.token_len = self.token.__len__()
        self.sign_table = lexer.sign_table
        self.log_info = []
        self.tab = 0
        self.quaternary = {}    # 四元式列表
        self.now_scope = ''
        self.now_quaternary = []

    def in_signtable(self, c):
        if c in [self.code['id'], self.code['string'], self.code['charRealNum'], self.code['constNum']]:
            return True
        return False

    def is_define(self, w, p, type_p='id'):
        result = False
        for i in self.sign_table:
            if i[0] == w and (i[2] == p or i[2] == 'global') and type_p == i[1]:
                result = True
                break
        return result

    # 获取下一个token值
    def _token_next(self, back_num=1):
        line, word, co = None, None, None
        try:
            line, word, co = self.token[self.index]
        except KeyError:
            word = ''
        self.index += 1
        if back_num == 1:
            return word
        else:
            return line, word, co

    # 返回到上一token
    def _token_redo(self):
        if self.index > 0:
            self.index -= 1

    # 匹配下一个token是否为c,是返回True， 否则返回False,返回到上一token值
    def _match_next(self, match_c, do_error=False, juge_other=False, log=True, pre_=False):
        result = ''
        l, w, c = self._token_next(3)
        s = "{:->" + str(self.tab+2) + "s} match  {:s}\t(Line: {:d})"
        if w:
            if juge_other:
                if c == self.code[match_c]:
                    result = w
            else:
                if w == match_c:
                    result = w
        else:
            l = self.token[self.token_len-1][0]
        if not result:
            if do_error:
                self._error("match error on %s not %s" % (w, match_c))
            self._token_redo()
        else:
            if log:
                self.log_info.append(s.format("", str(match_c), l))
        return result

    # 出错处理
    def _error(self, error_type=""):
        try:
            s = "Syner Error in %d Line (%s) after token %s" % (self.token[self.index-2][0], error_type, self.token[self.index - 2][1])
            self.error.append(s)
        except Exception as e:
            print(e)
        # try:
        #     pass
        #     # self.SynerOut.emit(self.log_info, self.error)
        #     # self.deleteLater()
        # except Exception as e:
        #     print(e)

    # 修饰词
    @show_log_info("about modifier")
    def modifier_s(self):
        c = self._token_next()
        if c not in self.modifier:
            self._token_redo()
            return False
        return True

    # 数据类型
    @show_log_info("about type")
    def type_s(self, do_error=False):
        c = self._token_next()
        if c not in self.s_type:
            if do_error:
                self._error("match error on %s not type" % c)
            self._token_redo()
            return ''
        return c

    Temp_index = 0

    def get_new_temp(self):
        result = 'T' + str(self.Temp_index)
        self.Temp_index += 1
        return result

    # 表达式  <表达式> -> <因子> <项>
    @show_log_info("about exp")
    def exp_s(self):
        result = ''
        result = self.yinzi_s()
        result2 = self.xiang_s(result)
        if result2:
            return result2
        return result

    # <因子> -> <因式> <因式递归>
    @show_log_info("about exp_yinzi")
    def yinzi_s(self):
        result = self.yinshi_s()
        if result:
            result2 = self.yinshi_closure(result)
            if result2:
                return result2
        return result

    # < 项 > -> + < 因子 > < 项 > | - < 因子 > < 项 > | $
    @show_log_info("about exp_xiang")
    def xiang_s(self, c):
        result = ''
        if self._match_next('+', pre_=True) or self._match_next('-', pre_=True):
            w = self.token[self.index - 1][1]
            result = self.yinzi_s()
            temp_ = self.get_new_temp()
            self.now_quaternary.append([w, c, result, temp_])
            result = temp_
            result2 = self.xiang_s(result)
            if result2:
                return result2
        return result

    # < 因式 > -> ( < 表达式 > ) | < id > | < 数字 >| <fun_use>
    @show_log_info("about exp_yinshi")
    def yinshi_s(self):
        _, w, c = self._token_next(3)
        result = ''
        if c == self.code['id']:
            # 检查是否定义， 不存在报错
            if self._match_next('('):
                self.fun_use_par_list()
                self._match_next(')')
                result = 'f_' + w
                self.now_quaternary.append(['CALL', w, '', result])
                if not self.is_define(w, self.now_scope, 'fun'):
                    self._error("not define fun %s in %s" % (w, self.now_scope))
            else:
                if not self.is_define(w, self.now_scope):
                    self._error("not define %s in %s" % (w, self.now_scope))
            result = w
        elif self.in_signtable(c):  # 常量
            result = w
        else:
            if w == '(':
                result = self.exp_s()
                self._match_next(')', True)
            else:
                self._error("no exp")
                self._token_redo()
        return result

    # <因式递归> -> * <因式> <因式递归> | / <因式> <因式递归> | $
    def yinshi_closure(self, c):
        result = ''
        if self._match_next('*', pre_=True) or self._match_next('/', pre_=True):
            w = self.token[self.index-1][1]
            result = self.yinshi_s()
            temp_ = self.get_new_temp()
            self.now_quaternary.append([w, c, result, temp_])
            result = temp_
            result2 = self.yinshi_closure(result)
            if result2:
                return result2
        return result

    # < 右值 > -> < 表达式 > | { < 多个数据 >}
    @show_log_info("about right values")
    def right_value_s(self):
        return self.exp_s()

    # <赋初值> -> = <右值> | $
    @show_log_info("about init value")
    def init_value_s(self, c):
        if self._match_next('=', pre_=True):
            self.now_quaternary.append(['=', c, '', self.right_value_s()])

    # < 声明 > -> < 修饰词 > < 类型 > < id > < 赋初值 >
    @show_log_info("about declare")
    def declare_s(self):
        type_ = self.type_s(self.modifier_s())
        if type_:
            self.exp_whole_s(type_)
            self.many_declare_s(type_)
            return True
        return False

    # {*}a[id|num]=3*(2+2)
    @show_log_info("about statement init value")
    def exp_whole_s(self, type_):
        w = self._match_next('id', True, True)
        self.init_value_s(w)
        if w:
            if self.is_define(w, self.now_scope):
                self._error("%s defined repeatedly in %s" % (w, self.now_scope))
            else:
                for index, i in enumerate(self.sign_table):
                    if i[0] == w and i[1] == 'id':
                        self.sign_table[index][3] = type_
                        self.sign_table[index][2] = self.now_scope
        self.many_declare_s(type_)

    #  {, exp_whole_s}
    def many_declare_s(self, type_):
        if self._match_next(',', pre_=True):
            self.exp_whole_s(type_)
            self.many_declare_s(type_)

    # < 声明语句 > -> < 声明 >;
    @show_log_info("about statement declare")
    def declare_2_s(self):
        if self.declare_s():
            self._match_next(';', True)
            return True
        return False

    # < 声明语句闭包 > -> < 声明语句 > < 声明语句闭包 > | $
    def declare_2_closure(self):
        if self.declare_2_s():
            self.declare_2_closure()

    # 函数定义， 函数声明
    @show_log_info("about functions")
    def fun_s(self):
        ty = self.type_s(self.modifier_s())
        if ty:
            w = self._match_next('id', do_error=True, juge_other=True)
            self._match_next('(', True)
            par_list = self.fun_desc_par_list()
            for index, i in enumerate(self.sign_table):
                if i[0] == w and i[1] == 'id':
                    self.sign_table[index][1] = 'fun'
                    self.sign_table[index][2] = 'global'
                    self.sign_table[index][3] = ty
                    self.sign_table[index][4] = par_list
                    break
            self._match_next(')', True)
            if self._match_next('{'):   # 函数定义
                for index, i in enumerate(self.sign_table):
                    for j in par_list:
                        if i[0] == j[1] and i[1] == 'id':
                            self.sign_table[index][2] = self.now_scope
                            self.sign_table[index][3] = j[0]
                        break
                self.fun_block()
                self._match_next('}', do_error=True)
            else:
                if self.is_define(w, self.now_scope, 'fun'):
                    self._error("%s defined repeatedly in %s" % (w, self.now_scope))
                self._match_next(';', True)  # 函数声

    @show_log_info("about function use par list")
    def fun_use_par_list(self):
        _, w, c = self._token_next(3)
        if self.in_signtable(c):
            if self._match_next(','):
                self.fun_use_par_list()
                return True
        else:
            self._token_redo()
            return False

    # 函数声明参数列表 par {<desc><type><*><id><[num]><value init><，闭包>}
    @show_log_info("about function desc par list")
    def fun_desc_par_list(self):
        type_ = self.type_s(do_error=self.modifier_s())
        list_p = []
        if type_:
            w = self._match_next('id', True, True)
            self.init_value_s(w)
            list_p = [(type_, w)]
            list_p += self.fun_desc_par_list_e()
        return list_p

    # 函数声明参数列表闭包， {， par}
    def fun_desc_par_list_e(self):
        list_p = []
        if self._match_next(',', pre_=True):
            list_p.append(self.fun_desc_par_list())
            list_p += self.fun_desc_par_list_e()
        return list_p

    # 函数快 :: <数据定义>  <其他语句> <return>
    @show_log_info("about function block")
    def fun_block(self):
        self.declare_2_closure()
        self.statement_s()

    # 语句
    @show_log_info("about statements ")
    def statement_s(self):
        while self.index < self.token_len:
            t = self._match_next('}')
            if t:
                self._token_redo()
                break
            self.statement_end_with_div()
            self.statement_if_s()
            self.statement_for_s()
            self.statement_while()

    # 以分号结尾的语句
    @show_log_info("about statement about start with id ")
    def statement_end_with_div(self):
        ind_old = self.index
        if self._match_next('id', juge_other=True, pre_=False):
            if self._match_next('('):
                self.index = ind_old
                self.fun_use_s()
            else:
                self.index = ind_old
                self.statement_init_value_s()
        else:
            # return 语句
            if self._match_next('return', pre_=False):
                result = self.exp_s()
                temp_ = self.get_new_temp()
                self.now_quaternary.append(['=', temp_, '', result])
            self._match_next(';')

    @show_log_info("about function use")
    def fun_use_s(self):
        w = self._match_next('id', True, True)
        self._match_next('(', True)
        self.fun_use_par_list()
        self._match_next(')', True)
        self._match_next(';', True)
        if not self.is_define(w, self.now_scope, 'fun'):
            self._error("not defien fun %s in %s" % (w, self.now_scope))
        temp_ = self.get_new_temp()
        self.now_quaternary.append(['CALL', w, '', temp_])
        return temp_

    # 赋值语句 <*><id><[]><value_init>;
    @show_log_info("about init values ")
    def statement_init_value_s(self):
        w = self._match_next('id', juge_other=True)
        if w:
            if not self.is_define(w, self.now_scope):
                self._error('not define %s in %s' % (w, self.now_scope))
            self.init_value_s(w)
            self._match_next(';', True)

    # if语句 if(bool_exp){statement}<else{statement}>
    @show_log_info("about statement if ")
    def statement_if_s(self):
        if self._match_next('if', pre_=False):
            self._match_next('(', True)
            ok_pos, err_pos = self.exp_bool()
            self._match_next(')', True)
            self._match_next('{', True)
            self.now_quaternary[ok_pos][3] = len(self.now_quaternary)
            self.statement_s()
            self._match_next('}', True)
            self.now_quaternary[err_pos][3] = len(self.now_quaternary)
            if self._match_next('else', pre_=False):
                self._match_next('{', True)
                self.statement_s()
                self._match_next('}', True)

    # bool 表达式 :: <exp> <>|<|==|!=> <exp>
    @show_log_info("about exp bool ")
    def exp_bool(self, ok_pos=0, err_pos=0):
        have_k = False
        have_not = False
        w = self._match_next('!', pre_=True)
        if w:
            have_not = True
        if self._match_next('(', pre_=True):
            have_k = True
        result1 = self.exp_s()
        w = self._token_next()
        if w in self.logic_sign:
            result2 = self.exp_s()
            if have_k:
                self._match_next(')', True)
            self.now_quaternary.append(['J'+w, result1, result2, ok_pos])
        else:
            self._token_redo()
            self.now_quaternary.append(['JNZ', result1, '', ok_pos])
        self.now_quaternary.append(['J', '', '', err_pos])
        if ok_pos == 0 and err_pos == 0:
            ok_pos = len(self.now_quaternary) - 2
            err_pos = len(self.now_quaternary) - 1
        if have_not:
            ok_pos, err_pos = err_pos, ok_pos
        ok_pos_, err_pos_ = self.exp_bool_many(ok_pos, err_pos)
        return ok_pos_, err_pos_

    # 多个bool表达式 && <bool_exp> or || <bool_exp>
    @show_log_info("about function exp bool eclo")
    def exp_bool_many(self, ok_pos, err_pos):
        l = len(self.now_quaternary)
        if self._match_next('&&', pre_=True) or self._match_next('||', pre_=True):
            if self.token[self.index-1][1] == '&&':
                self.now_quaternary[l-1][3] = err_pos
                self.now_quaternary[l-2][3] = ok_pos
                self.now_quaternary[ok_pos][3] = l
                ok_pos = l
                ok_pos, err_pos = self.exp_bool(ok_pos, err_pos)
            else:
                self.now_quaternary[l-2][3] = ok_pos
                self.now_quaternary[l-1][3] = err_pos
                self.now_quaternary[err_pos][3] = l
                err_pos = l+1
                ok_pos, err_pos = self.exp_bool(ok_pos, err_pos)
        return ok_pos, err_pos

    # for 语句 for(<赋值语句><,赋值语句闭包>;<bool_exp>;<后缀表达式>){statement}

    @show_log_info("about statements for")
    def statement_for_s(self):
        if self._match_next('for', pre_=True):
            self._match_next('(', True)
            self.for_init_exp()
            self._match_next(';', True)
            bool_start = len(self.now_quaternary)
            ok_pos, err_pos = self.exp_bool()
            self._match_next(';', True)
            start_pos = len(self.now_quaternary)
            self.later_exp()
            self.now_quaternary.append(['J', '', '', bool_start])  # 跳转到BOOL表达式
            self._match_next(')', True)
            self._match_next('{', True)
            self.now_quaternary[ok_pos][3] = len(self.now_quaternary)   # bool表达式正确进入循环
            self.statement_s()
            self.now_quaternary.append(['J', '', '', start_pos])  # 跳转到后缀表达式开始
            self.now_quaternary[err_pos][3] = len(self.now_quaternary)   # bool表达式错误跳出循环
            self._match_next('}', True)

    # a = 1, b = 2...
    @show_log_info("about statements for par1")
    def for_init_exp(self):
        w = self._match_next('id', juge_other=True, pre_=True)
        if w:
            self.init_value_s(w)
            self.for_init_exp_closure()

    def for_init_exp_closure(self):
        if self._match_next(',', pre_=True):
            self.for_init_exp()

    # 后缀表达式 a++ a-- a += exp a -= exp ...
    @show_log_info("about statements for par3")
    def later_exp(self):
        # if self._match_next('id', juge_other=True, pre_=True):
        #     if self._match_next('++') or self._match_next('--'):
        #         if self.token[self.index - 1] == '++':
        #
        #     elif self._match_next('+=') or self._match_next('-=') or\
        #             self._match_next('*=') or self._match_next('/=') or\
        #             self._match_next('>>=') or self._match_next('<<='):
        #         self.exp_s()
        #     else:
        #         self._error('more id')
        self.for_init_exp()


    # while 语句 while(bool_exp){statement} or while(bool_exp);
    @show_log_info("about statements while")
    def statement_while(self):
        if self._match_next('while', pre_=True):
            self._match_next('(', True)
            bool_start = len(self.now_quaternary)
            ok_pos, err_pos = self.exp_bool()

            self.now_quaternary[ok_pos][3] = len(self.now_quaternary)
            self._match_next(')', True)
            if self._match_next('{'):
                self.statement_s()
                self._match_next('}', True)
                self.now_quaternary.append(['J', '', '', bool_start])
                self.now_quaternary[err_pos][3] = len(self.now_quaternary)
            else:
                self.now_quaternary.append(['J', '', '', bool_start])
                self.now_quaternary[err_pos][3] = len(self.now_quaternary)
                self._match_next(';', True)

    def syner_start(self):
        while self.index < self.token_len-1:
            self.now_quaternary = []
            self.tab = 0
            if self._match_next(';', log=False):  # 空语句
                continue
            ind_old = self.index
            if self.type_s(self.modifier_s()):
               
                w = self._match_next('id', True, True, log=False)
                #  <desc><type><*>id
                if self._match_next('(', log=False):  # 函数
                    self.index = ind_old
                    self.now_scope = w
                    self.fun_s()
                    self.quaternary.update({self.now_scope: self.now_quaternary})
                else:       # 数据定义s
                    self.index = ind_old
                    self.now_scope = 'global'
                    self.declare_2_s()
                    self.quaternary.update({self.now_scope: self.now_quaternary})

    def run(self):
        try:
            self.syner_start()
            self.sinOut.emit(self.log_info, self.error, self.sign_table, self.quaternary)
        except Exception as e:
            print("run", e)

if __name__ == '__main__':
    syner = Syner("TestFile/testfile.txt")
    syner.run()
    print(syner.sign_table)
    print(syner.error)
    # for i in syner.log_info:
    #     print(i)
    keys = list(syner.quaternary.keys())
    print(syner.quaternary)
    print(keys)
    for k in keys:
        for index, i in enumerate(syner.quaternary[k]):
            print(index, '\t', i)
