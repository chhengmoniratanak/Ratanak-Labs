import requests
from rich import print as rprint

requests.packages.urllib3.disable_warnings()

headers = {"Accept": "application/yang-data+json"}

url = "https://devnetsandboxiosxe.cisco.com:443/restconf/data/Cisco-IOS-XE-native:native/banner/motd/banner"

response = requests.get(url=url, headers=headers, auth=("admin", "C1sco12345"), verify=False)
rprint(response.json())