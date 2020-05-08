from util.element import element
from copy import deepcopy


class production(object):
    def __init__(self, left, right):
        self.left = element(left)
        self.right = []
        for each_right in right.split(' '):
            self.right.append(element(each_right))
        # self.right = frozenset(self.right)
        self.forward = None
        self.dot_pos = None

    def product_eq(self, other):
        return self.left == other.left and self.right == other.right

    def __str__(self):
        if self.forward is None or self.dot_pos is None:
            return self.left.__str__() + '-->' + [tmp.__str__() for tmp in self.right].__str__()
        else:
            re = self.left.__str__() + '-->['
            for i in range(len(self.right)):
                if i == self.dot_pos:
                    re += ' ● '
                re += (' ' + self.right[i].__str__() + ' ')
            if self.dot_pos == len(self.right):
                re += ' ● '
            re += (']' + ' , ' + self.forward.__str__())
            return re

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.left.__str__() + " " + self.right.__str__() + " " + self.forward.__str__() + " " + self.dot_pos.__str__())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def make_production(left, right):
    re = []
    for each_pro in right:
        re.append(production(left, each_pro))
    return re


def make_item(prod, dot_pos, forward):
    re = deepcopy(prod)
    re.forward = forward
    re.dot_pos = dot_pos
    return re


def recover_item(prod):
    re = deepcopy(prod)
    re.dot_pos = None
    re.forward = None
    return re
