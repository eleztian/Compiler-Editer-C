
""" 
    语法分析
    LL(1)预测分析
"""
import copy


class Forecasting(object):

    def __init__(self, filename='', text='', analysis_text=''):
        self.grammar = {}
        self.analysis_text = analysis_text.strip()
        self.step = []
        self.follow_set = {}
        self.first_set = {}
        self.terminal_symbol = []
        self.non_terminal_symbol = []
        self.grammar_text = ''
        if filename != '':
            self.read_from_file(filename)
        else:
            self.grammar_text = text
        print(self.grammar_text)
        self.decompose_grammar(self.grammar_text)
        self.forecast_table = {}
        self.exp_index = -1
        self.sign_stack = ''

    # 读取文件 得到文法
    def read_from_file(self, filename):
        with open(filename, "r", encoding='utf8') as f:
            self.grammar_text = f.read().strip()

    # 分解语法 得到 文法字典， 终结符， 非终结符
    def decompose_grammar(self, text):
        text = text.strip()
        s = [i.split('->') for i in text.split('\n') if i]
        non_t = [i[0] for i in s]
        self.non_terminal_symbol = sorted(set(non_t), key=non_t.index)   # 非终结符

        t = []
        for i in s:
            m = i[1].split('|')
            try:
                self.grammar[i[0]] += m
            except KeyError:
                self.grammar[i[0]] = m
            t += m
        m = []
        for i in t:
            if i != '$':
                m += list(i)
        self.terminal_symbol = list(set(i for i in m if i not in list(self.non_terminal_symbol)))
        print("grammer:", self.grammar)
        print("non_ter:", self.non_terminal_symbol)
        print("ter:", self.terminal_symbol)

    def remove_dir_left_recursion(self, grammar):
        non_list = copy.deepcopy(list(self.non_terminal_symbol))
        flag = False
        for non in non_list:
            for gra in grammar[non]:
                if non == gra[0]:  # 左递归
                    flag = True
                    c = self.get_no_used_char(self.non_terminal_symbol)
                    self.non_terminal_symbol += c
                    self.grammar[c] = [gra[1::] + c]
                    self.grammar[c] += '$'
                    self.grammar[non] = []
                    grammar[non].remove(gra)
                    if self.grammar[non].__len__() == 0:
                        self.grammar[non] += c
                    else:
                        for index, i in enumerate(grammar[non]):
                            grammar[non][index] = i + c
                        self.grammar[non] += [i for i in grammar[non]]

                    break
        return flag

    def remove_left_recursion(self):
        non_list = copy.deepcopy(self.non_terminal_symbol)
        gram = copy.deepcopy(self.grammar)
        for non_index in range(non_list.__len__()):
            for j in range(non_index-1):
                for gra in gram[non_list[j]]:
                    flag = 0
                    for i, c in enumerate(gra):
                        if c == non_list[non_index]:
                            for g in gram[non_list[non_index]]:
                                str = gra.replace(c, g)
                                gram[non_list[j]] += [str]
                                flag = 1
                    if flag:
                        gram[non_list[j]].remove(gra)
        # 消除间接递归
        self.remove_dir_left_recursion(gram)
        print(self.grammar)

    @staticmethod
    def get_no_used_char(non_list):
        list_ = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                'W', 'X', 'Y', 'Z']
        for i in list_:
            if i not in non_list:
                return i

    def can_get_blank(self, non):
        def closure(non_ter, see_blank):
            result = False
            for gra in self.grammar[non_ter]:
                for i in gra:
                    if i not in self.terminal_symbol and i not in see_blank:
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
            for s in self.grammar[non_ter]:
                if s[0] in self.terminal_symbol:  # 首字符是终结符结束
                    fist_list += s[0]
                else:  # 第一个是非终结符 AX
                    t = 0
                    if s[t] == '$':
                        fist_list += '$'
                    else:
                        while self.can_get_blank(s[t]):  # A->$
                            fist_list += [i for i in get_first_one(s[t]) if i != '$']
                            if s.__len__() > t + 1:
                                if s[t + 1] in self.terminal_symbol:  # x 是终结符
                                    fist_list += s[t + 1]
                                    break
                            else:
                                fist_list += '$'
                                break
                            t += 1
                        else:
                            fist_list += get_first_one(s[t])
            return list(set(fist_list))
        self.first_set = {i: [] for i in self.non_terminal_symbol}
        for non in self.non_terminal_symbol:
            self.first_set[non] += get_first_one(non)
        print("First set:", self.first_set)

    def get_first_set_grammer(self, gra_text):
        first_list = []
        c = gra_text[0]
        if gra_text == '$':
            first_list += '$'
        else:
                for x in gra_text:
                    if x in self.non_terminal_symbol:
                        first_list += self.first_set[x]
                        if '$' not in self.grammar[x]:
                            break
                    else:
                        first_list += x
                    break
        return list(set(first_list))

    # 得到follow集
    def get_follow_set(self):
        def get_follow_one(non_ter):
            follow_list = []
            start = self.grammar_text[0]
            if non_ter == start:
                follow_list += '#'
            for non in self.non_terminal_symbol:
                for gra in self.grammar[non]:
                    gra_len = gra.__len__()
                    gra_non_index = gra_len
                    for index in range(gra_len):
                        if gra[index] == non_ter:
                            gra_non_index = index
                            break
                    if non != non_ter and gra_non_index < gra_len:  # B->XAX
                        if gra_non_index == (gra_len - 1):
                            follow_list += get_follow_one(non)
                        else:
                            index = gra_non_index + 1
                            if gra[index] in self.terminal_symbol:  # B->XAbX
                                follow_list += gra[index]
                            else:
                                list_t = self.get_first_set_grammer(gra[index::])
                                if '$' in list_t:
                                    follow_list += get_follow_one(non)
                                follow_list += [i for i in list_t if i != '$']
            return list(set(follow_list))

        # 初始化 清空
        for i in self.non_terminal_symbol:
            self.follow_set[i] = []
        for non in self.non_terminal_symbol:
            self.follow_set[non] += get_follow_one(non)
        print("Follow set:", self.follow_set)

    def set_analysis_text(self, text):
        self.analysis_text = text.strip()

    # 构造预测分析表 (non_ter, ter, gra)
    def create_forecasting_table(self):
        def add2table(non_ter, ter, grammar):
            grammar_t = grammar
            for i in ter:
                try:
                    self.forecast_table[non_ter][i] = grammar_t
                except Exception as e:
                    self.forecast_table[non_ter] = {}
                    self.forecast_table[non_ter][i] = grammar_t

        for non in self.non_terminal_symbol:
            for gra in self.grammar[non]:
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
        if self.exp_index == -1:
            self.analysis_text += '#'
            self.push_stack(self.non_terminal_symbol[0])
            print('stack: ', self.sign_stack)
            self.exp_index += 1

        #     符号栈不为空，没有匹配完成
        if self.sign_stack.__len__() != 0:
            c = self.pop_stack()
            if c in self.non_terminal_symbol:
                try:
                    t_c = self.analysis_text[self.exp_index]
                    into_t = self.forecast_table[c][t_c]
                    info_str = c + '->' + into_t
                    if into_t != '$':
                        self.push_stack(into_t[::-1])
                except:
                    info_str = '匹配出错'
                    result = False
            else:
                if c == self.analysis_text[self.exp_index]:
                    info_str = '匹配%s' % c
                    self.exp_index += 1
                else:
                    if c == '$':
                        info_str = self.analysis()
                    else:
                        info_str = '匹配出错'
                        result = False
            if self.sign_stack.__len__() == 0:
                if self.exp_index < self.analysis_text.__len__()-2:
                    info_str = '匹配失败'
                    result = False
                else:
                    info_str = '接受'
        else:
            return None
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
    pre.remove_left_recursion()
    pre.get_first_set()
    pre.get_follow_set()
    pre.create_forecasting_table()
    for i in range(30):
        pre.analysis()
