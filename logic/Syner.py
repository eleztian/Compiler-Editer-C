"""
    语法分析(递归下降) LL(1)
"""
from logic.ComplierBase import ComplierBase
from logic.Lexer import Lexer


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

    def in_signtable(self, c):
        if c in [self.code['id'], self.code['string'], self.code['charRealNum'], self.code['constNum']]:
            return True
        return False

    # 获取下一个token值
    def _token_next(self, back_num=1):
        line, word, co = None, None, None
        try:
            line, word, co = self.token[self.index]
        except KeyError:
            word = None
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
        result = False
        l, w, c = self._token_next(3)
        s = "{:->" + str(self.tab+2) +"s} match  {:s}\t(Line: {:d})"
        if w is not None:
            if juge_other:
                if c == self.code[match_c]:
                    result = True
            else:
                if w == match_c:
                    result = True
        else:
            w = 'null'
            l = self.token[self.token_len-1][0]
        if not result:
            if do_error:
                self._error("match error on %s not %s" % (w, match_c))
            self._token_redo()
        if log and not pre_:
            self.log_info.append(s.format("", str(match_c), l))
        return result

    # 出错处理
    def _error(self, error_type=""):
        try:
            s = "Syner Error in %d Line (%s) after token %s" % (self.token[self.index-2][0], error_type, self.token[self.index - 2][1])
            self.error.append(s)
            print("error in ", self.token[self.index - 2], error_type)
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
            return False
        return True

    # 表达式  <表达式> -> <因子> <项>
    @show_log_info("about exp")
    def exp_s(self):
        self.yinzi_s()
        self.xiang_s()

    # <因子> -> <因式> <因式递归>
    @show_log_info("about exp_yinzi")
    def yinzi_s(self):
        self.yinshi_s()
        self.yinshi_closure()

    # < 项 > -> + < 因子 > < 项 > | - < 因子 > < 项 > | $
    @show_log_info("about exp_xiang")
    def xiang_s(self):
        if self._match_next('+', pre_=True) or self._match_next('-', pre_=True):
            self.yinzi_s()
            self.xiang_s()

    # < 因式 > -> ( < 表达式 > ) | < id > | < 数字 >| <fun_use>
    @show_log_info("about exp_yinshi")
    def yinshi_s(self):
        _, w, c = self._token_next(3)
        if c == self.code['id']:
            if self._match_next('('):
                self.fun_use_par_list()
                self._match_next(')')
        elif self.in_signtable(c):
            pass
        else:
            if w == '(':
                self.exp_s()
                self._match_next(')', True)
            else:
                self._error("no exp")
                self._token_redo()

    # <因式递归> -> * <因式> <因式递归> | / <因式> <因式递归> | $
    def yinshi_closure(self):
        if self._match_next('*', pre_=True) or self._match_next('/', pre_=True):
            self.yinshi_s()
            self.yinshi_closure()

    # < 右值 > -> < 表达式 > | { < 多个数据 >}
    @show_log_info("about right values")
    def right_value_s(self):
        if self._match_next('{', pre_=True):
            self.many_value_s()
            self._match_next('}')
        else:
            self.exp_s()

    # <多个数据> -> <数字> <数字闭包>
    @show_log_info("about right many values")
    def many_value_s(self):
        w = self._token_next()
        if w.isdigit():
            self.many_value_closure()

    # < 数字闭包 > ->, < 数字 > < 数字闭包 > | $
    def many_value_closure(self):
        if self._match_next(',', pre_=True):
            _, w, c = self._token_next(3)
            if c in [self.code['charRealNum'], self.code['charRealNum'], self.code['string']]:
                self.many_value_closure()
            else:
                self._error('no number')

    # <赋初值> -> = <右值> | $
    @show_log_info("about init value")
    def init_value_s(self):
        if self._match_next('=', pre_=True):
            self.right_value_s()

    # < 声明 > -> < 修饰词 > < 类型 > < id > < 赋初值 >
    @show_log_info("about declare")
    def declare_s(self):
        if self.type_s(self.modifier_s()):
            self.exp_whole_s()
            self.many_declare_s()
            return True
        return False

    # {*}a[id|num]=3*(2+2)
    @show_log_info("about statement init value")
    def exp_whole_s(self):
        self.addr_closure()
        self._match_next('id', True, True)
        self.group_define_op_s()
        self.init_value_s()
        self.declare_closure()

    # { [num | $] }
    def group_define_op_s(self):
        if self._match_next('[', pre_=True):
            self._match_next('constNum', True, True)
            self._match_next(']', True)
            self.group_define_op_s()
        return True

    #  {, exp_whole_s}
    def many_declare_s(self):
        if self._match_next(',', pre_=True):
            self.exp_whole_s()
            self.many_declare_s()

    # 匹配若干 {*}
    @show_log_info("about addr *")
    def addr_closure(self):
        w = self._token_next()
        if w == '*':
            self.addr_closure()
            return True
        else:
            self._token_redo()
            return False

    #  <声明闭包> -> , <id>  < 赋初值 > <声明闭包> | $
    def declare_closure(self):
        if self._match_next(',', pre_=True):
            if self._match_next('id', juge_other=True):
                self.init_value_s()
                self.declare_closure()
            else:
                self._error('more ,')
            return True
        return False

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
        if self.type_s(self.modifier_s()):
            self._match_next('id', do_error=True, juge_other=True)
            self._match_next('(', True)
            if self.fun_desc_par_list():
                self._match_next(')', True)
                if self._match_next('{'):   # 函数定义
                    self.fun_block()
                    self._match_next('}', do_error=True)
                else:
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
        result = False
        if self.type_s(self.modifier_s()):
            self.addr_closure()
            self._match_next('id', True, True)
            self.group_define_op_s()
            self.init_value_s()
            self.fun_desc_par_list_e()
            result = True
        return result

    # 函数声明参数列表闭包， {， par}
    def fun_desc_par_list_e(self):
        if self._match_next(',', pre_=True):
            self.fun_desc_par_list()
            self.fun_desc_par_list_e()

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
                self.exp_s()
            self._match_next(';')

    @show_log_info("about function use")
    def fun_use_s(self):
        self._match_next('id', True, True)
        self._match_next('(', True)
        self.fun_use_par_list()
        self._match_next(')', True)
        self._match_next(';', True)

    # 赋值语句 <*><id><[]><value_init>;
    @show_log_info("about init values ")
    def statement_init_value_s(self):
        if self._match_next('id', do_error=self.addr_closure(), juge_other=True):
            self.group_define_op_s()
            self.init_value_s()
            self._match_next(';', True)

    # if语句 if(bool_exp){statement}<else{statement}>
    @show_log_info("about statement if ")
    def statement_if_s(self):
        if self._match_next('if', pre_=False):
            self._match_next('(', True)
            self.exp_bool()
            self._match_next(')', True)
            self._match_next('{', True)
            self.statement_s()
            self._match_next('}', True)
            if self._match_next('else', pre_=False):
                self._match_next('{', True)
                self.statement_s()
                self._match_next('}', True)

    # bool 表达式 :: <exp> <>|<|==|!=> <exp>
    @show_log_info("about exp bool ")
    def exp_bool(self):
        have_k = False
        self._match_next('!')
        if self._match_next('(', pre_=False):
            have_k = True
        self._match_next('!')
        self.exp_s()
        w = self._token_next()
        if w in self.logic_sign:
            self.exp_s()
            if have_k:
                self._match_next(')', True)
        else:
            self._token_redo()
        self.exp_bool_many()

    # 多个bool表达式 && <bool_exp> or || <bool_exp>
    @show_log_info("about function exp bool eclo")
    def exp_bool_many(self):
        if self._match_next('&&') or self._match_next('||'):
            self.exp_bool()

    # for 语句 for(<赋值语句><,赋值语句闭包>;<bool_exp>;<后缀表达式>){statement}

    @show_log_info("about statements for")
    def statement_for_s(self):
        if self._match_next('for', pre_=True):
            self._match_next('(', True)
            self.for_init_exp()
            self._match_next(';', True)
            self.exp_bool()
            self._match_next(';', True)
            self.later_exp()
            self._match_next(')', True)
            self._match_next('{', True)
            self.statement_s()
            self._match_next('}', True)

    # a = 1, b = 2...
    @show_log_info("about statements for par1")
    def for_init_exp(self):
        if self._match_next('id', juge_other=True, pre_=True):
            self.init_value_s()
            self.many_value_closure()

    # 后缀表达式 a++ a-- a += exp a -= exp ...
    @show_log_info("about statements for par3")
    def later_exp(self):
        if self._match_next('id', juge_other=True, pre_=True):
            if self._match_next('++') or self._match_next('--'):
                pass
            elif self._match_next('+=') or self._match_next('-=') or\
                    self._match_next('*=') or self._match_next('/=') or\
                    self._match_next('>>=') or self._match_next('<<='):
                self.exp_s()
            else:
                self._error('more id')

    # while 语句 while(bool_exp){statement} or while(bool_exp);
    @show_log_info("about statements while")
    def statement_while(self):
        if self._match_next('while', pre_=True):
            self._match_next('(', True)
            self.exp_bool()
            self._match_next(')', True)
            if self._match_next('{'):
                self.statement_s()
                self._match_next('}', True)
            else:
                self._match_next(';', True)

    @show_log_info("about statement return")
    def statement_return(self):
        if self._match_next('return'):
            self.exp_s()
            self._match_next(';', True)

    def syner_start(self):
        while self.index < self.token_len-1:
            self.tab = 0
            if self._match_next(';', log=False):  # 空语句
                continue
            ind_old = self.index
            self.modifier_s()
            if self.type_s(True):
                self.addr_closure()
                self._match_next('id', True, True, log=False)
                #  <desc><type><*>id
                if self._match_next('(', log=False):  # 函数
                    self.index = ind_old
                    self.fun_s()
                else:       # 数据定义
                    self.index = ind_old
                    self.declare_2_s()

    def run(self):
        try:
            self.syner_start()
            self._exit_message()
        except Exception as e:
            print("run", e)

if __name__ == '__main__':
    syner = Syner("TestFile/testfile.txt")
    syner.run()
    for i in syner.log_info:
        print(i)
