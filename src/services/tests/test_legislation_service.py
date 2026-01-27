"""
Unit tests for LegislationService
"""
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from io import BytesIO
import inspect
import pytest
from sqlalchemy.orm import Session
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
    Tests for LegislationService.get_legislation_info with S3 integration
    """

    @pytest.mark.asyncio
    async def test_get_legislation_info_returns_s3_file_data(self):
        """
        Test that get_legislation_info retrieves file from S3 and returns correct structure
        """
        mock_db = Mock(spec=Session)
        legislation_id = "123"
        file_content = b"This is the legislation text content"

        # Mock S3 responses
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {
                'Contents': [
                    {'Key': 'legislation/bill_123.txt'}
                ]
            }
        ]

        mock_head_response = {
            'Metadata': {
                'id': '123',
                'title': 'Test Bill',
                'status': 'active'
            }
        }

        mock_get_object_response = {
            'Body': BytesIO(file_content)
        }

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = mock_head_response
            mock_s3.get_object.return_value = mock_get_object_response

            result = await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert result['data'] == file_content
            assert result['filename'] == 'legislation/bill_123.txt'
            assert result['metadata']['id'] == '123'
            assert result['metadata']['title'] == 'Test Bill'

            mock_s3.get_paginator.assert_called_once_with('list_objects_v2')
            mock_s3.head_object.assert_called_once_with(
                Bucket='nova-legislation-bucket',
                Key='legislation/bill_123.txt'
            )
            mock_s3.get_object.assert_called_once_with(
                Bucket='nova-legislation-bucket',
                Key='legislation/bill_123.txt'
            )

    @pytest.mark.asyncio
    async def test_get_legislation_info_searches_multiple_objects(self):
        """
        Test that get_legislation_info iterates through S3 objects until match is found
        """
        mock_db = Mock(spec=Session)
        legislation_id = "456"

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {
                'Contents': [
                    {'Key': 'legislation/bill_123.txt'},
                    {'Key': 'legislation/bill_456.txt'},
                    {'Key': 'legislation/bill_789.txt'}
                ]
            }
        ]

        # First two calls return non-matching IDs, third one matches
        mock_head_responses = [
            {'Metadata': {'id': '123'}},
            {'Metadata': {'id': '456'}},  # This one matches
        ]

        mock_get_object_response = {
            'Body': BytesIO(b"Matching legislation content")
        }

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.side_effect = mock_head_responses
            mock_s3.get_object.return_value = mock_get_object_response

            result = await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert result['data'] == b"Matching legislation content"
            assert result['filename'] == 'legislation/bill_456.txt'
            assert mock_s3.head_object.call_count == 2  # Called twice before finding match

    @pytest.mark.asyncio
    async def test_get_legislation_info_handles_pagination(self):
        """
        Test that get_legislation_info handles multiple pages from S3
        """
        mock_db = Mock(spec=Session)
        legislation_id = "999"

        mock_paginator = MagicMock()
        # Multiple pages
        mock_paginator.paginate.return_value = [
            {'Contents': [{'Key': 'legislation/bill_100.txt'}]},
            {'Contents': [{'Key': 'legislation/bill_999.txt'}]},
        ]

        mock_head_responses = [
            {'Metadata': {'id': '100'}},
            {'Metadata': {'id': '999'}},  # Match in second page
        ]

        mock_get_object_response = {
            'Body': BytesIO(b"Found in second page")
        }

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.side_effect = mock_head_responses
            mock_s3.get_object.return_value = mock_get_object_response

            result = await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert result['data'] == b"Found in second page"
            assert result['filename'] == 'legislation/bill_999.txt'

    @pytest.mark.asyncio
    async def test_get_legislation_info_not_found_raises_error(self):
        """
        Test that get_legislation_info raises ValueError when legislation not found in S3
        """
        mock_db = Mock(spec=Session)
        legislation_id = "nonexistent"

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {
                'Contents': [
                    {'Key': 'legislation/bill_123.txt'},
                    {'Key': 'legislation/bill_456.txt'}
                ]
            }
        ]

        # None of the objects match
        mock_head_responses = [
            {'Metadata': {'id': '123'}},
            {'Metadata': {'id': '456'}},
        ]

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.side_effect = mock_head_responses

            with pytest.raises(ValueError) as exc_info:
                await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert f"Legislation with ID {legislation_id} not found in S3" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_legislation_info_handles_empty_bucket(self):
        """
        Test get_legislation_info when S3 bucket is empty
        """
        mock_db = Mock(spec=Session)
        legislation_id = "123"

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{}]

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator

            with pytest.raises(ValueError) as exc_info:
                await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert "not found in S3" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_legislation_info_handles_missing_metadata(self):
        """
        Test get_legislation_info when S3 object has no metadata
        """
        mock_db = Mock(spec=Session)
        legislation_id = "123"

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {'Contents': [{'Key': 'legislation/bill_no_metadata.txt'}]}
        ]

        # head_object returns no Metadata key
        mock_head_response = {}

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = mock_head_response

            with pytest.raises(ValueError) as exc_info:
                await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert "not found in S3" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_legislation_info_converts_id_to_string(self):
        """
        Test that get_legislation_info converts legislation_id to string for comparison
        """
        mock_db = Mock(spec=Session)
        legislation_id = 123  # Integer ID

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {'Contents': [{'Key': 'legislation/bill_123.txt'}]}
        ]

        mock_head_response = {
            'Metadata': {'id': '123'}  # Stored as string
        }

        mock_get_object_response = {
            'Body': BytesIO(b"Content")
        }

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = mock_head_response
            mock_s3.get_object.return_value = mock_get_object_response

            result = await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert result is not None
            assert result['metadata']['id'] == '123'

    @pytest.mark.asyncio
    async def test_get_legislation_info_handles_s3_client_error(self):
        """
        Test that get_legislation_info propagates S3 client errors
        """
        mock_db = Mock(spec=Session)
        legislation_id = "123"

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.side_effect = Exception("S3 connection error")

            with pytest.raises(Exception) as exc_info:
                await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert "S3 connection error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_legislation_info_with_large_file(self):
        """
        Test get_legislation_info with large file content
        """
        mock_db = Mock(spec=Session)
        legislation_id = "789"
        large_content = b"X" * 1000000  # 1MB file

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {'Contents': [{'Key': 'legislation/large_bill.txt'}]}
        ]

        mock_head_response = {
            'Metadata': {'id': '789'}
        }

        mock_get_object_response = {
            'Body': BytesIO(large_content)
        }

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = mock_head_response
            mock_s3.get_object.return_value = mock_get_object_response

            result = await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert len(result['data']) == 1000000
            assert result['data'] == large_content

    @pytest.mark.asyncio
    async def test_get_legislation_info_preserves_all_metadata(self):
        """
        Test that all metadata fields are preserved in the response
        """
        mock_db = Mock(spec=Session)
        legislation_id = "555"

        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {'Contents': [{'Key': 'legislation/bill_555.txt'}]}
        ]

        mock_head_response = {
            'Metadata': {
                'id': '555',
                'title': 'Complete Bill',
                'status': 'active',
                'sponsor': 'Senator Smith',
                'date_introduced': '2024-01-15',
                'custom_field': 'custom_value'
            }
        }

        mock_get_object_response = {
            'Body': BytesIO(b"Content")
        }

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = mock_head_response
            mock_s3.get_object.return_value = mock_get_object_response

            result = await LegislationService.get_legislation_info(legislation_id, mock_db)

            assert result['metadata']['id'] == '555'
            assert result['metadata']['title'] == 'Complete Bill'
            assert result['metadata']['sponsor'] == 'Senator Smith'
            assert result['metadata']['custom_field'] == 'custom_value'


class TestLegislationServiceStaticMethods:
    """
    Tests for static method behavior
    """

    def test_list_legislation_is_static_method(self):
        """
        Test that list_legislation is a static method
        """
        assert callable(LegislationService.list_legislation)

        assert isinstance(
            inspect.getattr_static(LegislationService, 'list_legislation'),
            staticmethod
        )

    def test_get_legislation_info_is_static_method(self):
        """
        Test that get_legislation_info is a static method
        """
        assert callable(LegislationService.get_legislation_info)

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

        with patch(
            'src.services.legislation.get_with_filters',
            new_callable=AsyncMock
            ) as mock_list, \
             patch('src.services.legislation.s3_client') as mock_s3:

            mock_list.return_value = {"items": [], "total": 0}

            # Mock S3 for get_legislation_info
            mock_paginator = MagicMock()
            mock_paginator.paginate.return_value = [
                {'Contents': [{'Key': 'test.txt'}]}
            ]
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = {'Metadata': {'id': 'test'}}
            mock_s3.get_object.return_value = {'Body': BytesIO(b"test")}

            await LegislationService.list_legislation(mock_db)
            await LegislationService.get_legislation_info("test", mock_db)

            assert mock_list.called
            assert mock_s3.get_paginator.called


class TestLegislationServiceIntegration:
    """
    Integration-style tests (still mocked, but test workflows)
    """

    @pytest.mark.asyncio
    async def test_list_then_get_workflow(self):
        """
        Test typical workflow: list all, then get specific item from S3
        """
        mock_db = Mock(spec=Session)

        list_result = {
            "items": [
                {"id": "1", "title": "Bill A"},
                {"id": "2", "title": "Bill B"}
            ],
            "total": 2
        }

        with patch(
            'src.services.legislation.get_with_filters',
            new_callable=AsyncMock
            ) as mock_list, \
             patch('src.services.legislation.s3_client') as mock_s3:

            mock_list.return_value = list_result

            mock_paginator = MagicMock()
            mock_paginator.paginate.return_value = [
                {'Contents': [{'Key': 'legislation/bill_1.txt'}]}
            ]
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = {
                'Metadata': {'id': '1', 'title': 'Bill A'}
            }
            mock_s3.get_object.return_value = {
                'Body': BytesIO(b"Full text of Bill A")
            }

            all_legislation = await LegislationService.list_legislation(mock_db)

            first_id = all_legislation["items"][0]["id"]
            details = await LegislationService.get_legislation_info(first_id, mock_db)

            assert len(all_legislation["items"]) == 2
            assert details['metadata']['id'] == "1"
            assert details['data'] == b"Full text of Bill A"

    @pytest.mark.asyncio
    async def test_multiple_get_calls_same_session(self):
        """
        Test multiple get_legislation_info calls with same session
        """
        mock_db = Mock(spec=Session)

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_paginator = MagicMock()

            mock_paginator.paginate.side_effect = [
                [{'Contents': [{'Key': 'bill_1.txt'}]}],
                [{'Contents': [{'Key': 'bill_2.txt'}]}],
                [{'Contents': [{'Key': 'bill_3.txt'}]}]
            ]

            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.side_effect = [
                {'Metadata': {'id': '1'}},
                {'Metadata': {'id': '2'}},
                {'Metadata': {'id': '3'}}
            ]
            mock_s3.get_object.side_effect = [
                {'Body': BytesIO(b"Bill 1 content")},
                {'Body': BytesIO(b"Bill 2 content")},
                {'Body': BytesIO(b"Bill 3 content")}
            ]

            result1 = await LegislationService.get_legislation_info("1", mock_db)
            result2 = await LegislationService.get_legislation_info("2", mock_db)
            result3 = await LegislationService.get_legislation_info("3", mock_db)

            assert result1['metadata']['id'] == "1"
            assert result2['metadata']['id'] == "2"
            assert result3['metadata']['id'] == "3"
            assert mock_s3.get_object.call_count == 3


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
def sample_s3_legislation_response():
    """
    Fixture providing sample S3 legislation response
    """
    return {
        'data': b"Be it enacted by the Senate and House of Representatives...",
        'metadata': {
            'id': '1',
            'title': 'Healthcare Reform Act',
            'status': 'active',
            'sponsor': 'Senator Johnson',
            'date_introduced': '2024-01-15'
        },
        'filename': 'legislation/healthcare_reform_act.txt'
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
        sample_s3_legislation_response
    ):
        """
        Test get_legislation_info using fixtures
        """
        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_paginator = MagicMock()
            mock_paginator.paginate.return_value = [
                {'Contents': [{'Key': sample_s3_legislation_response['filename']}]}
            ]
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = {
                'Metadata': sample_s3_legislation_response['metadata']
            }
            mock_s3.get_object.return_value = {
                'Body': BytesIO(sample_s3_legislation_response['data'])
            }

            result = await LegislationService.get_legislation_info("1", mock_db_session)

            assert result['data'] == sample_s3_legislation_response['data']
            assert result['metadata']['title'] == "Healthcare Reform Act"
            assert result['filename'] == sample_s3_legislation_response['filename']


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

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_paginator = MagicMock()
            mock_paginator.paginate.return_value = [
                {'Contents': [{'Key': 'test.txt'}]}
            ]
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = {'Metadata': {'id': '123'}}

            with pytest.raises(ValueError) as exc_info:
                await LegislationService.get_legislation_info("", mock_db)

            assert "not found in S3" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_legislation_info_with_none_id(self):
        """
        Test get_legislation_info with None as ID
        """
        mock_db = Mock(spec=Session)

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_paginator = MagicMock()
            mock_paginator.paginate.return_value = [
                {'Contents': [{'Key': 'test.txt'}]}
            ]
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = {'Metadata': {'id': '123'}}

            with pytest.raises(ValueError):
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

    @pytest.mark.asyncio
    async def test_get_legislation_info_with_special_characters_in_filename(self):
        """
        Test handling of special characters in S3 filenames
        """
        mock_db = Mock(spec=Session)

        with patch('src.services.legislation.s3_client') as mock_s3:
            mock_paginator = MagicMock()
            mock_paginator.paginate.return_value = [
                {'Contents': [{'Key': 'legislation/bill with spaces & special#chars.txt'}]}
            ]
            mock_s3.get_paginator.return_value = mock_paginator
            mock_s3.head_object.return_value = {'Metadata': {'id': '999'}}
            mock_s3.get_object.return_value = {'Body': BytesIO(b"content")}

            result = await LegislationService.get_legislation_info("999", mock_db)

            assert result['filename'] == 'legislation/bill with spaces & special#chars.txt'
