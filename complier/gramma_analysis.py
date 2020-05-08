import json
from collections import OrderedDict
from collections import defaultdict
from util.token import Token
from util.element import element
from util.produnction import make_production, make_item, recover_item
from util.tree import prepare_tree
from tabulate import tabulate

EPSILON = element('#')
DOLLAR = element('$')

def return_empty_str():
    return ''

class LR(object):
    def __init__(self, path):
        self.all_prod = []
        self.closures = OrderedDict()
        self.alphabet = set()
        self.first = {}
        self.producers = {}
        self.start = None
        self.goto = None
        self.action = None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for left in data.keys():
                if self.start is None:
                    self.all_prod += make_production(left + "_p", [left])
                    self.start = self.all_prod[0].left
                self.all_prod += make_production(left, data[left])
        for prod in self.all_prod:
            self.alphabet.add(prod.left)
            for rights in prod.right:
                self.alphabet.add(rights)
            if prod.left not in self.producers:
                self.producers[prod.left] = set()
            self.producers[prod.left].add(prod)
        self.alphabet.add(DOLLAR)
        self.alphabet_list = sorted(list(self.alphabet))
        self.alphabet_str_list = [str(e) for e in self.alphabet_list]
        self.init_first()
        self.init_closure()
        self.all_prod_str = [str(e) for e in self.all_prod]
        self.init_goto_action()

    def get_closure(self, start_I):
        closure = set(start_I)
        while True:
            tmp_closure = set()
            for item in closure:
                right = item.right
                dot_pos = item.dot_pos
                forward = item.forward
                if dot_pos >= len(right) or right[dot_pos].type != "VN":  # 遇到终结符或者末尾直接跳过
                    continue
                if dot_pos < len(right) and right[dot_pos].type == "VN":
                    beta = right[dot_pos + 1:]  # 非终结符之后所有element均为beta
                    first = self.get_first(beta + [forward])  # beta + 展望符 求first
                    B = right[dot_pos]  # 圆点之后的第一个符号
                    for prod in self.producers[B]:  # 对所有这个非终结符的产生式进行迭代
                        for b in first:  # 对first集所有的符号迭代
                            if b == EPSILON:  # 如果first集中出现了空串报错
                                print(beta + forward)
                                raise Exception("在beta-a产生式的first集中出现了空产生式")
                            pos = 0
                            while pos < len(prod.right) and prod.right[pos] == EPSILON:  # 预防万一跳过空串开头
                                pos += 1
                            tmp_item = make_item(prod, pos, b)
                            if tmp_item not in closure:
                                tmp_closure.add(tmp_item)
            if tmp_closure == set():
                break
            else:
                closure |= tmp_closure
        return frozenset(closure)

    def go(self, closure_I, X):
        next_closure = set()
        for item in closure_I:
            if item.dot_pos < len(item.right) and item.right[item.dot_pos] == X:
                from copy import deepcopy
                tmp_item = deepcopy(item)
                tmp_item.dot_pos += 1
                next_closure.add(tmp_item)
        return self.get_closure(list(next_closure))

    def init_closure(self):
        for prod in self.producers[self.start]:
            start_prod = prod
        start_I = make_item(start_prod, 0, DOLLAR)
        self.closures[self.get_closure([start_I])] = 0
        while True:
            D = set()
            for closure in self.closures.keys():
                for X in self.alphabet:
                    if X != EPSILON:
                        tmp_closure = self.go(closure, X)
                        if len(tmp_closure) != 0 and tmp_closure not in self.closures:
                            D.add(tmp_closure)
            if len(D) == 0:
                break
            else:
                for d in D:
                    self.closures[d] = len(self.closures)
                    
    def init_goto_action(self):
        for prod in self.producers[self.start]:
            start_prod = prod
        self.goto = {}
        self.action = {}
        self.states = list(self.closures.keys())
        for state_idx, state in enumerate(self.closures):
            self.goto[state_idx] = defaultdict(return_empty_str)
            self.action[state_idx] = defaultdict(return_empty_str)
            for ele in self.alphabet:
                if ele.type == 'VN':
                    tmp_goto = self.go(state, ele)
                    if tmp_goto in self.closures:
                        try:
                            goto_state_idx = self.states.index(tmp_goto)
                            self.goto[state_idx][ele] = 's_{}'.format(goto_state_idx)
                        except ValueError:
                            raise ValueError("Cannot find a state for goto")
            for prod in state:
                if prod.dot_pos >= len(prod.right):
                    recover_i = recover_item(prod)
                    try:
                        product_idx = self.all_prod_str.index(str(recover_i))
                        self.action[state_idx][prod.forward] = 'r_{}'.format(product_idx)
                    except ValueError:
                        raise ValueError("Cannot find a product for reduce")
                else:
                    a = prod.right[prod.dot_pos]
                    if a == EPSILON:
                        raise Exception("创建goto转移表时出现空产生式错误")
                    if a.type == 'VT':
                        goto_state = self.go(state, a)
                        try:
                            goto_state_idx = self.states.index(goto_state)
                            self.action[state_idx][a] = 's_{}'.format(goto_state_idx)
                        except ValueError:
                            raise ValueError("Cannot find a state for goto")
                if start_prod.product_eq(prod) and prod.dot_pos == 1 and prod.forward == DOLLAR:
                    self.action[state_idx][DOLLAR] = 'acc_0'

    def get_first(self, prod):
        first_set = set()
        have_epsilon = True
        for ele in prod:
            if not have_epsilon:
                break
            first_set |= self.first[ele]
            if EPSILON not in self.first[ele]:
                have_epsilon = False
        if have_epsilon:
            first_set.add(EPSILON)
        elif EPSILON in first_set:
            first_set.remove(EPSILON)
        return first_set

    def init_first(self):
        for elements in self.alphabet:
            if elements.type != 'VN':
                self.first[elements] = {elements}
            else:
                self.first[elements] = set()
        updated = True
        while updated:
            updated = False
            for prod in self.all_prod:
                tmp = self.get_first(prod.right)
                if not self.first[prod.left].issuperset(tmp):
                    updated = True
                self.first[prod.left] |= tmp

    def print_productions(self):
        for prod in self.all_prod:
            print(prod)

    def print_alphabet(self):
        for elements in self.alphabet:
            print(elements)

    def print_first(self):
        result = []
        for ele in self.alphabet:
            if ele.type == 'VN':
                result.append('{} {}'.format(ele, self.first[ele]))
        return '\n'.join(result)

    def print_closure(self):
        result = []
        for item in self.closures.keys():
            result.append(str(self.closures[item]))
            result.append('-' * 30)
            for prod in item:
                result.append(str(prod))
        return '\n'.join(result)
    
    def print_action_goto(self):
        result = []
        # table head
        result.append([str(e) for e in self.alphabet_list])
        # table body
        for state_idx in range(len(self.states)):
            r = []
            r.append(state_idx)
            for alpha in self.alphabet_list:
                if alpha.type == 'VT':
                    r.append(self.action[state_idx][alpha])
                else:
                    r.append(self.goto[state_idx][alpha])
            result.append(r)
        return tabulate(result[1:], result[0], tablefmt="grid")

    def analysis(self, tokens, debug=False):
        from copy import deepcopy
        _tokens = deepcopy(tokens)
        _tokens.append(Token('$', '_', tokens[-1].line))
        _token_list = [e.spec.upper() + '_vt' for e in tokens] + ['$_vt']
        token_list = []
        for e in _token_list:
            if e not in self.alphabet_str_list:
                raise ValueError("Cannot find spec '{}' in '{}'".format(e, self.alphabet_str_list))
            token_list.append(self.alphabet_list[self.alphabet_str_list.index(e)])
        state_stack = [0]
        prod_stack = ['$_vt']
        input_idx = 0
        flag = 0
        prods_used = []
        state_list = []
        reduce_list = []
        while True:
            current_state = state_stack[-1]
            current_token = token_list[input_idx]
            current_action = self.action[current_state][current_token]
            _t = _tokens[input_idx]
            if current_action.startswith('s_'):
                # if debug:
                #     print('> state --')
                #     print("Current STATES:", state_stack)
                #     print("Current PRODS:", prod_stack)
                #     print("Current Input:", token_list[input_idx:])
                next_state = int(current_action[2:])
                state_stack.append(next_state)
                prod_stack.append(str(current_token))
                input_idx += 1
                state_list.append(_t)
                # if debug:
                #     print('< state --')
                #     print("Current STATES:", state_stack)
                #     print("Current PRODS:", prod_stack)
                #     print("Current Input:", token_list[input_idx:])
            elif current_action.startswith('r_'):
                prod_idx = int(current_action[2:])
                prod_to_use = self.all_prod[prod_idx]
                pop_num = len(prod_to_use.right) if prod_to_use.right[0].type != 'epsilon' else 0
                reduce_list.append(_t)
                # if debug:
                #     print("> reduce --")
                #     print("Current STATES:", state_stack)
                #     print("Current PRODS:", prod_stack)
                #     print("Current Input:", token_list[input_idx:])
                #     print("Use Product:", prod_to_use)
                #     print("We want to pop {} items".format(pop_num))
                prods_used.append(prod_to_use)
                for _ in range(pop_num):
                    state_stack.pop()
                    prod_stack.pop()
                left = str(prod_to_use.left)
                prod_stack.append(left)
                # if debug:
                #     print("- reduce --")
                #     print("Current STATES:", state_stack)
                #     print("Current PRODS:", prod_stack)
                #     print("Current Input:", token_list[input_idx:])
                try:
                    alpha = self.alphabet_list[self.alphabet_str_list.index(prod_stack[-1])]
                    goto_state = int(self.goto[state_stack[-1]][alpha][2:])
                    state_stack.append(goto_state)
                except ValueError:
                    print("ERROR: cannot find a goto")
                    flag = 2
                    break
                # if debug:
                #     print("< reduce --")
                #     print("add state: {}".format(goto_state))
                #     print("Current STATES:", state_stack)
                #     print("Current PRODS:", prod_stack)
                #     print("Current Input:", token_list[input_idx:])
            elif current_action.startswith('acc'):
                flag = 1
                break
            else:
                flag = 2
                break
        if flag == 1:
            print("Success")
            print("++++++++++++++++++++++++++++++")
            for prod in prods_used:
                print(prod)
            print("++++++++++++++++++++++++++++++")
            return 0, prepare_tree(prods_used, tokens), '\n'.join([str(e) for e in prods_used])
        elif flag == 2:
            if len(reduce_list) > 0:
                prompt = "Error at Line [{}] near token [{}]".format(reduce_list[-1].line, reduce_list[-1])
            else:
                prompt = "Error at Line [{}] near token [{}]".format(state_list[-1].line, state_list[-1])
            print(prompt)
            return 1, prompt, "None"
        else:
            return 2, 'unknown error', "None"