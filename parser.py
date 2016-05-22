"""
Parse (our subset of) IDEAL.
"""

from parson import Grammar, join
from absyntax import (Box, Decl, Equation, Equate, Default, Conn, Put,
                      Add, Sub, Mul, Div, Ref, Of, Literal,)

def Maybe(*args):
    assert len(args) <= 1
    return args[0] if args else None

grammar = Grammar(r"""
program:   _ box* !/./.

box:       name '{'_ stmt* '}'_                    :Box.

stmt:      /var\b/_ name (','_ name)* ';'_         :Decl
         | /conn\b/_ expr (/to\b/_ expr)+ ';'_     :Conn
         | /put\b/_ [(name ':'_)? :Maybe] box ';'_ :Put
         | expr (equ expr)+ ';'_                   :Equation.

equ:       '='_ :Equate
         | '~'_ :Default.

expr:      term ( '+'_ term :Add
                | '-'_ term :Sub )*.
term:      atom ( '*'_ atom :Mul
                | '/'_ atom :Div )*.

atom:      '('_ number ','_ number ')'_            :complex :Literal
         | number                                  :complex :Literal
         | '('_ expr ')'_
         | name :Ref ('.'_ name :Of)*.

number:    int (frac exp? | exp)? _                :join :float.
int      = /(-?0)/ !/\d/
         | /(-?[1-9]\d*)/.
frac     = /([.]\d+)/.
exp      = /([eE][+-]?\d+)/.

name     = /([A-Za-z_][A-Za-z_0-9]*)/ _.

_        = (/\s+/ | comment)*.
comment  = '/*' (!'*/' /.|\n/)* '*/'.
""")
parser = grammar(**globals())


eg = """
rect {
    var ne, nw, se, sw, wd, ht;
    nw = sw + (0,1)*ht;
    ne = nw + wd;
    se = sw + wd;
    conn ne to nw to sw to se to ne;
}
triangle {
    var z1, z2, z3;
    conn z1 to z2 to z3 to z1;
}
pythagoras {
    put first: rect {
        sw = 0;
        ht = wd = 1;
    };
    put next: rect {
        nw = first.se;
        ht = wd = first.ht;
    };
    put last: rect {
        sw = first.ne;
        se = next.ne;
        ht = wd;
    };
}
main {
    /* Giving the center of a side,
       a corner, and another dimension. */
    put rect {
        (nw+sw)/2 = (0,1);
        nw = (0,2);
        wd = 1;
    };
}
"""
## from pprint import pprint
## for a in parser.program(eg): pprint(a)
#. ('box',
#.  'rect',
#.  (('decl', ('ne', 'nw', 'se', 'sw', 'wd', 'ht')),
#.   ('equation',
#.    ('ref', 'nw'),
#.    ('=', ('+', ('ref', 'sw'), ('*', ('literal', 1j), ('ref', 'ht'))))),
#.   ('equation', ('ref', 'ne'), ('=', ('+', ('ref', 'nw'), ('ref', 'wd')))),
#.   ('equation', ('ref', 'se'), ('=', ('+', ('ref', 'sw'), ('ref', 'wd')))),
#.   ('conn',
#.    (('ref', 'ne'),
#.     ('ref', 'nw'),
#.     ('ref', 'sw'),
#.     ('ref', 'se'),
#.     ('ref', 'ne')))))
#. ('box',
#.  'triangle',
#.  (('decl', ('z1', 'z2', 'z3')),
#.   ('conn', (('ref', 'z1'), ('ref', 'z2'), ('ref', 'z3'), ('ref', 'z1')))))
#. ('box',
#.  'pythagoras',
#.  (('put',
#.    'first',
#.    ('box',
#.     'rect',
#.     (('equation', ('ref', 'sw'), ('=', ('literal', 0j))),
#.      ('equation',
#.       ('ref', 'ht'),
#.       ('=', ('ref', 'wd'), '=', ('literal', (1+0j))))))),
#.   ('put',
#.    'next',
#.    ('box',
#.     'rect',
#.     (('equation', ('ref', 'nw'), ('=', ('of', ('ref', 'first'), 'se'))),
#.      ('equation',
#.       ('ref', 'ht'),
#.       ('=', ('ref', 'wd'), '=', ('of', ('ref', 'first'), 'ht')))))),
#.   ('put',
#.    'last',
#.    ('box',
#.     'rect',
#.     (('equation', ('ref', 'sw'), ('=', ('of', ('ref', 'first'), 'ne'))),
#.      ('equation', ('ref', 'se'), ('=', ('of', ('ref', 'next'), 'ne'))),
#.      ('equation', ('ref', 'ht'), ('=', ('ref', 'wd'))))))))
#. ('box',
#.  'main',
#.  (('put',
#.    None,
#.    ('box',
#.     'rect',
#.     (('equation',
#.       ('/', ('+', ('ref', 'nw'), ('ref', 'sw')), ('literal', (2+0j))),
#.       ('=', ('literal', 1j))),
#.      ('equation', ('ref', 'nw'), ('=', ('literal', 2j))),
#.      ('equation', ('ref', 'wd'), ('=', ('literal', (1+0j))))))),))
