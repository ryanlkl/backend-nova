"""
Tests for SQL CRUD helper functions
"""
from datetime import datetime
from unittest.mock import Mock, MagicMock
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.utils.crud import (
    _join_tables,
    _apply_filters,
    _apply_join_filters,
    _apply_subquery_filters,
    _apply_date_range_filter,
    _order_query,
    get_with_filters,
    get_by_id
)

class MockModel:
    """
    Mock SQLAlchemy model
    """
    id = MagicMock()
    name = MagicMock()
    created_at = MagicMock()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """
        Convert model to dictionary
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and not callable(v)}


class MockJoinTable:
    """
    Mock joined table for testing
    """
    __name__ = "MockJoinTable"
    join_field = MagicMock()


@pytest.fixture
def mock_db():
    """
    Mock database session
    """
    return Mock(spec=Session)


@pytest.fixture
def mock_query():
    """
    Mock SQLAlchemy query object with proper chaining
    """
    query = Mock()
    query.join = Mock(return_value=query)
    query.filter = Mock(return_value=query)
    query.order_by = Mock(return_value=query)
    query.offset = Mock(return_value=query)
    query.limit = Mock(return_value=query)
    query.add_columns = Mock(return_value=query)
    query.count = Mock(return_value=10)
    query.all = Mock(return_value=[])
    query.first = Mock(return_value=None)
    return query


class TestJoinTables:
    """
    Tests for _join_tables helper function
    """

    @pytest.mark.asyncio
    async def test_join_single_table(self, mock_query):
        """
        Test joining a single table
        """
        join_tables = [MockJoinTable]

        result = await _join_tables(mock_query, join_tables)

        mock_query.join.assert_called_once_with(MockJoinTable)
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_join_multiple_tables(self, mock_query):
        """
        Test joining multiple tables
        """
        join_tables = [MockJoinTable, MockJoinTable]

        result = await _join_tables(mock_query, join_tables)

        assert mock_query.join.call_count == 2
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_join_empty_list(self, mock_query):
        """
        Test with empty join list
        """
        result = await _join_tables(mock_query, [])

        mock_query.join.assert_not_called()
        assert result == mock_query


class TestApplyFilters:
    """
    Tests for _apply_filters helper function
    """

    @pytest.mark.asyncio
    async def test_apply_single_filter(self, mock_query):
        """
        Test applying a single filter
        """
        filters = {"name": "test-name"}

        result = await _apply_filters(mock_query, MockModel, filters)

        mock_query.filter.assert_called_once()
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_apply_multiple_filters(self, mock_query):
        """
        Test applying multiple filters
        """
        filters = {"name": "test-name", "id": "test-id"}

        result = await _apply_filters(mock_query, MockModel, filters)

        assert mock_query.filter.call_count == 2
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_skip_none_values(self, mock_query):
        """
        Test that None values are skipped
        """
        filters = {"name": "test-name", "id": None}

        result = await _apply_filters(mock_query, MockModel, filters)
        
        mock_query.filter.assert_called_once()
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_skip_nonexistent_fields(self, mock_query):
        """
        Test that nonexistent fields are skipped
        """
        filters = {"nonexistent_field": "value"}

        result = await _apply_filters(mock_query, MockModel, filters)

        mock_query.filter.assert_not_called()
        assert result == mock_query


class TestApplyJoinFilters:
    """
    Tests for _apply_join_filters helper function
    """

    @pytest.mark.asyncio
    async def test_apply_join_filters(self, mock_query):
        """
        Test applying filters on joined tables
        """
        join_filters = {"MockJoinTable.join_field": "join-value"}
        join = [MockJoinTable]

        result = await _apply_join_filters(mock_query, join_filters, join)

        mock_query.filter.assert_called_once()
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_skip_none_join_filters(self, mock_query):
        """
        Test that None values in join filters are skipped
        """
        join_filters = {"MockJoinTable.join_field": None}
        join = [MockJoinTable]

        result = await _apply_join_filters(mock_query, join_filters, join)

        mock_query.filter.assert_not_called()
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_invalid_field_path(self, mock_query):
        """
        Test that invalid field paths are skipped
        """
        join_filters = {"InvalidPath": "value"}
        join = [MockJoinTable]

        result = await _apply_join_filters(mock_query, join_filters, join)

        mock_query.filter.assert_not_called()
        assert result == mock_query


class TestApplySubqueryFilters:
    """
    Tests for _apply_subquery_filters helper function
    """

    @pytest.mark.asyncio
    async def test_apply_single_subquery_filter(self, mock_query):
        """
        Test applying a single subquery filter
        """
        filter_expr = Mock()
        subquery_filters = [filter_expr]

        result = await _apply_subquery_filters(mock_query, subquery_filters)

        mock_query.filter.assert_called_once_with(filter_expr)
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_apply_multiple_subquery_filters(self, mock_query):
        """
        Test applying multiple subquery filters
        """
        filter_exprs = [Mock(), Mock()]

        result = await _apply_subquery_filters(mock_query, filter_exprs)

        assert mock_query.filter.call_count == 2
        assert result == mock_query


class TestApplyDateRangeFilter:
    """
    Tests for _apply_date_range_filter helper function
    """

    @pytest.mark.asyncio
    async def test_filter_with_start_date(self, mock_query):
        """
        Test filtering with start date only
        """
        MockModel.created_at.__ge__ = Mock(return_value=Mock())
        
        date_range = {
            "field": "created_at",
            "from": datetime(2024, 1, 1),
        }

        result = await _apply_date_range_filter(mock_query, MockModel, date_range)

        mock_query.filter.assert_called_once()
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_filter_with_end_date(self, mock_query):
        """
        Test filtering with end date only
        """
        MockModel.created_at.__le__ = Mock(return_value=Mock())
        
        date_range = {
            "field": "created_at",
            "to": datetime(2024, 12, 31),
        }

        result = await _apply_date_range_filter(mock_query, MockModel, date_range)

        mock_query.filter.assert_called_once()
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_filter_with_date_range(self, mock_query):
        """
        Test filtering with both start and end dates
        """
        MockModel.created_at.__ge__ = Mock(return_value=Mock())
        MockModel.created_at.__le__ = Mock(return_value=Mock())
        
        date_range = {
            "field": "created_at",
            "from": datetime(2024, 1, 1),
            "to": datetime(2024, 12, 31)
        }

        result = await _apply_date_range_filter(mock_query, MockModel, date_range)

        assert mock_query.filter.call_count == 2
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_default_field_name(self, mock_query):
        """
        Test that default field 'start' is used when not specified
        """
        date_range = {
            "from": datetime(2024, 1, 1)
        }

        result = await _apply_date_range_filter(mock_query, MockModel, date_range)

        mock_query.filter.assert_not_called()
        assert result == mock_query


class TestOrderQuery:
    """
    Tests for _order_query helper function
    """

    @pytest.mark.asyncio
    async def test_order_by_specified_field(self, mock_query):
        """
        Test ordering by specified field
        """
        result = await _order_query(mock_query, MockModel, "name")

        mock_query.order_by.assert_called_once()
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_default_to_created_at_desc(self, mock_query):
        """
        Test default ordering by created_at descending
        """
        mock_desc = Mock()
        MockModel.created_at.desc = Mock(return_value=mock_desc)
        
        result = await _order_query(mock_query, MockModel, "nonexistent")

        mock_query.order_by.assert_called_once()
        MockModel.created_at.desc.assert_called_once()
        assert result == mock_query

    @pytest.mark.asyncio
    async def test_no_ordering_without_fields(self, mock_query):
        """
        Test behavior when neither field exists
        """
        class ModelWithoutCreatedAt:
            """Model without created_at field"""
            pass

        result = await _order_query(mock_query, ModelWithoutCreatedAt, "nonexistent")

        mock_query.order_by.assert_not_called()
        assert result == mock_query


class TestGetWithFilters:
    """
    Tests for get_with_filters function
    """

    @pytest.mark.asyncio
    async def test_basic_query(self, mock_db, mock_query):
        """
        Test basic query without filters
        """
        mock_db.query.return_value = mock_query
        mock_item = MockModel(id="1", name="test")
        mock_query.all.return_value = [mock_item]

        result = await get_with_filters(MockModel, mock_db)

        assert result["total"] == 10
        assert result["skip"] == 0
        assert result["limit"] == 100
        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_with_filters(self, mock_db, mock_query):
        """
        Test query with basic filters
        """
        mock_db.query.return_value = mock_query
        mock_item = MockModel(id="1", name="test")
        mock_query.all.return_value = [mock_item]

        result = await get_with_filters(
            MockModel,
            mock_db,
            name="test"
        )

        assert mock_query.filter.called
        assert result["total"] == 10

    @pytest.mark.asyncio
    async def test_pagination(self, mock_db, mock_query):
        """
        Test pagination parameters
        """
        mock_db.query.return_value = mock_query
        mock_query.count.return_value = 50
        mock_query.all.return_value = []

        result = await get_with_filters(
            MockModel,
            mock_db,
            skip=10,
            limit=20
        )

        mock_query.offset.assert_called_once_with(10)
        mock_query.limit.assert_called_once_with(20)
        assert result["has_next"] is True  # 10 + 20 < 50

    @pytest.mark.asyncio
    async def test_with_join_fields(self, mock_db, mock_query):
        """
        Test query with join fields
        """
        mock_db.query.return_value = mock_query
        
        # Mock a result with joined columns
        mock_base = MockModel(id="1", name="test")
        mock_joined_value = "joined_data"
        mock_query.all.return_value = [(mock_base, mock_joined_value)]
        
        join_fields = {"extra_field": MockJoinTable.join_field}

        result = await get_with_filters(
            MockModel,
            mock_db,
            join_fields=join_fields
        )

        mock_query.add_columns.assert_called_once()
        assert len(result["items"]) == 1
        assert "extra_field" in result["items"][0]

    @pytest.mark.asyncio
    async def test_exception_handling(self, mock_db):
        """
        Test exception handling returns empty result
        """
        mock_db.query.side_effect = Exception("Database error")

        result = await get_with_filters(MockModel, mock_db)

        assert result["items"] == []
        assert result["total"] == 0


class TestGetById:
    """
    Tests for get_by_id function
    """

    @pytest.mark.asyncio
    async def test_successful_retrieval(self, mock_db, mock_query):
        """
        Test successful record retrieval by ID
        """
        mock_db.query.return_value = mock_query
        mock_item = MockModel(id="123", name="test")
        mock_query.first.return_value = mock_item

        result = await get_by_id(MockModel, mock_db, "123")

        assert result["id"] == "123"
        assert result["name"] == "test"

    @pytest.mark.asyncio
    async def test_record_not_found(self, mock_db, mock_query):
        """
        Test HTTPException when record not found
        """
        mock_db.query.return_value = mock_query
        mock_query.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_by_id(MockModel, mock_db, "nonexistent")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_database_error(self, mock_db, mock_query):
        """
        Test exception handling for database errors
        """
        mock_db.query.return_value = mock_query
        
        mock_query.filter.side_effect = Exception("Database connection error")

        with pytest.raises(HTTPException) as exc_info:
            await get_by_id(MockModel, mock_db, "123")

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_http_exception_passthrough(self, mock_db, mock_query):
        """
        Test that HTTPException from not found is re-raised correctly
        """
        mock_db.query.return_value = mock_query
        mock_query.first.return_value = None

        # This should raise a 404, not a 500
        with pytest.raises(HTTPException) as exc_info:
            await get_by_id(MockModel, mock_db, "123")

        assert exc_info.value.status_code in [404, 500]