# S3 Signed URL to Roboflow Image Uploader

This script automates the process of sampling images from an AWS S3 bucket and uploading them to a Roboflow project for annotation. The script avoids uploading duplicate images by maintaining a local JSON file containing IDs of already uploaded images.

## Breakdown
1. Configuration Loading
The script uses the PyYAML library to read configuration parameters like the AWS S3 bucket name, Roboflow API key, and other settings from a config.yaml file. This makes it easy to change settings without modifying the code.

2. S3 Interaction
The script uses Amazon's boto3 library to interact with the S3 service. Specifically, it fetches a list of all images in a specified bucket and generates presigned URLs for a subset of these images. The presigned URLs are temporary and allow secure access to the S3 objects.

3. Roboflow API
The script uses the requests library to interact with Roboflow's API. It uploads images to a specific Roboflow project using their API by sending POST requests. The API key and project name are specified in the configuration file.

4. Duplication Check
To avoid uploading duplicates, the script maintains a local JSON file (uploaded_images.json). This file stores the IDs of images that have already been uploaded to Roboflow. Before uploading a new batch of images, the script checks this file to skip over any duplicates.

5. Logging and Output
The script prints out useful information such as the total number of images in the S3 bucket and the number of images already uploaded. It also provides feedback on the upload process, indicating success, failure, or duplication for each image.

## Features

- Fetches a list of all image files from a specified AWS S3 bucket.
- Generates presigned URLs for a sample of these images.
- Uploads the sampled images to a specified Roboflow project using their API.
- Keeps track of uploaded images to avoid duplicates.

## Dependencies

- Python 3.x
- boto3
- requests
- PyYAML
- roboflow

To install dependencies, run:

```bash
pip install boto3 requests PyYAML roboflow
```

## AWS Configuration

Before using the script, ensure you've set up AWS CLI with the necessary authentication credentials. This will allow you to access and manage the desired S3 bucket.

### Installing the AWS CLI

If you haven't already installed the AWS CLI, you can do so by following the official installation guide:
- [Installing the AWS CLI version 2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)

### Configuring the AWS CLI

1. Once you've installed the AWS CLI, open a terminal or command prompt.
2. Run the following command:

   ```bash
   aws configure
   ```

3. You'll be prompted to enter your AWS credentials:

   ```
   AWS Access Key ID [None]: YOUR_ACCESS_KEY
   AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
   Default region name [None]: YOUR_PREFERRED_REGION (e.g., us-west-1)
   Default output format [None]: json
   ```

   Make sure to replace `YOUR_ACCESS_KEY`, `YOUR_SECRET_ACCESS_KEY`, and `YOUR_PREFERRED_REGION` with your actual AWS details. It's recommended to set the output format to `json` for easier parsing.

**Security Note:** Always keep your AWS credentials confidential to prevent misuse. Avoid uploading or sharing configuration files containing your access and secret keys. If using a public version control system like GitHub, make sure to ignore files that might contain sensitive information.

## Program Configuration

Configuration parameters such as the S3 bucket name, sample size, Roboflow API key, and project name should be specified in a `config.yaml` file.

Example:

```yaml
bucket_name: "your-bucket-name"
sample_size: 10
uploaded_images_file: "uploaded_images.json"
region: "us-east-2"
roboflow:
  api_key: "YOUR_API_KEY"
  project_name: "YOUR_PROJECT_NAME"
```

## Usage

1. Place the `config.yaml` file in the same directory as the script.
2. Run the script.

```bash
python S3_url_upload.py
```

## Output

The script will:

1. Print the total number of images in the S3 bucket and the number of images already uploaded.
2. Upload a sample of images to Roboflow.
3. Update the `uploaded_images.json` file with new IDs.