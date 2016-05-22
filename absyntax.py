"""
Abstract syntax for IDEAL.
"""

def Box(name, *stmts):
    return 'box', name, stmts

def Decl(*names):
    return 'decl', names

def Equation(lhs, *parts):
    return 'equation', lhs, parts

def Equate():  return '='
def Default(): return '~'

def Conn(*points):
    return 'conn', points

def Put(opt_name, box):
    return 'put', opt_name, box

def Add(arg1, arg2):
    return '+', arg1, arg2

def Sub(arg1, arg2):
    return '-', arg1, arg2

def Mul(arg1, arg2):
    return '*', arg1, arg2

def Div(arg1, arg2):
    return '/', arg1, arg2

def Ref(name):
    return 'ref', name

def Of(ref, field):
    return 'of', ref, field

def Literal(n):
    return 'literal', n
