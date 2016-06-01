"""
Constraints are equations between expressions. We represent one as
an expression, with '=0' implicit. We try to reduce each expression to
a linear combination of variables plus a constant, then eliminate one
of the variables, and continue.
"""

from __future__ import division
import sys

from structs import Struct

def make_constant(value):
    return Combo({const_term: value})

def make_variable(name):
    return Combo({Variable(name): 1})

def equate(expr1, expr2):
    return expr1 - expr2

def solve(equations):
    consistent_so_far = True
    while equations:
        pending = []
        for expr in equations:
            try:
                combo = expr.evaluate()
            except Nonlinear:
                pending.append(expr)
            else:
                if combo.varies():
                    combo.pivot() # XXX name?
                elif zeroish(combo.constant()):
                    pass # A consistent but useless equation: drop it.
                else:
                    consistent_so_far = False
                    print 'Inconsistent', combo
        if pending == equations:
            return False
        equations = pending
    return consistent_so_far # N.B. might still be underconstrained

class Nonlinear(Exception):
    "An expression did not evaluate this time to a linear combo."

class Expr(object):
    def evaluate(self):
        abstract
    def get_value(self):
        try:
            combo = self.evaluate()
        except Nonlinear:
            raise NotFixed(self)
        return combo.constant()
    def __add__(self, other):     return Combine(self, 1, other)
    def __sub__(self, other):     return Combine(self, -1, other)
    def __mul__(self, other):     return Mul(self, other)
    def __truediv__(self, other): return Div(self, other)

class Combine(Struct('arg1 coeff arg2', supertype=(Expr,))):
    def evaluate(self):
        return self.arg1.evaluate().combine(self.coeff,
                                            self.arg2.evaluate())

class Mul(Struct('arg1 arg2', supertype=(Expr,))):
    def evaluate(self):
        combo1 = self.arg1.evaluate()
        combo2 = self.arg2.evaluate()
        if combo1.varies() and combo2.varies():
            raise Nonlinear()
        if combo1.varies(): return combo1.scale(combo2.constant())
        else:               return combo2.scale(combo1.constant())

class Div(Struct('arg1 arg2', supertype=(Expr,))):
    def evaluate(self):
        combo1 = self.arg1.evaluate()
        combo2 = self.arg2.evaluate()
        if combo2.varies():
            raise Nonlinear()
        return combo1.scale(1 / combo2.constant())

class Combo(Expr):
    def __init__(self, terms):
        self.terms = {v: c for v,c in terms.iteritems() if not zeroish(c)}
    def evaluate(self):
        return self
    def varies(self): # XXX this varies()/constant()/pivot() business duplicates work
        terms = self.scale(1).terms
        return any(v is not const_term for v in terms)
    def constant(self):
        terms = self.scale(1).terms
        if any(v is not const_term for v in terms):
            raise NotFixed(self)
        return terms.get(const_term, 0)
    def pivot(self):
        terms = self.scale(1).terms
        assert any(v is not const_term for v in terms)
        ve, ce = max(((vi, ci)
                      for vi,ci in terms.iteritems()
                      if vi is not const_term),
                     key=lambda (vi, ci): abs(ci))
        ve.become(Combo({v: -c/ce
                         for v,c in terms.iteritems()
                         if v is not ve}))
        # XXX Combo() does an unnecessary sweep of its argument
    def scale(self, c):
        accum = {}
        self.add_into(accum, c)
        return Combo(accum)
    def combine(self, c, other):
        accum = {}
        self.add_into(accum, 1)
        other.add_into(accum, c)
        return Combo(accum)
    def add_into(self, accum, c):
        for v, coeff in self.terms.iteritems():
            v.add_into(accum, c * coeff)

class NotFixed(Exception):
    "An expression could not be reduced to a constant value."

class Variable(object):
    def __init__(self, name):
        self.name = name
        self.combo = None
    def become(self, combo):
        assert self.combo is None
        self.combo = combo
    def add_into(self, accum, c):
        if self.combo is None:
            accum[self] = accum.get(self, 0) + c
        else:
            self.combo.add_into(accum, c)
    def get_value(self):
        try:
            if self.combo is None: raise NotFixed(self)
            return self.combo.constant()
        except NotFixed:
            print 'get_value of unfixed variable', self
            return 1            # (arbitrary)
    def __repr__(self):
        return self.name

const_term = Variable('<const>') # A fake variable for a combo's constant term.

def zeroish(u):
    "Is float u approximately zero?"
    return abs(u) <= epsilon

# XXX This is a dumb random pick for this value.
# Of course the goal is to get reasonable answers in the face
# of floating-point rounding. I started with exact equality tests
# in the places where zeroish() is now called, and the solver
# occasionally failed to find a solution. This did not even happen
# reproducibly, I'm guessing because the operations performed
# depend on the order of elements in hashtables, which varies
# from run to run. Let's see if the gremlins go away.
# (Or maybe the solver's just incorrect. I should review it.)
epsilon = sys.float_info.epsilon * 5
