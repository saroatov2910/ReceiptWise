import uuid
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def upload_image_to_s3(file_bytes: bytes, content_type: str) -> str:
    """Upload image bytes to S3 and return the public URL."""
    ext = content_type.split("/")[-1]
    key = f"receipts/{uuid.uuid4()}.{ext}"

    client = get_s3_client()
    client.put_object(
        Bucket=settings.AWS_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )

    url = f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
    return url


def delete_image_from_s3(image_url: str) -> None:
    """Delete an image from S3 by its URL. Silently ignores errors."""
    try:
        if not image_url or settings.AWS_BUCKET_NAME not in image_url:
            return
        key = image_url.split(f".amazonaws.com/")[-1]
        client = get_s3_client()
        client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)
    except ClientError:
        pass
