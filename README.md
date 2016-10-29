# bhp
Black Hat Python: Python Programming for Hackers and Pentesters

## BHP Net Tool
Replace netcat command with BHP Net Tool.

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
Capture http packet for example.

	$ python proxy.py 127.0.0.1 5555 www.google.com 80 False

	$ echo -ne "GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n" | python bhnet.py -t 127.0.0.1 -p 5555

## SSH

### Execute shell command through ssh

After the ssh connection establishment, server send a command to client. Then client execute a command and return result to server.

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

## Reverse SSH tunneling
Execute following command on your machine.

	$ python rforward.py sshserver:22 -p 5555 -r httpserver:80 --user username

Then your machine becomes sshclient and establish *reverse ssh tunneling* to sshserver:22.
sshserver listen 5555 port.
If httpclient connects to the sshserver:5555, the packet is forwarded to httpserver:80.

`httpserver` <---*tcp*---> `sshclient` <---*reverse ssh tunneling*---> `sshserver` <---*tcp*---> `httpclient`

The following ssh command is equivalent to the above.

	$ ssh -R 5555:httpserver:80 -p 22 username@sshserver
