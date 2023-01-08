from fastapi import APIRouter
import requests

access_token="EAA19FQdInKYBAOBg8ZADYYvufMgtZCr1RZB83JKkKcdicB3cKOCUA3Sjn62XCGN88BnnDKzQW7IBtwW3Vnvt4ZCnZACIFPNur2MNJxCfkGcpoMRhApwWfZAZC6kLgLCoTM80aQn35fZCcxsqMs44H0pG9SdKZC8ClPCI4tK8DZCgYPpnyX8GCybvtw"
sandbox_access_token="EAA19FQdInKYBAG88ZA63FRwkkZBAOzahnh63c0MrkjUkZBiK3MwO9GjDFsbcumcI49GQub4rjmWKAWRZCtKrdwepvqJf7ZA5MU2eRRHwf3j6usSACWYyQdImgZABqRwprsakoEQgUlvWluTSry67uH6U49oYyyTxHhVnFW11RO0lZBZBcZC2tzwN5kZCaNFm2SmnYZD"

router = APIRouter()

# Use this endpoint to parse the metric.
router.get("/facebook")
def facebook(metrics, dimensions, filters):
    metrics, dimensions, filters
    base = "https://graph.facebook.com/v15.00/me/messages?access_token=" + access_token



# create seperate functions for each metric I want to bring back into the data.