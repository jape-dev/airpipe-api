from google_auth_oauthlib.flow import Flow
import hashlib
import os
from api.config import Config
from pathlib import Path
from api.core.static_data import ChannelType


DOMAIN_URL = Config.DOMAIN_URL
CLIENT_SECRETS_PATH = Config.CLIENT_SECRETS_PATH
SCOPE_GOOGLE_ADS = "https://www.googleapis.com/auth/adwords"
SCOPE_GOOGLE_ANALYTICS = "https://www.googleapis.com/auth/analytics.readonly"
SCOPE_GOOGLE_SHEETS = "https://www.googleapis.com/auth/spreadsheets"
SCOPE_YOUTUBE = ["https://www.googleapis.com/auth/yt-analytics-monetary.readonly", "https://www.googleapis.com/auth/yt-analytics.readonly", "https://www.googleapis.com/auth/youtube.readonly"]
REDIRECT_URI = f"{DOMAIN_URL}/connector/google/oauth2_callback"

# p = Path(__file__).with_name(CLIENT_SECRETS_PATH)
# filename = p.absolute()
filename = CLIENT_SECRETS_PATH


def authorize(channel_type: ChannelType = ChannelType.google):
    if channel_type == ChannelType.google:
        flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE_GOOGLE_ADS])
        print("scope set to google ads")
    elif channel_type == ChannelType.google_analytics:
        flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE_GOOGLE_ANALYTICS])
        print("scope set to google analytics")
    elif channel_type == ChannelType.sheets:
        flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE_GOOGLE_SHEETS])
        print("scope set to google sheets")
    elif channel_type == ChannelType.youtube:
        flow = Flow.from_client_secrets_file(filename, scopes=SCOPE_YOUTUBE)
        print("scope set to youtube")
    else:
        raise ValueError("Channel must be google or google analytics")

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


def oauth2callback(
    passthrough_val, state, code, token, channel_type: ChannelType = ChannelType.google
):
    if passthrough_val != state:
        raise ValueError("State does not match")
    if channel_type == ChannelType.google:
        flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE_GOOGLE_ADS])
        print("scope set to google ads")
    elif channel_type == ChannelType.google_analytics:
        flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE_GOOGLE_ANALYTICS])
        print("scope set to google analytics")
    elif channel_type == ChannelType.sheets:
        flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE_GOOGLE_SHEETS])
        print("scope set to google sheets")
    elif channel_type == ChannelType.youtube:
        flow = Flow.from_client_secrets_file(filename, scopes=[SCOPE_YOUTUBE])
        print("scope set to youtube")
    else:
        raise ValueError("Channel must be google, google_analytics or sheets")

    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)

    refresh_token = flow.credentials.refresh_token

    return refresh_token
