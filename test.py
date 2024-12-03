import requests
import json

# Endpoint URL
url = "http://127.0.0.1:5000/predict"  # Use your local Flask server URL

# Sample payload with symptoms
payload = {
    "symptoms": ["fever", "cough", "fatigue"]
}

# Make a POST request
try:
    response = requests.post(url, json=payload)

    # Check the status code
    if response.status_code == 200:
        print("Success!")
        print("Response Data:", response.json())
    else:
        print(f"Failed with status code: {response.status_code}")
        print("Response Content:", response.text)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
