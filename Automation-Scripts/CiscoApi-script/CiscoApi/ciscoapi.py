import requests
from rich import print as rprint

username = "devnetuser"
password = "RG!_Yw919_83"

cookies_url = "https://sandbox-sdwan-2.cisco.com/j_security_check"
cookies_body = {
    "j_username": username,
    "j_password": password
}
cookies_headers = {
    "Content-Type": "application/x-www-form-urlencoded"}

cookies_response = requests.post(url=cookies_url, data=cookies_body, headers=cookies_headers, verify=False)
jsession_cookie = cookies_response.cookies["JSESSIONID"]

token_url = "https://sandbox-sdwan-2.cisco.com/dataservice/client/token"
cookies = {"JSESSIONID": jsession_cookie}
token_response = requests.get(url=token_url, cookies=cookies, verify=False)
csrf_token = token_response.text

endpoint_url = "https://sandbox-sdwan-2.cisco.com/dataservice/device"
endpoint_headers = {"X-XSRF-TOKEN": csrf_token, "Cookie": f"JSESSIONID={jsession_cookie}"}
endpoint_response = requests.get(url=endpoint_url, headers=endpoint_headers, cookies=cookies, verify=False)
rprint(endpoint_response.json())
