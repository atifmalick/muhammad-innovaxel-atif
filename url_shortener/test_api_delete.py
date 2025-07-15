import requests

shortcode = "cBe6fr"  # replace with your existing shortcode if needed

url = f"http://127.0.0.1:5000/shorten/{shortcode}"

response = requests.delete(url)
print("Status Code:", response.status_code)

if response.status_code == 204:
    print("Short URL deleted successfully!")
else:
    print("Failed to delete — maybe already deleted or invalid shortcode.")
