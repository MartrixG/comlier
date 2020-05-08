from collections import namedtuple
from .token import Token
from copy import deepcopy

class node(object):
    def __init__(self, element):
        self.fa = self
        self.child = []
        self.element = element

    def add(self, child):
        self.child.append(child)

    def define_fa(self, fa):
        self.fa = fa
    
    def is_leaf(self):
        return len(self.child) == 0

_current_line = 1
_tree_str = ''
def DFS_search(root, level = 0):
    global _current_line
    global _tree_str
    print("  " * level, end='')
    _tree_str += '  ' * level
    print(root.element.name, end='')
    _tree_str += root.element.name
    if root.element.type == 'VT':
        _current_line = root.value.line
        if root.value.value != '_':
            print(' : {}'.format(root.value.value), end='')
            _tree_str += ' : {}'.format(root.value.value)
    print(' ({})'.format(_current_line))
    _tree_str += ' ({})'.format(_current_line) + '\n'
    for child in root.child:
        DFS_search(child, level + 1)


def prepare_tree(prods, tokens):
    to_reduce = []
    for prod in prods:
        rights = prod.right
        tmp_node = node(prod.left)
        for right in rights[::-1]:
            if right.type == 'VN':
                if to_reduce[-1].element == right:
                    tmp_node.add(to_reduce[-1])
                    to_reduce.pop()
            if right.type != 'VN':
                terminal = node(right)
                tmp_node.add(terminal)
        tmp_node.child = tmp_node.child[::-1]
        to_reduce.append(tmp_node)
    assert len(to_reduce) == 1
    prepare_token(to_reduce[0], 0, tokens)
    
    root = to_reduce[0]
    DFS_search(root)

    global _current_line
    _current_line = 1
    
    global _tree_str
    result = deepcopy(_tree_str)
    _tree_str = ''
    return result

def prepare_token(root, pos, tokens):
    if root.element.type == 'VT':
        root.value = tokens[pos]
        return pos + 1
    elif root.element.type == 'epsilon':
        root.value = Token('#', 'epsilon', -1)
        return pos
    else:
        for child in root.child:
            pos = prepare_token(child, pos, tokens)
        return pos