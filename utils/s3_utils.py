import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError

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

def generate_presigned_url(object_key:str) -> str:
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={'Bucket': settings.AWS_AWS_STORAGE_BUCKET_NAME, 'Key': object_key},
            ExpiresIn=3600
        )
        return url
    except:
        return None
    
def delete_from_s3(object_key:str) -> bool:
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=object_key
        )
        return 
    except NoCredentialsError:
        return
    except Exception as e:
        # print(f"Error deleting file from S3: {e}")
        return 