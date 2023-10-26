from google.cloud import storage
import requests
import urllib.parse

# ************* SET THESE VARIABLES *************
GCS_BUCKET_NAME = "YOUR_GCS_BUCKET_NAME"
ROBOFLOW_API_KEY = "YOUR_ROBOFLOW_API_KEY"
ROBOFLOW_PROJECT_NAME = "YOUR_ROBOFLOW_PROJECT_NAME"
GOOGLE_APPLICATION_CREDENTIALS = "path/to/your-service-account-file.json"
# ***********************************************

def get_gcs_signed_url(bucket_name: str, blob_name: str) -> str:
    """Generate a signed URL for a GCS object."""
    storage_client = storage.Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    
    url = blob.generate_signed_url(
        version="v4",
        expiration=3600,  # 1 hour in seconds
        method="GET"
    )
    return url

def get_gcs_objects(bucket_name: str) -> list:
    """Fetch the list of object keys in the given GCS bucket."""
    storage_client = storage.Client.from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs()

    object_names = []
    for blob in blobs:
        object_names.append(blob.name)
    return object_names

def upload_to_roboflow(api_key: str, project_name: str, presigned_url: str, img_name='', split="train"):
    """Upload an image to Roboflow."""
    API_URL = "https://api.roboflow.com"
    if img_name == '':
        img_name = presigned_url.split("/")[-1]

    upload_url = "".join([
        API_URL + "/dataset/" + project_name + "/upload",
        "?api_key=" + api_key,
        "&name=" + img_name,
        "&split=" + split,
        "&image=" + urllib.parse.quote_plus(presigned_url),
    ])
    response = requests.post(upload_url)

    # Check response code
    if response.status_code == 200:
        print(f"Successfully uploaded {img_name} to {project_name}")
        return True
    else:
        print(f"Failed to upload {img_name}. Error: {response.content.decode('utf-8')}")
        return False

if __name__ == "__main__":
    # Fetch list of available blobs
    available_blobs = get_gcs_objects(GCS_BUCKET_NAME)
    
    # Optional: Filter the blobs here
    # e.g., available_blobs = [blob for blob in available_blobs if "some_condition"]
    
    # Upload blobs to Roboflow
    for blob in available_blobs:
        blob_url = get_gcs_signed_url(GCS_BUCKET_NAME, blob)
        upload_to_roboflow(ROBOFLOW_API_KEY, ROBOFLOW_PROJECT_NAME, blob_url)
