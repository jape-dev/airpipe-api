from google.oauth2 import id_token
from google.auth.transport import requests
from google.cloud import secretmanager
from api.config import Config
import google_crc32c
import os
from pathlib import Path

CLIENT_ID = Config.GOOGLE_CLIENT_ID
PROJECT_ID = Config.GOOGLE_PROJECT_ID
PROJECT_NUMBER = Config.GOOGLE_PROJECT_NUMBER
GOOGLE_APPLICATION_CREDENTIALS_PATH = Config.GOOGLE_APPLICATION_CREDENTIALS_PATH

p = Path(__file__).with_name(GOOGLE_APPLICATION_CREDENTIALS_PATH)
filename = p.absolute()
print(str(filename))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(filename)


class Secret:
    def __init__(self, token):
        # Get id from token.
        self.id = self.validate_token_get_id(token)
        self.client = secretmanager.SecretManagerServiceClient()

    def validate_token_get_id(self, token):
        # Validate token and return id.
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            return idinfo["sub"]
        except ValueError:
            print("INVALID REFRESH TOKEN")
            pass

    def create_secret_version(self, refresh_token):
        # Check if secret exists
        if not self.does_secret_exists():
            # If not, create secret
            parent = f"projects/{PROJECT_ID}"

            # Create the secret.
            self.client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": self.id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )

        # Create secret version under secret
        parent = self.client.secret_path(PROJECT_ID, self.id)

        # Convert the string payload into a bytes. This step can be omitted if you
        # pass in bytes instead of a str for the payload argument.
        payload = refresh_token.encode("UTF-8")

        # Calculate payload checksum. Passing a checksum in add-version request
        # is optional.
        crc32c = google_crc32c.Checksum()
        crc32c.update(payload)

        # Add the secret version.
        self.client.add_secret_version(
            request={
                "parent": parent,
                "payload": {
                    "data": payload,
                    "data_crc32c": int(crc32c.hexdigest(), 16),
                },
            }
        )

    def does_secret_exists(self):
        parent = f"projects/{PROJECT_ID}"

        # List all secret versions.
        for secret in self.client.list_secrets(request={"parent": parent}):
            secret_name = f"projects/{PROJECT_NUMBER}/secrets/{self.id}"
            if secret.name == secret_name:
                return True

        return False

    def get_secret_version(self):
        name = f"projects/{PROJECT_ID}/secrets/{self.id}/versions/latest"

        # Access the secret version.
        response = self.client.access_secret_version(request={"name": name})

        # Verify payload checksum.
        crc32c = google_crc32c.Checksum()
        crc32c.update(response.payload.data)
        if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            print("Data corruption detected.")
            return response

        return response.payload.data.decode("UTF-8")
