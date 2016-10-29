# bhp
Black Hat Python: Python Programming for Hackers and Pentesters

## BHP Net Tool
Replace netcat command with BHP Net Tool.

### Execute shell command
* netcat command

	server side:

		$ mkfifo /tmp/f
		$ cat /tmp/f | /bin/sh -i 2>&1 | nc -l 127.0.0.1 5555 > /tmp/f

	client side:

		$ nc 127.0.0.1 5555

* BHP Net Tool.

	server side:

		$ python bhnet.py -t 127.0.0.1 -p 5555 -l -c

	client side:

		$ python bhnet.py -t 127.0.0.1 -p 5555
		Ctrl-D
		<BHP:#> ls -al

## Reverse SSH tunneling
Execute following command on your machine.

	$ python rforward.py sshserver:22 -p 5555 -r httpserver:80 --user username

Then your machine becomes sshclient and establish *reverse ssh tunneling* to sshserver:22.
sshserver listen 5555 port.
If httpclient connects to the sshserver:5555, the packet is forwarded to httpserver:80.

`httpserver` <---*tcp*---> `sshclient` <---*reverse ssh tunneling*---> `sshserver` <---*tcp*---> `httpclient`

The following ssh command is equivalent to the above.

	$ ssh -R 5555:httpserver:80 -p 22 username@sshserver
