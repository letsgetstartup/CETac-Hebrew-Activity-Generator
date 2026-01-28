import os
import vertexai
from vertexai.generative_models import GenerativeModel
import google.auth

# Setup environment
os.environ["GCP_PROJECT_ID"] = "cetac-fe437"
os.environ["GCP_REGION"] = "us-central1"
# model = "gemini-pro"
model = "gemini-1.0-pro"

print(f"Testing access to {model} in {os.environ['GCP_PROJECT_ID']} / {os.environ['GCP_REGION']}")

try:
    creds, project = google.auth.default()
    print(f"Authenticated as: {getattr(creds, 'service_account_email', 'User Credentials')}")
except Exception as e:
    print(f"Auth warning: {e}")

try:
    vertexai.init(project="cetac-fe437", location="us-central1")
    model_obj = GenerativeModel(model)
    response = model_obj.generate_content("Hello, can you hear me?")
    print("SUCCESS: Generation worked!")
    print(f"Response: {response.text}")
except Exception as e:
    print("FAILURE: Generation failed.")
    print(f"Error: {e}")
