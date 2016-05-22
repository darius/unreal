"""
Abstract syntax for IDEAL.
"""

from structs import Struct

Box = Struct('box', 'name stmts')

Decl = Struct('decl', 'names')

Conn = Struct('conn', 'points')
Put = Struct('put', 'opt_name box')

Equate = Struct('=', 'parts')
Default = Struct('~', 'parts')

Add = Struct('+', 'arg1 arg2')
Sub = Struct('-', 'arg1 arg2')
Mul = Struct('*', 'arg1 arg2')
Div = Struct('/', 'arg1 arg2')

Ref = Struct('ref', 'name')
Of = Struct('of', 'ref field')

Literal = Struct('literal', 'value')
