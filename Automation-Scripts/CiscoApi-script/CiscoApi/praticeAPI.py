import requests
from rich import print as rprint

username = "devnetuser"
password = "Cisco123!"

GET_TOKEN_URL = "https://sandboxdnac.cisco.com/dna/system/api/v1/auth/token"
TOKEN_RESPONSE = requests.post(url=GET_TOKEN_URL, auth=(username, password), verify=False)
TOKEN = TOKEN_RESPONSE.json()["Token"]


MY_URL = "https://sandboxdnac.cisco.com/dna/intent/api/v1/network-device"
MY_HEADERS = {"X-Auth-Token": TOKEN}
MY_RESPONSE = requests.get(url=MY_URL, headers=MY_HEADERS, verify=False)
result = MY_RESPONSE.json()["response"]

for device in result:
    print(device["hostname"], device["macAddress"], device["managementIpAddress"])
