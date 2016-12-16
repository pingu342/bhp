# -*- coding: utf-8 -*-

import argparse
import socket
import os

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7f else b'.' for x in s])
        result.append( b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text) )

    print b'\n'.join(result)

def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    args = parser.parse_args()
    return args.host

# リッスンするホストのIPアドレス
host = parse_options()

print ("Listen %s ..." % (host))

# rawソケットを作成しパブリックなインターフェースにバインド
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# キャプチャー結果にIPヘッダーを含めるように指定
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# パケットの読み込み
while True:
    try:
        buf = sniffer.recvfrom(65565)[0];
        if len(buf):
            hexdump(buf)
            print '----'
    except Exception as e:
        print "Exiting ..."
        break

sniffer.close()

# Windowsの場合はプロミスキャスモードを無効化
if os.name == "nt":
    sniffer.ioctrl(socket.SIO_RCVALL, socket.RCVALL_OFF)

