import copy


class Grammar(object):

    def __init__(self, filename='', text='', remove_left_closure=False):
        if filename:
            self.read_from_file(filename)
        else:
            self.grammar_text = '-->' + text[0] + '\n' + text.strip()
        self.non_terminal_symbol = []
        self.terminal_symbol = []
        self.grammar = {}
        self.grammar_list = []
        self.decompose_grammar(self.grammar_text)
        if remove_left_closure:
            self.remove_left_recursion()

    # 读取文件 得到文法
    def read_from_file(self, filename):
        with open(filename, "r", encoding='utf8') as f:
            self.grammar_text = f.read().strip()
            # self.grammar_text = '-->' + self.grammar_text[0] + '\n' + self.grammar_text

    # 分解语法 得到 文法字典， 终结符， 非终结符
    def decompose_grammar(self, text):
        text = text.strip()
        s = [i.split('->') for i in text.split('\n') if i]
        print(s)
        non_t = [i[0] for i in s]
        self.non_terminal_symbol = sorted(set(non_t), key=non_t.index)  # 非终结符
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
        self.get_list_grammar()
        print("grammer:", self.grammar)
        print("non_ter:", self.non_terminal_symbol)
        print("ter:", self.terminal_symbol)
        print("grammar_list:", self.grammar_list)

    def get_list_grammar(self):
        for i in self.non_terminal_symbol:
            for j in self.grammar[i]:
                self.grammar_list.append(i + '->' + j)

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


if __name__ =="__main__":
    g = Grammar(filename='TestFile/lr.txt')
    g.remove_left_recursion()