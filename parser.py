"""
Parse (our subset of) IDEAL.
"""

from parson import Grammar, Unparsable
import interpreter

grammar = Grammar(r"""
program:   _ box* :end.

box:       name '{'_ [stmt* :hug] '}'_                  :Box.

stmt:      'var'__ name (','_ name)* ';'_          :hug :Decl
         | 'conn'__ expr ('to'__ expr)+ ';'_       :hug :Conn
         | 'put'__ [name ':'_ | :None] box (';'_)?      :Put
         | justify string 'at'__ expr ';'_              :Text
         | expr ('='_ expr)+ ';'_                  :hug :Equate 
         | expr ('~'_ expr)+ ';'_                  :hug :Default.

justify:   {'left'|'right'|'center'}__ | :'center'.

__       = /\b/_.   # (i.e. a keyword must match up to a word boundary)

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
parser = grammar.bind(interpreter)
parse = parser.program
