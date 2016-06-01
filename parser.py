"""
Parse (our subset of) IDEAL.
"""

from parson import Grammar, push, Unparsable
import interpreter, solver

grammar = Grammar(r"""
program:   _ box* !/./.

box:       name '{'_ [stmt* :hug] '}'_                  :Box.

stmt:      'var'__ name (','_ name)* ';'_          :hug :Decl
         | 'conn'__ expr ('to'__ expr)+ ';'_       :hug :Conn
         | 'put'__ [name ':'_ | :None] box (';'_)?      :Put
         | {'left'|'right'|'center'|}__ string
             'at'__ expr ';'_                           :Text
         | expr ('='_ expr)+ ';'_                  :hug :Equate 
         | expr ('~'_ expr)+ ';'_                  :hug :Default.

__ = /\b/_.   # (i.e. a keyword must match up to a word boundary)

expr:      term ( '+'_ term :Add
                | '-'_ term :Sub )*.
term:      factor ( '*'_ factor :Mul
                  | '/'_ factor :Div )*.

factor:    atom ('['_ expr ','_ expr ']'_ :Relatively)*.

atom:      '('_ number ','_ number ')'_        :complex :Literal
         | number                              :complex :Literal
         | '-'_ atom                                    :Negate
         | '('_ expr ')'_
         | unaryfn '('_ expr ')'_                       :CallPrim
         | name :Ref ('.'_ name :Of)*.

unaryfn:   'abs'__   :Abs
         | 'cis'__   :Cis
         | 'unit'__  :Unit.

number:    { '-'? (/\d*/ '.' /\d+/ | /\d+/) } _  :float.

string   = '"' {/[^\\"]*/} '"' _.

name     = /([A-Za-z_][A-Za-z_0-9]*)/ _.

_        = (/\s+/ | comment)*.
comment  = '/*' (!'*/' /.|\n/)* '*/'.
""")
parser = grammar(Abs=push(solver.Abs),
                 Cis=push(solver.Cis),
                 Unit=push(solver.Unit),
                 **interpreter.__dict__)
parse = parser.program
