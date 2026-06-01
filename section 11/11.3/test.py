import requests
url = "http://127.0.0.1:5000/items"

data = {
    "name":"papaya"
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())