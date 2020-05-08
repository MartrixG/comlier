import wx
from UI.GUI import GUI
from complier.lexical_analysis import Scanner
from complier.gramma_analysis import LR
from tabulate import tabulate
import os
import pickle

if __name__ == "__main__":
    app = wx.App()
    frame = GUI(None, 'Grammar LR')
    app.MainLoop()

    # selected_fa_files = ['data/DFA/IDN.json', 'data/DFA/keyWord.json', 'data/DFA/number.json', 'data/DFA/operator.json']
    # #f = open('data/test_grammar.txt')
    # f = open('test.txt')
    # code = f.read()
    # lexical = Scanner(selected_fa_files, code)
    # Tokens, errors = lexical.analysis()
    # for token in Tokens:
    #     print(token)
    # #grammar_lr = LR('data/grammar/c_style.json')
    # grammar_lr = LR('c_style.json')
    # print("LR built")

    # os.makedirs("logs/", exist_ok=True)
    # first_print = grammar_lr.print_first()
    # closure_print = grammar_lr.print_closure()
    # action_goto_print = grammar_lr.print_action_goto()
    # with open("logs/print_first.txt", 'w', encoding='utf-8') as f:
    #     f.write(first_print)
    # with open("logs/print_closure.txt", 'w', encoding='utf-8') as f:
    #     f.write(closure_print)
    # with open("logs/print_action_goto.txt", 'w', encoding='utf-8') as f:
    #     f.write(action_goto_print)

    # grammar_lr.analysis(Tokens, debug=True)