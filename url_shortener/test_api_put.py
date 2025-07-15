import requests

shortcode = "cBe6fr"  # replace with your generated shortcode if different
new_url = "https://updated-example.com"

url = f"http://127.0.0.1:5000/shorten/{shortcode}"
data = {
    "url": new_url
}

response = requests.put(url, json=data)
print("Status Code:", response.status_code)
print("Response JSON:", response.json())
