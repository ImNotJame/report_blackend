import boto3
import logging
from botocore.config import Config
from app.config import (
    R2_ENDPOINT,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    R2_PUBLIC_URL
)

logger = logging.getLogger("report-backend")

# Initialize boto3 S3 client for Cloudflare R2
try:
    r2_client = boto3.client(
        service_name="s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4")
    )
    logger.info("Initialized Cloudflare R2 client successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Cloudflare R2 client: {str(e)}")
    r2_client = None

def upload_file_to_r2(file_content: bytes, unique_name: str, content_type: str) -> str:
    """
    Uploads a file to the Cloudflare R2 bucket and returns its public URL.
    """
    if not r2_client:
        raise Exception("R2 client is not initialized.")
        
    try:
        logger.info(f"Uploading file {unique_name} to Cloudflare R2 bucket: {R2_BUCKET_NAME}")
        r2_client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=unique_name,
            Body=file_content,
            ContentType=content_type
        )
        public_url = f"{R2_PUBLIC_URL}/{unique_name}"
        logger.info(f"File uploaded successfully. Public URL: {public_url}")
        return public_url
    except Exception as e:
        logger.error(f"Cloudflare R2 upload failed for {unique_name}: {str(e)}")
        raise Exception(f"R2 upload failed: {str(e)}")


def get_file_from_r2(file_key: str):
    """
    Downloads a file from Cloudflare R2 and returns the object response.
    """
    if not r2_client:
        raise Exception("R2 client is not initialized.")

    try:
        return r2_client.get_object(Bucket=R2_BUCKET_NAME, Key=file_key)
    except Exception as e:
        logger.error(f"Cloudflare R2 download failed for {file_key}: {str(e)}")
        raise Exception(f"R2 download failed: {str(e)}")
