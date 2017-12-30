# flashre tools

## Naming strategies

In practice, the "error" strategy find most of the functions. The "CamelCase"
one only finds few more functions, and some false positives.

```
python -m flashre.main naming ~/Projects/flashre/dumps/w-03/dump_w03-hw.bin --offset 0xC00000
```

```
python -m flashre.main naming ~/Projects/flashre/dumps/w-03/dump_w03-hw.bin --offset 0xC00000 --strategy camelcase
```

## Hints

The goal is to understand functions purposes based on the string that they
manipulate. Somehow, it is a generic version of the auto-naming strategies.
Decompiling the whole binary with r2m2 being too slow, this command relies on
objdump output.

```
grep mov dump.binary.objdump > movs.txt
python -m flashre.main hints ~/Projects/flashre/dumps/w-03/dump_w03-hw.bin movs.txt --offset 0xC00000
```
