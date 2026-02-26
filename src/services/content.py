"""
Docstring for services.content
"""
import uuid
from datetime import datetime, timezone
from fastapi import  UploadFile, BackgroundTasks, Response

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from src.models.market import Market
from src.models.legislation import Legislation
from src.models.insight import Insight
from src.schema.content import FilterParams, SortField, SortOrder, ContentType

from src.utils.embeddings import index_document, delete_from_vector_db
from src.utils.s3 import upload_to_s3, delete_from_s3, download_from_s3

class ContentService:
    """
    Docstring for ContentService
    """
    CONTENT_MAP = {
        ContentType.market: {
            "model": Market,
            "bucket": "nova-market-trends-bucket",
        },
        ContentType.legislation: {
            "model": Legislation,
            "bucket": "nova-legislation-bucket",
        },
    }

    @staticmethod
    def list_content(db: Session, filters: FilterParams, apply_inner_sort: bool = True):
        """
        Docstring for list_content
        
        :param db: Description
        :type db: Session
        :param filters: Description
        :type filters: FilterParams
        :param apply_inner_sort: Description
        :type apply_inner_sort: bool


        This function fetches all data from market, insight, legislation database and returns it in a sorted.
        The assumption here being that this function is used to list all documents in the content store, so we wouldnt need to render
        the s3 objects.
        """
        
        # match to table we are fetching data from
        content_map = {
        ContentType.market: Market,
        ContentType.legislation: Legislation,
        ContentType.insight: Insight,
        }

        table = content_map[filters.content_type]
        offset = filters.page * filters.page_size
        query = db.query(table)

        # if we want to sort at the individual table level
        if apply_inner_sort:
            columns_map = {
                SortField.created_at: table.created_at,
                SortField.updated_at: table.updated_at,
                SortField.title: table.title,
                SortField.source: table.source,
            }

            sort_column = columns_map[filters.sort_by]
            sort_expression = (
                asc(sort_column) if filters.order == SortOrder.asc else desc(sort_column)
            )
            query = query.order_by(sort_expression)

        table_data = query.offset(offset).limit(filters.page_size).all()
        total = db.query(table).count()

        return {
            "message": "success",
            "table": filters.content_type.value,
            "page": filters.page,
            "page_size": filters.page_size,
            "total": total,
            "sort_by": filters.sort_by.value,
            "order": filters.order.value,
            "data": [m.to_dict() for m in table_data],
        }

    
    @staticmethod
    def list_all_content(db: Session, filters: FilterParams):
        """
        Docstring for list_all_content
        
        :param db: Description
        :type db: Session
        :param filters: Description
        :type filters: FilterParams
        
        This function wraps around list_content and is used to provide pagination functionality, and applies optional sorting
        at the global scope for all content types.
        
        """

        aggregated_data = []
        total = 0

        # Fetch all records for each content type without applying per-table pagination.
        # Pagination is applied only after aggregating and globally sorting the results.
        content_map = {
            ContentType.market: Market,
            ContentType.legislation: Legislation,
            ContentType.insight: Insight,
        }

        search_query = filters.search.lower().strip() if filters.search else ""

        for content_type in (
            ContentType.market,
            ContentType.legislation,
            ContentType.insight,
        ):
            table = content_map[content_type]
            query = db.query(table)

            # Collect all rows for this content type
            table_rows = query.all()

            for row in table_rows:
                item = row.to_dict()
                
                # Apply search filter if provided
                if search_query:
                    title = (item.get("title") or "").lower()
                    description = (item.get("description") or "").lower()
                    source = (item.get("source") or "").lower()
                    
                    if not (search_query in title or search_query in description or search_query in source):
                        continue
                
                item["content_type"] = content_type.value
                aggregated_data.append(item)
                total += 1

        reverse = filters.order == SortOrder.desc
        aggregated_data.sort(
            key=lambda x: x[filters.sort_by.value],
            reverse=reverse,
        )
        # Pagination after aggregation
        start = filters.page * filters.page_size
        end = start + filters.page_size

        return {
            "message": "success",
            "content_type": "all",
            "page": filters.page,
            "page_size": filters.page_size,
            "total": total,
            "data": aggregated_data[start:end],
        }

    @staticmethod
    def get_content(db: Session, content_id: str, content_type: ContentType):
        """
        Docstring for get_content
        
        :param db: Description
        :type db: Session
        :param content_id: Description
        :type content_id: str
        :param content_type: Description
        :type content_type: ContentType
        
        get a specific content object
        """
        # TODO: are we returing a file object at this point or just metadata, i assume metadata
        model = ContentService.CONTENT_MAP[content_type]["model"]
        data = db.get(model, content_id)

        if not data:  
            raise ValueError("Content not found")

        return {
            "message": "success",
            "data": data.to_dict(),
        }
    
    @staticmethod
    async def upload_content(
        content_type: ContentType,
        db: Session,
        title: str,
        description: str | None,
        file: UploadFile,
        background_tasks: BackgroundTasks,
    ):
        if content_type not in ContentService.CONTENT_MAP:
            raise ValueError("Unsupported content type")

        model = ContentService.CONTENT_MAP[content_type]["model"]
        bucket = ContentService.CONTENT_MAP[content_type]["bucket"]

        ALLOWED_EXTENSIONS = {"pdf", "docx", "csv", "xlsx", "pptx", "txt"}
        MAX_FILE_SIZE = 10 * 1024 * 1024

        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file type: {file_ext}")

        file_bytes = await file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            raise ValueError("File too large")

        entry = model(
            id=uuid.uuid4(),
            title=title,
            description=description,
            source="user",
            file_type=file_ext,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        try:
            print(f"Creating DB entry for content with title: {title} and ID: {entry.id}")
            db.add(entry)
            db.commit()
            db.refresh(entry)

            print(f"Created DB entry with ID: {entry.id}")

            # upload raw file
            upload_to_s3(file_bytes, file_ext, bucket, f"{entry.id}.{file_ext}")

            # background vector indexing
            background_tasks.add_task(
                index_document,
                content_type.value,  # collection name
                str(entry.id),
                file_ext,
                file_bytes,
            )

        except Exception:
            db.rollback()
            raise

        return {
            "message": "Upload successful",
            "id": str(entry.id),
            "file_size": len(file_bytes),
        }
    
    @staticmethod
    def delete_content(
        db: Session,
        content_id: str,
        content_type: ContentType,
        background_tasks: BackgroundTasks
        ):
        """
        Docstring for delete_content
        """
        if content_type not in ContentService.CONTENT_MAP:
            raise ValueError(f"No configuration for content type: {content_type}")

        model = ContentService.CONTENT_MAP[content_type]["model"]
        bucket = ContentService.CONTENT_MAP[content_type]["bucket"]

        item = db.get(model, content_id)
        if not item:
            raise ValueError("Content not found")

        # TODO: Note some records in s3 dont have id persay but use the name so discuss this
        s3_key = f"{item.id}.{item.file_type}"  
        try:
            delete_from_s3(bucket, s3_key)
        except Exception as e:
            raise ValueError(f"Failed to delete file from S3: {str(e)}")

        # --- Delete DB record ---
        db.delete(item)
        db.commit()

        # --- Delete from Chroma ---
        background_tasks.add_task(
            delete_from_vector_db,
            content_id=content_id,
            content_type=content_type,
        )

        return {"message": f"Content {content_id} deleted successfully from {content_type.value}"}
    

    @staticmethod
    def download_content(
        db: Session,
        content_id: str,
        content_type: ContentType,
    ):
        """
        Download content file based on content domain (market, legislation, etc.)
        """

        if content_type not in ContentService.CONTENT_MAP:
            raise ValueError(f"No configuration for content type: {content_type}")

        config = ContentService.CONTENT_MAP[content_type]
        model = config["model"]
        bucket = config["bucket"]

        item = db.get(model, content_id)
        if not item:
            raise ValueError("Content not found")

        s3_key = f"{item.id}.{item.file_type}"
        try:
            file_bytes = download_from_s3(bucket, s3_key)
        except FileNotFoundError as e:
            raise ValueError(f"File not found in storage: {e}") from e
        except (PermissionError, RuntimeError) as e:
            raise IOError(f"Storage unavailable: {e}") from e

        filename = f"{item.title or item.id}.{item.file_type}"
        media_type = item.file_type or "application/octet-stream"

        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )