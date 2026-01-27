"""
Docstring for services.legislation
"""
from sqlalchemy.orm import Session
from src.utils.crud import get_with_filters, get_by_id
from src.models.legislation import Legislation
from src.utils.s3 import s3_client

class LegislationService:
    """
    Docstring for LegislationService
    """
    @staticmethod
    async def list_legislation(db: Session):
        """
        Retrieves all legislation entries in the database
        """
        legislation = await get_with_filters(Legislation, db, filters={})
        return legislation

    @staticmethod
    async def get_legislation_info(legislation_id, db: Session):
        """
        Retrieves detailed information about a specific legislation entry
        :param legislation_id: The ID of the legislation entry

        """
        # get legislation by id in metadata
        metadata_key = "id"
        bucket_name = "nova-legislation-bucket"
        paginator = s3_client.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' not in page:
                continue

            for obj in page['Contents']:
                response = s3_client.head_object(Bucket=bucket_name, Key=obj['Key'])

                metadata = response.get('Metadata', {})

                if metadata.get(metadata_key) == str(legislation_id):
                    legislation_object = s3_client.get_object(Bucket=bucket_name, Key=obj['Key'])
                    legislation_data = legislation_object['Body'].read()
                    return {
                        "data": legislation_data,
                        "metadata": metadata,
                        "filename": obj['Key']
                    }

        raise ValueError(f"Legislation with ID {legislation_id} not found in S3.")
