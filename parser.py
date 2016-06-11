"""
Parse (our subset of) IDEAL.
"""

from parson import Grammar, Unparsable
import interpreter

grammar = Grammar(r""" box* :end.

box:       name '{' [stmt* :hug] '}'               :Box.

stmt:      "var" name ++ ',' ';'              :hug :Decl
         | "conn" expr ("to" expr)+ ';'       :hug :Conn
         | "put" [name ':' | :None] box ';'?       :Put
         | justify string "at" expr ';'            :Text
         | expr ('=' expr)+ ';'               :hug :Equate 
         | expr ('~' expr)+ ';'               :hug :Default.

justify:   {"left"~|"right"~|"center"~} FNORD
         | :'center'.

expr:      term   ( '+' term   :Add
                  | '-' term   :Sub )*.
term:      factor ( '*' factor :Mul
                  | '/' factor :Div )*.

factor:    atom ('[' expr ',' expr ']' :Relatively)*.

atom:      '(' number ',' number ')'      :complex :Literal
         | number                         :complex :Literal
         | '-' atom                                :Negate
         | '(' expr ')'
         | unaryfn '(' expr ')'                    :CallPrim
         | name :Ref ('.' name :Of)*.

unaryfn:   "abs"   :Abs
         | "cis"   :Cis
         | "unit"  :Unit.

name:      /([A-Za-z_][A-Za-z_0-9]*)/.

number  ~: { '-'? (/\d*/ '.' /\d+/ | /\d+/) } FNORD   :float.

string  ~: '"' {/[^\\"]*/} '"' FNORD.

FNORD   ~: (/\s+/ | comment)*.
comment ~: '/*' (!'*/' :anyone)* '*/'.
""")
parse = grammar.bind(interpreter)
