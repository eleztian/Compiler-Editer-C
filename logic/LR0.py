from logic.Stack import Stack
from logic.Grammar import Grammar
from logic.Automata import DFA

""" 
    语法分析
    LR(0)分析
"""


class LR0(object):
    def __init__(self, filename='', text='', analysis_text=''):
        self.grammar = Grammar(filename=filename, text=text)
        self.analysis_text = analysis_text.strip()
        self.items = []  # 项目集合
        self.dfa = DFA()    # DFA
        self.action = []    #Actoon表
        self.goto = []  # goto表
        self.state_stack = Stack()
        self.sign_stack = Stack()
        self.last_str_stack = Stack()

    # 创建DFA
    def create_dfa(self):
        # 得到一个文法衍生的一条子集合
        def items(gra_id, p_pos):
            is_ter = False  # 用于判断是否为终结节点
            list_t = [(gra_id, p_pos)]
            gr_n = self.grammar.grammar_list[gra_id].split('->')[1]
            # 判断 . 是否在最后
            if (p_pos+1) < gr_n.__len__():
                start = 0
                # 遍历 添加
                while start < list_t.__len__():
                    gr_n = self.grammar.grammar_list[list_t[start][0]].split('->')[1]
                    p_pos = list_t[start][1] + 1
                    # 如果 . 后面是非终结符， 添加相应的项目
                    if gr_n[p_pos] in self.grammar.non_terminal_symbol:
                        list_t += [(index, -1)
                                   for index, i in enumerate(self.grammar.grammar_list)
                                   if i[0] == gr_n[p_pos]]
                        list_t = list(set(list_t))
                    # . 后移一位
                    start += 1
            else:
                is_ter = True
            # print(list_t)
            return list_t, is_ter

        # 递归调用获取所有文法的Items()， 返回 节点标号
        def closure(gra_id, p_pos):
            # 获取一个节点集合
            list_items, is_ter = items(gra_id, p_pos)
            # 添加节点
            pos, have = self.dfa.add_items(list_items)
            if not is_ter:  # 非终结节点
                if not have:
                    # 遍历这个节点，得到后续集合
                    for i in list_items:
                        pos2 = closure(i[0], i[1] + 1)
                        c = self.grammar.grammar_list[i[0]][4+i[1]]
                        # 添加关系
                        self.dfa.add_relationship((pos, c, pos2))
            else:
                # 终结节点
                self.dfa.add_relationship((pos, '', -2))
            return pos

        # 开始
        closure(0, -1)

        print('DFA')
        print(self.grammar.grammar_list)
        print(self.dfa.node_list.__len__())
        print(self.dfa.get_items_show(self.grammar.grammar_list))
        print(self.dfa.relationship)
        # self.dfa.show_graph('d')
        self.create_lr0_table()

    # 创建LR(0)分析表
    def create_lr0_table(self):
        action_head = self.grammar.terminal_symbol + ['#']
        # 初始化清空表
        self.action = {s: {} for s in range(self.dfa.node_list.__len__())}
        self.goto = {s: {} for s in range(self.dfa.node_list.__len__())}
        # 遍历DFA关系
        for relation in self.dfa.relationship:
            # 如果是终结节点
            if relation[2] == -2:
                # 如果是文法入口，acc
                if self.dfa.node_list[relation[0]][0][0] == 0:
                    self.action[relation[0]]['#'] = 'acc'
                else:
                    # 归约
                    t = 'r' + str(self.dfa.node_list[relation[0]][0][0])
                    for i in action_head:
                        self.action[relation[0]][i] = t
            #  非终结节点
            else:
                # 移进
                # 终结字符
                if relation[1] in self.grammar.terminal_symbol:
                    self.action[relation[0]][relation[1]] = ('S' + str(relation[2]))
                #     非终结字符
                else:
                    self.goto[relation[0]][relation[1]] = relation[2]
        print(self.action)
        print(self.goto)

    # LR0分析
    def analysis_lr0(self):
        result = True
        over = False
        input_sign = self.last_str_stack.top()
        a = self.action[int(self.state_stack.top())]
        print(a, input_sign)
        info = ''
        if a.__len__() == 0:
            print("error")
            result = False
        else:
            try:
                s = a[input_sign]
                if s[0] == 'S':
                    # 移进
                    print('移进')
                    self.sign_stack.push(input_sign)
                    print(s[1::])
                    self.state_stack.push([int(s[1::])])
                    print(s[1::], self.state_stack.items)
                    self.last_str_stack.pop()
                    info = '移进'
                elif s[0] == 'r':
                    # 归约
                    print('归约')
                    gra = self.grammar.grammar_list[int(s[1::])]
                    print()
                    print(gra)
                    self.state_stack.pop(len(gra[3::]))
                    self.sign_stack.pop(len(gra[3::]))
                    self.sign_stack.push(gra[0])
                    try:
                        k = self.goto[self.state_stack.top()]
                        self.state_stack.push([int(k[gra[0]])])
                        info = '归约'
                    except Exception as e:
                        print('error', e)
                        result = False
                else:
                    # 接受
                    if s == 'acc':
                        info = '接受'
                        print('acc')
                        over = True
                        result = False
            except Exception as e:
                print("error", e)
                result = False

        print(self.state_stack.items)
        print(self.sign_stack.items)
        print(self.last_str_stack.items)
        return result, over, info

    def analysis_init(self):
        self.state_stack.items = []
        self.sign_stack.items = []
        self.last_str_stack.items = []
        self.state_stack.push([0])
        self.sign_stack.push('#')
        self.last_str_stack.push('#' + self.analysis_text[::-1])
        print(self.last_str_stack.items)

    def set_analysis_text(self, text=''):
        self.analysis_text = text.strip()

if __name__ == '__main__':
    lr = LR0(filename='TestFile/lr.txt', analysis_text='ad')
    lr.create_dfa()
    lr.analysis_init()
    print('start')
    while True:
        lr.analysis_lr0()
