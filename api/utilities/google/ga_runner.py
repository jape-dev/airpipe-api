import os

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from api.config import Config
from api.utilities.google.secret import Secret
import sys

VERSION = "v13"
GOOGLE_ADS_DEVELOPER_TOKEN = Config.GOOGLE_ADS_DEVELOPER_TOKEN
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET

REFRESH_ERROR = "INVALID REFRESH TOKEN"


def create_client(token):
    try:
        secret = Secret(token)
        refresh_token = secret.get_secret_version()
        credentials = {
            "developer_token": GOOGLE_ADS_DEVELOPER_TOKEN,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "use_proto_plus": "true",
        }
        return GoogleAdsClient.load_from_dict(credentials, version=VERSION)
    except Exception as e:
        # Make a redirect page back to the Google Sign In Page
        raise ValueError(f"Invalid refresh token: {e}")


def handleGoogleAdsException(ex: GoogleAdsException):
    print(
        f'Request with ID "{ex.request_id}" failed with status '
        f'"{ex.error.code().name}" and includes the following errors:'
    )
    for error in ex.failure.errors:
        print(f'\tError with message "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)
