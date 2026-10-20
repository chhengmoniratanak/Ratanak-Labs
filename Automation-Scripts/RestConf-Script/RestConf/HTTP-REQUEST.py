import requests

requests.packages.urllib3.disable_warnings()

headers = {"Accept": "application/json"}
url = "https://gorest.co.in/public/v2/users"

response = requests.get(url=url, headers=headers, verify=False)
print(response.json()[0]["email"])