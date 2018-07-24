# FlashRE tools

This repository contains a set of tools that ease reversing the Toshiba FlashAir
cards:
- telnet: interact with the card
- dump: get text dumps and convert them to binary
- hints: identify functions that manipulates specific strings
- naming: auto-name functions using error format strings 
- xref: explore functions call-graph

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
flashre hints dump.bin  --offset 0xc00000 --reverse <(echo 0xc67c4a)
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

# naming

Two auto-naming strategies are implemented.  In practice, the "error" strategy
find most of the functions. The "CamelCase" one only finds few more functions,
and some false positives.

```
$ flashre naming --offset 0xc00000 dump.bin
[..]
af DP.dp_UpdateWinStart_O 0xcfac98
af TEL.SendLoginMessage 0xc67c4a
af WPS.WPS_SetSecInfo 0xc3959e
af SDH.SD_HOST_TEST_Read 0xc9a78c
af FAT.fat_remove_file 0xc2eac8
```

```
$ flashre naming --offset 0xc00000 dump.bin --strategy camelcase
[..]
af SendDeauthMessageToAP 0xc393d4
af InitializeWPS 0xc80624
af WaitForTermination 0xc8019e
af CntMeasure_Timeout_Frmblk 0xc97848
af WlanWpsPin 0xc31242
```

### xref

This commands helps exploring functions by printing their call-graph:
```
$ flashre xref --offset 0xC00000 dump.bin 0xc67c4a
0xc67c4a,0xc7fb84,0xc12a8e,0xc7512e,0xc67bfa,0xc7517a,0xc12abe
0xc7fb84
0xc12a8e,0xc35960
0xc7512e,0xc12a8e
0xc67bfa,0xc7517a,0xc12a8e,0xc7512e
0xc7517a,0xc12a8e
0xc12abe,0xc35960
0xc35960,0xc47700,0xc36344,0xc79cc8,0xc362aa,0xc7fb84,0xc8083c
0xc7517a,0xc12a8e
[..]
```

The --reverse argument return the functions that are calling the function given
as a parameter:
```
$ flashre xref --offset 0xC00000 dump.bin --reverse 0xc67c4a
['0xc6786a']
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
