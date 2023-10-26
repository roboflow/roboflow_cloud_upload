import boto3
import requests
import urllib.parse
from botocore.config import Config

# ************* SET THESE VARIABLES *************
S3_BUCKET_NAME = "roboflowpulltestimages"
ROBOFLOW_API_KEY = "zZehudVV984QOf28TYFB"
ROBOFLOW_PROJECT_NAME = "vacuum-challenge"
# ***********************************************

def generate_presigned_url(bucket_name: str, object_name: str, region: str = 'us-east-2') -> str:
    """Generate a presigned URL for an S3 object."""
    s3 = boto3.client('s3', region_name=region, config=Config(signature_version='s3v4'))
    url = s3.generate_presigned_url('get_object',
                                    Params={'Bucket': bucket_name, 'Key': object_name},
                                    ExpiresIn=3600)
    return url

def get_s3_objects(bucket_name: str) -> list:
    """Fetch the list of object keys in the given S3 bucket."""
    s3 = boto3.client('s3')
    objects = []
    response = s3.list_objects_v2(Bucket=bucket_name)
    for obj in response['Contents']:
        objects.append(obj['Key'])
    return objects

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
    # Fetch list of available images
    available_images = get_s3_objects(S3_BUCKET_NAME)
    
    # Optional: Filter the images here
    # e.g., available_images = [img for img in available_images if "some_condition"]
    
    # Upload images to Roboflow
    for image in available_images:
        presigned_url = generate_presigned_url(S3_BUCKET_NAME, image)
        upload_to_roboflow(ROBOFLOW_API_KEY, ROBOFLOW_PROJECT_NAME, presigned_url)
