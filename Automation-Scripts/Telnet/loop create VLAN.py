#!/usr/bin/env python3

import getpass
import sys
import telnetlib

HOST = "192.168.122.72"
user = input("Enter your telnet username: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until("Username: ".encode('ascii'))
tn.write((user + "\n").encode('ascii'))
if password:
    tn.read_until(b"Password: ")
    tn.write((password + "\n").encode('ascii'))

tn.write(b"conf t\n")

for n in range (2,10):
         tn.write(b"vlan "+ str(n).encode('ascii') +b"\n")
         tn.write(b"name Python_VLAN_" + str(n).encode('ascii')+b"\n")

tn.write(b"end\n")
tn.write(b"exit\n")

print (tn.read_all())
