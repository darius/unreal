# unreal

Christopher Van Wyk's IDEAL picture language redone in Python: or
anyway, some subset thereof, as far as I get, for the sake of
understanding it better. This currently doesn't do:

  * drawing anything but line segments
  * re, im, conj functions
  * pens
  * boundaries and set operations

What it does do:

  * solve so-called 'slightly nonlinear' constraints
  * default constraints (like `a ~ b`)
  * other built-in functions

To run it: `python unreal.py sourcefile1 sourcefile2 ... >out.svg`

This uses [Parson](https://github.com/darius/parson) for parsing.

The full language is explained in the [IDEAL User's
Manual](https://web.cecs.pdx.edu/~trent/gnu/groff/103.ps).

Other interpreters I know of (and so far have only glanced at):

  * [Original IDEAL](http://freaknet.org/martin/tape/stuff/ditroff/ideal/)
  * [Argand](https://github.com/ALPHA-60/argand)
