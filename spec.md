# Spec: Daily Market Report (`daily_report.py`)

## Purpose
Generates and emails a daily market report each morning covering IKO.AX (ASX-listed stock),
the ASX 200 index, Bitcoin (BTC/AUD), Korean tech peers, and news sentiment.

---

## Inputs

| Source | Data |
|---|---|
| Yahoo Finance (`yfinance`) | IKO.AX price history (90 days), ASX 200 index (^AXJO), Korean tech peers (5 days) |
| CoinGecko API | Bitcoin price and 24h change in AUD |
| NewsAPI | Recent headlines (last 3 days) for IKO, Samsung, SK Hynix, Korea semiconductors |
| `config.json` | Gmail credentials, app password, NewsAPI key |

---

## Output
A plain-text email sent to the user's own Gmail address with:
- Subject: `Daily Market Report - [Day, Date]`
- ASX 200 index level and daily change
- IKO.AX price and daily change
- IKO in-depth analysis (see below)
- Bitcoin price and 24h change

---

## IKO.AX In-Depth Analysis Sections

1. **Price Action** — day move, overnight gap, position within 5-day range
2. **RSI (14-day)** — momentum signal: overbought / oversold / neutral
3. **MACD (12/26/9)** — trend direction, signal line crossover, histogram
4. **Bollinger Bands (20-day, 2 std dev)** — volatility, %B position
5. **Moving Averages** — SMA20 vs SMA50, golden/death cross, price vs SMA20
6. **Risk Metrics** — annualised volatility, beta vs ASX 200
7. **Volume Analysis** — today's volume vs 20-day average
8. **AI Supply Chain Peers** — Samsung, SK Hynix, KOSPI, Nvidia, TSMC daily and weekly moves + macro signal
9. **News Sentiment** — up to 12 headlines scored positive/negative/neutral, outlook summary

---

## AI Supply Chain Peers

| Name | Ticker |
|---|---|
| Samsung Electronics | 005930.KS |
| SK Hynix | 000660.KS |
| KOSPI Index | ^KS11 |
| Nvidia | NVDA |
| TSMC | TSM |

Macro signal thresholds (average daily % move across all peers):
- `> +1.5%` → STRONG TAILWIND
- `> +0.3%` → MILD TAILWIND
- `< -0.3%` → MILD HEADWIND
- `< -1.5%` → STRONG HEADWIND
- Otherwise → NEUTRAL

---

## News Sentiment Logic
- Searches 4 queries via NewsAPI, deduplicates, keeps up to 12 headlines
- Scores each headline by matching positive/negative keyword lists
- Outlook: BULLISH if 60%+ positive, BEARISH if 50%+ negative, otherwise MIXED

---

## Config (`config.json`)
```json
{
  "email": "user@gmail.com",
  "app_password": "...",
  "news_api_key": "..."
}
```

---

## Scheduling
- Intended to run at 7:00 AM daily via Windows Task Scheduler
- On Mondays, market data reflects Friday's last close (no weekend trading)
- Non-trading days: report labels data with the last trading date instead of "today"

---

## Constraints
- Does NOT support multiple recipients
- Does NOT store historical reports to disk
- Does NOT support HTML email — plain text only
- Requires internet connection for all data sources

---

## Dependencies
```
yfinance
numpy
requests
```
Standard library: `smtplib`, `json`, `pathlib`, `datetime`, `email`
