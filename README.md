# FlashRE tools

## Naming strategies

In practice, the "error" strategy find most of the functions. The "CamelCase"
one only finds few more functions, and some false positives.

```
python -m flashre naming ~/Projects/flashre/dumps/w-03/dump_w03-hw.bin --offset 0xC00000
```

```
python -m flashre naming ~/Projects/flashre/dumps/w-03/dump_w03-hw.bin --offset 0xC00000 --strategy camelcase
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

## telnet

```
python -m flashre.main telnet
```

```
python -m flashre.main telnet -c help
```

## Update

Verify an update checksum:
```
python -m flashre.main update update.bin
```

Build a fake update:
```
python -m flashre.main update fake.bin --fake <(echo ABC)
```

## Dump

Converting a dump made using telnet:
```
python -m flashre dump --convert ../dumps/w-03/logs/dump_w03.0x000000-0x200000.v30001.txt
```
