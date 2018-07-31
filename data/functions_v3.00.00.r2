af asm.strlen 0xc7fb84
af asm.strcmp 0xc7cd58
af asm.strcpy 0xc7cf70
af asm.strchr 0xc7c41c
af asm.memset 0x804800
af asm.memcmp 0x803fdc
af asm.memcpy 0x802f74 # maybe
af asm.strsep 0xc842c4 # maybe
af asm.rindex 0xc7de0c # maybe
af asm.strstr 0xc7c074 # maybe
af asm.index 0xc82978
af asm.strncasecmp 0xc38168 # maybe
af strtol 0xc3b5f8 # maybe

af reset_handler 0x100
af nmi_handler 0x8e2


# Found using Sibyl
af asm.strcat 0xc7c094
af asm.strncpy 0xc78178
af asm.strncmp 0xc77540
af atoi 0xc46808
#af memcpy 0x0cf7808
af strchr 0xc7c41c


# Named according to strings found in functions
af WPA.zmalloc 0xc7512e
af WPA.zfree 0xc7517a
af TEL.start 0xc6784c

# TELNET related
af TEL.Init 0xc6786a


# Named according to the usage context
af MAYBE.printf 0xc12a8e
af MAYBE.sprintf 0xc12abe


af MAYBE.accept 0xc7819c
af MAYBE.send 0x802b7c

# NetBSD sys/socket.h & sys/netinet/in.h
# AF_INET = 2
#
# SOCK_STREAM = 1
# SOCK_DGRAM = 2
# SOCK_RAW = 3
#
# IPPROTO_ICMP = 1
# IPPROTO_TCP = 6
# IPPROTO_UDP = 17
#
af bind 0xc371b0
af MAYBE.connect 0xC73784
af socket 0xC78C58
af MAYBE.setsockopt 0xC614EC
af MAYBE.sendto 0x804004
af MAYBE.recv 0x804844
#af MAYBE.recv 0x8030D8 # recvmsg ?
af MAYBE.recvfrom 0x803d6c
af MAYBE.recvfrom_wrapper 0x803d50
af MAYBE.close 0xc26e2c
af MAYBE.sck_close 0xc26e2c
af MAYBE.listen 0xc4e03c
# SHUT_WR=1
af MAYBE.shutdown 0xc803ec

af MAYBE.inet_pton 0xc7c400
af MAYBE.inet_aton 0xc80b44
af MAYBE.inet_addr 0xc73d48
af MAYBE.getaddrinfo 0xc62a42

af MAYBE.parse_config 0xc15f4e

af fcn.sys_dwn 0xc4693e # halting the system


# FatFS
af MAYBE.f_open 0x802128
af MAYBE.f_read 0x8022f6
af MAYBE.f_seek 0x802766


# MITRON
af MITRON.sta_tsk 0x812258
