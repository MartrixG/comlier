from util.DFA import DFA
import json

from util.token import Token
from util.code import code


class Scanner(object):
    def __init__(self, json_files, codes):
        self.keyWord = {}
        self.operator = {}
        self.dfas = []
        for file in json_files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data['name'][0] == 'number':
                self.numDFA = DFA(data)
                self.dfas.append(["numbers DFA", self.numDFA])
            elif data['name'][0] == 'IDN':
                self.idnDFA = DFA(data)
                self.dfas.append(["Identifiers DFA", self.idnDFA])
            elif data['name'][0] == 'keyWord':
                keyWord = data['keys'][0].split(' ')
            elif data['name'][0] == 'operator':
                self.opDFA = DFA(data)
                self.dfas.append(['operators DFA', self.opDFA])
            else:
                raise SyntaxError()
        self.code = code(codes)
        for i in range(len(keyWord)):
            self.keyWord[keyWord[i]] = i

    def analysis(self):
        token = []
        error = []
        src_code = self.code
        while src_code.has_next():
            now_ch = src_code.get_now()
            if now_ch in (' ', '\t', '\n', '\r'):
                src_code.get_next()
                continue
            elif '0' <= now_ch <= '9':
                re, spec, line = self.numDFA.scan(src_code)
            elif now_ch in self.opDFA.F.keys():
                re, spec, line = self.opDFA.scan(src_code)
            elif now_ch.isalpha() or now_ch == '_':
                re, spec, line = self.idnDFA.scan(src_code)
                if re in self.keyWord:
                    spec = re.upper()
            if re != -1:
                token.append(Token(re, spec, line))
            else:
                error.append(Token(spec, 'error', line))
        return token, error
