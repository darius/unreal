"""
Constraints are equations between expressions. We represent one as
an expression, with '=0' implicit. We try to reduce each expression to
a linear combination of variables plus a constant, then eliminate one
of the variables, and continue.
"""

from __future__ import division
import cmath, math, sys

from structs import Struct

def make_constant(value):
    return Combo({const_term: value})

def make_variable(name):
    return Combo({Variable(name): 1})

def Equate(defaulty, expr1, expr2):
    return defaulty, expr1 - expr2

def solve(equations):
    consistent_so_far = True
    while equations:
        pending = []
        for defaulty, expr in equations:
            try:
                combo = expr.evaluate()
            except Nonlinear:
                pending.append((defaulty, expr))
            else:
                terms = combo.expand()
                if varies(terms):
                    eliminate_a_variable(terms)
                elif defaulty or zeroish(constant(terms)):
                    # The equation was either only a default (so we
                    # don't care if it's inconsistent) or it reduced
                    # to an uninformative 0=0: drop it.
                    pass 
                else:
                    consistent_so_far = False
                    print 'Inconsistent', combo
        if pending == equations:
            return False # Made no progress on remaining equations; give up.
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
        terms = combo.expand()
        if varies(terms):
            raise NotFixed(self)
        return constant(terms)
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
        terms1 = combo1.expand()
        terms2 = combo2.expand()
        if varies(terms1) and varies(terms2):
            raise Nonlinear()
        if varies(terms1): return combo1.scale(constant(terms2))
        else:              return combo2.scale(constant(terms1))

class Div(Struct('arg1 arg2', supertype=(Expr,))):
    def evaluate(self):
        combo1 = self.arg1.evaluate()
        combo2 = self.arg2.evaluate()
        terms2 = combo2.expand()
        if varies(terms2):
            raise Nonlinear()
        return combo1.scale(1 / constant(terms2))

class NonlinearFn(Struct('fn arg', supertype=(Expr,))):
    def evaluate(self):
        combo = self.arg.evaluate()
        terms = combo.expand()
        if varies(terms):
            raise Nonlinear()
        value = constant(terms)
        assert isinstance(value, (int, float, complex)), 'type: %s, value: %r' % (type(value), value)
        return make_constant(self.fn(value))

def cis(angle):
    assert zeroish(angle.imag)   # XXX complain some other way
    return cmath.exp(1j * math.radians(angle.real))

def unit(value):
    assert not zeroish(value)
    return value / abs(value)

def Abs(arg):  return NonlinearFn(abs, arg)
def Cis(arg):  return NonlinearFn(cis, arg)
def Unit(arg): return NonlinearFn(unit, arg)

class Combo(Expr):
    def __init__(self, terms):
        self.terms = {v: c for v,c in terms.iteritems() if not zeroish(c)}
    def evaluate(self):
        return self
    def expand(self):
        self.terms = self.scale(1).terms
        return self.terms
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
    def __repr__(self):
        return '(%r)' % self.terms

def varies(terms):
    return any(v is not const_term for v in terms)

def constant(terms):
    assert not varies(terms)
    return terms.get(const_term, 0)

def eliminate_a_variable(terms):
    ve, ce = max(((vi, ci)
                  for vi,ci in terms.iteritems()
                  if vi is not const_term),
                 key=lambda (vi,ci): abs(ci))
    ve.become(Combo({v: -c/ce
                     for v,c in terms.iteritems()
                     if v is not ve}))

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
