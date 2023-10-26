import boto3
from botocore.config import Config
import json
import yaml
from roboflow.config import API_URL
import os
import urllib
import requests

def load_config(file_path: str = "config.yaml") -> dict:
    """
    Load configuration from a YAML file.
    
    Args:
        file_path (str, optional): The path to the configuration file. Defaults to "config.yaml".
    
    Returns:
        dict: The configuration loaded from the file as a dictionary.
    """
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def get_s3_objects(bucket_name: str):
    """
    Fetch the list of object keys in the given S3 bucket.
    
    Args:
        bucket_name (str): The name of the S3 bucket.
        
    Returns:
        list: A list containing the object keys in the S3 bucket.
    """
    s3 = boto3.client('s3')
    objects = []
    response = s3.list_objects_v2(Bucket=bucket_name)
    for obj in response['Contents']:
        objects.append(obj['Key'])
    return objects

def load_uploaded_images(file_path: str) -> set:
    """
    Load a set of uploaded image IDs from a local file.
    
    Args:
        file_path (str): The path to the local file.
        
    Returns:
        set: A set containing the IDs of uploaded images.
    """
    try:
        with open(file_path, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_uploaded_images(file_path: str, uploaded_image_ids: set):
    """
    Save the set of uploaded image IDs to a local file.
    
    Args:
        file_path (str): The path to the local file.
        uploaded_image_ids (set): The set containing the IDs of uploaded images.
    """
    with open(file_path, 'w') as f:
        json.dump(list(uploaded_image_ids), f)

def generate_presigned_url(bucket_name: str, object_name: str, region: str = 'us-east-2') -> str:
    """
    Generate a presigned URL for an S3 object.
    
    Args:
        bucket_name (str): The name of the S3 bucket.
        object_name (str): The name of the S3 object.
        region (str, optional): The AWS region where the bucket resides. Defaults to 'us-east-2'.
        
    Returns:
        str: A presigned URL for the specified S3 object.
    """
    s3 = boto3.client('s3', region_name=region, config=Config(signature_version='s3v4'))
    url = s3.generate_presigned_url('get_object',
                                    Params={'Bucket': bucket_name, 'Key': object_name},
                                    ExpiresIn=3600)
    return url

def upload_to_roboflow(rf_config, presigned_url: str, img_name='', split="train"):
    """
    Upload an image to Roboflow.
    
    Args:
        rf_config (dict): The configuration for the Roboflow API.
        presigned_url (str): The presigned URL of the image to upload.
        img_name (str, optional): The name of the image. Defaults to the basename of the URL.
        split (str, optional): The data split for the image. Defaults to 'train'.
        
    Returns:
        Union[str, bool]: Returns the image ID if successful, False otherwise.
    """
    # Check if specified image name
    if img_name == '':
        img_name=os.path.basename(presigned_url)

    """Upload an image to Roboflow."""
    # Generate API URL:
    upload_url = "".join(
        [
            API_URL + "/dataset/" + rf_config['project_name'] + "/upload",
            "?api_key=" + rf_config['api_key'] ,
            "&name=" + img_name,
            "&split=" + split,
            "&image=" + urllib.parse.quote_plus(presigned_url),
        ]
    )
    # Get response
    response = requests.post(upload_url)

    # Parse response
    responsejson = None
    # Get json
    try:
        responsejson = response.json()
    except:
        pass
    # Check status code
    if response.status_code == 200:
        if responsejson:
            if "duplicate" in responsejson.keys():
                print(f"\tDuplicate image, did not upload: {presigned_url}")
            elif not responsejson.get("success"):
                print(f"Server rejected image: {responsejson}")
                return False
            else:
                print(f"\tUploaded image {img_name} to Roboflow")
            return responsejson.get("id")
        else:
            print(f"\tupload image {image_path} 200 OK, weird response: {response}")
            return False
    else:
        if responsejson:
            print(f"\tBad response: {response.status_code}: {responsejson}")
        else:
            print(f"\tBad response: {response}")
        return False

if __name__ == "__main__":
    # Load configurations
    config = load_config()

    # Step 1: Get S3 objects
    all_images = get_s3_objects(config['bucket_name'])

    # Step 2: Load already uploaded images
    uploaded_image_ids = set(load_uploaded_images(config['uploaded_images_file']))

    # Print image counts
    print(f"Total images in S3 bucket: {len(all_images)}")
    print(f"Number of images already uploaded: {len(uploaded_image_ids)}")

    # Step 3: Filter out already uploaded images
    remaining_images = [img for img in all_images if img not in uploaded_image_ids]

    # Step 4, 5, and 6: Generate presigned URLs, upload and save uploaded images
    for img in remaining_images[:config['sample_size']]:
        presigned_url = generate_presigned_url(config['bucket_name'], img, config['region'])
        image_id = upload_to_roboflow(config['roboflow'], presigned_url)
        
        # Add image_id to set if it's not False
        if image_id:
            uploaded_image_ids.add(img)

        # Save that image was uploaded (Can do this after loop too to reduce number of saves)
        save_uploaded_images(config['uploaded_images_file'], uploaded_image_ids)
