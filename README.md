# bhp
Black Hat Python: Python Programming for Hackers and Pentesters

# Reverse SSH tunneling

Execute following command on your machine.

	$ python rforward.py sshserver:22 -p 5555 -r httpserver:80 --user username

Then your machine becomes sshclient and establish *reverse ssh tunneling* to sshserver:22.
sshserver listen 5555 port.
If httpclient connects to the sshserver:5555, the packet is forwarded to httpserver:80.

`httpserver` <---*tcp*---> `sshclient` <---*reverse ssh tunneling*---> `sshserver` <---*tcp*---> `httpclient`


