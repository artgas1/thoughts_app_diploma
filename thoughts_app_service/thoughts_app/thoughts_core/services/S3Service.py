import os
import boto3
from .logger import logger

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
HOST = "https://s3.timeweb.cloud"
REGION = "ru-1"


class S3Service:
    # TODO: add crud for covers

    @staticmethod
    def upload_file(upload_file):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            endpoint_url=HOST,
            region_name=REGION,
        )

        try:
            response = s3.put_object(
                Bucket=S3_BUCKET_NAME, Key=upload_file.name, Body=upload_file
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                logger.info("File uploaded successfully.")
                return True
            else:
                logger.error("Failed to upload file.")
                return False
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False

    @staticmethod
    def get_file(key):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            endpoint_url=HOST,
            region_name=REGION,
        )

        try:
            response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
            file_content = response["Body"].read()
            return file_content
        except Exception as e:
            logger.error(f"Failed to retrieve file: {e}")
