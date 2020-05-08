class code(object):
    def __init__(self, src):
        self.src = src
        self.pos = 0
        self.line = 1
        self.column = 0
        self.last_len = 0
        self.length = len(src)

    def has_next(self):
        return not(self.pos == self.length)

    def get_next(self):
        if self.pos + 1 == self.length:
            self.pos += 1
            return ''
        self.pos += 1
        re = self.src[self.pos]
        if self.src[self.pos - 1] == '\n' or self.src[self.pos - 1] == '\r':
            self.line += 1
            self.last_len = self.column
            self.column = 0
        self.column += 1
        return re

    def get_now(self):
        return self.src[self.pos]

    def get_pos(self, back):
        return "line:{:}, column:{:}".format(self.line, self.column - 1 - back)
