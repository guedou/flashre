# FlashRE tools

This repository contains a set of tools that ease reversing the Toshiba FlashAir
cards:
- telnet: interact with the card
- dump: get text dumps and convert them to binary
- hints: identify functions that manipulates specific strings

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

### hints

The goal is to understand functions purposes based on the strings that they
manipulate. Somehow, it is a generic version of the auto-naming strategies.

```
flashre hints dump.bin --offset 0xC00000 telnet
0xc11a68 0xc11aa2 SD_WLAN/WELCOME.HTM
0xc11a68 0xc11aae /SD_WLAN/WELCOME.HTM
0xc11a68 0xc11abe 1:/WELCOME.HTM
0xc11a68 0xc11ac8 1:/WELCOME.HTM
====
0xc67c4a 0xc67c6a Welcome to FlashAir\r\n
0xc67c4a 0xc67cac Welcome to FlashAir\r\n
```

The --reverse argument outputs strings manipulated by functions:
```
flashre hints ../dumps/w-03/dump_w03-hw.bin  --offset 0xc00000 --reverse <(echo 0xc67c4a)
0xc67c4a  0xccf586 ESC R4161 built 16:20:27, Oct  6 2014
0xc67c4a  0xce4fec Welcome to FlashAir\x0d
0xc67c4a  0xce5172 [TEL] (error) %s:%d
0xc67c4a  0xce5161 SendLoginMessage
0xc67c4a  0xce5187 cannot get memory(%d)
0xc67c4a  0xce519e %s%s%s
0xc67c4a  0xce4fec Welcome to FlashAir\x0d
0xc67c4a  0xccf586 ESC R4161 built 16:20:27, Oct  6 2014
0xc67c4a  0xce51a5 [TEL] (error) %s:%d
0xc67c4a  0xce5161 SendLoginMessage
0xc67c4a  0xce51ba send(%d)
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

## Update

Verify an update checksum:
```
python -m flashre.main update update.bin
```

Build a fake update:
```
python -m flashre.main update fake.bin --fake <(echo ABC)
```
