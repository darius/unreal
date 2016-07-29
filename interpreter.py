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
    types = {}
    for box in defs:
        define(types, box.name, box)
    root_env = Environment(types, [], [], [], '', ({},))

    # First create all the variables...
    types['main'].make(root_env)
    # ...then create the constraints. We waited because an equation
    # might use forward refs.
    for constrainer, env in root_env.constrainers:
        constrainer.constrain(env)

    # Take the constraints in reverse order because, e.g., in `put foo
    # { x=y; }`, the `x=y` gets appended after foo's own equations,
    # but is considered more specific. Try to resolve the more
    # specific constraints first.
    solver.solve(root_env.constraints[::-1])

    renderer.begin()
    for drawer, env in root_env.drawers:
        drawer.draw(env)
    renderer.end()

def define(dict_, name, value):
    assert name not in dict_, "Multiple definition: %s" % name
    dict_[name] = value

class Box(Struct('name stmts')):
    def make(self, env):
        for stmt in self.stmts:
            stmt.build(env)
    def prepend(self, stmts):
        return Box(self.name, stmts + self.stmts)

class Decl(Struct('names')):
    def build(self, env):
        for name in self.names:
            define(env.frames[-1], name, solver.make_variable(env.prefix + name))

class Path(Struct('points')):
    def build(self, env):
        env.add_drawer(self)
    def draw(self, env):
        points = [p.evaluate(env).get_value() for p in self.points]
        self.render(map(to_coords, points))

class Conn(Path):   render = staticmethod(renderer.polyline)
class Spline(Path): render = staticmethod(renderer.spline)

class Pen(Struct('points count box start end')):
    # XXX maybe make this (except for `points`) all an optional field in Conn
    def build(self, env):
        # XXX Should we require len(points) to be 2?
        #     Or work over each pair of successive points?
        #     It looks like real IDEAL requires at least 2 but ignores any left over.
        assert len(self.points) == 2, "'conn using' must connect exactly two points"
        zero, one = self.points

        # XXX The true semantics is problematic for us in requiring
        #  count to be evaluated to a number before we can instantiate
        #  the boxes -- so far we've never interleaved creating
        #  objects with solving constraints. I think we could do this
        #  without a massive overhaul, but I'm not gonna try
        #  tonight. Instead, require `count` to be a literal.
        assert isinstance(self.count, Literal), "XXX crude implementation restriction"
        assert self.count.value.imag == 0
        n = self.count.value.real
        assert n == int(n)
        n = int(n)
        ps = [Relatively(Div(Literal(i), self.count), zero, one)
              for i in range(n + 1)]
        for a_exp, b_exp in zip(ps[:-1], ps[1:]):
            segment = Put(None, self.box.prepend((Equate((self.start, a_exp)),
                                                  Equate((self.end, b_exp)))))
            segment.build(env)

class Compass(Struct('center boundary_point')):
    def build(self, env):
        env.add_drawer(self)
    def draw(self, env):
        points = [p.evaluate(env).get_value() for p in (self.center,
                                                        self.boundary_point)]
        renderer.circle(*map(to_coords, points))

class Text(Struct('justified string where')):
    def build(self, env):
        env.add_drawer(self)
    def draw(self, env):
        at = self.where.evaluate(env).get_value()
        renderer.text(self.string, self.justified, to_coords(at))

def to_coords(point):
    return point.real, point.imag

class Put(Struct('opt_name box')):
    def build(self, env):
        name = self.opt_name or gensym()  # (The default name's just for debugging.)
        subenv = env.spawn(name)
        env.types[self.box.name].make(subenv)
        define(env.frames[-1], name, subenv.frames[-1])
        self.box.make(subenv)

def gensym():
    return '#%d' % next(counter)
counter = count(1)

class Equate(Struct('parts')):
    defaulty = False
    def build(self, env):
        env.add_constrainer(self)
    def constrain(self, env):
        def eq(lhs, rhs):
            env.constraints.append(solver.Equate(self.defaulty, lhs, rhs))
            return rhs
        reduce(eq, (expr.evaluate(env) for expr in self.parts))

class Default(Equate):
    defaulty = True

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

def Negate(expr): return Mul(Literal(-1+0j), expr)

class CallPrim(Struct('fn arg')):
    def evaluate(self, env):
        return self.fn(self.arg.evaluate(env))

def Abs():  return solver.Abs
def Cis():  return solver.Cis
def Unit(): return solver.Unit

class Relatively(Struct('coord zero one')):
    """Linear interpolate/extrapolate, i.e. `coord` in the coordinate
    system that places 0 at `zero` and 1 at `one`."""
    def evaluate(self, env):
        coord = self.coord.evaluate(env)
        zero = self.zero.evaluate(env)
        one = self.one.evaluate(env)
        return zero + (one - zero) * coord;
