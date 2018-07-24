# FlashRE tools

This repository contains a set of tools that ease reversing the Toshiba FlashAir
cards:
- telnet: interact with the card
- dump: get text dumps and convert them to binary

## Commands Examples

### telnet

Open a Telnet session:
```
flashre telnet
Welcome to FlashAir
ESC R4539 built 15:37:44, Aug 28 2015
> dump -l 0x80
dump -l 0x80
address=0x00000000 length=0x80
 0001d808 0008df18 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
 00000000 00000000 00000000 00000000
address=0x00000080
```

Send a single command:
```
flashre telnet -c version
version
FA9CAW3AW3.00.01
> 
```

### dump

Dump 2MB at address 0:
```
flashre dump dump.log
```
The --begin and --end arguments can be used to adjust the dump size.

Convert a text dump to a binary
```
flashre dump --convert dump.log > dump.bin
```

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

## Update

Verify an update checksum:
```
python -m flashre.main update update.bin
```

Build a fake update:
```
python -m flashre.main update fake.bin --fake <(echo ABC)
```
