import boto3
from django.conf import settings

def upload_to_s3(file_id,file,content_type):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    s3_key = f"uploads/{file_id}"

    if isinstance(file, str):
        with open(file, "rb") as f:
            s3_client.upload_fileobj(
                f, 
                settings.AWS_STORAGE_BUCKET_NAME, 
                s3_key,
                ExtraArgs={"ContentType": content_type if content_type else "application/octet-stream"}
            )
    else:
        s3_client.upload_fileobj(
            file, 
            settings.AWS_STORAGE_BUCKET_NAME, 
            s3_key, 
            ExtraArgs={"ContentType": content_type if content_type else "application/octet-stream"}
        )

    # file_url = f"{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
    # return file_url

