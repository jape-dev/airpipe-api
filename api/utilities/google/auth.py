from google_auth_oauthlib.flow import Flow
import hashlib
import os
from api.config import Config
from pathlib import Path
from api.utilities.google.secret import Secret


DOMAIN_URL = Config.DOMAIN_URL
CLIENT_SECRETS_PATH = Config.CLIENT_SECRETS_PATH
SCOPE = "https://www.googleapis.com/auth/adwords"
REDIRECT_URI = f"{DOMAIN_URL}/connector/google/oauth2_callback"

# p = Path(__file__).with_name(CLIENT_SECRETS_PATH)
# filename = p.absolute()
filename = CLIENT_SECRETS_PATH


def authorize():
    flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE])
    flow.redirect_uri = REDIRECT_URI

    # Create an anti-forgery state token as described here:
    # https://developers.google.com/identity/protocols/OpenIDConnect#createxsrftoken
    passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        state=passthrough_val,
        prompt="consent",
        include_granted_scopes="true",
    )

    return {"authorization_url": authorization_url, "passthrough_val": passthrough_val}


def oauth2callback(passthrough_val, state, code, token):
    if passthrough_val != state:
        raise ValueError("State does not match")

    flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE])
    flow.redirect_uri = REDIRECT_URI

    flow.fetch_token(code=code)

    refresh_token = flow.credentials.refresh_token
    # return refresh_token
    secret = Secret(token)
    secret.create_secret_version(refresh_token)
