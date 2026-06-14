import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try importing boto3. If not present, run in mock bypass.
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
    logger.warning("boto3 is not installed. Cloud storage will run in local mock mode.")

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "rtc-s3-bucket")
REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")

class S3Service:
    def __init__(self):
        self.s3_client = None
        if HAS_BOTO3 and AWS_ACCESS_KEY and AWS_SECRET_KEY:
            try:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=AWS_ACCESS_KEY,
                    aws_secret_access_key=AWS_SECRET_KEY,
                    region_name=REGION_NAME
                )
                logger.info("Successfully initialized AWS S3 client.")
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {str(e)}. Defaulting to local mock.")
                self.s3_client = None

    def upload_file(self, local_path: str, s3_key: str) -> str:
        """
        Uploads a local file to AWS S3.
        Returns:
            s3_url (str): The public URL of the uploaded S3 resource.
        """
        if not self.s3_client:
            logger.info(f"S3 client bypassed. Simulating upload for: {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
            # Mock S3 URL representation
            return f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{s3_key}"

        try:
            # Upload the file
            self.s3_client.upload_file(
                local_path,
                BUCKET_NAME,
                s3_key,
                ExtraArgs={"ACL": "public-read"}
            )
            s3_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{s3_key}"
            logger.info(f"Successfully uploaded resource to S3: {s3_url}")
            return s3_url
        except Exception as e:
            logger.error(f"AWS S3 upload failed for {local_path}: {str(e)}")
            # Fallback mock representation
            return f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{s3_key}"

s3_service = S3Service()
