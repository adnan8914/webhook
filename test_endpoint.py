import requests
import json

# Test the root endpoint
print("Testing root endpoint (GET /):")
try:
    response = requests.get("https://webhook--mdadnan17.replit.app/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("✓ Root endpoint is working!\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test the webhook endpoint (POST /inbound-call)
print("Testing webhook endpoint (POST /inbound-call):")
try:
    # Simulate Twilio form data
    test_data = {
        "From": "+1234567890",
        "To": "+0987654321"
    }
    response = requests.post(
        "https://webhook--mdadnan17.replit.app/inbound-call",
        data=test_data
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response Content Type: {response.headers.get('content-type')}")
    print(f"Response (first 500 chars): {response.text[:500]}")
    
    if response.status_code == 200:
        print("✓ Webhook endpoint is responding!")
    else:
        print(f"⚠ Webhook returned status {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

