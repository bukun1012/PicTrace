import boto3
from django.conf import settings
from uuid import uuid4


def upload_to_s3(file):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    file_extension = file.name.split(".")[-1]
    file_name = f"avatars/{uuid4()}.{file_extension}"

    # 確定 Content-Type
    content_type = file.content_type if hasattr(file, "content_type") else "image/jpeg"

    try:
        file.seek(0)
        s3.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_name,
            ExtraArgs={
                "ContentType": content_type,  # 新增 Content-Type
                "ContentDisposition": "inline",  # ✅ 讓瀏覽器內嵌顯示，而不是下載
            },
        )

        file_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_name}"
        return file_url
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
