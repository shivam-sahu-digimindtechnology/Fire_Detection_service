import os
import boto3
from datetime import datetime, timezone
import threading

from app.core.config import (
    AWS_SECRET_ACCESS_KEY,
    AWS_ACCESS_KEY_ID,
    S3_BUCKET_NAME,
    S3_FOLDER,
    S3_URL
)

class S3StorageService:
    def __init__(self):
        self.access_key = AWS_ACCESS_KEY_ID
        self.secret_key = AWS_SECRET_ACCESS_KEY
        self.bucket_name = S3_BUCKET_NAME
        
        # Ensure base folder ends with a slash if provided, e.g. "company_doc/"
        raw_folder = S3_FOLDER if S3_FOLDER else "company_doc"
        self.base_folder = raw_folder.strip("/")
        
        self.s3_url_prefix = S3_URL
        self.s3_client = None

        if self.access_key and self.secret_key and self.bucket_name:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key
                )
                print("✅ AWS S3 Connection Initialized Successfully.")
            except Exception as e:
                print(f"❌ Error initializing AWS S3 Connection: {e}")

    def generate_s3_key(self, filename, is_image_or_clip=False):
        now = datetime.now(timezone.utc)
        date_folder = now.strftime("%d-%m-%Y")

        # Path: company_doc/fire_detection_data/DD-MM-YYYY/images/filename
        if is_image_or_clip:
            s3_key = f"{self.base_folder}/fire_detection_data/{date_folder}/images/{filename}"
        else:
            s3_key = f"{self.base_folder}/fire_detection_data/{date_folder}/{filename}"

        return s3_key

    def _upload_worker(self, file_path, s3_key, content_type):
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_file(
                Filename=str(file_path),
                Bucket=self.bucket_name,
                Key=s3_key,
                ExtraArgs=extra_args
            )
            print(f"☁️ S3 Uploaded Successfully: {s3_key}")
        except Exception as e:
            print(f"❌ S3 Upload Failed ({s3_key}): {e}")

    def upload_file_async(self, file_path, filename, is_image_or_clip=False, content_type=None):
        s3_key = self.generate_s3_key(filename, is_image_or_clip=is_image_or_clip)

        if self.s3_client:
            thread = threading.Thread(
                target=self._upload_worker,
                args=(file_path, s3_key, content_type),
                daemon=True
            )
            thread.start()

        # Dynamic S3 Public URL Return
        if self.s3_url_prefix:
            file_url = f"{self.s3_url_prefix.rstrip('/')}/{s3_key}"
        else:
            file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"

        return file_url