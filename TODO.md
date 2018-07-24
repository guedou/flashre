# Things todo, issues, improvements ...

## Before BHUS

- auto detect sub-commands
- test requirements.txt

## Important

- implement LDCB/STCB in sem.py, and emulate NMI.putchar_STCB(0x3F4) !
- add JSR based function calls to get_prologue()

## misc ...

- fix offset related issues in cache files
- add short CLI arguments
- look for movs using r2 '/x' like done in reverse xref
- use the `nearest_prologues()` function
- implement unit tests
- implement a cache in .config/flashre/SHA256/
  interact with a global config: binary filename, flush, ...
- auto load sub commands
- add per file license
- telnet: port the watchdog for full memory dumps

## radare2

- bug: izz and -m !
  => inconsistent usage of offset in the tools and the outputs ?
- afr does not list functions that are not reachable
- remove "hits: 1" output

## Possible bugs

- naming:
   - error: not match for '\n[SEC] (error)'
