import os
import wx
import json
import pickle
from tabulate import tabulate
from complier.lexical_analysis import Scanner
from complier.gramma_analysis import LR


class GUI(wx.Frame):
    def __init__(self, parent, title):
        super(GUI, self).__init__(parent, title=title, size=(1500, 600))
        if os.path.exists('grammar_lr.pkl'):
            self.grammar_lr = pickle.load(open('grammar_lr.pkl', 'rb'))
            print("Use cached Grammar LR")
        else:
            self.grammar_lr = LR('c_style.json')
            with open("grammar_lr.pkl", 'wb') as f:
                pickle.dump(self.grammar_lr, f)
            print("Grammar LR Built")
        os.makedirs("logs/", exist_ok=True)
        first_print = self.grammar_lr.print_first()
        closure_print = self.grammar_lr.print_closure()
        action_goto_print = self.grammar_lr.print_action_goto()
        with open("logs/print_first.txt", 'w', encoding='utf-8') as f:
            f.write(first_print)
        with open("logs/print_closure.txt", 'w', encoding='utf-8') as f:
            f.write(closure_print)
        with open("logs/print_action_goto.txt", 'w', encoding='utf-8') as f:
            f.write(action_goto_print)
        self.InitUI()
        self.Centre()
        self.Show()
        self.output_lr_box.SetValue(self.grammar_lr.print_action_goto())

    def InitUI(self):
        default_font = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(0, 0)

        text_input = wx.StaticText(panel, label="Input")
        sizer.Add(text_input, pos=(0, 0), flag=wx.ALL, border=5)
        self.input_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER | wx.HSCROLL)
        self.input_box.SetFont(default_font)
        sizer.Add(self.input_box, pos=(0, 1), span=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)

        text_output = wx.StaticText(panel, label="Output")
        sizer.Add(text_output, pos=(0, 2), flag=wx.ALL, border=5)
        self.output_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL | wx.HSCROLL)
        sizer.Add(self.output_box, pos=(0, 3), span=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)
        self.output_box.SetFont(default_font)

        text_output_lr = wx.StaticText(panel, label="LR Analysis")
        sizer.Add(text_output_lr, pos=(0, 4), flag=wx.ALL, border=5)
        self.output_lr_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL | wx.HSCROLL)
        self.output_lr_box.SetFont(default_font)
        sizer.Add(self.output_lr_box, pos=(0, 5), span=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)

        text_output_prod = wx.StaticText(panel, label="Products")
        sizer.Add(text_output_prod, pos=(0, 6), flag=wx.ALL, border=5)
        self.output_prod_box = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL | wx.HSCROLL)
        self.output_prod_box.SetFont(default_font)
        sizer.Add(self.output_prod_box, pos=(0, 7), span=(2, 1), flag=wx.EXPAND | wx.ALL, border=5)

        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableCol(3)
        sizer.AddGrowableCol(5)
        sizer.AddGrowableCol(7)

        buttonSelectCodeFile = wx.Button(panel, label="Select Code File")
        buttonSelectCodeFile.Bind(wx.EVT_BUTTON, self.OnPressSelectCodeFileBtn)
        sizer.Add(buttonSelectCodeFile, pos=(2, 0), span=(1, 2), flag=wx.ALL, border=5)

        buttonProcess = wx.Button(panel, label="Process")
        buttonProcess.Bind(wx.EVT_BUTTON, self.OnPressProcessBtn)
        sizer.Add(buttonProcess, pos=(2, 2), span=(1, 2), flag=wx.ALL, border=5)

        panel.SetSizerAndFit(sizer)

    def OnPressSelectCodeFileBtn(self, event):
        wildcard = 'All files(*.*)|*.*'
        dialog = wx.FileDialog(None, 'select', os.getcwd(), '', wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            dialog.Destroy
            try:
                f_in = open(file_path, 'r', encoding='utf-8')
                self.code_file = file_path
                self.input_box.SetValue(''.join(f_in.readlines()))
            except:
                wx.MessageBox("Cannot load file", "Error", wx.OK | wx.ICON_ERROR)

    def OnPressProcessBtn(self, event):
        selected_fa_files = ['data/DFA/IDN.json', 'data/DFA/keyWord.json', 'data/DFA/number.json', 'data/DFA/operator.json']
        lexical = Scanner(selected_fa_files, self.input_box.GetValue())
        Tokens, errors = lexical.analysis()
        status_code, prompt, prods = self.grammar_lr.analysis(Tokens, debug=True)
        self.output_box.SetValue(prompt)
        self.output_prod_box.SetValue(prods)
        # self.output_box.SetValue('\n'.join(tokens))
        # output_fa_text = ""
        # for dfa_name, dfa in lexical.dfas:
        #     output_fa_text += '{}\n'.format(dfa_name)
        #     dfa_table = dfa.get_list()
        #     output_fa_text += tabulate(dfa_table[1:], dfa_table[0], tablefmt="grid") + '\n'
        # self.output_fa_box.SetValue(output_fa_text)
