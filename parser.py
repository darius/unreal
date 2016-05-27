"""
Parse (our subset of) IDEAL.
"""

from parson import Grammar
import interpreter

grammar = Grammar(r"""
program:   _ box* !/./.

box:       name '{'_ [stmt* :hug] '}'_                  :Box.

stmt:      'var'__ name (','_ name)* ';'_          :hug :Decl
         | 'conn'__ expr ('to'__ expr)+ ';'_       :hug :Conn
         | 'put'__ [name ':'_ | :None] box ';'_         :Put
         | expr ('='_ expr)+ ';'_                  :hug :Equate 
         | expr ('~'_ expr)+ ';'_                  :hug :Default.

__ = /\b/_.   # (i.e. a keyword must match up to a word boundary)

expr:      term ( '+'_ term :Add
                | '-'_ term :Sub )*.
term:      atom ( '*'_ atom :Mul
                | '/'_ atom :Div )*.

atom:      '('_ number ','_ number ')'_            :complex :Literal
         | number                                  :complex :Literal
         | '('_ expr ')'_
         | name :Ref ('.'_ name :Of)*.

number:    { '-'? uint (frac exp? | exp)? } _      :float.
uint     = '0' !/\d/
         | /[1-9]\d*/.
frac     = '.' /\d+/.
exp      = /[eE][+-]?\d+/.

name     = /([A-Za-z_][A-Za-z_0-9]*)/ _.

_        = (/\s+/ | comment)*.
comment  = '/*' (!'*/' /.|\n/)* '*/'.
""")
parser = grammar(**interpreter.__dict__)


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
## for a in parser.program(eg): pprint(a.as_sexpr())
#. ('box',
#.  'rect',
#.  (('decl', ('ne', 'nw', 'se', 'sw', 'wd', 'ht')),
#.   ('=',
#.    (('ref', 'nw'),
#.     ('+', ('ref', 'sw'), ('*', ('literal', 1j), ('ref', 'ht'))))),
#.   ('=', (('ref', 'ne'), ('+', ('ref', 'nw'), ('ref', 'wd')))),
#.   ('=', (('ref', 'se'), ('+', ('ref', 'sw'), ('ref', 'wd')))),
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
#.     (('=', (('ref', 'sw'), ('literal', 0j))),
#.      ('=', (('ref', 'ht'), ('ref', 'wd'), ('literal', (1+0j))))))),
#.   ('put',
#.    'next',
#.    ('box',
#.     'rect',
#.     (('=', (('ref', 'nw'), ('of', ('ref', 'first'), 'se'))),
#.      ('=', (('ref', 'ht'), ('ref', 'wd'), ('of', ('ref', 'first'), 'ht')))))),
#.   ('put',
#.    'last',
#.    ('box',
#.     'rect',
#.     (('=', (('ref', 'sw'), ('of', ('ref', 'first'), 'ne'))),
#.      ('=', (('ref', 'se'), ('of', ('ref', 'next'), 'ne'))),
#.      ('=', (('ref', 'ht'), ('ref', 'wd'))))))))
#. ('box',
#.  'main',
#.  (('put',
#.    None,
#.    ('box',
#.     'rect',
#.     (('=',
#.       (('/', ('+', ('ref', 'nw'), ('ref', 'sw')), ('literal', (2+0j))),
#.        ('literal', 1j))),
#.      ('=', (('ref', 'nw'), ('literal', 2j))),
#.      ('=', (('ref', 'wd'), ('literal', (1+0j))))))),))
