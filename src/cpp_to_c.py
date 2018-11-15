#!/usr/bin/env python
import argparse, os.path, re
from lex import lex
from sym import SymbolTable

class ClassSplit:
    def __init__(self, out):
        # Split Function defs outside the struct define
        self.out = out
        self.struct = ''
        self.funcs = ''

    def write_def(self, data):
        self.struct += data

    def write_func(self, data):
        self.funcs += data

    def __str__(self):
        return '%s\n%s' % (self.struct, self.funcs)

    def __del__(self):
        self.out.write(self.struct)
        self.out.write(self.funcs)

class CTCompiler:
    def __init__(self, symbols, fname, fout):
        self.symbols = symbols
        self.lexy = lex(fname) # Lexical Analyzer
        self.out = open(fout, 'w')

    def assertEqual(self, expected, found):
        if expected != found:
            raise Exception('Line %d: Expected %s, found %s' % (self.lexy.line_number, expected, found))

    def __compiler_directive(self):
        token = self.lexy.next()
        if token.value() in ['ifndef', 'ifdef']:
            self.out.write('#%s ' % token.value())
            token = self.lexy.next()
            self.assertEqual(token.type(), 'identifier')
            self.out.write('%s\n' % token.value())
            while True:
                if self.lexy.peek().value() == '#':
                    self.lexy.next()
                    if self.lexy.peek().value() == 'endif':
                        self.out.write('#endif\n')
                        break
                    else:
                        self.__compiler_directive()
                self.parse()
        elif token.value() == 'define':
            self.out.write('#%s ' % token.value())
            token = self.lexy.next()
            self.assertEqual(token.type(), 'identifier')
            self.out.write('%s\n' % token.value())
            # TODO: handle defining a value or statement, etc
        elif token.value() == 'include':
            token = self.lexy.next()
            if token.type() == 'string':
                self.out.write('#include %s\n' % token.value())
        else:
            raise Exception('Line %d: %s' % (self.lexy.line_number, str(token)))

    def __template(self):
        token = self.lexy.next()
        self.assertEqual(token.value(), '<')
        template_vars = []
        peek = self.lexy.peek().value()
        while self.lexy.peek().value() != '>':
            var = []
            while self.lexy.peek().value() not in [',', '>']:
                token = self.lexy.next()
                var.append(token.value())
            template_vars.append(' '.join(var))
            if self.lexy.peek().value() == ',':
                self.lexy.next()
        token = self.lexy.next()
        self.assertEqual(token.value(), '>')
        token = self.lexy.next()
        if token.type() == 'class':
            token = self.lexy.next()
            className = token.value()
            template = self.symbols.get(self.symbols.search(value=className, kind='template'))
            for parm, val in zip(template_vars, template[-1]):
                vtype, name = parm.split()
                self.symbols.insert(name, vtype, data=val)
            self.__class_internals(className)
        else:
            raise Exception('Line %d: %s' % (self.lexy.line_number, str(token)))

    def __class(self):
        token = self.lexy.next()
        className = token.value()
        self.__class_internals(className)

    def __class_internals(self, className):
        class_id = self.symbols.insert(className, 'class')
        self.symbols.descend_scope(className)
        out = ClassSplit(self.out)
        token = self.lexy.next()
        self.assertEqual(token.value(), '{')
        out.write_def('typedef struct\n{\n')
        while self.lexy.peek().value() != '}':
            self.__class_member_declaration(class_id, out)
        token = self.lexy.next()
        self.assertEqual(token.value(), '}')
        out.write_def('} %s;' % className)
        self.symbols.ascend_scope()

    def __class_member_declaration(self, class_id, out):
        token = self.lexy.next()
        if token.value() in ['private', 'public']: # Ignore these, since C can't encapsulate
            token = self.lexy.next()
            self.assertEqual(token.value(), ':')
        else:
            self.parse()

    def parse(self):
        token = self.lexy.next()
        if token.type() == 'symbol' and token.value() == '#':
            self.__compiler_directive()
        elif token.value() == 'template':
            self.__template()
        elif token.value() == 'class':
            self.__class()
        else:
            raise Exception('Line %d: %s' % (self.lexy.line_number, str(token)))

    def start(self):
        while self.lexy.peek() != None:
            self.parse()

    def __del__(self):
        self.out.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses a C++ source file and converts it to human readable C code")
    parser.add_argument("--input-files", help="c++ input files, parsed first to last", nargs='+', required=True)
    parser.add_argument("--out-dir", help="Output directory", required=True)
    parser.add_argument("--template-definition", help="Definition for template (one allowed per template) in the format ClassName\\<opt1,opt2\\>", action='append')

    args = parser.parse_args()

    symbols = SymbolTable()

    for template in args.template_definition:
        m = re.match('(?P<name>\w+)\<(?P<vars>[\w,]+)\>', template)
        symbols.insert(m.group('name'), 'template', data=m.group('vars').split(','))

    for fname in args.input_files:
        fout, ext = os.path.splitext(fname)
        if ext != '.h':
            ext = '.c'
        fout = os.path.join(args.out_dir, '%s%s' % (os.path.basename(fout), ext))

        ctc = CTCompiler(symbols, fname, fout)
        ctc.start()
