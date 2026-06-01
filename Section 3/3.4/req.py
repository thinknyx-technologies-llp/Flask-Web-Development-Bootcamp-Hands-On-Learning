import requests
url = "http://127.0.0.1:5000/posts"
data = {"title": "Hello from thinknyx"}

response = requests.post(url, json = data)
print(response.json())