"""
Abstract syntax for IDEAL.
"""

from structs import Struct

Box = Struct('box', 'name stmts')

def Decl(names):
    return 'decl', names

def Conn(points):
    return 'conn', points

def Equate(parts):  return '=', parts
def Default(parts): return '~', parts

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
