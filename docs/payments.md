# Payment Data System

This document explains how the payment data system works, including data fetching from the Bank of England, the API endpoints, the scheduler, and frontend recommendations.

---

## Overview

The payment system fetches UK financial statistics from the **Bank of England (BoE) API** and stores them in PostgreSQL. The frontend can then display these statistics on a dashboard.

**Data Sources:**
- Bank of England Statistical Interactive Database (BoE API)
- UK Finance Reports (manual data for payment method breakdown)

---

## Data We Fetch

| Metric | BoE Series Code | Unit | Description |
|--------|-----------------|------|-------------|
| Total Consumer Credit | LPMVZRI | £ millions | Total outstanding consumer credit |
| Credit Card Lending | LPMAUYN | £ millions | Outstanding credit card balances |
| Mortgage Approvals | LPMB3PS | thousands | Number of mortgage approvals |
| Bank Rate | IUMABEDR | % | Bank of England base rate |

---

## API Endpoints

### Base URL: `/api/v1/payment`

### GET `/stats`
Returns the main dashboard statistics with current values and month-over-month changes.

**Response:**
```json
{
  "total_consumer_credit": {
    "value": "£476.2B",
    "raw_value": 476226,
    "change": 2.5,
    "trend": "up",
    "period": "vs last month"
  },
  "credit_card_lending": { ... },
  "mortgage_approvals": { ... },
  "bank_rate": { ... },
  "last_updated": "2024-02-29T12:00:00"
}
```

### GET `/payment-methods`
Returns UK payment method market share breakdown.

**Response:**
```json
{
  "methods": [
    { "name": "Debit Cards", "percentage": 42, "color": "#3B82F6" },
    { "name": "Credit Cards", "percentage": 12, "color": "#8B5CF6" },
    { "name": "Faster Payments", "percentage": 25, "color": "#10B981" },
    { "name": "Direct Debit", "percentage": 11, "color": "#F59E0B" },
    { "name": "Cash", "percentage": 6, "color": "#6B7280" },
    { "name": "Other", "percentage": 4, "color": "#EC4899" }
  ],
  "source": "UK Finance Payments Report 2025",
  "last_updated": "2025-06-01"
}
```

### GET `/trend-alerts`
Returns alerts for metrics with significant changes (>5%).

**Response:**
```json
{
  "alerts": [
    {
      "metric": "Credit Card Lending",
      "change": 7.2,
      "direction": "up",
      "message": "Credit Card Lending increased by 7.2%"
    }
  ],
  "last_updated": "2024-02-29T12:00:00"
}
```

### POST `/refresh`
Manually triggers a data refresh from the BoE API.

**Response:**
```json
{
  "success": true,
  "records_saved": 96,
  "message": "Successfully fetched and saved 96 records"
}
```

---

## Scheduler

The app includes an automatic scheduler that refreshes BoE data daily.

### How It Works

1. **Technology:** APScheduler (AsyncIO scheduler)
2. **Schedule:** Daily at 6:00 AM UTC
3. **Why 6 AM UTC?** BoE typically updates their data in the morning UK time

### Configuration

The scheduler is defined in `src/utils/scheduler.py`:

```python
# Runs daily at 6:00 AM UTC
scheduler.add_job(
    refresh_boe_data_job,
    trigger=CronTrigger(hour=6, minute=0),
    id="boe_data_refresh",
    name="Daily BoE Data Refresh"
)
```

### Lifecycle

- **Starts:** When the FastAPI app starts (via lifespan event)
- **Stops:** When the FastAPI app shuts down
- **Logs:** Info messages on each refresh attempt

### Manual Refresh

You can also trigger a refresh manually via the `/payment/refresh` endpoint. This is useful for:
- Initial data population
- Testing
- Forcing an update after BoE releases new data

---

## Database Schema

### Table: `payment_statistics`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| series_code | TEXT | BoE series code (e.g., LPMVZRI) |
| metric_name | TEXT | Human-readable name |
| date | DATE | Data point date |
| value | FLOAT | The numeric value |
| unit | TEXT | Unit type (millions_gbp, percent, etc.) |
| source | TEXT | Data source (default: Bank of England) |
| created_at | TEXT | Record creation time (ISO format) |
| updated_at | TEXT | Last update time (ISO format) |

---

## Frontend Recommendations

### Dashboard Layout

A clean, informative dashboard for UK payment statistics:

```
┌─────────────────────────────────────────────────────────────┐
│  PAYMENT INSIGHTS DASHBOARD                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │ Consumer    │ │ Credit Card │ │ Mortgage    │ │ Bank   ││
│  │ Credit      │ │ Lending     │ │ Approvals   │ │ Rate   ││
│  │             │ │             │ │             │ │        ││
│  │  £476.2B    │ │  £2.98B     │ │  64,200     │ │ 5.25%  ││
│  │  ↑ +2.5%    │ │  ↑ +1.8%    │ │  ↓ -3.2%    │ │ — 0%   ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
│                                                             │
│  ┌──────────────────────────┐  ┌────────────────────────┐  │
│  │  Payment Methods         │  │  Trend Alerts          │  │
│  │  [PIE CHART]             │  │  ⚠️ Credit up 7.2%     │  │
│  │                          │  │  📉 Mortgages down 5%  │  │
│  │  42% Debit               │  │                        │  │
│  │  25% Faster Payments     │  │  Last updated: 6:00 AM │  │
│  │  12% Credit              │  │                        │  │
│  │  ...                     │  │                        │  │
│  └──────────────────────────┘  └────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. Stat Cards (Top Row)
Display each metric in a card with:
- **Large value** (e.g., "£476.2B")
- **Change indicator** with arrow (↑/↓/—)
- **Percentage change** with color (green=up, red=down, gray=stable)
- **Subtle label** (e.g., "vs last month")

**UI Tips:**
- Use semantic colors: green for growth (not always good!), red for decline
- Consider context: mortgage approval decline might be neutral, not bad
- Show the raw trend, let users interpret

#### 2. Payment Methods (Pie/Donut Chart)
Best displayed as a **donut chart**:
- Use the colors from the API response
- Show percentages on hover
- Include a legend
- Add source attribution ("Source: UK Finance 2025")

**Libraries:** Chart.js, Recharts, or ApexCharts

#### 3. Trend Alerts Panel
Display as a notification/alert list:
- Icon based on direction (📈/📉)
- Metric name and change percentage
- Optional: click to see historical chart

**Show when:**
- Change > 5% (significant movement)
- Empty state: "All metrics stable this month"

### Historical Charts (Optional Enhancement)

If you want to show trends over time:

```
GET /payment/stats?history=true  (would need to implement)
```

Display as a **line chart** showing:
- 12-24 months of data
- Multiple series toggle (show/hide metrics)
- Hover for exact values

### Mobile Considerations

- Stack stat cards vertically on mobile
- Make pie chart full-width
- Collapse trend alerts into expandable section
- Ensure touch targets are large enough

### Color Scheme Suggestion

```css
/* Stat card backgrounds */
--card-bg: #F8FAFC;
--card-border: #E2E8F0;

/* Trend colors */
--trend-up: #10B981;     /* Green */
--trend-down: #EF4444;   /* Red */
--trend-stable: #6B7280; /* Gray */

/* Chart colors (from API) */
--debit: #3B82F6;
--credit: #8B5CF6;
--faster: #10B981;
--direct-debit: #F59E0B;
--cash: #6B7280;
--other: #EC4899;
```

### Loading States

Show skeleton loaders while fetching:
- Stat cards: pulsing rectangles
- Pie chart: circular skeleton
- Alerts: list item skeletons

### Error Handling

Display user-friendly messages:
- "Unable to load payment data. Please try again."
- Show last successful update time
- Offer manual refresh button

---

## Testing

Run tests with:
```bash
pytest tests/test_payment_service.py -v
```

Tests cover:
- BoE configuration validation
- CSV parsing logic
- Error page detection
- Stat calculations (up/down/stable trends)
- Value formatting (billions, percentages)
- Payment methods data
- Trend alerts generation

---

## Troubleshooting

### "BoE API returned an error page"
- One or more series codes may be invalid
- Check BoE website for current valid codes
- The API blocking may have increased - check headers

### "Connection timeout to Supabase"
- Check if Supabase project is paused (free tier)
- Verify network allows port 5432
- Check credentials in app_config.py

### "0 records saved"
- Data may already exist (updates don't count as new)
- Check the date range being fetched
- Verify series codes are returning data
