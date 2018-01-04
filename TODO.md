# Things todo, issues, improvements ...

## Commands that need to be merged

- convert
- dump
- watchdog


## misc ...

- add short CLI arguments
- look for movs using r2 '/x' like done in reverse xref
- implement '__main__' in each sub-command ?
- use the `nearest_prologues()` function
- implement unit tests
- implement a cache in .config/flashre/SHA256/
  interact with a global config: binary filename, flush, ...
- auto load sub commands
- add per file license


## radare2

- bug: izz and -m !
  => inconsistent usage of offset in the tools and the outputs ?
- afr does not list functions that are not reachable
- remove "hits: 1" output


## Possible bugs

- naming:
   - error: not match for '\n[SEC] (error)'
