"""
Abstract syntax for IDEAL.
"""

from itertools import count
import operator

from structs import Struct
import linear_constraints as LC

class Environment(Struct('types drawers things')):
    def spawn(self, things):
        return Environment(self.types, self.drawers, things)

def start(defs):
    env = Environment({box.name: box for box in defs}, [], {})
    env.types['main'].make(env)
    for drawer, subenv in env.drawers:
        drawer.draw(subenv)

counter = count(1)

def gensym():
    return 'g#%d' % next(counter)

class Box(Struct('name stmts')):
    def make(self, env):
        for stmt in self.stmts:
            stmt.run(env)

class Decl(Struct('names')):
    def run(self, env):
        for name in self.names:
            env.things[name] = LC.Number()

class Conn(Struct('points')):
    def run(self, env):
        env.drawers.append((self, env))
    def draw(self, env):
        print 'conn', [p.evaluate(env).get_value() for p in self.points]

class Put(Struct('opt_name box')):
    def run(self, env):
        name = self.opt_name or gensym()
        subenv = env.spawn({}) # XXX need current env too, for equate
        env.things[name] = env.types[self.box.name].make(subenv)
        for stmt in self.box.stmts:
            stmt.run(subenv)

class Default(Struct('parts')): pass # XXX

class Equate(Struct('parts')):
    def run(self, env):
        lhs = self.parts[0]
        for rhs in self.parts[1:]:
            LC.equate(lhs.evaluate(env), rhs.evaluate(env))
            lhs = rhs

class Ref(Struct('name')):
    def evaluate(self, env):
        return env.things[self.name]

class Of(Struct('ref field')):
    def evaluate(self, env):
        return self.ref.evaluate(env)[self.field]

class Literal(Struct('value')):
    def evaluate(self, env):
        return self.value

class BinaryOp(Struct('arg1 arg2')):
    def evaluate(self, env):
        return self.operate(self.arg1.evaluate(env),
                            self.arg2.evaluate(env))

class Add(BinaryOp): operate = operator.add
class Sub(BinaryOp): operate = operator.sub
class Mul(BinaryOp): operate = operator.mul
class Div(BinaryOp): operate = operator.truediv
