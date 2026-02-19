"""
Payment Service

This service handles:
1. Fetching payment data from the Bank of England API
2. Storing it in our database
3. Calculating trends (month-over-month, year-over-year changes)
4. Returning data in a format the frontend can use
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from src.models.payment import PaymentStatistic
from src.schema.payment import (
    StatItem, 
    TrendDirection,
    MarketPulseStatsResponse,
    TrendAlert,
    TrendAlertsResponse
)


# ============================================
# Bank of England API Configuration
# ============================================

# These are the series codes from the Bank of England database
# Each code represents a specific metric they track
# Find more at: https://www.bankofengland.co.uk/boeapps/iadb/
BOE_SERIES = {
    "LPMVZRI": {
        "name": "Total Consumer Credit",
        "unit": "millions_gbp"
    },
    "LPMAUYN": {
        "name": "Credit Card Lending",
        "unit": "millions_gbp"
    },
    "LPMB3PS": {
        "name": "Mortgage Approvals",
        "unit": "thousands"
    },
    "IUMABEDR": {
        "name": "Bank Rate",
        "unit": "percent"
    }
}

# Base URL for the Bank of England statistics API
BOE_API_URL = "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp"

# Headers to make the request look like a browser (BoE blocks requests without these)
# The BoE has strong anti-bot protection, so we need comprehensive browser-like headers
BOE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/csv,text/plain,*/*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.bankofengland.co.uk/boeapps/iadb/Index.asp",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "no-cache",
}


class PaymentService:
    """
    Handles all payment-related data operations.
    
    Main methods:
    - fetch_boe_data(): Gets fresh data from Bank of England
    - get_market_pulse_stats(): Returns formatted stats for the dashboard
    - get_payment_methods(): Returns payment method breakdown
    - get_trend_alerts(): Returns notable trends
    """

    # ============================================
    # Fetching data from Bank of England
    # ============================================
    
    @staticmethod
    async def fetch_boe_data(db: Session, months_back: int = 24) -> Dict:
        """
        Fetch payment data from the Bank of England API and save to database.
        
        How it works:
        1. Build the API URL with the series codes we want
        2. Make the HTTP request to get CSV data
        3. Parse the CSV into rows
        4. Save each row to our database
        
        Args:
            db: Database session
            months_back: How many months of history to fetch (default 24)
            
        Returns:
            Dict with success status and count of records saved
        """
        # Calculate date range (from X months ago to now)
        date_from = (datetime.now() - timedelta(days=months_back * 30)).strftime("%d/%b/%Y")
        date_to = "now"
        
        # Join all series codes with commas
        series_codes = ",".join(BOE_SERIES.keys())
        
        # Build the API URL with all required parameters
        params = {
            "csv.x": "yes",  # We want CSV format (easier to parse)
            "Datefrom": date_from,
            "Dateto": date_to,
            "SeriesCodes": series_codes,
            "UsingCodes": "Y",
            "CSVF": "TN"  # Tabular format, no titles
        }
        
        try:
            # Make the API request (with headers so BoE doesn't block us)
            # follow_redirects=True is required as BoE returns a 302 redirect
            async with httpx.AsyncClient(timeout=30.0, headers=BOE_HEADERS, follow_redirects=True) as client:
                response = await client.get(BOE_API_URL, params=params)
                response.raise_for_status()
                
            # Parse the CSV response
            records_saved = PaymentService._parse_and_save_csv(db, response.text)
            
            # Check if we got an error page instead of CSV
            if records_saved == -1:
                return {
                    "success": False,
                    "error": "BoE API returned an error page instead of CSV data. Check series codes are valid."
                }
            
            return {
                "success": True,
                "records_saved": records_saved,
                "message": f"Successfully fetched and saved {records_saved} records"
            }
            
        except httpx.HTTPError as e:
            # Something went wrong with the API request
            return {
                "success": False,
                "error": f"Failed to fetch from BoE API: {str(e)}"
            }
        except Exception as e:
            # Something else went wrong
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    @staticmethod
    def _parse_and_save_csv(db: Session, csv_text: str) -> int:
        """
        Parse the CSV from Bank of England and save to database.
        
        The CSV format looks like:
        DATE,LPMVZRI,LPMAUYN,LPMB3PS,IUMABEDR
        31 Jan 2024,1234.5,567.8,45678,5.25
        29 Feb 2024,1245.6,570.2,46000,5.25
        
        Returns the number of records saved, or -1 if the response was invalid.
        """
        # Check if we got HTML error page instead of CSV
        if csv_text.strip().startswith("<!DOCTYPE") or csv_text.strip().startswith("<html"):
            return -1  # Signal that we got an error page, not CSV
            
        lines = csv_text.strip().split("\n")
        if len(lines) < 2:
            return 0
        
        # Verify first line looks like CSV headers
        if not lines[0].startswith("DATE"):
            return -1
            
        # First line is headers (the series codes)
        headers = lines[0].split(",")
        records_saved = 0
        
        # Process each data row
        for line in lines[1:]:
            if not line.strip():
                continue
                
            values = line.split(",")
            if len(values) < 2:
                continue
            
            # First column is the date
            try:
                date_str = values[0].strip()
                date = datetime.strptime(date_str, "%d %b %Y").date()
            except ValueError:
                # Skip rows with invalid dates
                continue
            
            # Process each series code column
            for i, header in enumerate(headers[1:], start=1):
                series_code = header.strip()
                
                # Skip if we don't know this series code
                if series_code not in BOE_SERIES:
                    continue
                    
                # Skip if no value
                if i >= len(values) or not values[i].strip():
                    continue
                
                try:
                    value = float(values[i].strip())
                except ValueError:
                    continue
                
                # Check if we already have this data point
                existing = db.query(PaymentStatistic).filter(
                    PaymentStatistic.series_code == series_code,
                    PaymentStatistic.date == date
                ).first()
                
                if existing:
                    # Update existing record
                    existing.value = value
                    existing.updated_at = datetime.now().isoformat()
                else:
                    # Create new record
                    new_stat = PaymentStatistic(
                        series_code=series_code,
                        metric_name=BOE_SERIES[series_code]["name"],
                        date=date,
                        value=value,
                        unit=BOE_SERIES[series_code]["unit"]
                    )
                    db.add(new_stat)
                    records_saved += 1
        
        db.commit()
        return records_saved

    # ============================================
    # Getting formatted stats for the frontend
    # ============================================

    @staticmethod
    async def get_market_pulse_stats(db: Session) -> MarketPulseStatsResponse:
        """
        Get the main dashboard statistics.
        
        This returns the latest value for each metric plus the change
        compared to the previous month.
        """
        stats = {}
        last_updated = None
        
        for series_code, info in BOE_SERIES.items():
            stat_item = PaymentService._calculate_stat_for_series(db, series_code, info)
            if stat_item:
                # Convert series code to a nice field name
                field_name = info["name"].lower().replace(" ", "_")
                stats[field_name] = stat_item
                
                # Track the most recent update
                latest = db.query(PaymentStatistic).filter(
                    PaymentStatistic.series_code == series_code
                ).order_by(desc(PaymentStatistic.updated_at)).first()
                
                if latest and (not last_updated or latest.updated_at > last_updated):
                    last_updated = latest.updated_at
        
        return MarketPulseStatsResponse(
            total_consumer_credit=stats.get("total_consumer_credit"),
            credit_card_lending=stats.get("credit_card_lending"),
            mortgage_approvals=stats.get("mortgage_approvals"),
            bank_rate=stats.get("bank_rate"),
            last_updated=last_updated
        )

    @staticmethod
    def _calculate_stat_for_series(db: Session, series_code: str, info: Dict) -> Optional[StatItem]:
        """
        Calculate the stat item for one series.
        
        Gets the latest two data points and calculates the change between them.
        """
        # Get the latest 2 records for this series (for calculating change)
        recent = db.query(PaymentStatistic).filter(
            PaymentStatistic.series_code == series_code
        ).order_by(desc(PaymentStatistic.date)).limit(2).all()
        
        if not recent:
            return None
        
        latest = recent[0]
        
        # Format the value for display
        if info["unit"] == "millions_gbp":
            # Convert to billions if large enough
            if latest.value >= 1000:
                formatted_value = f"£{latest.value / 1000:.1f}B"
            else:
                formatted_value = f"£{latest.value:.0f}M"
        elif info["unit"] == "percent":
            formatted_value = f"{latest.value:.2f}%"
        elif info["unit"] == "count":
            formatted_value = f"{latest.value:,.0f}"
        else:
            formatted_value = str(latest.value)
        
        # Calculate change if we have a previous month
        if len(recent) >= 2:
            previous = recent[1]
            if previous.value != 0:
                change = ((latest.value - previous.value) / previous.value) * 100
            else:
                change = 0
        else:
            change = 0
        
        # Determine trend direction
        if change > 0.5:
            trend = TrendDirection.up
        elif change < -0.5:
            trend = TrendDirection.down
        else:
            trend = TrendDirection.stable
        
        return StatItem(
            value=formatted_value,
            raw_value=latest.value,
            change=round(change, 1),
            trend=trend,
            period="vs last month"
        )

    # ============================================
    # Trend alerts
    # ============================================

    @staticmethod
    async def get_trend_alerts(db: Session) -> TrendAlertsResponse:
        """
        Get notable trends that are worth highlighting.
        
        An alert is generated when a metric has changed by more than 5%
        compared to the previous month.
        """
        alerts = []
        
        for series_code, info in BOE_SERIES.items():
            stat = PaymentService._calculate_stat_for_series(db, series_code, info)
            
            if stat and abs(stat.change) >= 5:
                # This is a significant change worth alerting
                if stat.trend == TrendDirection.up:
                    message = f"{info['name']} increased by {stat.change}%"
                else:
                    message = f"{info['name']} decreased by {abs(stat.change)}%"
                
                alerts.append(TrendAlert(
                    metric=info["name"],
                    change=abs(stat.change),
                    direction=stat.trend,
                    message=message
                ))
        
        # Sort by biggest changes first
        alerts.sort(key=lambda x: x.change, reverse=True)
        
        # Get last updated time
        latest = db.query(PaymentStatistic).order_by(
            desc(PaymentStatistic.updated_at)
        ).first()
        
        return TrendAlertsResponse(
            alerts=alerts,
            last_updated=latest.updated_at if latest else None
        )

    # ============================================
    # Historical data for charts
    # ============================================

    @staticmethod
    async def get_history(db: Session, months: int = 24):
        """
        Get historical data for all metrics - for frontend charts.
        
        Returns time series data ordered chronologically.
        """
        from src.schema.payment import HistoryResponse, MetricHistory, HistoryDataPoint
        
        result = {}
        
        for series_code, info in BOE_SERIES.items():
            # Get all records for this series, ordered by date
            records = db.query(PaymentStatistic).filter(
                PaymentStatistic.series_code == series_code
            ).order_by(PaymentStatistic.date).limit(months).all()
            
            if records:
                data_points = [
                    HistoryDataPoint(
                        date=record.date.strftime("%Y-%m-%d"),
                        value=record.value
                    )
                    for record in records
                ]
                
                metric_history = MetricHistory(
                    metric_name=info["name"],
                    unit=info["unit"],
                    data=data_points
                )
                
                # Map series code to field name
                field_name = info["name"].lower().replace(" ", "_")
                result[field_name] = metric_history
        
        return HistoryResponse(
            total_consumer_credit=result.get("total_consumer_credit"),
            credit_card_lending=result.get("credit_card_lending"),
            mortgage_approvals=result.get("mortgage_approvals"),
            bank_rate=result.get("bank_rate"),
            months_included=months
        )

    # ============================================
    # Legacy methods (keeping for backwards compatibility)
    # ============================================
    
    @staticmethod
    def list_payment_data():
        """Old mock data method - keeping for backwards compatibility"""
        return [
            {"id": 1, "amount": 100.00, "currency": "USD", "status": "Completed"},
            {"id": 2, "amount": 250.50, "currency": "EUR", "status": "Pending"},
            {"id": 3, "amount": 75.25, "currency": "GBP", "status": "Failed"}
        ]

    @staticmethod
    def get_payment_info():
        """Old mock data method - keeping for backwards compatibility"""
        return {
            "provider": "Stripe",
            "currency": "USD",
        }
