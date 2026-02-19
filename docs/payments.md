# Payment Data System

This document explains how the payment data system works, including data fetching from the Bank of England, the API endpoints, the scheduler, and frontend recommendations.

---

## Overview

The payment system fetches UK financial statistics from the **Bank of England (BoE) API** and stores them in PostgreSQL. The frontend can then display these statistics on a dashboard.

**Data Source:**
- Bank of England Statistical Interactive Database (BoE API)

> **Note:** All data comes directly from the BoE API. There is no hardcoded or manually maintained data.

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

**All data is fetched from the Bank of England API and stored in the database. The `change` field is calculated from real historical data.**

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

## Frontend Data Handling

This section explains how to interpret, destructure, and handle the API responses in your frontend application.

### TypeScript Interfaces

Define these types to match the API responses:

```typescript
// Trend direction enum
type TrendDirection = 'up' | 'down' | 'stable';

// Individual stat item (used in /stats response)
interface StatItem {
  value: string;        // Formatted display value, e.g. "£476.2B"
  raw_value: number;    // Raw numeric value for calculations
  change: number;       // Percentage change, e.g. 2.5 or -3.2
  trend: TrendDirection;
  period: string;       // Always "vs last month"
}

// GET /payment/stats response
interface PaymentStatsResponse {
  total_consumer_credit: StatItem | null;
  credit_card_lending: StatItem | null;
  mortgage_approvals: StatItem | null;
  bank_rate: StatItem | null;
  last_updated: string | null;  // ISO datetime string
}

// Alert for significant changes
interface TrendAlert {
  metric: string;
  change: number;
  direction: TrendDirection;
  message: string;
}

// GET /payment/trend-alerts response
interface TrendAlertsResponse {
  alerts: TrendAlert[];
  last_updated: string | null;
}

// POST /payment/refresh response
interface RefreshResponse {
  success: boolean;
  records_saved?: number;
  message?: string;
  error?: string;
}
```

### Fetching Data

```typescript
const API_BASE = 'http://localhost:8000/api/v1';

// Fetch payment stats
async function fetchPaymentStats(): Promise<PaymentStatsResponse> {
  const response = await fetch(`${API_BASE}/payment/stats`);
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
}

// Fetch trend alerts
async function fetchTrendAlerts(): Promise<TrendAlertsResponse> {
  const response = await fetch(`${API_BASE}/payment/trend-alerts`);
  if (!response.ok) throw new Error('Failed to fetch trend alerts');
  return response.json();
}

// Trigger manual refresh
async function refreshData(): Promise<RefreshResponse> {
  const response = await fetch(`${API_BASE}/payment/refresh`, {
    method: 'POST'
  });
  return response.json();
}
```

### Destructuring Responses

#### Stats Response

```typescript
// Fetch and destructure stats
const stats = await fetchPaymentStats();

// Destructure individual metrics (may be null if no data)
const {
  total_consumer_credit,
  credit_card_lending,
  mortgage_approvals,
  bank_rate,
  last_updated
} = stats;

// Use with null checks
if (total_consumer_credit) {
  console.log(total_consumer_credit.value);    // "£476.2B"
  console.log(total_consumer_credit.change);   // 2.5
  console.log(total_consumer_credit.trend);    // "up"
}

// Convert to array for mapping (useful for rendering cards)
const statItems = [
  { key: 'consumer_credit', label: 'Consumer Credit', data: total_consumer_credit },
  { key: 'credit_cards', label: 'Credit Card Lending', data: credit_card_lending },
  { key: 'mortgages', label: 'Mortgage Approvals', data: mortgage_approvals },
  { key: 'bank_rate', label: 'Bank Rate', data: bank_rate },
].filter(item => item.data !== null);
```

#### Trend Alerts Response

```typescript
const { alerts, last_updated } = await fetchTrendAlerts();

// Filter by direction if needed
const increasingTrends = alerts.filter(a => a.direction === 'up');
const decreasingTrends = alerts.filter(a => a.direction === 'down');

// Sort by largest change
const sortedAlerts = [...alerts].sort((a, b) => b.change - a.change);
```

### React Component Example

```tsx
import { useState, useEffect } from 'react';

function StatCard({ label, data }: { label: string; data: StatItem | null }) {
  if (!data) return <div className="stat-card loading">No data</div>;

  const trendColor = {
    up: 'text-green-500',
    down: 'text-red-500',
    stable: 'text-gray-500'
  }[data.trend];

  const trendIcon = {
    up: '↑',
    down: '↓',
    stable: '—'
  }[data.trend];

  return (
    <div className="stat-card">
      <h3 className="text-sm text-gray-500">{label}</h3>
      <p className="text-2xl font-bold">{data.value}</p>
      <p className={`text-sm ${trendColor}`}>
        {trendIcon} {data.change > 0 ? '+' : ''}{data.change}% {data.period}
      </p>
    </div>
  );
}

function PaymentDashboard() {
  const [stats, setStats] = useState<PaymentStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPaymentStats()
      .then(setStats)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!stats) return <div>No data available</div>;

  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard label="Consumer Credit" data={stats.total_consumer_credit} />
      <StatCard label="Credit Cards" data={stats.credit_card_lending} />
      <StatCard label="Mortgages" data={stats.mortgage_approvals} />
      <StatCard label="Bank Rate" data={stats.bank_rate} />
    </div>
  );
}
```

### Handling Edge Cases

```typescript
// 1. Null stat items (no data in database)
const value = stats.total_consumer_credit?.value ?? 'N/A';

// 2. Format the last_updated date
function formatLastUpdated(isoString: string | null): string {
  if (!isoString) return 'Never';
  const date = new Date(isoString);
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 3. Determine if data is stale (older than 24 hours)
function isDataStale(lastUpdated: string | null): boolean {
  if (!lastUpdated) return true;
  const updateTime = new Date(lastUpdated).getTime();
  const now = Date.now();
  const hoursSinceUpdate = (now - updateTime) / (1000 * 60 * 60);
  return hoursSinceUpdate > 24;
}

// 4. Show warning if stale
if (isDataStale(stats.last_updated)) {
  console.warn('Payment data may be outdated');
}

// 5. Handle empty alerts array
const hasAlerts = alerts.length > 0;
// Show "All metrics stable" message when no alerts
```

### Data Refresh Pattern

```typescript
function usePaymentData() {
  const [stats, setStats] = useState<PaymentStatsResponse | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadStats = async () => {
    const data = await fetchPaymentStats();
    setStats(data);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const result = await refreshData();
      if (result.success) {
        // Reload stats after successful refresh
        await loadStats();
      } else {
        throw new Error(result.error);
      }
    } catch (err) {
      console.error('Refresh failed:', err);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => { loadStats(); }, []);

  return { stats, refreshing, handleRefresh };
}
```

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
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Trend Alerts                                         │  │
│  │  ⚠️ Credit Card Lending up 7.2%                       │  │
│  │  📉 Mortgage Approvals down 5%                        │  │
│  │                                                        │  │
│  │  Last updated: 6:00 AM                                │  │
│  └──────────────────────────────────────────────────────┘  │
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

#### 2. Trend Alerts Panel
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
