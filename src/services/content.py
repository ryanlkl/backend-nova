"""
Docstring for services.content
"""
import uuid
from datetime import datetime, timezone
from fastapi import  UploadFile, BackgroundTasks, Response, HTTPException
from typing import Optional


from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from src.models.market import Market
from src.models.legislation import Legislation
from src.models.insight import Insight
from src.models.content import ContentHub
from src.schema.content import FilterParams, SortField, SortOrder, ContentType
from uuid import UUID

from src.utils.embeddings import index_document, delete_from_vector_db
from src.utils.s3 import upload_to_s3, delete_from_s3, download_from_s3

class ContentService:
    """
    Docstring for ContentService
    """

    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "ppt", "pptx", "xls", "xlsx", "csv"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
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

    #############################################
    #                                           #   
    #                                           #   
    #          WEB SCRAPER ENDPOINTS            #   
    #                                           #
    #                                           #
    #############################################

    @staticmethod
    def list_content(db: Session, filters: FilterParams, apply_inner_sort: bool = True):

        content_map = {
            ContentType.market: Market,
            ContentType.legislation: Legislation,
            ContentType.insight: Insight,
        }

        table = content_map[filters.content_type]
        offset = filters.page * filters.page_size
        query = db.query(table)

        # filter user uploaded content
        if filters.user_only:
            query = query.filter(table.source == "user")

        if apply_inner_sort:
            sort_column = getattr(table, filters.sort_by.value)

            sort_expression = (
                asc(sort_column)
                if filters.order == SortOrder.asc
                else desc(sort_column)
            )

            query = query.order_by(sort_expression)

        rows = query.offset(offset).limit(filters.page_size).all()

        total_query = db.query(table)

        if filters.user_only:
            total_query = total_query.filter(table.source == "user")

        total = total_query.count()

        return {
            "message": "success",
            "table": filters.content_type.value,
            "page": filters.page,
            "page_size": filters.page_size,
            "total": total,
            "sort_by": filters.sort_by.value,
            "order": filters.order.value,
            "data": [{**r.to_dict(), "content_type": filters.content_type.value} for r in rows]
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

        for content_type in (
            ContentType.market,
            ContentType.legislation, 
            ContentType.insight):

            # specify which table we are fetching data from and sort once for all aggregated records
            scoped_filters = filters.model_copy(update={"content_type": content_type})
            result = ContentService.list_content(db, scoped_filters, apply_inner_sort=False)

            for item in result["data"]:
                item["content_type"] = content_type.value
                aggregated_data.append(item)

            total += result["total"]

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
   
    # @staticmethod
    # async def upload_content(
    #     content_type: ContentType,
    #     db: Session,
    #     title: str,
    #     description: str,
    #     file: UploadFile,
    #     background_tasks: BackgroundTasks,
    # ):
    #     if content_type not in ContentService.CONTENT_MAP:
    #         raise ValueError("Unsupported content type")

    #     model = ContentService.CONTENT_MAP[content_type]["model"]
    #     bucket = ContentService.CONTENT_MAP[content_type]["bucket"]

    #     ALLOWED_EXTENSIONS = {"pdf", "docx", "txt","ppt", "pptx", "xls", "xlsx", "csv",}
    #     MAX_FILE_SIZE = 10 * 1024 * 1024

    #     file_ext = file.filename.split(".")[-1].lower()
    #     if file_ext not in ALLOWED_EXTENSIONS:
    #         raise ValueError(f"Invalid file type: {file_ext}")

    #     file_bytes = await file.read()
    #     if len(file_bytes) > MAX_FILE_SIZE:
    #         raise ValueError("File too large")

    #     entry = model(
    #         id=uuid.uuid4(),
    #         title=title,
    #         description=description,
    #         source="user",
    #         file_type=file_ext,
    #         created_at=datetime.now(timezone.utc).isoformat(),
    #         updated_at=datetime.now(timezone.utc).isoformat(),
    #     )

    #     try:
    #         db.add(entry)
    #         db.commit()
    #         db.refresh(entry)

    #         # upload raw file
    #         upload_to_s3(file_bytes, file_ext, bucket, f"{entry.id}.{file_ext}")

    #         # background vector indexing
    #         background_tasks.add_task(
    #             index_document,
    #             content_type.value,  # collection name enum
    #             str(entry.id),
    #             file_ext,
    #             file_bytes,
    #         )

    #     except Exception:
    #         db.rollback()
    #         raise

    #     return {
    #         "message": "Upload successful",
    #         "id": str(entry.id),
    #         "file_size": len(file_bytes),
    #     }
    
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
        file_bytes = download_from_s3(bucket, s3_key)
        if file_bytes is None:
            raise ValueError("Failed to download file from S3")

        filename = f"{item.title or item.id}.{item.file_type}"
        media_type = item.file_type or "application/octet-stream"

        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    

    #############################################
    #                                           #   
    #                                           #   
    #                CONTENT_HUB                #   
    #                                           #
    #                                           #
    #############################################
    @staticmethod
    def list_content_hub(filters: FilterParams, db: Session):
        query = db.query(ContentHub)

        # Filter by content_type if specified
        if filters.content_type:
            query = query.filter(ContentHub.content_type == filters.content_type.value)

        # Filter by user-only content
        if filters.user_only:
            query = query.filter(ContentHub.uploaded_by != None)  # or some specific field indicating user

        # Apply search
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                ContentHub.title.ilike(search_term) | ContentHub.description.ilike(search_term)
            )

        total = query.count()

        # Sorting
        columns_map = {
            SortField.created_at: ContentHub.created_at,
            SortField.updated_at: ContentHub.updated_at,
            SortField.title: ContentHub.title,
            SortField.file_type: ContentHub.file_type,
            SortField.content_type: ContentHub.content_type,
        }
        sort_col = columns_map.get(filters.sort_by, ContentHub.created_at)
        sort_expression = asc(sort_col) if filters.order == SortOrder.asc else desc(sort_col)
        query = query.order_by(sort_expression)

        # Pagination
        offset = filters.page * filters.page_size
        rows = query.offset(offset).limit(filters.page_size).all()

        return {
            "message": "success",
            "content_type": filters.content_type.value if filters.content_type else "all",
            "page": filters.page,
            "page_size": filters.page_size,
            "total": total,
            "data": [r.to_dict() for r in rows],
        }
        

    @staticmethod
    async def upload_content(
        db: Session,
        content_type: ContentType,
        title: str,
        description: str | None,
        file: UploadFile,
        background_tasks: BackgroundTasks,
    ):
        """
        Upload a user file to the content hub table.

        Args:
        -----
        db: SQLAlchemy Session
        content_type: ContentType enum
        title: str
        description: str or None
        file: UploadFile
        background_tasks: BackgroundTasks

        Returns:
        -------
        dict: upload status, file_size, and id
        """

        # Validate file extension
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ContentService.ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file type: {file_ext}")

        # Read file bytes and validate size
        file_bytes = await file.read()
        if len(file_bytes) > ContentService.MAX_FILE_SIZE:
            raise ValueError("File too large")

        # Create ContentHub entry
        entry = ContentHub(
            id=uuid.uuid4(),
            title=title,
            description=description,
            content_type=content_type.value,  # store as string
            file_type=file_ext,
            file_size=len(file_bytes),
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

        try:
            db.add(entry)
            db.commit()
            db.refresh(entry)

            # Upload file to S3
            bucket_name = "nova-content-bucket"
            upload_to_s3(file_bytes, file_ext, bucket_name, f"{entry.id}.{file_ext}")

            # Background indexing
            # background_tasks.add_task(
            #     index_document,
            #     content_type.value,  # collection name
            #     str(entry.id),
            #     file_ext,
            #     file_bytes,
            # )

        except Exception:
            db.rollback()
            raise

        return {
            "message": "Upload successful",
            "id": str(entry.id),
            "file_size": len(file_bytes),
            "content_type": content_type.value,
        }
    

    @staticmethod
    async def update_content_hub(
        db: Session,
        content_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        file: Optional[UploadFile] = None,
    ):
        """
        Update a ContentHub record, optionally replacing the file.
        
        :param db: SQLAlchemy session
        :param content_id: UUID of the content to update
        :param title: Optional new title
        :param description: Optional new description
        :param content_type: Optional new content type
        :param file: Optional new file to replace the existing one
        :return: dict with updated record
        """
        bucket = "nova-content-bucket"
        entry = db.query(ContentHub).filter(ContentHub.id == content_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Content not found")

        # Update fields if provided
        if title is not None:
            entry.title = title
        if description is not None:
            entry.description = description
        if content_type is not None:
            entry.content_type = content_type.value  # store enum value as text

        # Handle file replacement
        if file:
            # Read the new file once
            file_bytes = await file.read()
            file_ext = file.filename.split(".")[-1].lower()

            if file_ext not in ContentService.ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"Invalid file type: {file_ext}")

            # Delete old file from S3
            old_key = f"{entry.id}.{entry.file_type}"
            delete_from_s3(bucket, old_key)
            
            # Upload new file
            new_key = f"{entry.id}.{file_ext}"
            upload_to_s3(file_bytes, file_ext, bucket, new_key)

            # Update metadata
            entry.file_type = file_ext
            entry.file_size = len(file_bytes)

        # Update the timestamp
        entry.updated_at = datetime.now(timezone.utc).isoformat()

        try:
            db.add(entry)
            db.commit()
            db.refresh(entry)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update content")

        return {
            "message": "Updated successfully",
            "data": {
                "id": str(entry.id),
                "title": entry.title,
                "description": entry.description,
                "content_type": entry.content_type,
                "updated_at": entry.updated_at,
            },
        }
    

    @staticmethod
    def download_contenthub(
        db: Session,
        content_id: str,
    ):
        """
        Download content file based on content domain (market, legislation, etc.)
        """
        model = ContentHub
        bucket = "nova-content-bucket"

        item = db.get(model, content_id)
        if not item:
            raise ValueError("Content not found")

        s3_key = f"{item.id}.{item.file_type}"
        file_bytes = download_from_s3(bucket, s3_key)
        if file_bytes is None:
            raise ValueError("Failed to download file from S3")

        filename = f"{item.title or item.id}.{item.file_type}"
        media_type = item.file_type or "application/octet-stream"

        return Response(
            content=file_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )
    
    @staticmethod
    def delete_contenthub_item(
        db: Session,
        content_id: str,
        ):
        """
        Docstring for delete_content
        """
        model = ContentHub
        bucket = "nova-content-bucket"

        item = db.get(model, content_id)
        if not item:
            raise ValueError("Content not found")

        s3_key = f"{item.id}.{item.file_type}"  
        try:
            delete_from_s3(bucket, s3_key)
        except Exception as e:
            raise ValueError(f"Failed to delete file from S3: {str(e)}")

        # --- Delete DB record ---
        db.delete(item)
        db.commit()
        return {"message": f"Content {content_id} deleted successfully. File deleted: {s3_key}"}
    