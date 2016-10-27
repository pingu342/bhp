# -*- coding: utf-8 -*-

# example:
#   sshserver(192.168.0.200:2200)にssh接続し、sshserverの5555番ポートへの通信をwww.google.com:80にforwardingにする
#   $ python rforward.py 192.168.0.200:2200 -p 5555 -r www.google.com:80 --user pi

import threading
import socket
import select
import paramiko
import argparse
import getpass
import sys

# 辞書にドットでアクセスできるようにする
class Options(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def parse_addr(addr, port):
    tmp = addr.split(":", 1)
    if len(tmp) == 2:
        return (tmp[0], int(tmp[1]))
    if (port == 0):
        sys.exit(1)
    return (tmp[0], port)

def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument('sshserver')
    parser.add_argument('-p', type=int)
    parser.add_argument('-r')
    parser.add_argument('--user')
    parser.add_argument('--password', nargs="?")
    parser.add_argument('--keyfile', nargs="?")
    args = parser.parse_args()
    options = Options({"readpass":True, "user":args.user, "keyfile":args.keyfile, "look_for_keys":False, "port":args.p})
    return (options, parse_addr(args.sshserver, 22), parse_addr(args.r, 0))

def main():
    options, server, remote = parse_options()
    password = None
    if options.readpass:
        password = getpass.getpass('Enter SSH password: ')
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    print('Connecting to ssh host %s:%d ...' % (server[0], server[1]))
    try:
        client.connect(
                server[0], server[1], username=options.user,
                key_filename=options.keyfile,
                look_for_keys=options.look_for_keys, password=password)
    except Exception as e:
        print('*** Failed to connect to %s:%d: %r' % (server[0], server[1], e))
        sys.exit(1)

    print('Now forwarding remote port %d to %s:%d ...' % (
        options.port, remote[0], remote[1]))

    try:
        reverse_forward_tunnel(options.port, remote[0], remote[1], client.get_transport())
    except KeyboardInterrupt:
        print('C-c: port forwarding stopped.')
        sys.exit(0)

def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward('', server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(
                target=handler, args=(chan, remote_host, remote_port))

        thr.setDaemon(True)
        thr.start()

def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print('Forwarding request to %s:%d failed: %r' % (host, port, e))
        return

    print('Connected!  Tunnel open %r -> %r -> %r' % (chan.origin_addr,
        chan.getpeername(), (host, port)))

    while (True):
        r, w, x = select.select((sock, chan), {}, {})
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    print('Tunnel closed from %r' % (chan.origin_addr,))

main()
