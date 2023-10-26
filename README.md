# Uploading Images to Roboflow using Presigned URLs

This repository contains a script for uploading images to a Roboflow project using presigned URLs. The script supports AWS S3, Azure Blob Storage, and Google Cloud Storage.

## Table of Contents
1. [Requirements](#requirements)
2. [Flow Overview](#flow-overview)
3. [Getting Started](#getting-started)
    - [AWS S3](#aws-s3)
    - [Azure Blob Storage](#azure-blob-storage)
    - [Google Cloud Storage](#google-cloud-storage)
4. [Usage](#usage)

## Requirements
- Python 3.x
- boto3 for AWS S3
- azure-storage-blob for Azure
- google-cloud-storage for Google Cloud

## Flow Overview
1. Load configuration from a YAML file.
2. Fetch the list of object keys from the respective cloud storage.
3. Load a set of already uploaded image IDs.
4. Generate a presigned URL for each image.
5. Upload the image to Roboflow using the presigned URL.
6. Save the IDs of successfully uploaded images.

## Getting Started

### AWS S3

Install the AWS SDK for Python (`boto3`):

```bash
pip install boto3
```

Code to generate a presigned URL:

```python
import boto3
from botocore.config import Config

def generate_presigned_url_aws(bucket_name, object_name, region='us-east-2'):
    s3 = boto3.client('s3', region_name=region, config=Config(signature_version='s3v4'))
    url = s3.generate_presigned_url('get_object',
                                    Params={'Bucket': bucket_name, 'Key': object_name},
                                    ExpiresIn=3600)
    return url
```

### Azure Blob Storage

Install the Azure Blob Storage client library for Python:

```bash
pip install azure-storage-blob
```

Code to generate a signed URL:

```python
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

def generate_signed_url_azure(blob_service_client, container_name, blob_name):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    sas_token = generate_blob_sas(blob_service_client.account_name,
                                  container_name,
                                  blob_name,
                                  account_key=blob_service_client.credential.account_key,
                                  permission=BlobSasPermissions(read=True),
                                  expiry=datetime.utcnow() + timedelta(hours=1))
    url = blob_client.url + '?' + sas_token
    return url
```

### Google Cloud Storage

Install the Google Cloud Storage client library for Python:

```bash
pip install google-cloud-storage
```

Code to generate a signed URL:

```python
from google.cloud import storage

def generate_signed_url_gcp(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(expiration=datetime.timedelta(hours=1), method='GET')
    return url
```

## Usage

Load the configuration, fetch object keys, and generate presigned URLs, then use `upload_to_roboflow()` to upload images. Save uploaded image IDs to avoid re-uploads.

```python
import requests
import urllib.parse

API_URL = "https://api.roboflow.com"

def upload_single_image_to_roboflow(api_key: str, project_name: str, signed_url: str, image_name: str, split: str = "train") -> bool:
    """
    Uploads a single image to Roboflow using a signed URL.

    Args:
        api_key (str): Your Roboflow API key.
        project_name (str): Your Roboflow project name.
        signed_url (str): The signed URL for the image you want to upload.
        image_name (str): The name you want to give to the image.
        split (str): The data split you want to assign to the image (train/test/val).
    
    Returns:
        bool: True if upload was successful, False otherwise.
    """
  
    # Construct the upload URL for Roboflow API
    upload_url = "".join(
        [
            API_URL + "/dataset/" + project_name + "/upload",
            "?api_key=" + api_key,
            "&name=" + image_name,
            "&split=" + split,
            "&image=" + urllib.parse.quote_plus(signed_url)
        ]
    )
    
    # Make the POST request to upload the image
    response = requests.post(upload_url)
    
    if response.status_code == 200:
        print(f"Successfully uploaded {image_name} to {project_name}")
        return True
    else:
        print(f"Failed to upload {image_name}. Error: {response.content.decode('utf-8')}")
        return False

# Example usage
api_key = "YOUR_API_KEY"
project_name = "YOUR_PROJECT_NAME"
signed_url = "YOUR_SIGNED_URL"
image_name = "example_image.jpg"

upload_single_image_to_roboflow(api_key, project_name, signed_url, image_name)
```

Replace the placeholders (`YOUR_API_KEY`, `YOUR_PROJECT_NAME`, `YOUR_SIGNED_URL`) with your actual values, then run the script to upload the image.