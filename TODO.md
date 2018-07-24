# Things todo, issues, improvements ...

## Important

- implement LDCB/STCB in sem.py, and emulate NMI.putchar_STCB(0x3F4) !
- add JSR based function calls to get_prologue()


## Commands that need to be merged

- convert
- dump
- watchdog
- have a look at `~/restored/crash_33c3`


## misc ...

- setup.py & requirements.txt (scapy, miasm, r2pipe)
- fix offset related issues in cache files
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

## Telnet

- flash dump using telnet directly
-  -> check why the old code does not work anymore ..
- full memory dump using the watchdog
- dump conversion, using struct !
-  struct.pack(">I", struct.unpack("<I", data)[0]) # Convert from LE to BE !
- -> it seems that the printf %08x converts data to LE
- TODO: telnet based memory dump


