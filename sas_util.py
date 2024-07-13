import datetime
import google.auth.credentials
from google.cloud import storage
from google.auth.transport.requests import Request
import google.auth


def generate_signed_url(gs_uri: str):
    bucket_name = gs_uri.split("//")[1].split("/")[0]
    blob_name = gs_uri.split("//")[1].split("/", 1)[1]

    bucket = storage.Client().bucket(bucket_name)
    blob = bucket.blob(blob_name)

    credentials, _ = google.auth.default()

    try:
        if not credentials.token:
            credentials.refresh(Request())
    except:
        pass

    return blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15),
        method="GET",
        access_token=credentials.token,
        service_account_email=credentials.service_account_email,
    )
