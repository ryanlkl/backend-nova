import os
import sys
import unittest
from unittest.mock import patch

from fastapi import HTTPException


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.services.market import MarketService


class TestMarketService(unittest.TestCase):
    def test_get_market_object_requires_bucket(self):
        with self.assertRaises(HTTPException) as ctx:
            MarketService.get_market_object("any", "")
        self.assertEqual(ctx.exception.status_code, 400)

    @patch("src.services.market.download_from_s3")
    @patch("src.services.market.s3_client")
    def test_get_market_object_matches_metadata_id(self, mock_s3, mock_download):
        mock_s3.list_objects_v2.return_value = {
            "Contents": [{"Key": "A2A Payments.txt"}],
            "IsTruncated": False
        }
        mock_s3.head_object.return_value = {
            "Metadata": {"id": "uuid-123"},
            "ContentType": "text/plain"
        }
        mock_download.return_value = b"hello"

        result = MarketService.get_market_object("uuid-123", "test-bucket")
        self.assertEqual(result["key"], "A2A Payments.txt")
        self.assertEqual(result["content_type"], "text/plain")

    @patch("src.services.market.download_from_s3")
    @patch("src.services.market.s3_client")
    def test_get_market_object_matches_metadata_title(self, mock_s3, mock_download):
        mock_s3.list_objects_v2.return_value = {
            "Contents": [{"Key": "A2A Payments.txt"}],
            "IsTruncated": False
        }
        mock_s3.head_object.return_value = {
            "Metadata": {"title": "A2A Payments"},
            "ContentType": "text/plain"
        }
        mock_download.return_value = b"hello"

        result = MarketService.get_market_object("A2A Payments", "test-bucket")
        self.assertEqual(result["key"], "A2A Payments.txt")

    @patch("src.services.market.download_from_s3")
    @patch("src.services.market.s3_client")
    def test_get_market_object_matches_filename_stem(self, mock_s3, mock_download):
        mock_s3.list_objects_v2.return_value = {
            "Contents": [{"Key": "A2A Payments.txt"}],
            "IsTruncated": False
        }
        mock_s3.head_object.return_value = {
            "Metadata": {},
            "ContentType": "text/plain"
        }
        mock_download.return_value = b"hello"

        result = MarketService.get_market_object("A2A Payments", "test-bucket")
        self.assertEqual(result["key"], "A2A Payments.txt")

    @patch("src.services.market.s3_client")
    def test_get_market_object_not_found(self, mock_s3):
        mock_s3.list_objects_v2.return_value = {
            "Contents": [{"Key": "A2A Payments.txt"}],
            "IsTruncated": False
        }
        mock_s3.head_object.return_value = {
            "Metadata": {"id": "uuid-123"},
            "ContentType": "text/plain"
        }

        with self.assertRaises(HTTPException) as ctx:
            MarketService.get_market_object("missing", "test-bucket")
        self.assertEqual(ctx.exception.status_code, 404)

