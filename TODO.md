# Things todo, issues, improvements ...

## Before BHUS

- auto detect sub-commands
- test requirements.txt
- test "flashre emulate strlen.bin"
- use a cache per binary
- fix offset related issues in cache files
  - test with radare2 2.6.0
  - flashre hints; rm get_prologues.cache: flashare hints -m 0xC00000

## Important

- implement LDCB/STCB in sem.py, and emulate NMI.putchar_STCB(0x3F4) !
- add JSR based function calls to get_prologue()

## misc ...

- use the `nearest_prologues()` function
- implement unit tests
- implement a cache in .config/flashre/SHA256/
  interact with a global config: binary filename, flush, ...
- telnet: port the watchdog for full memory dumps
  => use radare2 2.6.0

## radare2

- bug: izz and -m !
  => inconsistent usage of offset in the tools and the outputs ?
- afr does not list functions that are not reachable
- remove "hits: 1" output

## Possible bugs

- naming:
   - error: not match for '\n[SEC] (error)'
