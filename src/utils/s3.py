"""
Docstring for lambda.s3_config
"""
import boto3
from app_config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION
)

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Create function to upload to S3
def upload_to_s3(document, content_type, bucket: str, object_name: str = None):
    """
    Docstring for upload_to_s3
    
    :param file_name: Description
    :type file_name: str
    :param bucket: Description
    :type bucket: str
    :param object_name: Description
    :type object_name: str
    """
    if object_name is None:
        object_name = file_name
    try:
        s3_client.put_object(
            Bucket=bucket,
            Key=object_name,
            Body=document,
            ContentType=content_type
        )
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False
    return True

# Create function to download from S3
def download_from_s3(bucket: str, object_name: str):
    """
    Docstring for download_from_s3
    
    :param bucket: Description
    :type bucket: str
    :param object_name: Description
    :type object_name: str
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=object_name)
        return response['Body'].read()
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return None

# Create function to delete from S3
def delete_from_s3(bucket: str, object_name: str):
    """
    Docstring for delete_from_s3
    
    :param bucket: Description
    :type bucket: str
    :param object_name: Description
    :type object_name: str
    """
    try:
        s3_client.delete_object(Bucket=bucket, Key=object_name)
    except Exception as e:
        print(f"Error deleting file from S3: {e}")
        return False
    return True