"""S3-compatible storage service (Minio / AWS S3).

Handles uploading and URL generation for offline content packs.
"""
import json
import logging
from io import BytesIO

import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                config=BotoConfig(signature_version="s3v4"),
            )
        return self._client

    def _pack_key(self, skill_id: str) -> str:
        return f"packs/{skill_id}.json"

    def upload_pack(self, skill_id: str, pack_data: dict) -> str:
        """Upload a JSON pack to S3 and return the object key."""
        key = self._pack_key(skill_id)
        body = json.dumps(pack_data, ensure_ascii=False).encode("utf-8")

        self.client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=BytesIO(body),
            ContentType="application/json",
            ContentLength=len(body),
        )
        logger.info("Uploaded pack %s (%d bytes)", key, len(body))
        return key

    def get_pack_url(self, skill_id: str) -> str:
        """Return the public URL for a pack (bucket has public-read policy)."""
        key = self._pack_key(skill_id)
        return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{key}"

    def generate_presigned_url(self, skill_id: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL (for private buckets)."""
        key = self._pack_key(skill_id)
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": key},
            ExpiresIn=expires_in,
        )

    def pack_exists(self, skill_id: str) -> bool:
        """Check if a pack already exists in S3."""
        key = self._pack_key(skill_id)
        try:
            self.client.head_object(Bucket=settings.S3_BUCKET, Key=key)
            return True
        except ClientError:
            return False

    def delete_pack(self, skill_id: str) -> None:
        """Delete a pack from S3."""
        key = self._pack_key(skill_id)
        self.client.delete_object(Bucket=settings.S3_BUCKET, Key=key)
        logger.info("Deleted pack %s", key)

    def ensure_bucket(self) -> None:
        """Create the bucket if it doesn't exist (dev convenience)."""
        try:
            self.client.head_bucket(Bucket=settings.S3_BUCKET)
        except ClientError:
            self.client.create_bucket(Bucket=settings.S3_BUCKET)
            logger.info("Created bucket %s", settings.S3_BUCKET)


s3_service = S3Service()
