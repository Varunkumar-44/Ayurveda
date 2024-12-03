import requests
import json

# Endpoint URL
url = "http://127.0.0.1:5000/feedback"  # Replace with your local Flask server URL

# Sample feedback payload
payload = {
    "disease": "bronchitis",  # Replace with the disease name you want to test
    "remedyIndex": 3          # Index of the remedy to prioritize (1-based)
}

# Make a POST request
try:
    response = requests.post(url, json=payload)

    # Check the status code
    if response.status_code == 200:
        print("Feedback successfully updated!")
        print("Response Data:", response.json())
    else:
        print(f"Failed with status code: {response.status_code}")
        print("Response Content:", response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
