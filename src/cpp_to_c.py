#!/usr/bin/env python
import argparse
from lex import lex
from sym import SymbolTable

class CTCompiler:
    def __init__(self, fname):
        self.lexy = lex(fname) # Lexical Analyzer

    def parse(self):
        token = self.lexy.next()
        print(token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parses a C++ source file and converts it to human readable C code")
    parser.add_argument("--input-files", help="c++ input files, parsed first to last", nargs='+', required=True)

    args = parser.parse_args()

    for fname in args.input_files:
        ctc = CTCompiler(fname)
        ctc.parse()
