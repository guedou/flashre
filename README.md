# FlashRE tools

[![GitHub tag](https://img.shields.io/github/tag/guedou/flashre.svg)](https://github.com/guedou/flashre/releases)
[![Docker Automated buil](https://img.shields.io/docker/automated/guedou/flashre.svg)](https://hub.docker.com/r/guedou/flashre/)
[![Twitter Follow](https://img.shields.io/twitter/follow/guedou.svg?style=social)](https://twitter.com/intent/follow?screen_name=guedou)

This repository contains a set of tools that ease reversing the Toshiba FlashAir
cards:
- `telnet`: interact with the card
- `dump`: get text dumps and convert them to binary
- `hints`: identify functions that manipulates specific strings
- `naming`: auto-name functions using error format strings 
- `xref`: explore functions call-graph
- `update`: display firmware update, and build fake ones

The radare2 IO plugin located in `tools/` ease interacting with the card:
```
export R2M2_ARCH=mepl
r2 -i io_flashair.py -qc 'e asm.arch=r2m2 ; o flashair:// ; px 16 ; pd 2' --
- offset -   0 1  2 3  4 5  6 7  8 9  A B  C D  E F  0123456789ABCDEF
0x00000000  08d8 0100 18df 0800 0000 0000 0000 0000  ................
        ,=< 0x00000000      08d80100       JMP 0x100
       ,==< 0x00000004      18df0800       JMP 0x8E2
```

Some real usages are presented in the BlackHat USA 2018 briefing named
[Reversing a Japanese Wireless SD Card - From Zero to Code
Execution](https://www.blackhat.com/us-18/briefings.html#reversing-a-japanese-wireless-sd-card-from-zero-to-code-execution).


## Installing flashre

flashre can easily be installed using the following commands. It is however
recommended to use a [virtualenv](https://virtualenv.pypa.io/).
```
pip install -r requirements.txt
python setup.py install
```

## Docker

A [Docker](https://www.docker.com/) image is provided to ease using flashre. It
is based on the [guedou/r2m2](https://github.com/guedou/r2m2) image and contains
useful tools such as [radare2](https://github.com/radare/radare2), [miasm2](https://github.com/cea-sec/miasm), [binutils](https://www.gnu.org/software/binutils/) with MeP support, and [Sibyl](https://github.com/cea-sec/Sibyl).

This image is built on [Docker Hub](https://hub.docker.com) and can easily be
pulled as follows:

```
flashre$ docker pull guedou/flashre

flashre$ $ docker run --rm -it -v $PWD:/data guedou/flashre flashre hints --offset 0xc00000 /data/dump_w03.bin update
0xc20580 0xc20c82 update -f %s
====
0xc3335a 0xc33478 propertyupdate
====
0xc96870 0xc969c6 FwUpdate error f_open(%s) ret=%d\n
0xc96870 0xc96a36 \nUpdate fail. Unexpected target name.\n
0xc96870 0xc96b3e \nUpdate reserved.\n
====
0xc9b502 0xc9b51a USAGE: sd update filename
0xc9b502 0xc9b65a \nUpdate fail. Unexpected target name.\n
0xc9b502 0xc9b722 \nUpdate success.\n
0xc9b502 0xc9b780 Update error.(checksum)\n
====
0xcfac98 0xcfacb4 dp_UpdateWinStart_O
```

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
0xc15f4e 0xc16c04 TELNET
====
0xc6784c 0xc67852 TELNET start\n
====
0xc67936 0xc6794c telnet terminate\n
====
0xc7fa92 0xc7fb18 TELNET_CreateResHistory
====
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
0xc6786a
```

### update

Verify an update checksum:
```
$ flashre update fwupdate.fbn
###[ FlashAir Update Header ]### 
  card      = 'FLASHAIR'
  type      = 'MAIN2'
  unk0      = '\x01\x02\x03\x04'
  unk1      = 0x1c7e
  unk2      = 0x1f00250f
  checksum  = 0xc2
  unk3      = 0x0
  length    = 1047568
```

Build a fake update and verify the checksum:
```
$ flashre update fake_update.bin --fake <(echo -n ABC) --type RF
###[ FlashAir Update Header ]### 
  card      = 'FLASHAIR'
  type      = 'RF'
  unk0      = '\x01\x02\x03\x04'
  unk1      = 0x0
  unk2      = 0x0
  checksum  = 0xc6
  unk3      = 0x0
  length    = 3
```
