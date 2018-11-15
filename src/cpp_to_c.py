#!/usr/bin/env python
import argparse, os.path
from lex import lex
from sym import SymbolTable

class CTCompiler:
    def __init__(self, symbols, fname, fout):
        self.symbols = symbols
        self.lexy = lex(fname) # Lexical Analyzer
        self.out = open(fout, 'w')

    def __compiler_directive(self):
        token = self.lexy.next()
        if token.value() in ['ifndef', 'ifdef']:
            self.out.write('#%s ' % token.value())
            token = self.lexy.next()
            if not token.type() == 'identifier':
                raise Exception('Line %d: Expected identifier, found %s' % (self.lexy.line_number, str(token)))
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
            if not token.type() == 'identifier':
                raise Exception('Line %d: Expected identifier, found %s' % (self.lexy.line_number, str(token)))
            self.out.write('%s\n' % token.value())
            # TODO: handle defining a value or statement, etc
        elif token.value() == 'include':
            token = self.lexy.next()
            if token.type() == 'string':
                self.out.write('#include %s\n' % token.value())
        else:
            raise Exception('Line %d: %s' % (self.lexy.line_number, str(token)))

    def parse(self):
        while self.lexy.peek() != None:
            token = self.lexy.next()
            if token.type() == 'symbol' and token.value() == '#':
                self.__compiler_directive()
            else:
                break
        raise Exception('Line %d: %s' % (self.lexy.line_number, str(token)))

    def __del__(self):
        self.out.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses a C++ source file and converts it to human readable C code")
    parser.add_argument("--input-files", help="c++ input files, parsed first to last", nargs='+', required=True)
    parser.add_argument("--out-dir", help="Output directory", required=True)

    args = parser.parse_args()

    symbols = SymbolTable()

    for fname in args.input_files:
        fout, ext = os.path.splitext(fname)
        if ext != '.h':
            ext = '.c'
        fout = os.path.join(args.out_dir, '%s%s' % (os.path.basename(fout), ext))

        ctc = CTCompiler(symbols, fname, fout)
        ctc.parse()
