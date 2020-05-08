import string


class DFA(object):
    def __init__(self, data):
        self.name = data['name'][0]
        self.Q = data['Q'][0].split(' ')
        self.sigma = data['sigma'][0].split(' ')
        self.q0 = data['q0'][0]
        species = data['F'][0].split(' ')
        self.F = {}
        self.error = {}
        for spec in species:
            tmp = spec.split(",")
            if tmp[0] == 'comma':
                tmp[0] = tmp[1] = ','
            self.F[tmp[0]] = tmp[1]
        tmp = ""
        for item in data['t']:
            tmp += item
        t = {}
        for item in tmp.split(' '):
            key, value = item.split(',')
            key = [key]
            if key[0] == 'digit':
                key = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            if key[0] == 'letter':
                key = [i for i in string.ascii_letters]
            if key[0] == 'comma':
                key = [',']
                value = value[0] + ','
            for each_key in key:
                t[value[0] + each_key] = value[1]
        for error in data['error'][0].split(';'):
            state, statement = error.split(':')
            self.error[state] = statement
        self.t = t

    def scan(self, src_code):
        re = ''
        now_state = self.q0
        now_ch = src_code.get_now()
        while True:
            if self.t.get(now_state + now_ch, None) is not None:
                now_state = self.t.get(now_state + now_ch)
            elif self.t.get(now_state + 'exc*', None) is not None and now_ch != '*':
                now_state = self.t.get(now_state + 'exc*')
            elif now_state in self.F.keys():
                return re, self.F.get(now_state), src_code.line
            else:
                while src_code.has_next():
                    if src_code.get_now() not in (string.ascii_letters, '_', string.digits):
                        break
                    re += src_code.get_next()
                return -1, self.error[now_state] + "at " + src_code.get_pos(len(re)) + ".", src_code.line
            re += now_ch
            now_ch = src_code.get_next()

    def get_list(self):
        re = []
        line = ["s\\Q"]
        for s in self.Q:
            line.append(s)
        re.append(line)
        for s in self.sigma:
            line = [s]
            for to in self.Q:
                tmp = to + s
                if self.t.get(tmp, None) is None:
                    line.append('err')
                else:
                    line.append(self.t.get(tmp))
            re.append(line)
        return re

    def __repr__(self):
        re = self.name + ":\n" + "s\\Q\t"
        for s in self.Q:
            re += s + '\t'
        re += '\n'
        for s in self.sigma:
            re += s + '\t'
            for to in self.Q:
                tmp = to + s
                if self.t.get(tmp, None) is None:
                    re += 'err\t'
                else:
                    re += self.t.get(tmp) + '\t'
            re += '\n'
        return re
