import requests
from rich import print as rprint

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

username = "devnetuser"
password = "Cisco123!"

token_url = "https://sandboxdnac.cisco.com/dna/system/api/v1/auth/token"
token_response = requests.post(url=token_url, auth=(username, password), verify=False)
token = token_response.json()["Token"]

endpoint_url = "https://sandboxdnac.cisco.com/dna/intent/api/v1/network-device"
headers = {"X-Auth-Token": token}
endpoint_response = requests.get(url=endpoint_url, headers=headers, verify=False)
result = endpoint_response.json()["response"]
for device in result:
    print(device["hostname"], device["macAddress"], device["managementIpAddress"])