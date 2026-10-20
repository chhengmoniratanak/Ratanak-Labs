from datetime import datetime
from scrapli.driver.core import IOSXEDriver

#pip install scrapli
#pip install scrapli[paramiko]

# 1. Use dashes (-) instead of colons (:) for Windows-safe filenames
my_time = datetime.now().strftime("%H-%M-%S")

command_to_send = input("Enter command to send: ")

MY_DEVICE = {
    "host": "devnetsandboxiosxec8k.cisco.com",
    "auth_username": "chhengmoniratanak",
    "auth_password": "__W-d7r_4YO56o",
    "port": 22,
    "auth_strict_key": False,
    "transport": "paramiko",  # Explicitly required on Windows
}

# 2. Connect and run command
with IOSXEDriver(**MY_DEVICE) as conn:
    result = conn.send_command(command_to_send)

# 3. Clean up spaces in command name for the file (e.g., 'show_run')
safe_command = command_to_send.replace(" ", "_")
filename = f"{safe_command}_{my_time}.txt"

# 4. Write raw result directly to file using "w" mode
with open(filename, "w") as f:
    f.write(result.result)

print(f"Success! Output saved to {filename}")
