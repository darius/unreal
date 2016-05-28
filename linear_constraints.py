"""
A linear constraint requires a linear combination of variables to = 0.
We represent the constraint as a linear expression, with the '=0' implicit.
"""

import constraints
import linear_equations

class Variable(constraints.Variable):
    def __init__(self, name):
        constraints.Variable.__init__(self)
        self.name = name
    def __str__(self):
        return '<Variable %s>' % self.name

class Constraint(constraints.Constraint):
    def __init__(self, lin_exp):
        self.lin_exp = lin_exp
        for variable in lin_exp.variables():
            variable.constrain(self)
    def get_variables(self):
        return self.lin_exp.variables()
    def solve(self):
        eqns = [c.lin_exp for c in self.get_connected_constraints()]
        for variable, value in linear_equations.solve_equations(eqns).items():
            variable.assign(value)

def equate(expr1, expr2):
    zero(expr1 - expr2)

def zero(expr):
    Constraint(expr.lin_exp)

class Number(object):
    def __init__(self, lin_exp):
        self.lin_exp = lin_exp
    def get_value(self):
        e = self.lin_exp
        return e.constant + sum(c * v.get_value() for v,c in e.terms.items())
    def as_scalar(self):
        assert self.lin_exp.is_constant(), 'nope %r' % self.lin_exp
        return self.lin_exp.constant
    def combine(self, c, e2, c2):
        return Number(self.lin_exp.combine(c, e2.lin_exp, c2))
    def scale(self, c):
        return Number(self.lin_exp.scale(c))
    def __str__(self):
        return '<Number %r>' % self.lin_exp
    def __neg__(self):            return self.scale(-1)
    def __add__(self, other):     return self.combine(1, other, 1)
    def __sub__(self, other):     return self.combine(1, other, -1)
    def __truediv__(self, other): return self.scale(1. / other.as_scalar())
    def __mul__(self, other):
        if self.lin_exp.is_constant():
            return other.scale(self.lin_exp.constant)
        else:
            return self.scale(other.as_scalar())
