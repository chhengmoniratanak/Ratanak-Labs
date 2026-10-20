import requests
from rich import print as rprint

requests.packages.urllib3.disable_warnings()


url = "https://devnetsandboxiosxe.cisco.com:443/restconf/data/ietf-interfaces:interfaces/interface=Loopback123"

response = requests.delete(url=url, auth=("admin", "C1sco12345"), verify=False)
rprint(response)