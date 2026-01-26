"""
Docstring for services.market
"""
import base64

from fastapi import HTTPException
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError


from src.models.market import Market
from src.utils.crud import get_with_filters
from src.utils.s3 import s3_client, download_from_s3


class MarketService:
    """
    Docstring for MarketService
    """
    @staticmethod
    async def list_market_items(db: Session):
        """
        Retrieves all market entries in the database
        """
        return await get_with_filters(Market, db, filters={})

    @staticmethod
    def get_market_object(item_id: str, bucket: str):
        """
        Retrieves a market object from storage by matching metadata id/title or filename
        """
        if not bucket:
            raise HTTPException(status_code=400, detail="Bucket name is required")

        continuation_token = None
        while True:
            list_kwargs = {"Bucket": bucket}
            if continuation_token:
                list_kwargs["ContinuationToken"] = continuation_token

            response = s3_client.list_objects_v2(**list_kwargs)
            for obj in response.get("Contents", []):
                key = obj.get("Key")
                if not key:
                    continue

                head = s3_client.head_object(Bucket=bucket, Key=key)
                metadata = head.get("Metadata", {})
                filename = key.split("/")[-1]
                stem = filename.rsplit(".", 1)[0]
                match_id = metadata.get("id") == item_id
                match_title = metadata.get("title") == item_id
                match_filename = stem == item_id
                if match_id or match_title or match_filename:
                    content = download_from_s3(bucket, key)
                    if content is None:
                        raise HTTPException(
                            status_code=502,
                            detail="Failed to download market object"
                        )
                    encoded = base64.b64encode(content).decode("ascii")
                    return {
                        "id": item_id,
                        "bucket": bucket,
                        "key": key,
                        "metadata": metadata,
                        "content_type": head.get("ContentType"),
                        "content_base64": encoded
                    }

            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken")

        raise HTTPException(status_code=404, detail="Market object not found")
    
