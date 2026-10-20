from scrapli.driver.core import IOSXEDriver

# 1. Define device connection details
MY_DEVICE = {
    "host": "10.10.10.11",
    "auth_username": "john",
    "auth_password": "cisco",
    "auth_strict_key": False,
    "transport": "paramiko",
    "ssh_config_file": True,
}


#using scrapli to connect to a device and send configuration commands manually
# with IOSXEDriver(**MY_DEVICE) as conn:
#     response = conn.send_configs(["interface loopback 1", "ip address 1.1.1.1 255.255.255.255"])
#     print(response.result)


#send configuration commands from a file using scrapli
with IOSXEDriver(**MY_DEVICE) as conn:
    response = conn.send_configs_from_file("config.txt")
    print(response.result)
