from scrapli.driver.core import IOSXEDriver

# 1. Define device connection details
MY_DEVICE = [{
    "host": "10.10.10.11",
    "auth_username": "john",
    "auth_password": "cisco",
    "auth_strict_key": False,
    "transport": "paramiko",
    "ssh_config_file": True,
},
{
    "host": "10.10.10.12",
    "auth_username": "john",
    "auth_password": "cisco",
    "auth_strict_key": False,
    "transport": "paramiko",
    "ssh_config_file": True,
},
{
    "host": "10.10.10.13",
    "auth_username": "john",
    "auth_password": "cisco",
    "auth_strict_key": False,
    "transport": "paramiko",
    "ssh_config_file": True,
}
]

# python3 -m pip install scrapli[textfsm]

for device in MY_DEVICE:
    with IOSXEDriver(**device) as conn:
        response = conn.send_command("show version")
        structured_response = response.textfsm_parse_output()
        # print(structured_response)
    for info in structured_response:
        print(f"Device hostname: {info['hostname']} is running IOS version: {info['version']} and software image: {info['software_image']}")
