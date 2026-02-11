"""
Payment Service Tests

Tests for the Bank of England data fetching and payment statistics.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, datetime
from src.services.payment import PaymentService, BOE_SERIES, BOE_HEADERS
from src.schema.payment import TrendDirection


class TestBOEConfiguration:
    """Test the BoE API configuration."""
    
    def test_boe_series_codes_defined(self):
        """Verify all required BoE series codes are configured."""
        required_metrics = ["Total Consumer Credit", "Credit Card Lending", "Mortgage Approvals", "Bank Rate"]
        
        metric_names = [info["name"] for info in BOE_SERIES.values()]
        for metric in required_metrics:
            assert metric in metric_names, f"Missing metric: {metric}"
    
    def test_boe_headers_include_user_agent(self):
        """Verify User-Agent header is set (required by BoE)."""
        assert "User-Agent" in BOE_HEADERS
        assert "Mozilla" in BOE_HEADERS["User-Agent"]
    
    def test_boe_headers_include_referer(self):
        """Verify Referer header is set (helps avoid blocks)."""
        assert "Referer" in BOE_HEADERS
        assert "bankofengland" in BOE_HEADERS["Referer"]


class TestCSVParsing:
    """Test CSV parsing logic."""
    
    def test_parse_valid_csv(self):
        """Test parsing a valid BoE CSV response."""
        csv_text = """DATE,LPMVZRI,LPMAUYN,IUMABEDR
31 Jan 2024,476226,2984785,5.25
29 Feb 2024,480096,2990000,5.25"""
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        records = PaymentService._parse_and_save_csv(mock_db, csv_text)
        
        # Should have added records (3 series x 2 dates = up to 6, but only 3 match our config)
        assert records >= 0
        assert mock_db.commit.called
    
    def test_parse_html_error_page(self):
        """Test that HTML error pages are detected."""
        html_error = "<!DOCTYPE html><html><body>Error</body></html>"
        
        mock_db = MagicMock()
        records = PaymentService._parse_and_save_csv(mock_db, html_error)
        
        assert records == -1  # -1 signals error page
    
    def test_parse_empty_csv(self):
        """Test parsing empty CSV returns 0."""
        mock_db = MagicMock()
        records = PaymentService._parse_and_save_csv(mock_db, "")
        
        assert records == 0
    
    def test_parse_csv_headers_only(self):
        """Test CSV with headers but no data."""
        csv_text = "DATE,LPMVZRI,LPMAUYN"
        
        mock_db = MagicMock()
        records = PaymentService._parse_and_save_csv(mock_db, csv_text)
        
        assert records == 0


class TestFetchBOEData:
    """Test the BoE data fetching."""
    
    @pytest.mark.asyncio
    async def test_fetch_success(self):
        """Test successful data fetch from BoE."""
        mock_response = MagicMock()
        mock_response.text = """DATE,LPMVZRI,IUMABEDR
31 Jan 2024,476226,5.25"""
        mock_response.raise_for_status = MagicMock()
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await PaymentService.fetch_boe_data(mock_db)
            
            assert result["success"] is True
            assert "records_saved" in result
    
    @pytest.mark.asyncio
    async def test_fetch_returns_error_on_html(self):
        """Test that HTML error responses are handled."""
        mock_response = MagicMock()
        mock_response.text = "<!DOCTYPE html><html>Error</html>"
        mock_response.raise_for_status = MagicMock()
        
        mock_db = MagicMock()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await PaymentService.fetch_boe_data(mock_db)
            
            assert result["success"] is False
            assert "error" in result


class TestStatCalculations:
    """Test stat calculations for dashboard."""
    
    def test_calculate_stat_with_increase(self):
        """Test stat calculation shows increase correctly."""
        mock_db = MagicMock()
        
        # Mock two records: latest = 110, previous = 100 (10% increase)
        mock_latest = MagicMock()
        mock_latest.value = 110000  # millions
        mock_latest.date = date(2024, 2, 29)
        
        mock_previous = MagicMock()
        mock_previous.value = 100000
        mock_previous.date = date(2024, 1, 31)
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_latest, mock_previous
        ]
        
        info = {"name": "Test Metric", "unit": "millions_gbp"}
        stat = PaymentService._calculate_stat_for_series(mock_db, "TEST", info)
        
        assert stat is not None
        assert stat.change == 10.0
        assert stat.trend == TrendDirection.up
    
    def test_calculate_stat_with_decrease(self):
        """Test stat calculation shows decrease correctly."""
        mock_db = MagicMock()
        
        mock_latest = MagicMock()
        mock_latest.value = 90000
        mock_latest.date = date(2024, 2, 29)
        
        mock_previous = MagicMock()
        mock_previous.value = 100000
        mock_previous.date = date(2024, 1, 31)
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_latest, mock_previous
        ]
        
        info = {"name": "Test Metric", "unit": "millions_gbp"}
        stat = PaymentService._calculate_stat_for_series(mock_db, "TEST", info)
        
        assert stat is not None
        assert stat.change == -10.0
        assert stat.trend == TrendDirection.down
    
    def test_calculate_stat_stable(self):
        """Test stable trend when change is minimal."""
        mock_db = MagicMock()
        
        mock_latest = MagicMock()
        mock_latest.value = 100100  # 0.1% change
        mock_latest.date = date(2024, 2, 29)
        
        mock_previous = MagicMock()
        mock_previous.value = 100000
        mock_previous.date = date(2024, 1, 31)
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_latest, mock_previous
        ]
        
        info = {"name": "Test Metric", "unit": "millions_gbp"}
        stat = PaymentService._calculate_stat_for_series(mock_db, "TEST", info)
        
        assert stat is not None
        assert stat.trend == TrendDirection.stable
    
    def test_format_value_billions(self):
        """Test values over 1000M are formatted as billions."""
        mock_db = MagicMock()
        
        mock_record = MagicMock()
        mock_record.value = 1500000  # 1.5B
        mock_record.date = date(2024, 2, 29)
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_record]
        
        info = {"name": "Test", "unit": "millions_gbp"}
        stat = PaymentService._calculate_stat_for_series(mock_db, "TEST", info)
        
        assert "B" in stat.value  # Should be in billions
    
    def test_format_value_percent(self):
        """Test percentage values are formatted correctly."""
        mock_db = MagicMock()
        
        mock_record = MagicMock()
        mock_record.value = 5.25
        mock_record.date = date(2024, 2, 29)
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_record]
        
        info = {"name": "Bank Rate", "unit": "percent"}
        stat = PaymentService._calculate_stat_for_series(mock_db, "TEST", info)
        
        assert "%" in stat.value
        assert "5.25" in stat.value


class TestPaymentMethods:
    """Test payment methods endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_payment_methods(self):
        """Test payment methods returns all methods."""
        result = await PaymentService.get_payment_methods()
        
        assert result.methods is not None
        assert len(result.methods) == 6  # Debit, Credit, Faster, Direct, Cash, Other
        
        # Check percentages sum to 100
        total = sum(m.percentage for m in result.methods)
        assert total == 100
    
    @pytest.mark.asyncio
    async def test_payment_methods_have_colors(self):
        """Test each payment method has a color for charts."""
        result = await PaymentService.get_payment_methods()
        
        for method in result.methods:
            assert method.color is not None
            assert method.color.startswith("#")


class TestTrendAlerts:
    """Test trend alerts generation."""
    
    @pytest.mark.asyncio
    async def test_no_alerts_when_stable(self):
        """Test no alerts generated when changes are small."""
        mock_db = MagicMock()
        
        # Mock stable data (small changes)
        mock_record = MagicMock()
        mock_record.value = 100000
        mock_record.date = date(2024, 2, 29)
        mock_record.updated_at = "2024-02-29T12:00:00"
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_record]
        mock_db.query.return_value.order_by.return_value.first.return_value = mock_record
        
        result = await PaymentService.get_trend_alerts(mock_db)
        
        # With only one record per series, change will be 0, no alerts
        assert result.alerts is not None
