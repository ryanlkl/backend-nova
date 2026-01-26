"""
SQL CRUD helper functions for database interactions
"""
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

async def _join_tables(query, join: list):
    """
    Helper function to join tables in a query
    
    :param query: SQLAlchemy query object
    :param join: List of tables to join
    :type join: list
    """
    for table in join:
        query = query.join(table)
    return query

async def _apply_filters(query, model, filters: dict):
    """
    Helper function to apply filters to a query
    
    :param query: SQLAlchemy query object
    :param model: Model class to query (found in src/models)
    :param filters: Dictionary of filters to apply
    :type filters: dict
    """
    for field, value in filters.items():
        if hasattr(model, field) and value is not None:
            query = query.filter(getattr(model, field) == value)
    return query

async def _apply_join_filters(query, join_filters: dict, join: list):
    """
    Helper function to add fields from joined tables to a query
    
    :param query: SQLAlchemy query object
    :param join_filters: Dictionary of fields to include from joined tables
    :type join_filters: dict
    """
    for field_path, value in join_filters.items():
        if value is not None:
            parts = field_path.split(".")
            if len(parts) == 2:
                table_name, field_name = parts
                for join_table in (join or []):
                    if join_table.__name__ == table_name and hasattr(join_table, field_name):
                        query = query.filter(getattr(join_table, field_name) == value)
                        break

    return query

async def _apply_subquery_filters(query, subquery_filters: list):
    """
    Helper function to apply subquery filters to a query
    
    :param query: SQLAlchemy query object
    :param subquery_filters: List of filter expressions to apply using subqueries
    :type subquery_filters: list
    """
    for filter_expression in subquery_filters:
        query = query.filter(filter_expression)
    return query

async def _apply_date_range_filter(query, model, date_range: dict):
    """
    Helper function to apply date range filter to a query
    
    :param query: SQLAlchemy query object
    :param model: Model class to query (found in src/models)
    :param date_range: Dictionary with 'field', 'from', and 'to' keys for date filtering
    :type date_range: dict
    """
    date_field = date_range.get("field", "start")
    start_date = date_range.get("from")
    end_date = date_range.get("to")

    if hasattr(model, date_field):
        if start_date:
            query = query.filter(getattr(model, date_field) >= start_date)
        if end_date:
            query = query.filter(getattr(model, date_field) <= end_date)

    return query

async def _order_query(query, model, order_by):
    """
    Helper function to order a query
    
    :param query: SQLAlchemy query object
    :param model: Model class to query (found in src/models)
    :param order_by: Field to order results by
    """
    if hasattr(model, order_by):
        query = query.order_by(getattr(model, order_by))
    elif hasattr(model, 'created_at'):
        query = query.order_by(getattr(model, 'created_at').desc())
    return query

async def get_with_filters(
        model,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        order_by=None,
        join: list = None,
        join_fields: dict = None,
        join_filters: dict = None,
        subquery_filters: list = None,
        date_range: dict = None,
        **filters
):
    """
    Filtered retrieval of records from SQL database
    
    :param model: Model class to query (found in src/models)
    :param db: Database session (dependency injection from endpoint)
    :type db: Session
    :param skip: Starting index for pagination
    :type skip: int
    :param limit: Maximum number of records to retrieve
    :type limit: int
    :param order_by: Field to order results by
    :param join: Joins to include in the query
    :type join: list
    :param join_fields: Fields to include from joined tables
    :type join_fields: dict
    :param join_filters: Filters to apply on joined tables
    :type join_filters: dict
    :param subquery_filters: Filters to apply using subqueries
    :type subquery_filters: list
    :param date_range: Date range for filtering records
    :type date_range: dict
    :param filters: Additional filters to apply
    """
    try:
        query = db.query(model)

        if join:
            query = await _join_tables(query, join)

        if len(filters) > 0:
            query = await _apply_filters(query, model, filters)

        if join_filters:
            query = await _apply_join_filters(query, join_filters, join)
        
        if subquery_filters:
            query = await _apply_subquery_filters(query, subquery_filters)

        if date_range:
            query = await _apply_date_range_filter(query, model, date_range)
        
        total_count = query.count()

        if order_by:
            query = await _order_query(query, model, order_by)

        query = query.offset(skip).limit(limit)

        if join_fields:
            query = query.add_columns(*join_fields.values())

        rows = query.all()
        results = []

        for item in rows:
            if join_fields:
                base_obj = item[0].to_dict().copy()
                for idx, field_name in enumerate(join_fields.keys(), start = 1):
                    base_obj[field_name] = item[idx]
                results.append(base_obj)

            else:
                item_dicst = item.to_dict() if hasattr(item, 'to_dict') else item.__dict__.copy()
                results.append(item_dicst)

        return {
            "items": results,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "order_by": str(order_by) if order_by else None,
            "has_next": skip + limit < total_count
        }

    except Exception as e:
        print(f"Error in get_with_filters: {e}")
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "order_by": str(order_by) if order_by else None,
            "has_next": False
        }
    
async def get_by_id(model, db: Session, record_id: str):
    """
    Retrieves a single record by its ID
    
    :param model: Model class to query (found in src/models)
    :param db: Database session (dependency injection from endpoint)
    :type db: Session
    :param record_id: ID of the record to retrieve
    :type record_id: str
    """
    try:
        record = db.query(model).filter(model.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return record.to_dict() if hasattr(record, 'to_dict') else record.__dict__.copy()
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_by_id: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")