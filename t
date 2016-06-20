#!/bin/bash
set -euo pipefail; shopt -s failglob  # 'Bash strict mode'

# A crude test suite.
# This uses out/ and ref/ directories which I didn't check in to the repo.

./test-run trivial
./test-run 1
./test-run 2
./test-run 3 eg/library
./test-run 4 eg/library
./test-run pythagoras eg/library
./test-run pythagoras-squares eg/library
./test-run forwardref
./test-run list1 eg/library
./test-run list2 eg/library
./test-run wavy
./test-run regular-n-gon
./test-run concentrics eg/library
