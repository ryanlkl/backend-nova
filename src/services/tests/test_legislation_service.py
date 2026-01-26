"""
Unit tests for LegislationService
"""
from unittest.mock import Mock, AsyncMock, patch
import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.services.legislation import LegislationService
from src.models.legislation import Legislation


class TestLegislationServiceListLegislation:
    """
    Tests for LegislationService.list_legislation
    """

    @pytest.mark.asyncio
    async def test_list_legislation_returns_all_entries(self):
        """
        Test that list_legislation returns all legislation entries
        """

        mock_db = Mock(spec=Session)
        expected_result = {
            "items": [
                {"id": "1", "title": "Bill A", "status": "active"},
                {"id": "2", "title": "Bill B", "status": "pending"}
            ],
            "total": 2,
            "skip": 0,
            "limit": 100,
            "has_next": False
        }
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = expected_result

            result = await LegislationService.list_legislation(mock_db)

            assert result == expected_result
            mock_get.assert_called_once_with(Legislation, mock_db, filters={})

    @pytest.mark.asyncio
    async def test_list_legislation_calls_get_with_filters(self):
        """
        Test that list_legislation calls get_with_filters with correct parameters
        """

        mock_db = Mock(spec=Session)
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"items": [], "total": 0}

            await LegislationService.list_legislation(mock_db)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == Legislation
            assert call_args[0][1] == mock_db
            assert call_args[1]['filters'] == {}

    @pytest.mark.asyncio
    async def test_list_legislation_with_empty_database(self):
        """
        Test list_legislation when database is empty
        """

        mock_db = Mock(spec=Session)
        expected_result = {
            "items": [],
            "total": 0,
            "skip": 0,
            "limit": 100,
            "has_next": False
        }
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = expected_result

            result = await LegislationService.list_legislation(mock_db)

            assert result["items"] == []
            assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_list_legislation_with_large_dataset(self):
        """
        Test list_legislation with pagination info
        """

        mock_db = Mock(spec=Session)
        expected_result = {
            "items": [{"id": str(i), "title": f"Bill {i}"} for i in range(100)],
            "total": 250,
            "skip": 0,
            "limit": 100,
            "has_next": True
        }
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = expected_result

            result = await LegislationService.list_legislation(mock_db)

            assert len(result["items"]) == 100
            assert result["total"] == 250
            assert result["has_next"] is True

    @pytest.mark.asyncio
    async def test_list_legislation_handles_database_error(self):
        """
        Test that list_legislation propagates database errors
        """

        mock_db = Mock(spec=Session)
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Database connection error")

            with pytest.raises(Exception) as exc_info:
                await LegislationService.list_legislation(mock_db)
            
            assert "Database connection error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_legislation_db_session_not_modified(self):
        """
        Test that list_legislation doesn't modify the database session
        """

        mock_db = Mock(spec=Session)
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"items": [], "total": 0}

            await LegislationService.list_legislation(mock_db)

            mock_db.add.assert_not_called()
            mock_db.commit.assert_not_called()
            mock_db.rollback.assert_not_called()


class TestLegislationServiceGetLegislationInfo:
    """
    Tests for LegislationService.get_legislation_info
    """

    @pytest.mark.asyncio
    async def test_get_legislation_info_returns_single_entry(self):
        """
        Test that get_legislation_info returns a single legislation entry
        """

        mock_db = Mock(spec=Session)
        legislation_id = "test-id-123"
        expected_result = {
            "id": legislation_id,
            "title": "Test Bill",
            "description": "Test description",
            "status": "active"
        }
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = expected_result

            result = await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert result == expected_result
            assert result["id"] == legislation_id
            mock_get.assert_called_once_with(Legislation, mock_db, legislation_id)

    @pytest.mark.asyncio
    async def test_get_legislation_info_calls_get_by_id(self):
        """
        Test that get_legislation_info calls get_by_id with correct parameters
        """

        mock_db = Mock(spec=Session)
        legislation_id = "abc-123"
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"id": legislation_id}

            await LegislationService.get_legislation_info(legislation_id, mock_db)

            mock_get.assert_called_once()
            call_args = mock_get.call_args[0]
            assert call_args[0] == Legislation
            assert call_args[1] == mock_db
            assert call_args[2] == legislation_id

    @pytest.mark.asyncio
    async def test_get_legislation_info_with_different_ids(self):
        """
        Test get_legislation_info with various ID formats
        """

        mock_db = Mock(spec=Session)
        test_ids = ["123", "abc-def-456", "uuid-format-id", "12345"]
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            for test_id in test_ids:
                mock_get.return_value = {"id": test_id}
                
                # Act
                result = await LegislationService.get_legislation_info(test_id, mock_db)
                
                # Assert
                assert result["id"] == test_id

    @pytest.mark.asyncio
    async def test_get_legislation_info_not_found_raises_error(self):
        """
        Test that get_legislation_info raises HTTPException when legislation not found
        """

        mock_db = Mock(spec=Session)
        legislation_id = "nonexistent-id"
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = HTTPException(status_code=404, detail="Record not found")

            with pytest.raises(HTTPException) as exc_info:
                await LegislationService.get_legislation_info(legislation_id, mock_db)
            
            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_legislation_info_handles_database_error(self):
        """
        Test that get_legislation_info propagates database errors
        """

        mock_db = Mock(spec=Session)
        legislation_id = "test-id"
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Database error")

            with pytest.raises(Exception) as exc_info:
                await LegislationService.get_legislation_info(legislation_id, mock_db)
            
            assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_legislation_info_with_complete_data(self):
        """
        Test get_legislation_info returns complete legislation data
        """

        mock_db = Mock(spec=Session)
        legislation_id = "full-data-id"
        expected_result = {
            "id": legislation_id,
            "title": "Comprehensive Health Bill",
            "description": "A bill to improve healthcare",
            "status": "active",
            "sponsor": "Senator Smith",
            "date_introduced": "2024-01-15",
            "full_text": "Be it enacted...",
            "committee": "Health Committee"
        }
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = expected_result

            result = await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert result == expected_result
            assert all(key in result for key in expected_result.keys())

    @pytest.mark.asyncio
    async def test_get_legislation_info_db_session_not_modified(self):
        """
        Test that get_legislation_info doesn't modify the database session
        """

        mock_db = Mock(spec=Session)
        legislation_id = "test-id"
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"id": legislation_id}

            await LegislationService.get_legislation_info(legislation_id, mock_db)

            mock_db.add.assert_not_called()
            mock_db.commit.assert_not_called()
            mock_db.rollback.assert_not_called()


class TestLegislationServiceStaticMethods:
    """
    Tests for static method behavior
    """

    def test_list_legislation_is_static_method(self):
        """
        Test that list_legislation is a static method
        """
        # No instance needed to call static method
        assert callable(LegislationService.list_legislation)
        
        # Verify it's a static method
        import inspect
        assert isinstance(
            inspect.getattr_static(LegislationService, 'list_legislation'),
            staticmethod
        )

    def test_get_legislation_info_is_static_method(self):
        """
        Test that get_legislation_info is a static method
        """
        assert callable(LegislationService.get_legislation_info)
        
        import inspect
        assert isinstance(
            inspect.getattr_static(LegislationService, 'get_legislation_info'),
            staticmethod
        )

    @pytest.mark.asyncio
    async def test_can_call_without_instance(self):
        """
        Test that methods can be called without creating instance
        """
        mock_db = Mock(spec=Session)
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_list, \
             patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            
            mock_list.return_value = {"items": [], "total": 0}
            mock_get.return_value = {"id": "test"}
            
            # Call without creating instance
            await LegislationService.list_legislation(mock_db)
            await LegislationService.get_legislation_info("test", mock_db)
            
            # Both should work
            assert mock_list.called
            assert mock_get.called


class TestLegislationServiceIntegration:
    """
    Integration-style tests (still mocked, but test workflows)
    """

    @pytest.mark.asyncio
    async def test_list_then_get_workflow(self):
        """
        Test typical workflow: list all, then get specific item
        """

        mock_db = Mock(spec=Session)
        
        list_result = {
            "items": [
                {"id": "1", "title": "Bill A"},
                {"id": "2", "title": "Bill B"}
            ],
            "total": 2
        }
        
        detail_result = {
            "id": "1",
            "title": "Bill A",
            "description": "Detailed description",
            "full_text": "Full text..."
        }
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_list, \
             patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            
            mock_list.return_value = list_result
            mock_get.return_value = detail_result

            # 1. Get list of all legislation
            all_legislation = await LegislationService.list_legislation(mock_db)
            
            # 2. Get details for first item
            first_id = all_legislation["items"][0]["id"]
            details = await LegislationService.get_legislation_info(first_id, mock_db)

            assert len(all_legislation["items"]) == 2
            assert details["id"] == "1"
            assert "full_text" in details

    @pytest.mark.asyncio
    async def test_multiple_get_calls_same_session(self):
        """
        Test multiple get_legislation_info calls with same session
        """

        mock_db = Mock(spec=Session)
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [
                {"id": "1", "title": "Bill 1"},
                {"id": "2", "title": "Bill 2"},
                {"id": "3", "title": "Bill 3"}
            ]

            result1 = await LegislationService.get_legislation_info("1", mock_db)
            result2 = await LegislationService.get_legislation_info("2", mock_db)
            result3 = await LegislationService.get_legislation_info("3", mock_db)

            assert result1["id"] == "1"
            assert result2["id"] == "2"
            assert result3["id"] == "3"
            assert mock_get.call_count == 3


# Fixtures for cleaner tests
@pytest.fixture
def mock_db_session():
    """
    Fixture providing a mocked database session
    """
    return Mock(spec=Session)


@pytest.fixture
def sample_legislation_list():
    """
    Fixture providing sample legislation list response
    """
    return {
        "items": [
            {
                "id": "1",
                "title": "Healthcare Reform Act",
                "status": "active",
                "date_introduced": "2024-01-15"
            },
            {
                "id": "2",
                "title": "Education Funding Bill",
                "status": "pending",
                "date_introduced": "2024-02-01"
            }
        ],
        "total": 2,
        "skip": 0,
        "limit": 100,
        "has_next": False
    }


@pytest.fixture
def sample_legislation_detail():
    """
    Fixture providing sample legislation detail response
    """
    return {
        "id": "1",
        "title": "Healthcare Reform Act",
        "description": "A comprehensive bill to reform healthcare",
        "status": "active",
        "sponsor": "Senator Johnson",
        "date_introduced": "2024-01-15",
        "full_text": "Be it enacted by the Senate...",
        "committee": "Health Committee",
        "vote_count": {"yes": 45, "no": 30, "abstain": 5}
    }


class TestLegislationServiceWithFixtures:
    """
    Tests using fixtures for cleaner setup
    """

    @pytest.mark.asyncio
    async def test_list_legislation_with_fixture(
        self,
        mock_db_session,
        sample_legislation_list
    ):
        """
        Test list_legislation using fixtures
        """
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_legislation_list
            
            result = await LegislationService.list_legislation(mock_db_session)
            
            assert result == sample_legislation_list
            assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_get_legislation_info_with_fixture(
        self,
        mock_db_session,
        sample_legislation_detail
    ):
        """
        Test get_legislation_info using fixtures
        """
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_legislation_detail
            
            result = await LegislationService.get_legislation_info("1", mock_db_session)
            
            assert result == sample_legislation_detail
            assert result["title"] == "Healthcare Reform Act"
            assert "vote_count" in result


class TestLegislationServiceEdgeCases:
    """
    Tests for edge cases and boundary conditions
    """

    @pytest.mark.asyncio
    async def test_list_legislation_with_none_db(self):
        """
        Test behavior when db session is None
        """
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = AttributeError("'NoneType' object has no attribute")
            
            with pytest.raises(AttributeError):
                await LegislationService.list_legislation(None)

    @pytest.mark.asyncio
    async def test_get_legislation_info_with_empty_id(self):
        """
        Test get_legislation_info with empty string ID
        """
        mock_db = Mock(spec=Session)
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = HTTPException(status_code=404, detail="Record not found")
            
            with pytest.raises(HTTPException):
                await LegislationService.get_legislation_info("", mock_db)

    @pytest.mark.asyncio
    async def test_get_legislation_info_with_none_id(self):
        """
        Test get_legislation_info with None as ID
        """
        mock_db = Mock(spec=Session)
        
        with patch('src.services.legislation.get_by_id', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = HTTPException(status_code=404, detail="Record not found")
            
            with pytest.raises(HTTPException):
                await LegislationService.get_legislation_info(None, mock_db)

    @pytest.mark.asyncio
    async def test_list_legislation_with_special_characters_in_data(self):
        """
        Test that special characters in data are handled correctly
        """
        mock_db = Mock(spec=Session)
        result_with_special_chars = {
            "items": [
                {
                    "id": "1",
                    "title": "Bill with 'quotes' and \"double quotes\"",
                    "description": "Contains <html> & special chars"
                }
            ],
            "total": 1
        }
        
        with patch('src.services.legislation.get_with_filters', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = result_with_special_chars
            
            result = await LegislationService.list_legislation(mock_db)
            
            assert "quotes" in result["items"][0]["title"]
            assert "<html>" in result["items"][0]["description"]