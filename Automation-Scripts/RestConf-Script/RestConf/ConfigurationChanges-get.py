import requests
from rich import print as rprint

requests.packages.urllib3.disable_warnings()

headers = {"Accept": "application/yang-data+json"}

url = "https://devnetsandboxiosxe.cisco.com:443/restconf/data/ietf-interfaces:interfaces/interface=Loopback123"

response = requests.get(url=url, headers=headers, auth=("admin", "C1sco12345"), verify=False)
rprint(response.json())