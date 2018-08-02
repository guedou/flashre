# Things todo, issues, improvements ...

## Improvements

- add JSR based function calls to `get_prologue()`
- implement a cache per binary in .config/flashre/
  interact with a global config: binary filename, flush, ...
- telnet: implement a watchdog for full memory dumps

## radare2

- bug: izz and -m !
  => inconsistent usage of offset in the tools and the outputs ?
- afr does not list functions that are not reachable
- remove "hits: 1" output

## Possible bugs

- naming:
   - error: not match for '\n[SEC] (error)'
