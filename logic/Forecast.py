from logic.Grammar import Grammar
""" 
    语法分析
    LL(1)预测分析
"""


class Forecasting(object):

    def __init__(self, filename='', text='', analysis_text=''):
        # 处理文法， 并消除左递归和回溯
        self.grammar = Grammar(filename=filename, text=text, remove_left_closure=True)
        self.analysis_text = analysis_text.strip()
        self.step = []
        self.follow_set = {}    # follow集合
        self.first_set = {}     # First集合
        self.forecast_table = {}    # 预测分析表
        self.exp_index = -1
        self.sign_stack = ''    # 符号栈

    # 递归判断是否可以得到 $
    def can_get_blank(self, non):
        def closure(non_ter, see_blank):
            result = False
            for gra in self.grammar.grammar[non_ter]:
                for i in gra:
                    if i not in self.grammar.terminal_symbol and i not in see_blank:
                        see_blank += i
                        if i == '$':
                            result = True
                            break
                        else:
                            result = closure(i, see_blank)
                    else:
                        result = False
            return result
        see_blank = [non]
        return closure(non, see_blank)

    # 得到非终结符first集
    def get_first_set(self):
        def get_first_one(non_ter):
            fist_list = []
            # 遍历non_ter开始的文法
            for s in self.grammar.grammar[non_ter]:
                if s[0] in self.grammar.terminal_symbol:  # 首字符是终结符结束
                    fist_list += s[0]
                else:  # 第一个是非终结符 AX
                    t = 0
                    if s[t] == '$':
                        fist_list += '$'
                    else:
                        while self.can_get_blank(s[t]):  # A->$
                            fist_list += [i for i in get_first_one(s[t]) if i != '$']
                            if s.__len__() > t + 1:
                                if s[t + 1] in self.grammar.terminal_symbol:  # x 是终结符
                                    fist_list += s[t + 1]
                                    break
                            else:
                                fist_list += '$'
                                break
                            t += 1
                        else:
                            fist_list += get_first_one(s[t])
            return list(set(fist_list))
        # 初始化并清空 First集合
        self.first_set = {i: [] for i in self.grammar.non_terminal_symbol}
        # 遍历所有的非终结节点
        for non in self.grammar.non_terminal_symbol:
            self.first_set[non] += get_first_one(non)
        print("First set:", self.first_set)

    # 得到某一条文法的first集合
    def get_first_set_grammer(self, gra_text):
        first_list = []
        if gra_text == '$':
            first_list += '$'
        else:
                for x in gra_text:
                    if x in self.grammar.non_terminal_symbol:
                        first_list += self.first_set[x]
                        if '$' not in self.grammar.grammar[x]:
                            break
                    else:
                        first_list += x
                    break
        return list(set(first_list))

    # 得到follow集
    def get_follow_set(self):
        def get_follow_one(non_ter, last_ter):
            follow_list = []
            start = self.grammar.grammar_text[0]
            if non_ter == start:
                follow_list += '#'
            for non in self.grammar.non_terminal_symbol:
                for gra in self.grammar.grammar[non]:
                    gra_len = gra.__len__()
                    gra_non_index = gra_len
                    for index in range(gra_len):
                        if gra[index] == non_ter:
                            gra_non_index = index
                            break
                    if non != non_ter and gra_non_index < gra_len:  # B->XAX
                        if gra_non_index == (gra_len - 1):
                            if non != last_ter:
                                follow_list += get_follow_one(non, non_ter)
                            else:
                                follow_list += self.follow_set[non]
                        else:
                            index = gra_non_index + 1
                            if gra[index] in self.grammar.terminal_symbol:  # B->XAbX
                                follow_list += gra[index]
                            else:
                                list_t = self.get_first_set_grammer(gra[index::])
                                if '$' in list_t:
                                    if non != last_ter:
                                        follow_list += get_follow_one(non, non_ter)
                                    else:
                                        follow_list += self.follow_set[non]
                                follow_list += [i for i in list_t if i != '$']
            return list(set(follow_list))

        # 初始化 清空
        for i in self.grammar.non_terminal_symbol:
            self.follow_set[i] = []
        last_ter = ''
        for non in self.grammar.non_terminal_symbol:
            self.follow_set[non] += get_follow_one(non, last_ter)
            last_ter = non
        print("Follow set:", self.follow_set)

    # 设置分析语句
    def set_analysis_text(self, text):
        self.analysis_text = text.strip()

    # 构造预测分析表 (non_ter, ter, gra)
    def create_forecasting_table(self):
        def add2table(non_ter, ter, grammar):
            grammar_t = grammar
            for i in ter:
                try:
                    self.forecast_table[non_ter][i] = grammar_t
                except Exception:
                    self.forecast_table[non_ter] = {}
                    self.forecast_table[non_ter][i] = grammar_t

        for non in self.grammar.non_terminal_symbol:
            for gra in self.grammar.grammar[non]:
                list_first = self.get_first_set_grammer(gra)

                add2table(non, [i for i in list_first if i != '$'], gra)
                if '$' in list_first:
                    list_follow = self.follow_set[non]
                    add2table(non, list_follow, gra)
                    if '#' in list_follow:
                        add2table(non, ['#'], gra)
        print(self.forecast_table)

    # 单步分析
    def analysis(self):  # TODO: 步凑表格存储
        result = True
        info_str = ''
        # 初始化
        if self.exp_index == -1:
            self.analysis_text += '#'
            self.push_stack(self.grammar.non_terminal_symbol[0])
            print('stack: ', self.sign_stack)
            self.exp_index += 1

        # 符号栈不为空，没有匹配完成
        if self.sign_stack.__len__() != 0:
            c = self.pop_stack()
            if c in self.grammar.non_terminal_symbol:
                try:
                    t_c = self.analysis_text[self.exp_index]
                    into_t = self.forecast_table[c][t_c]
                    info_str = c + '->' + into_t
                    if into_t != '$':
                        # 反序入栈
                        self.push_stack(into_t[::-1])
                except:
                    info_str = '匹配出错'
                    result = False
            else:
                # 匹配成功
                if c == self.analysis_text[self.exp_index]:
                    info_str = '匹配%s' % c
                    self.exp_index += 1
                else:
                    # 若果 为空则进行又一次分析
                    if c == '$':
                        info_str = self.analysis()
                    else:
                        # 匹配出错
                        info_str = '匹配出错'
                        result = False
            # 符号栈为空
            if self.sign_stack.__len__() == 0:
                # 字符没有分析完， 匹配失败
                if self.exp_index < self.analysis_text.__len__()-2:
                    info_str = '匹配失败'
                    result = False
                else:
                    # 分析完成，匹配成功
                    info_str = '接受'
        else:
            return None
        # 返回 提示信息 和 运行结果
        return info_str, result

    def push_stack(self, str):
        self.sign_stack += str

    def pop_stack(self):
        str = self.sign_stack[self.sign_stack.__len__()-1]
        self.sign_stack = self.sign_stack[:self.sign_stack.__len__()-1]
        return str

    def get_head_stack(self):
        return self.sign_stack[self.sign_stack.__len__() - 1]

    def analysis_init(self):
        self.exp_index = -1
        self.sign_stack = ''
        self.analysis_text = ''

if __name__ == '__main__':
    pre = Forecasting(filename='ll_.txt', analysis_text='i+i*i')
    pre.get_first_set()
    pre.get_follow_set()
    pre.create_forecasting_table()
    for i in range(30):
        pre.analysis()
