# C (or possibly C++) code generation for Rhea

import helper
import ast
import parser

c = helper.CFile('tmp.c')
repl = False

def line(number, source_file):
	c.line(number, source_file)

def gen_init(is_repl):
	global c
	global repl
	repl = is_repl
	c = helper.CFile('tmp.c')
	if repl:
		c['#include "repl.h"']
	c['#include "runtime.h"']

def gen_assign(name, value):
	c(name + ' = ')
	value.eval()
	
def mangle(name):
	fun_name = name.replace('.', '$p')
	fun_name = fun_name.replace('*', '$m')
	fun_name = fun_name.replace('/', '$d')
	fun_name = fun_name.replace('+', '$a')
	fun_name = fun_name.replace('-', '$s')
#	fun_name = fun_name.replace('*', '$t')
	return fun_name
	
def gen_lookup(name):
	c(name)
	
def gen_define(name, value):
	if isinstance(value, ast.Function):
		fun_name = mangle(name)
		if(name[0] == '$'):
			fun_name = fun_name[1:]
		c[str(value.return_type) + ' ' + fun_name + ' (' + str(value.arguments) + ') ']
		value.eval()
	else:
		c(str(value.type) + ' ' + name + ' = ')
		value.eval()
		
def gen_literal(value):
	c(value)
		
def gen_block(body):
	with c.block(''):
		for i in body:
			i.eval()
			gen_end()
	
def gen_call(subject, name, arguments):
	nsubject = subject
	instance = False
	isubject = None
	if not subject[0].isupper():
		if(parser.isnumber(nsubject)):
			try:
				int(subject)
				isubject = ast.LiteralInt(subject)
				nsubject = 'Int'
			except:
				nsubject = 'Float'
				isubject = ast.LiteralFloat(subject)
		else:
			nsubject = parser.index[nsubject].type
			isubject = parser.index[subject]
		instance = True
	fn_name = ''
	for i in arguments:
		fn_name += i.type + '$_'
	if instance:
		fn_name += mangle(nsubject) + '$i' + mangle(name)
	else:
		fn_name += mangle(nsubject) + '$x' + mangle(name)
	if repl:
		c('printf("%g", ')
	c(fn_name + ' (')
	if not instance:
		try:
			arguments[0].eval()
		except:
			pass
		for i in arguments[1:]:
			c(', ')
			i.eval()
	else:
		isubject.eval()
		for i in arguments:
			c(', ')
			i.eval()
	c(')')
	if repl:
		c(')')
def gen_end():
	c[';']
	
def gen_close():
	c.close()