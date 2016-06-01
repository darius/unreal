"""
A linear constraint requires a linear combination of variables to = 0.
We represent the constraint as a linear expression, with the '=0' implicit.
"""

from __future__ import division
import sys

def make_constant(value):
    return LinExp(value, ())

def make_variable(name):
    return LinExp(0, [(Variable(name), 1)])

def equate(expr1, expr2):
    return expr1 - expr2

def solve(eqns):
    for variable, value in solve_equations(eqns).items():
        variable.assign(value)

class Variable(object):
    def __init__(self, name):
        self.constraints = set()
        self.name = name
        self.value = None
    def get_value(self):
        assert self.value is not None, "Unsolved: %r" % self
        return self.value
    def assign(self, value):
        assert self.value is None or self.value == value
        self.value = value
    def __repr__(self):
        return self.name

class LinExp(object):
    "A linear expression in some variables."
    def __init__(self, constant, terms):
        self.constant = constant
        self.terms = {var: val for var, val in terms if val != 0} # XXX use zeroish?

    def get_value(self):
        return self.constant + sum(c * v.get_value()
                                   for v,c in self.terms.items())
    def as_scalar(self):
        assert self.is_constant(), 'nope %r' % self
        return self.constant
    def __add__(self, other):     return self.combine(1, other, 1)
    def __sub__(self, other):     return self.combine(1, other, -1)
    def __truediv__(self, other): return self.scale(1 / other.as_scalar())
    def __mul__(self, other):
        if self.is_constant():
            return other.scale(self.constant)
        else:
            return self.scale(other.as_scalar())

    def combine(self, c, e2, c2):
        return LinExp(c * self.constant + c2 * e2.constant,
                      ((var, (c * self.coefficient(var)
                              + c2 * e2.coefficient(var)))
                       for var in self.variables() | e2.variables()))
    def scale(self, c):
        return self.combine(c, zero, 0)
    def coefficient(self, variable):
        return self.terms.get(variable, 0)
    def variables(self):
        return set(self.terms.iterkeys())
    def a_variable(self):
        return next(self.terms.iterkeys(), None)
    def is_constant(self):
        return not self.terms
    # The remaining methods treat LinExps as equations implicitly ==
    # 0. So one is inconsistent if it's something like 5==0, it
    # defines a variable if it's something like 1*x-3==0 (with just
    # one variable), and so on.
    def is_inconsistent(self):
        return self.is_constant() and not zeroish(self.constant)
    def is_tautology(self):
        return self.is_constant() and zeroish(self.constant)
    def defines_var(self):
        vars = self.terms.keys()
        return (vars if len(vars) == 1 and zeroish(1 - self.coefficient(vars[0]))
                else ())
    def substitute_for(self, var, eq):
        """Return an equivalent equation with var eliminated by
        resolving against eq (which must have a term for var)."""
        # self - (self[var]/eq[var]) * eq
        c = -self.coefficient(var) / eq.coefficient(var)
        return self.combine(1, eq, c)
    def normalize(self):
        """Return an equivalent equation with a variable's coefficient
        rescaled to 1."""
        var = self.a_variable()
        return self.scale(1 / self.coefficient(var))
    def __repr__(self):
        items = sorted(self.terms.items())
        if self.constant:
            items = [('', self.constant)] + items
        if not items: return '(0 = 0)'
        def format((var, c)):
            if var == '': return '%s' % c
            if c == 1:    return '%s' % (var,)
            if c == -1:   return '-%s' % (var,)
            return '%s%s' % (c, var)
        def combiner(pair):      # XXX rename
            f = format(pair)
            return ' - ' + f[1:] if f.startswith('-') else ' + ' + f
        return '(0 = %s%s)' % (format(items[0]),
                               ''.join(map(combiner, items[1:])))

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

zero = LinExp(0, ())

def solve_equations(eqs):
    """Return a dict mapping variables to values, for those variables
    eqs constrains to a value. An eq is a LinExp implicitly equated to
    0."""
    consistent, eqs = reduce_equations(eqs)
    if not consistent:
        return {}               # or None, or what?
    return {var: -le.constant
            for le in eqs
            for var in le.defines_var()}

def reduce_equations(eqs):
    """Try to reduce eqs to an equivalent system with each variable
    defined by a single equation. The first result is False if the
    eqs are inconsistent. The result may still be underconstrained."""
    for i, eqi in enumerate(eqs):
        var = eqi.a_variable()
        if not var: continue
        for j, eqj in enumerate(eqs):
            if i == j: continue
            eqs[j] = eqj.substitute_for(var, eqi)
            if eqs[j].is_inconsistent():
                return False, eqs
    return True, [eq.normalize() for eq in eqs if not eq.is_tautology()]
