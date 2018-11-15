#!/usr/bin/env python
# Lexical Analysis
import string, re, sys

punctuation = string.printable[62:94]
whitespace = string.printable[94:]

class Token:
    def __init__(self, mylexeme):
        self.mytype = self.checktype(mylexeme)
        self.mylexeme = mylexeme

    def checktype(self, mylexeme):
        if mylexeme.isdigit():
            return "number"
        elif len(mylexeme) > 1 and (mylexeme[0] == "'" and mylexeme[-1] == "'"):
            return "character"
        elif len(mylexeme) > 1 and (mylexeme[0] == '"' and mylexeme[-1] == '"'):
            return "stringz"
        elif mylexeme in ['bool', 'class', 'char', 'cin', 'cout', 'else', 'false', 'if', 'int', 'itoa', 'main', 'new', 'null', 'object', 'public', 'private', 'return', 'true', 'void', 'while']:
            return mylexeme # keywords
        elif re.match("[a-zA-Z0-9_]+", mylexeme):
            return "identifier"
        elif re.match("-=|\+=|\+\+|--|!|<<|>>|<=|>=|==|!=|&&|\|\||<|=|>|\*|\+|-|/|%|\#|\|", mylexeme): # Need to specify what type of symbol it is (math, boolean, logic)
            return "symbol"
        elif re.match("//|\"|\$|&|\'|,|\.|:|;|\?|@|\\|\^|_|`|~|\(|\)|\{|\}|\[|\]", mylexeme):
            return "punctuation"
        else:
            return "unknown"

    def type(self):
        return self.mytype

    def value(self):
        return self.mylexeme

    def __str__(self):
        return '%s:\t%s' % (self.mytype, self.mylexeme)

class lex:
    def __init__(self, filename):
        self.line_number = 1
        self.lexy = self.lexer(filename)
        self.next_stored = None
        self.acurrent = None

    def peek(self):
        if not self.next_stored:
            self.next_stored = self.lexy.next()
        return self.next_stored

    def next(self):
        if self.next_stored:
            next_stored = self.next_stored
            self.next_stored = None
            self.acurrent = next_stored
            return next_stored
        else:
            self.acurrent = self.lexy.next()
            return self.acurrent

    def current(self):
        return self.acurrent

    def lexer(self, filename):
        for line in open(filename, 'r'):
            line = line.split("//")[0]
            symbols = re.findall("'\\\\.?'|'.?'|\".+\"|[a-zA-Z0-9_]+|[0-9]+|-[0-9]+|//|/\*|\*/|-=|\+=|\+\+|--|<<|>>|<=|>=|==|!=|&&|\|\||!|\"|\#|\$|%|&|\'|\(|\)|\*|\+|,|-|\.|/|:|;|<|=|>|\?|@|\[|\]|\\\\|\]|\^|_|`|\{|\||\}|~", line.strip())
            for symbol in symbols:
                yield Token(symbol)
            self.line_number += 1
        while 1:
            yield None

if __name__ == "__main__":
    test = lex(sys.argv[1])
    token = 1
    while token != None:
        token = test.next()
        if token:
            raw_input(token.atype() + "    \t" + token.lexeme().replace('\\', '\\\\'))
