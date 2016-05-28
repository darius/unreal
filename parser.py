"""
Parse (our subset of) IDEAL.
"""

from parson import Grammar, Unparsable
import interpreter

grammar = Grammar(r"""
program:   _ box* !/./.

box:       name '{'_ [stmt* :hug] '}'_                  :Box.

stmt:      'var'__ name (','_ name)* ';'_          :hug :Decl
         | 'conn'__ expr ('to'__ expr)+ ';'_       :hug :Conn
         | 'put'__ [name ':'_ | :None] box ';'_         :Put
         | expr ('='_ expr)+ ';'_                  :hug :Equate 
         | expr ('~'_ expr)+ ';'_                  :hug :Default
         | {'left'|'right'|}__ string 'at'__ expr ';'_  :Text.

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

string   = '"' {/[^\\"]*/} '"' _.

name     = /([A-Za-z_][A-Za-z_0-9]*)/ _.

_        = (/\s+/ | comment)*.
comment  = '/*' (!'*/' /.|\n/)* '*/'.
""")
parser = grammar(**interpreter.__dict__)
parse = parser.program
