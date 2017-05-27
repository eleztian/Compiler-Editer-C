import graphviz as gv
import functools
graph = functools.partial(gv.Graph, format='png')  # 无向图
digraph = functools.partial(gv.Digraph, format='png')   # 有向图


class NFA(object):
    """
    不确定的有穷自动机
    """
    # 向图中添加节点
    @staticmethod
    def add_nodes(graph_, nodes):
        for n in nodes:
            if isinstance(n, tuple):
                graph_.node(str(n[0]), **n[1])
            else:
                graph_.node(str(n))
        return graph_

    # 向图中添加关系
    @staticmethod
    def add_edges(graph_, edges):
        for e in edges:
            if isinstance(e[0], tuple):
                graph_.edge(*e[0], **e[1])
            else:
                graph_.edge(*e)
        return graph_

    # 给图设置样式
    @staticmethod
    def apply_styles(graph_, styles):
        graph_.graph_attr.update(
            ('graph' in styles and styles['graph']) or {}
        )
        graph_.node_attr.update(
            ('nodes' in styles and styles['nodes']) or {}
        )
        graph_.edge_attr.update(
            ('edges' in styles and styles['edges']) or {}
        )
        return graph_

    def __init__(self, node_list=[], relationship=[], start_list=[], end_list=[]):
        self.node_list = node_list    # 状态集
        self.relationship = set(relationship)   # 关系集
        self.path = set([i[1] for i in self.relationship if i[1] != '$'])   # 终结符
        self.start_list = start_list    # 开始节点
        self.end_list = end_list    # 终结节点

    # 清空 自动机
    def clear(self):
        self.node_list = []
        self.start_list = []
        self.end_list = []
        self.relationship = set()
        self.path = set()

    # 添加节点
    def add_items(self, gra_list=[]):
        have = False
        pos = self.node_list.__len__()
        if gra_list:
            if gra_list in self.node_list:
                pos = self.node_list.index(gra_list)
                have = True
            else:
                self.node_list.append(gra_list)
            return pos, have
        else:
            self.node_list.append(pos)
            return pos

    # 添加关系   eg:（from c to）
    def add_relationship(self, relation):
        self.relationship.add(relation)
        if relation[1] != '$':
            self.path.add(relation[1])

    # 将 自动机 按一定的格式转化字符串
    def get_items_show(self, grammar_list):
        list_t = []
        for j in self.node_list:
            t = ''
            for i in j:
                t += (grammar_list[i[0]][0:i[1] + 4] + '.' + grammar_list[i[0]][i[1] + 4::] + ' ')
            list_t.append(t)
        return list_t

    # 获取 node_list 关于path_ch 的闭包  即. path_ch_closure(node_list)
    def k_closure_to(self, node_list, path_ch):
        result = []
        x = list(node_list)
        while True:
            t = x
            x = []
            for ch in self.relationship:
                # 若果 ch在node_list 且数据为patc_ch 则添加到x列表中
                if ch[0] in t and ch[1] == path_ch:
                    x.append(ch[2])
            # 全部找完 退出
            if not len(x):
                break
            result += x
        return result

    # NFA -> DFA
    def trans2dfa(self):
        st_list = []    # 状态号（节点号）
        dfa_start_list = []  # dfa 开始节点
        dfa_end_list = []   # dfa 结束节点
        dfa_relation_list = []  # dfa 关系
        nfa2dfa_table = []  # 转化表
        # 首行首列
        th1_list = self.start_list
        th1_list = self.k_closure_to(th1_list, '$') + th1_list
        # 添加一个节点（子集）
        st_list.append(th1_list)
        index = 0   # 节点编号
        while True:
            # 全部找完退出
            if index == len(st_list):
                break
            th1_list = st_list[index]
            # 识别 终结状态 和 非终结状态
            for i in th1_list:
                if i in self.start_list:
                    dfa_start_list.append(index)
                elif i in self.end_list:
                    dfa_end_list.append(index)
            x = []  # 新的一行
            # 求每一个终结符的 子集
            for path in self.path:
                thx_list = self.k_closure_to(th1_list, path)
                thx_list = self.k_closure_to(thx_list, '$') + thx_list
                if thx_list and thx_list not in st_list:    # 不为空且不存在
                    # 添加新节点(子集)
                    st_list.append(thx_list)
                x.append(thx_list)
                # 不为空， 添加关系
                if thx_list:
                    dfa_relation_list.append((index, path, st_list.index(thx_list)))
            # 添加到表中
            nfa2dfa_table.append((th1_list, x))
            index += 1  # 编号递增
        print(self.path)
        # 返回信息
        return list(range(0, len(st_list))), dfa_relation_list, dfa_start_list, dfa_end_list, nfa2dfa_table

    # 生成图片
    def show_graph(self, filename):
        # 样式信息
        styles = {
            'graph': {
                'size': '20,5',
                'label': filename,
                'rankdir': 'LR',
            },
        }
        self.node_list += self.end_list
        new_node_list = list(self.node_list)
        try:
            # 设置开始节点形状
            for i in self.start_list:
                new_node_list[self.node_list.index(i)] = \
                    (i, {'label': 'start'+str(i), 'shape': 'doublecircle'})
            #  设置终结节点形状
            for i in self.end_list:
                # 既是start又是end
                if i in self.start_list:
                    new_node_list[self.node_list.index(i)] = \
                        (i, {'label': 'Start&end' + str(i), 'shape': 'Mdiamond'})
                else:
                    new_node_list[self.node_list.index(i)] = \
                        (i, {'label': 'end'+str(i), 'shape': 'doubleoctagon'})
        except Exception as e:
            print(e)
        # 生成DOT
        g6 = self.add_edges(
            self.add_nodes(digraph(), new_node_list),
            [((str(i[0]), str(i[2])), {'label': i[1]}) for i in self.relationship]
        )
        # 设置样式
        self.apply_styles(g6, styles)
        # 执行graphviz 生成图片
        g6.render('img/'+filename)


class DFA(NFA):
    """
    确定的有穷自动机
    """
    # DFA -> MFA  最小化
    def trans2mfa(self):
        t = []
        # 识别既是开始节点又是终结节点
        for i in self.end_list:
            if i in self.start_list:
                t.append(i)
        t2 = list(set(self.end_list) - set(t))
        # 得到 终结集合 ，非中介集合， 既是开始节点又是终结节点集合
        group_ok = new_group = [t2, list(set(self.node_list) - set(t2) - set(t)), t]
        try:
            # 移除空集
            group_ok.remove([])
        except ValueError:
            pass
        while True:
            group = new_group
            new_group = []
            flag = False
            for g in group:
                t_group = []
                # 如果 i 指向了其他集合 则将他加入到新的集合t_group中
                for i in self.relationship:
                    if i[0] in g and i[2] not in g:
                        t_group.append(i[0])
                # t_group 部位空
                if t_group:
                    # 将他分为两个集合
                    s1 = list(set(g) - set(t_group))
                    # s1 不为空， 将他们添加到new_group中
                    if s1:
                        flag = True
                        new_group.append(t_group)
                        new_group.append(s1)
                        print('g', group_ok,g)
                        group_ok.remove(g)
                        group_ok.append(s1)
                        group_ok.append(t_group)
                        print(group_ok)
            # 没有新的集合了则退出
            if not flag:
                break
        # 以下是将数据转化为 一般格式 并返回信息
        node_list = list(range(0, len(group_ok)))
        relation = []
        print('t', group_ok)
        for index, g in enumerate(group_ok):
            if g:
                relation += [(index, i[1], i[2]) for i in self.relationship if i[0] == g[0]]
        new_relation = []
        for i in relation:
            for index, r in enumerate(group_ok):
                if i[2] in r:
                    new_relation.append((i[0], i[1], index))
                    break
        start_list = []
        end_list = []
        for index, g in enumerate(group_ok):
            for i in self.start_list:
                if i in g:
                    start_list.append(index)
            for i in self.end_list:
                if i in g:
                    end_list.append(index)
        return node_list, new_relation, start_list, end_list, group_ok


class MFA(DFA):
    """
    最小化的有穷自动机
    """
    pass
