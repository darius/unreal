"""
Interpreter for IDEAL abstract syntax.
"""

from itertools import count
import operator

from structs import Struct
import linear_constraints as LC
import linear_equations as LE

class Environment(Struct('types drawers frames')):
    def spawn(self, frame):
        return Environment(self.types, self.drawers, self.frames + (frame,))

def run(defs):
    env = Environment({box.name: box for box in defs}, [], ({},))
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
            lin_exp = LE.LinExp(0, [(LC.Variable(name), 1)])
            env.frames[-1][name] = LC.Number(lin_exp)

class Conn(Struct('points')):
    def run(self, env):
        env.drawers.append((self, env))
    def draw(self, env):
        print 'conn', [p.evaluate(env).get_value() for p in self.points]

class Text(Struct('justified string where')):
    def run(self, env):
        env.drawers.append((self, env))
    def draw(self, env):
        at = self.where.evaluate(env).get_value()
        print 'text', self.justified, 'at', at, repr(self.string)

class Put(Struct('opt_name box')):
    def run(self, env):
        name = self.opt_name or gensym()  # (The default name's just for debugging.)
        subenv = env.spawn({})
        env.types[self.box.name].make(subenv)
        env.frames[-1][name] = subenv.frames[-1]
        for stmt in self.box.stmts:
            stmt.run(subenv)

class Default(Struct('parts')): pass # XXX

class Equate(Struct('parts')):
    def run(self, env):
        reduce(LC.equate, (expr.evaluate(env) for expr in self.parts))

class Ref(Struct('name')):
    def evaluate(self, env):
        for frame in reversed(env.frames):
            try:
                return frame[self.name]
            except KeyError:
                pass
        raise KeyError("Unbound name", self.name)

class Of(Struct('ref field')):
    def evaluate(self, env):
        return self.ref.evaluate(env)[self.field]

class Literal(Struct('value')):
    def evaluate(self, env):
        return LC.Number(LE.LinExp(self.value, ()))

class BinaryOp(Struct('arg1 arg2')):
    def evaluate(self, env):
        return self.operate(self.arg1.evaluate(env),
                            self.arg2.evaluate(env))

class Add(BinaryOp): operate = operator.add
class Sub(BinaryOp): operate = operator.sub
class Mul(BinaryOp): operate = operator.mul
class Div(BinaryOp): operate = operator.truediv

class Interpolate(Struct('alpha zero one')):
    def evaluate(self, env):
        alpha = self.alpha.evaluate(env)
        zero = self.zero.evaluate(env)
        one = self.one.evaluate(env)
        return zero + (one - zero) * alpha;
