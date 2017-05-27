from logic.Automata import NFA, DFA, MFA
from logic.Stack import Stack


class RegularExp(object):
    # 操作符 按优先级从小到大排序
    operator_list = ('#', '|', '.', '*')

    # 判断是否是操作数
    @staticmethod
    def is_operand(ch):
        # 若果不是操作符返回True
        if ch not in ('#', '*', '|', ')', '(', '.'):
            return True
        return False

    def __init__(self, regual_text=''):
        self.regual_text = regual_text.strip()
        # if not self.check_regual():
        #     raise Exception('RegularExp Error')
        # else:
        self.regual_text = self.add_operate()
        self.rpn = ''
        self.trans2rpn()
        self.nfa = NFA()
        self.dfa = DFA()
        self.mfa = MFA()
        print("new")

    # 识别NFA
    def check_regual(self):
        current_index = 0
        kuohao_num = 0
        leng = len(self.regual_text)
        result = False
        # 遍历查看 匹配规则
        while current_index < leng:
            result = True
            ch = self.regual_text[current_index]
            if self.is_operand(ch):
                pass
            elif ch == '*':
                if current_index != 0:
                    if self.regual_text[current_index - 1] not in ('(', '|'):
                        result = False
                else:
                    result = False
            elif ch == '|':
                if current_index != 0:
                    if self.regual_text[current_index - 1] == '(':
                        result = False
                else:
                    result = False
            elif ch == '(':
                kuohao_num += 1
            elif ch == ')':
                if current_index != 0:
                    if self.regual_text[current_index - 1] == '(':
                        result = False
                else:
                    result = False
                if kuohao_num == 0:
                    result = False
                else:
                    kuohao_num -= 1
            else:
                return False
            if result:
                current_index += 1
            else:
                break
        if kuohao_num != 0:
            result = False
        return result

    # 添加.连接符
    def add_operate(self):
        def is_need_add(last_c):
            if last_c.isalpha() or last_c == '(':
                return True
            else:
                return False

        leng = len(self.regual_text)
        new_regual_text = ''
        add_flag = False
        for index, ch in enumerate(self.regual_text):
            new_regual_text += ch
            if index != leng - 1:
                if ch == '*':
                    add_flag = is_need_add(self.regual_text[index + 1])
                elif ch == ')':
                    add_flag = is_need_add(self.regual_text[index + 1])
                elif self.is_operand(ch):
                    add_flag = is_need_add(self.regual_text[index + 1])
                else:
                    add_flag = False
                if add_flag:
                    new_regual_text += '.'
        return new_regual_text

    # 生成逆波兰式
    def trans2rpn(self):
        operator_stack = Stack()
        rpn_stack = Stack()
        # 放入一个优先级最低的运算符作为结束标志
        operator_stack.push('#')
        for ch in self.regual_text:
            # ch 是操作数
            if self.is_operand(ch):
                rpn_stack.push(ch)
            # ch是运算符，分情况讨论
            else:
                if ch == '(':
                    operator_stack.push(ch)
                # 将距离栈operator_stack栈顶的最近的'('之间的运算符，逐个出栈，依次压入栈rpn_stack，此时抛弃'('
                elif ch == ')':
                    while True:
                        t = operator_stack.pop()
                        if t == '(':
                            break
                        else:
                            rpn_stack.push(t)
                # 若x是除'('和')'外的运算符，则再分如下情况讨论
                else:
                    top_c = operator_stack.top()
                    if top_c == '(':
                        operator_stack.push(ch)
                    # 若当前栈operator_stack的栈顶元素不为'('，则将ch与栈operator_stack的栈顶元素比较，
                    # 若ch的优先级大于栈operator_stack栈顶运算符优先级，则将ch直接压入栈operator_stack。
                    # 否者，将栈operator_stack的栈顶运算符弹出，压入栈rpn_stack中，直到栈operator_stack的栈顶运算符优先级别低于（不包括等于）ch的优先级，
                    # 或栈rpn_stack的栈顶运算符为'('，此时再则将ch压入栈operator_stack;
                    else:
                        if self.operator_list.index(ch) > self.operator_list.index(top_c):
                            operator_stack.push(ch)
                        else:
                            while top_c != '(' and \
                                            self.operator_list.index(ch) <= self.operator_list.index(top_c):
                                rpn_stack.push(operator_stack.pop())
                                top_c = operator_stack.top()
                            operator_stack.push(ch)
        #  当表达式读取完成后运算符堆栈中尚有运算符时，则依序取出运算符到操作数堆栈，直到运算符堆栈为空。
        while not operator_stack.empty():
            rpn_stack.push(operator_stack.pop())
        #  去掉添加的运算符
        if rpn_stack.top() == '#':
            rpn_stack.pop()
        # 翻转栈
        rpn_stack.items.reverse()
        self.rpn = rpn_stack.items

    # 生成NFA
    def trans2nfa(self):
        current_index = -1
        # 清空nfa
        self.nfa.clear()

        # 连接运算1
        def point():
            # 取两个操作数
            n1, n2 = do_one()   # 结束
            n3, n4 = do_one()   # 开始
            # 添加关系
            self.nfa.add_relationship((n4, '$', n1))
            return n3, n2

        # 闭包运算
        def closure():
            # n1开始 n2 结束
            n1, n2 = do_one()
            self.nfa.add_relationship((n2, '$', n1))
            # 新建首尾两个状态点
            n4 = self.nfa.add_items()
            n3 = self.nfa.add_items()
            # 添加$连线
            self.nfa.add_relationship((n4, '$', n1))
            self.nfa.add_relationship((n2, '$', n3))
            self.nfa.add_relationship((n4, '$', n3))
            return n4, n3   # 返回 开始 和 结束 状态编号

        # 或运算
        def or_op():
            n1, n2 = do_one()
            n3, n4 = do_one()
            # 新建首尾两个状态点
            n5 = self.nfa.add_items()
            n6 = self.nfa.add_items()
            # 添加$连线
            self.nfa.add_relationship((n5, '$', n1))
            self.nfa.add_relationship((n5, '$', n3))
            self.nfa.add_relationship((n2, '$', n6))
            self.nfa.add_relationship((n4, '$', n6))
            return n5, n6

        # 获取一个 状态 返回 开始和结束编号
        def do_one():
            nonlocal current_index
            current_index += 1
            # 获取一个字符
            t = self.rpn[current_index]
            result = ()
            # 是操作符，执行相应的函数，得到返回值
            if t == '.':
                result = point()
            elif t == '|':
                result = or_op()
            elif t == '*':
                result = closure()
            # 是操作数，则添加 状态，返回开始 和 结束编号
            else:
                t1 = self.nfa.add_items()
                t2 = self.nfa.add_items()
                self.nfa.add_relationship((t2, t, t1))
                result = (t2, t1)
            return result

        # 开始递归执行
        start, end = do_one()
        # 设置 nfa大开始状态和终结状态号
        self.nfa.start_list, self.nfa.end_list = [start], [end]
        print(self.nfa.start_list, self.nfa.end_list, self.nfa.node_list, self.nfa.relationship)
        # 生成nfa图片
        self.nfa.show_graph('nfa')

    # 生成NFA
    def trans2dfa(self):
        self.trans2nfa()
        node_list, relationship, start_list, end_list, table = self.nfa.trans2dfa()
        # 根据参数 新建 DFA
        self.dfa = DFA(node_list, relationship, start_list, end_list)
        self.dfa.show_graph('dfa')

    # 生成MFA
    def trans2mfa(self):
        self.trans2dfa()
        print('ss', self.dfa.end_list)
        node_list, relationship, start_list, end_list, table = self.dfa.trans2mfa()
        # 根据参数 新建 MFA
        self.mfa = MFA(node_list, relationship, start_list, end_list)
        self.mfa.show_graph('mfa')


if __name__ == '__main__':
    regual = RegularExp('a*(bc*)*')
    regual.trans2mfa()
    print(regual.mfa.start_list, regual.mfa.end_list)
