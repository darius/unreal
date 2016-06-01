"""
Interpreter for IDEAL abstract syntax.
"""

from itertools import count
import operator

from structs import Struct
import renderer, solver

class Environment(Struct('types constrainers constraints drawers prefix frames')):
    def spawn(self, name):
        return Environment(self.types, self.constrainers, self.constraints, self.drawers,
                           self.prefix + name + '.', self.frames + ({},))
    def add_constrainer(self, constrainer):
        self.constrainers.append((constrainer, self))
    def add_drawer(self, drawer):
        self.drawers.append((drawer, self))

def run(defs):
    root_env = Environment({box.name: box for box in defs},
                           [], [], [], '', ({},))
    # First create all the variables...
    root_env.types['main'].make(root_env)

    # ...then create the constraints. We waited because an equation
    # might use forward refs.
    for constrainer, env in root_env.constrainers:
        constrainer.constrain(env)

    solver.solve(root_env.constraints)

    renderer.begin()
    for drawer, env in root_env.drawers:
        drawer.draw(env)
    renderer.end()

class Box(Struct('name stmts')):
    def make(self, env):
        for stmt in self.stmts:
            stmt.build(env)

class Decl(Struct('names')):
    def build(self, env):
        for name in self.names:
            env.frames[-1][name] = solver.make_variable(env.prefix + name)

class Conn(Struct('points')):
    def build(self, env):
        env.add_drawer(self)
    def draw(self, env):
        points = [p.evaluate(env).get_value() for p in self.points]
        renderer.polyline(map(to_coords, points))

class Text(Struct('justified string where')):
    def build(self, env):
        env.add_drawer(self)
    def draw(self, env):
        at = self.where.evaluate(env).get_value()
        renderer.text(self.string, self.justified or 'center', to_coords(at))

def to_coords(point):
    return point.real, point.imag

class Put(Struct('opt_name box')):
    def build(self, env):
        name = self.opt_name or gensym()  # (The default name's just for debugging.)
        subenv = env.spawn(name)
        env.types[self.box.name].make(subenv)
        env.frames[-1][name] = subenv.frames[-1]
        self.box.make(subenv)

def gensym():
    return '#%d' % next(counter)
counter = count(1)

class Default(Struct('parts')):
    def build(self, env):
        assert False, "XXX unimplemented"

class Equate(Struct('parts')):
    def build(self, env):
        env.add_constrainer(self)
    def constrain(self, env):
        def eq(lhs, rhs):
            env.constraints.append(solver.equate(lhs, rhs))
            return rhs
        reduce(eq, (expr.evaluate(env) for expr in self.parts))

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
        return solver.make_constant(self.value)

class BinaryOp(Struct('arg1 arg2')):
    def evaluate(self, env):
        return self.operate(self.arg1.evaluate(env),
                            self.arg2.evaluate(env))

class Add(BinaryOp): operate = operator.add
class Sub(BinaryOp): operate = operator.sub
class Mul(BinaryOp): operate = operator.mul
class Div(BinaryOp): operate = operator.truediv

def Negate(expr): return Sub(Literal(0j), expr)

class Relatively(Struct('coord zero one')):
    """Linear interpolate/extrapolate, i.e. `coord` in the coordinate
    system that places 0 at `zero` and 1 at `one`."""
    def evaluate(self, env):
        coord = self.coord.evaluate(env)
        zero = self.zero.evaluate(env)
        one = self.one.evaluate(env)
        return zero + (one - zero) * coord;
