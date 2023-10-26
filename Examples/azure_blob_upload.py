from azure.storage.blob import BlobServiceClient
import requests
import urllib.parse

# ************* SET THESE VARIABLES *************
AZURE_CONNECTION_STRING = "YOUR_AZURE_CONNECTION_STRING"
AZURE_CONTAINER_NAME = "YOUR_AZURE_CONTAINER_NAME"
ROBOFLOW_API_KEY = "YOUR_ROBOFLOW_API_KEY"
ROBOFLOW_PROJECT_NAME = "YOUR_ROBOFLOW_PROJECT_NAME"
# ***********************************************

def get_blob_sas_url(blob_service_client, container_name: str, blob_name: str) -> str:
    """Generate a SAS URL for an Azure Blob."""
    from azure.storage.blob import generate_blob_sas, BlobSasPermissions
    from datetime import datetime, timedelta

    sas_token = generate_blob_sas(
        blob_service_client.account_name,
        container_name,
        blob_name,
        account_key=blob_service_client.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    
    blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    return blob_url

def get_azure_blob_objects(container_name: str) -> list:
    """Fetch the list of blob names in the given Azure Blob container."""
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container_name)
    
    blobs = []
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        blobs.append(blob.name)
    return blobs

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
    available_blobs = get_azure_blob_objects(AZURE_CONTAINER_NAME)
    
    # Optional: Filter the blobs here
    # e.g., available_blobs = [blob for blob in available_blobs if "some_condition"]
    
    # Initialize Azure Blob Service Client
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    
    # Upload blobs to Roboflow
    for blob in available_blobs:
        blob_url = get_blob_sas_url(blob_service_client, AZURE_CONTAINER_NAME, blob)
        upload_to_roboflow(ROBOFLOW_API_KEY, ROBOFLOW_PROJECT_NAME, blob_url)
