#!/usr/bin/env python3

import getpass
import telnetlib
import time # Added for wait operations

user = input("Enter your telnet username: ")
password = getpass.getpass()

# The main logic to iterate through switches and apply configurations
try:
    # Use 'with open' to ensure the file is always closed
    with open('myswitches', 'r') as f:
        for line in f:
            # line.strip() is correct, ensuring HOST has no whitespace
            HOST = line.strip()

            if not HOST:
                continue # Skip any blank lines in the file

            # Use f-strings for cleaner printing
            print(f"--- Processing switch: {HOST} ---")

            # --- Telnet Connection ---
            try:
                # Default Telnet port is 23
                tn = telnetlib.Telnet(HOST)
            except Exception as e:
                # Catch connection errors and continue to the next switch
                print(f"Error connecting to {HOST}: {e}. Skipping switch.")
                continue # Go to the next line/switch in the file

            # --- Login ---
            # Wait for "Username: " prompt
            tn.read_until(b"Username: ")
            tn.write(user.encode('ascii') + b"\n")

            if password:
                # Wait for "Password: " prompt
                tn.read_until(b"Password: ")
                tn.write(password.encode('ascii') + b"\n")

            # Read initial banner/prompt to clear it.
            tn.read_until(b'#', timeout=5) 
            
            # CRITICAL FIX 1: Read any leftover data (command echo, etc.) to ensure a clean buffer.
            tn.read_very_eager() 

            # --- Configuration Commands ---
            
            # CRITICAL FIX 2: Disable paging (terminal length 0) to ensure 'show run' returns everything
            tn.write(b"terminal length 0\n") 
            tn.read_until(b'#', timeout=5) # Wait for prompt after disabling paging

            tn.write(b"conf t\n")
            # Wait for the config prompt before sending commands
            tn.read_until(b'#', timeout=5) 

            for n in range (2,21):
                # Using f-strings and .encode() for a cleaner approach to sending bytes
                tn.write(f"vlan {n}\n".encode('ascii'))
                tn.write(f"name Python_VLAN_{n}\n".encode('ascii'))

            tn.write(b"end\n") # Exit configuration mode
            
            # Wait for the expected prompt after 'end'
            tn.read_until(b'#', timeout=5) 
            
            # CRITICAL FIX 5: Aggressively flush the buffer after configuration commands
            # Send a newline to guarantee the device outputs a clean prompt.
            tn.write(b"\n") 
            tn.read_until(b'#', timeout=5) # Read the new, clean prompt
            tn.read_very_eager() # Final aggressive clear of any echoes.
            
            # --- START RELIABLE CONFIG CAPTURE ---
            
            # Now, send the commands to get the running config and a marker command
            tn.write(b"show run\n") # 1. Get the running config
            tn.write(b"show clock\n") # 2. Send a short, unique command as a delimiter

            # CRITICAL FIX 6: Read until the echo of the delimiter command appears.
            # This is the most reliable way to ensure we capture the full 'show run' output.
            readoutput = tn.read_until(b'show clock', timeout=20)
            
            # Read the rest of the output (show clock output and the final prompt)
            tn.read_until(b'#', timeout=5)
            
            # Wait a brief moment before disconnecting
            time.sleep(0.5)
            
            tn.write(b"exit\n") # Disconnect

            # Open file for writing (text mode: 'w')
            saveoutput = open(f"switch_{HOST}.config", "w")

            # Decode the bytes into a string for writing to the text file
            saveoutput.write(readoutput.decode('ascii'))
            
            saveoutput.close()

            # --- Output ---
            print(f"Configuration applied and output saved to switch_{HOST}.config")
            # Print the output to the console for review
            print("--- Device Output Snippet (Cleaned) ---")
            
            # Clean up the output for display: remove the command and the final delimiter
            decoded_output = readoutput.decode('ascii')
            
            # Find the start of the actual configuration data after the 'show run' echo
            start_index = decoded_output.find('show run\r\n')
            if start_index != -1:
                decoded_output = decoded_output[start_index + len('show run\r\n'):]
            
            # Remove the final delimiter 'show clock'
            cleaned_output = decoded_output.split('show clock')[0].strip()

            print(cleaned_output[:500] + "...") 
            print("-----------------------------")


except FileNotFoundError:
    print("Error: The file 'myswitches' was not found.")
except Exception as e:
    # This catch block is for general script errors, not connection errors handled above.
    print(f"An unexpected script error occurred: {e}")
