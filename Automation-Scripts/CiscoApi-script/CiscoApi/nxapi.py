import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

switchuser = 'admin'
switchpassword = 'admin'

auth_url = 'https://192.168.0.108/api/mo/aaaLogin.json'
auth_body = {
    "aaaUser": {
        "attributes": {
            "name": switchuser,
            "pwd": switchpassword
            }
        }
    }
auth_response = requests.post(
    auth_url, json=auth_body, timeout=5, verify=False).json()

token = auth_response['imdata'][0]['aaaLogin']['attributes']['token']

cookies = {}
cookies['APIC-Cookie'] = token
headers = {"content-type": "application/json"}

# Get the list of interfaces
interfaces_url = 'https://192.168.0.108/api/node/class/l1PhysIf.json?'
interfaces_response = requests.get(
    interfaces_url, headers=headers, cookies=cookies, verify=False).json()

print(interfaces_response)