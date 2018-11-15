#!/usr/bin/env python
import sys

def MessageHandler(message):
    sys.stderr.write(message + '\n')
    exit(1)

class SymbolTable:
	def __init__(self):
		self.symbol_table = {}
		self.scope = 'global.'
		self.sym = self.genSym()

	def table(self): # For debug
		return self.symbol_table

	def descend_scope(self, id):
		self.scope += id + '.'

	def ascend_scope(self, scope=None):
		self.scope = self.scope[0:self.scope[0:-1].rindex('.')+1]

	def current_scope(self):
		return self.scope

	def insert(self, name, kind, data=None, scope=None):
		if not scope:
			scope = self.scope
		symid = kind[0].upper() + self.sym.next().zfill(6)
		if not name:
			name = symid
		self.symbol_table[symid] = [scope, name, kind, data]
		return symid

	def get_data(self, symid):
		return self.symbol_table[symid][3]

	def add_data(self, symid, key, value):
		if self.symbol_table[symid][3]:
			self.symbol_table[symid][3][key] = value
		else:
			self.symbol_table[symid][3] = {}
			self.symbol_table[symid][3][key] = value

	def get(self, symid):
		if type(symid) == list:
			items = []
			for item in symid:
				items.append(self.get(item))
			itemstr = ', '.join([item[2] + ' ' + item[1] for item in items])
			MessageHandler('Unable to resolve difference between items; %s.' % itemstr)
		if symid != None and symid in self.symbol_table:
			return self.symbol_table[symid]
		else:
			return [None, None, None, None]

	def search(self, value=None, scope=None, kind=None):
		keys = []
		this_type = None
		if scope and not kind:
			kind_id = symboltable.search(value, scope, 'param')
			if not kind_id:
				kind_id = symboltable.search(value, scope, 'lvar')
			if not kind_id:
				kind_id = symboltable.search(value, scope, 'method')
			if not kind_id:
				kind_id = symboltable.search(value, scope, 'ivar')
			if kind_id:
				kind = symboltable.get(kind_id)[2]
		if kind in ['method', 'ivar'] and scope:
			this = None
			try:
				this = symboltable.get(symboltable.search('this', scope + value + '.', 'param'))
			except:
				pass
			if not this or this == [None, None, None, None]: # The search fails if value is a method instead of a variable
				this = symboltable.get(symboltable.search('this', scope, 'param'))
			if this != [None, None, None, None] and this[0] != 'global.main.':
				this_type = symboltable.get(symboltable.search(this[3]['type'], 'global.', 'class'))
		for key in self.symbol_table:
			in_this_scope = None
			if this_type:
				in_this_scope = self.in_scope(self.symbol_table[key][0], this_type[0] + this_type[1] + '.')
			if (value == None or self.symbol_table[key][1] == value) and (kind == None or self.symbol_table[key][2] == kind) and (scope == None or self.in_scope(self.symbol_table[key][0], scope) or in_this_scope):
				keys.append(key)
		if len(keys) == 1:
			return keys[0]
		elif len(keys) == 0:
			return None
		else:
			return keys

	def in_scope(self, item_scope, check_scope=None):
		if not check_scope:
			check_scope = self.scope
		# Is item in check_scope?
		if item_scope == 'global.' or item_scope == check_scope:
			return True
		else:
			return False


	def genSym(self):
		count = 0
		while 1:
			yield str(count)
			count += 1

	def lblGen(self, lbl):
		zeros = 7 - len(lbl)
		return lbl.upper() + self.sym.next().zfill(zeros)

