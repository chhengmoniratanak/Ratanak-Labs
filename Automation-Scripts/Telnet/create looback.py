import getpass
import sys
import telnetlib

HOST = "192.168.122.132"
user = input("Enter your telnet username: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until("Username: ".encode('ascii'))
tn.write((user + "\n").encode('ascii'))
if password:
    tn.read_until(b"Password: ")
    tn.write((password + "\n").encode('ascii'))

tn.write(b"enable\n")
tn.write(b"cisco\n")
tn.write(b"conf t\n")
tn.write(b"int loop 0\n")
tn.write(b"ip address 1.1.1.1 255.255.255.255\n")
tn.write(b"int loop 1\n")
tn.write(b"ip address 2.2.2.2 255.255.255.255\n")
tn.write(b"end\n")
tn.write(b"exit\n")
