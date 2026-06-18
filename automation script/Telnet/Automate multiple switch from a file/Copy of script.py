#!/usr/bin/env python3

import getpass
import sys
import telnetlib

user = input("Enter your telnet username: ")
password = getpass.getpass()

# Use 'with open' to ensure the file is always closed
try:
    with open('myswitches', 'r') as f:
        for line in f:
            # line.strip() is correct, ensuring HOST has no whitespace
            HOST = line.strip()
            
            if not HOST:
                continue # Skip any blank lines in the file
            
            # Use f-strings for cleaner printing
            print(f"Configuring Switch {HOST}")

            # --- Telnet Connection ---
            try:
                tn = telnetlib.Telnet(HOST)
            except Exception as e:
                # Catch connection errors (like the one you were seeing) and continue to the next switch
                print(f"Error connecting to {HOST}: {e}. Skipping switch.")
                continue # Go to the next line/switch in the file

            # --- Login ---
            tn.read_until(b"Username: ")
            tn.write(user.encode('ascii') + b"\n")
            
            if password:
                tn.read_until(b"Password: ")
                tn.write(password.encode('ascii') + b"\n")

            # --- Configuration Commands ---
            tn.write(b"conf t\n")

            for n in range (2,16):
                # Using f-strings and .encode() for a cleaner approach to sending bytes
                tn.write(f"vlan {n}\n".encode('ascii'))
                tn.write(f"name Python_VLAN_{n}\n".encode('ascii'))
                
            tn.write(b"end\n")
            tn.write(b"exit\n")

            # --- Output ---
            # Decode the bytes from tn.read_all() before printing
            print(tn.read_all().decode('ascii'))

except FileNotFoundError:
    print("Error: The file 'myswitches' was not found.")
except Exception as e:
    print(f"An unexpected script error occurred: {e}")