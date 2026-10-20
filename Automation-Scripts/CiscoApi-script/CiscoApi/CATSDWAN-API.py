import requests
from rich import print as rprint

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

username = "devnetuser"
password = "RG!_Yw919_83"

cookie_url = "https://sandbox-sdwan-2.cisco.com/j_security_check"
cookie_body = {"j_username": username,
        "j_password": password}
cookie_headers = {"Content-Type": "application/x-www-form-urlencoded"}

cookie_response = requests.post(url=cookie_url, data=cookie_body, headers=cookie_headers, verify=False)
jsession_cookie = cookie_response.cookies["JSESSIONID"]

token_url = "https://sandbox-sdwan-2.cisco.com/dataservice/client/token"
cookies = {"JSESSIONID": jsession_cookie}
token_response = requests.get(url=token_url, cookies=cookies, verify=False)
csrf_token = token_response.text

endpoint_url = "https://sandbox-sdwan-2.cisco.com/dataservice/device"
endpoint_headers = {"X-XSRF-TOKEN": csrf_token}
endpoint_response = requests.get(url=endpoint_url, headers=endpoint_headers, cookies=cookies, verify=False)
rprint(endpoint_response.json())