#!/usr/bin/env python3
"""
daily_report.py
Daily market report: IKO.AX, ASX 200, Bitcoin.
IKO analysis combines textbook technical/risk indicators with
Korean tech market narrative (Samsung, SK Hynix) and news sentiment.
"""

import json
import smtplib
import numpy as np
import yfinance as yf
import requests
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── load config ──────────────────────────────────────────────────────────────────
CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH) as f:
    config = json.load(f)

SENDER        = config["email"]
APP_PASSWORD  = config["app_password"]
RECIPIENT     = config["email"]
NEWS_API_KEY  = config["news_api_key"]

# ── fetch price history ──────────────────────────────────────────────────────────
def fetch(ticker, period="90d"):
    try:
        hist = yf.Ticker(ticker).history(period=period)
        return hist if not hist.empty else None
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

# ── technical indicators ─────────────────────────────────────────────────────────

def rsi(closes, period=14):
    """Wilder RSI - Technical Analysis of Financial Markets (Murphy)."""
    deltas   = np.diff(closes)
    gains    = np.where(deltas > 0, deltas, 0.0)
    losses   = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    for g, l in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + l) / period
    if avg_loss == 0:
        return 100.0
    return round(100 - (100 / (1 + avg_gain / avg_loss)), 1)

def ema(closes, span):
    k, result = 2 / (span + 1), [closes[0]]
    for p in closes[1:]:
        result.append(p * k + result[-1] * (1 - k))
    return np.array(result)

def macd(closes):
    """MACD (12,26,9) - Murphy."""
    ml  = ema(closes, 12) - ema(closes, 26)
    sig = ema(ml, 9)
    return round(ml[-1], 4), round(sig[-1], 4), round((ml - sig)[-1], 4)

def bollinger(closes, period=20):
    """Bollinger Bands (20-day, 2 std dev) - Murphy."""
    if len(closes) < period:
        return None, None, None, None
    w   = closes[-period:]
    mid = np.mean(w)
    std = np.std(w, ddof=1)
    upper, lower = mid + 2*std, mid - 2*std
    pct_b = (closes[-1] - lower) / (upper - lower) if upper != lower else 0.5
    return round(upper, 3), round(mid, 3), round(lower, 3), round(pct_b, 2)

def sma(closes, period):
    return round(np.mean(closes[-period:]), 3) if len(closes) >= period else None

def annualised_vol(closes):
    """Annualised volatility = std(daily returns) x sqrt(252) - Bodie, Kane & Marcus."""
    if len(closes) < 10:
        return None
    r = np.diff(closes) / closes[:-1]
    return round(np.std(r, ddof=1) * np.sqrt(252) * 100, 1)

def calc_beta(iko_closes, mkt_closes):
    """Beta via OLS - CAPM (Bodie, Kane & Marcus)."""
    n = min(len(iko_closes), len(mkt_closes))
    if n < 20:
        return None
    r_i = np.diff(iko_closes[-n:]) / iko_closes[-n:-1]
    r_m = np.diff(mkt_closes[-n:]) / mkt_closes[-n:-1]
    n2  = min(len(r_i), len(r_m))
    cov = np.cov(r_i[-n2:], r_m[-n2:])[0][1]
    var = np.var(r_m[-n2:], ddof=1)
    return round(cov / var, 2) if var != 0 else None

def volume_signal(hist):
    avg = hist["Volume"].iloc[:-1].tail(20).mean()
    today = hist["Volume"].iloc[-1]
    return int(today), round(today / avg, 2) if avg else None

# ── analyse IKO ──────────────────────────────────────────────────────────────────
def analyse_iko(hist, mkt_hist):
    closes = hist["Close"].values
    price  = closes[-1]

    r_val                         = rsi(closes)
    macd_val, sig_val, macd_h     = macd(closes)
    bb_upper, bb_mid, bb_lower, pct_b = bollinger(closes)
    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50)
    vol   = annualised_vol(closes)
    b     = calc_beta(closes, mkt_hist["Close"].values) if mkt_hist is not None else None
    today_vol, vol_ratio = volume_signal(hist)

    open_      = hist["Open"].iloc[-1]
    prev_close = hist["Close"].iloc[-2]
    week_start = hist["Close"].iloc[-5] if len(hist) >= 5 else hist["Close"].iloc[0]
    high_5d    = hist["High"].tail(5).max()
    low_5d     = hist["Low"].tail(5).min()
    last_date  = hist.index[-1]
    # Label as "last trading day" when the report runs on a non-trading day
    today_obj  = datetime.now().date()
    is_live    = hasattr(last_date, 'date') and last_date.date() == today_obj
    trade_label = "today" if is_live else last_date.strftime("%a %d %b")

    return {
        "price":        round(price, 3),
        "trade_label":  trade_label,
        "day_pct":      round((price - open_) / open_ * 100, 2),
        "overnight":  round((price - prev_close) / prev_close * 100, 2),
        "week_pct":   round((price - week_start) / week_start * 100, 2),
        "high_5d":    round(high_5d, 3),
        "low_5d":     round(low_5d, 3),
        "rsi":        r_val,
        "macd":       macd_val,
        "macd_sig":   sig_val,
        "macd_hist":  macd_h,
        "bb_upper":   bb_upper,
        "bb_mid":     bb_mid,
        "bb_lower":   bb_lower,
        "pct_b":      pct_b,
        "sma20":      sma20,
        "sma50":      sma50,
        "volatility": vol,
        "beta":       b,
        "vol_ratio":  vol_ratio,
        "today_vol":  today_vol,
    }

# ── Korean tech correlation ──────────────────────────────────────────────────────
KOREAN_PEERS = {
    "Samsung Electronics": "005930.KS",
    "SK Hynix":            "000660.KS",
    "KOSPI Index":         "^KS11",
}

def get_korean_tech():
    results = {}
    for name, ticker in KOREAN_PEERS.items():
        hist = fetch(ticker, "5d")
        if hist is None or len(hist) < 2:
            results[name] = None
            continue
        close      = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2]
        pct        = round((close - prev_close) / prev_close * 100, 2)
        week_start = hist["Close"].iloc[0]
        week_pct   = round((close - week_start) / week_start * 100, 2)
        last_date   = hist.index[-1]
        today_obj   = datetime.now().date()
        is_live     = hasattr(last_date, 'date') and last_date.date() == today_obj
        trade_label = "today" if is_live else last_date.strftime("%a %d %b")
        results[name] = {"price": round(close, 2), "day_pct": pct, "week_pct": week_pct, "trade_label": trade_label}
    return results

def korean_narrative(peers):
    """Derive macro tailwind/headwind from Samsung + SK Hynix moves."""
    lines = []
    lines.append("[ Korean Tech Peers - Market Narrative ]")

    scores = []
    for name, data in peers.items():
        if data is None:
            lines.append(f"  {name}: Data unavailable")
            continue
        direction = "UP" if data["day_pct"] >= 0 else "DOWN"
        lines.append(f"  {name}: {direction} {data['day_pct']:+.2f}% ({data['trade_label']})  |  {data['week_pct']:+.2f}% this week")
        scores.append(data["day_pct"])

    if scores:
        avg = sum(scores) / len(scores)
        if avg > 1.5:
            signal = "STRONG TAILWIND - Korean tech sector surging. Bullish backdrop for IKO."
        elif avg > 0.3:
            signal = "MILD TAILWIND - Korean tech peers trending positive."
        elif avg < -1.5:
            signal = "STRONG HEADWIND - Korean tech sector under pressure. Watch IKO closely."
        elif avg < -0.3:
            signal = "MILD HEADWIND - Korean tech peers trending negative."
        else:
            signal = "NEUTRAL - Korean tech sector moving sideways."
        lines.append(f"")
        lines.append(f"  Macro Signal: {signal}")

    return "\n".join(lines)

# ── news sentiment ───────────────────────────────────────────────────────────────
POSITIVE_WORDS = {
    "surge", "soar", "rise", "gain", "beat", "strong", "record", "growth",
    "bullish", "breakthrough", "boom", "rally", "upgrade", "demand", "profit",
    "partnership", "deal", "contract", "investment", "innovation", "lead",
    "outperform", "optimistic", "rebound", "recovery", "milestone", "expand"
}
NEGATIVE_WORDS = {
    "fall", "drop", "decline", "crash", "miss", "weak", "cut", "loss",
    "bearish", "slowdown", "concerns", "warning", "downgrade", "tariff",
    "sanction", "recall", "layoff", "penalty", "risk", "uncertainty",
    "underperform", "disappoint", "slump", "halt", "ban", "fine"
}

def score_headline(text):
    words = set(text.lower().split())
    pos   = len(words & POSITIVE_WORDS)
    neg   = len(words & NEGATIVE_WORDS)
    if pos > neg:   return "positive"
    if neg > pos:   return "negative"
    return "neutral"

def get_news():
    queries = [
        "IKO ASX stock",
        "Samsung Electronics AI chips",
        "SK Hynix HBM memory AI",
        "Korea technology semiconductor",
    ]
    headlines = []
    seen      = set()
    cutoff    = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

    for q in queries:
        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q":        q,
                    "from":     cutoff,
                    "sortBy":   "publishedAt",
                    "pageSize": 5,
                    "language": "en",
                    "apiKey":   NEWS_API_KEY,
                },
                timeout=10,
            )
            resp.raise_for_status()
            for article in resp.json().get("articles", []):
                title = article.get("title", "").strip()
                if title and title not in seen:
                    seen.add(title)
                    headlines.append({
                        "title":     title,
                        "source":    article.get("source", {}).get("name", ""),
                        "sentiment": score_headline(title),
                    })
        except Exception as e:
            print(f"News fetch error ({q}): {e}")

    return headlines[:12]

def news_narrative(headlines):
    lines = []
    lines.append("[ News Sentiment - Market Narrative ]")

    if not headlines:
        lines.append("  No recent headlines found.")
        return "\n".join(lines)

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for h in headlines:
        counts[h["sentiment"]] += 1

    total = len(headlines)
    lines.append(f"  Sentiment: {counts['positive']} positive / "
                 f"{counts['neutral']} neutral / {counts['negative']} negative "
                 f"({total} headlines, last 3 days)")
    lines.append("")

    pos_ratio = counts["positive"] / total
    if pos_ratio >= 0.6:
        outlook = "BULLISH narrative - majority of news flow is positive."
    elif counts["negative"] / total >= 0.5:
        outlook = "BEARISH narrative - significant negative news flow."
    else:
        outlook = "MIXED narrative - no clear directional sentiment."
    lines.append(f"  Outlook: {outlook}")
    lines.append("")

    lines.append("  Top Headlines:")
    shown = 0
    for sentiment in ("positive", "negative", "neutral"):
        for h in headlines:
            if h["sentiment"] == sentiment and shown < 5:
                tag = "[+]" if sentiment == "positive" else ("[-]" if sentiment == "negative" else "[~]")
                src = f" ({h['source']})" if h["source"] else ""
                lines.append(f"  {tag} {h['title']}{src}")
                shown += 1

    return "\n".join(lines)

# ── build full IKO insights ──────────────────────────────────────────────────────
def build_insights(d, peers, headlines):
    lines = []
    p = d["price"]

    # Price action
    lines.append("[ Price Action ]")
    if d["week_pct"] > 2:
        lines.append(f"  Strong upward momentum: +{d['week_pct']}% over 5 days.")
    elif d["week_pct"] < -2:
        lines.append(f"  Downward pressure: {d['week_pct']}% over 5 days.")
    else:
        lines.append(f"  Consolidating: {d['week_pct']:+.2f}% over 5 days.")
    if abs(d["overnight"]) >= 1:
        move = "gapped UP" if d["overnight"] > 0 else "gapped DOWN"
        lines.append(f"  Overnight {move} {abs(d['overnight']):.2f}% vs prior close.")
    range_5d = d["high_5d"] - d["low_5d"]
    if range_5d > 0:
        pos = (p - d["low_5d"]) / range_5d
        if pos >= 0.8:
            lines.append(f"  Near 5-day high (${d['high_5d']}) - price showing strength.")
        elif pos <= 0.2:
            lines.append(f"  Near 5-day low (${d['low_5d']}) - watch for support level.")
        else:
            lines.append(f"  Mid-range. 5-day band: ${d['low_5d']} - ${d['high_5d']}.")

    # RSI
    lines += ["", "[ RSI (14-day) - Momentum Oscillator ]"]
    r = d["rsi"]
    if r:
        interp = ("OVERBOUGHT - potential pullback signal." if r > 70 else
                  "OVERSOLD - potential recovery signal." if r < 30 else
                  "Bullish momentum building." if r > 55 else
                  "Bearish momentum building." if r < 45 else "Neutral zone.")
        lines.append(f"  RSI: {r}  ->  {interp}")

    # MACD
    lines += ["", "[ MACD (12/26/9) - Trend & Momentum ]"]
    if d["macd"]:
        direction = "Bullish" if d["macd"] > d["macd_sig"] else "Bearish"
        cross     = "MACD above signal line." if d["macd"] > d["macd_sig"] else "MACD below signal line."
        momentum  = "Increasing" if d["macd_hist"] > 0 else "Decreasing"
        lines.append(f"  Signal: {direction} - {cross}")
        lines.append(f"  Histogram: {d['macd_hist']:+.4f}  ({momentum} momentum)")

    # Bollinger
    lines += ["", "[ Bollinger Bands (20-day, 2 std dev) - Volatility ]"]
    if d["bb_upper"]:
        pb   = d["pct_b"]
        zone = ("Upper band - statistically elevated, watch for mean reversion." if pb > 0.8 else
                "Lower band - statistically depressed, watch for bounce." if pb < 0.2 else
                "Within normal range.")
        lines.append(f"  Upper: ${d['bb_upper']}  |  Mid: ${d['bb_mid']}  |  Lower: ${d['bb_lower']}")
        lines.append(f"  %B: {pb:.0%}  ->  {zone}")

    # Moving averages
    lines += ["", "[ Moving Averages - Trend Direction ]"]
    if d["sma20"] and d["sma50"]:
        trend = "Bullish (Golden Cross)" if d["sma20"] > d["sma50"] else "Bearish (Death Cross)"
        vs20  = "above" if p > d["sma20"] else "below"
        lines.append(f"  SMA20: ${d['sma20']}  |  SMA50: ${d['sma50']}")
        lines.append(f"  Trend: {trend}")
        lines.append(f"  Price is {vs20} its 20-day average.")

    # Risk
    lines += ["", "[ Risk Metrics - Bodie, Kane & Marcus ]"]
    if d["volatility"]:
        vrisk = ("Low volatility" if d["volatility"] < 20 else
                 "Moderate volatility" if d["volatility"] < 40 else "High volatility")
        lines.append(f"  Annualised Volatility: {d['volatility']}%  ({vrisk})")
    if d["beta"]:
        brisk = ("High beta - amplifies market moves." if d["beta"] > 1.2 else
                 "Low beta - relatively defensive." if d["beta"] < 0.8 else
                 "Market-like sensitivity.")
        lines.append(f"  Beta vs ASX 200: {d['beta']}  ({brisk})")

    # Volume
    lines += ["", "[ Volume Analysis ]"]
    if d["vol_ratio"]:
        vsig = ("Significantly above average - strong conviction." if d["vol_ratio"] > 1.5 else
                "Slightly above average - moderate participation." if d["vol_ratio"] > 1.1 else
                "Below average - low conviction, treat move cautiously." if d["vol_ratio"] < 0.7 else
                "Average volume - normal trading activity.")
        lines.append(f"  Volume: {d['today_vol']:,}  ({d['vol_ratio']}x 20-day average)")
        lines.append(f"  {vsig}")

    # Korean tech narrative
    lines += ["", korean_narrative(peers)]

    # News sentiment
    lines += ["", news_narrative(headlines)]

    return "\n".join(lines)

# ── ASX 200 ──────────────────────────────────────────────────────────────────────
def get_asx200(hist):
    if hist is None or len(hist) < 2:
        return None, None
    close, prev = hist["Close"].iloc[-1], hist["Close"].iloc[-2]
    return round(close, 2), round((close - prev) / prev * 100, 2)

# ── Bitcoin ──────────────────────────────────────────────────────────────────────
def get_btc_price():
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "aud", "include_24hr_change": "true"},
            timeout=10,
        )
        resp.raise_for_status()
        d = resp.json()["bitcoin"]
        return d["aud"], round(d["aud_24h_change"], 2)
    except Exception as e:
        print(f"Error fetching BTC: {e}")
        return None, None

# ── helpers ──────────────────────────────────────────────────────────────────────
def arrow(val):  return "UP" if val >= 0 else "DOWN"
def fmt_pct(val): return f"{val:+.2f}%"

# ── build email ──────────────────────────────────────────────────────────────────
def build_email(iko, asx_price, asx_pct, btc_price, btc_pct, peers, headlines):
    today    = datetime.now().strftime("%A, %d %B %Y")
    iko_line = (f"AUD ${iko['price']:.3f}  [{arrow(iko['day_pct'])} {fmt_pct(iko['day_pct'])} {iko['trade_label']}]"
                if iko else "Data unavailable")
    asx_line = (f"{asx_price:,.2f}  [{arrow(asx_pct)} {fmt_pct(asx_pct)}]"
                if asx_price else "Data unavailable")
    btc_line = (f"AUD ${btc_price:,.0f}  [{arrow(btc_pct)} {fmt_pct(btc_pct)} in 24h]"
                if btc_price else "Data unavailable")
    insights = build_insights(iko, peers, headlines) if iko else "No data available."

    subject = f"Daily Market Report - {today}"
    body    = f"""Daily Market Report
===================
{today}

ASX 200 Index
--------------
Level:  {asx_line}

IKO.AX  (IKO Industries - ASX)
--------------------------------
Price:  {iko_line}

IKO.AX - In-Depth Analysis
============================
{insights}

Bitcoin (BTC)
--------------
Price:  {btc_line}

---
Methodology: RSI (Wilder), MACD (Murphy), Bollinger Bands (Murphy),
Beta & Volatility (Bodie, Kane & Marcus), Korean peer correlation,
News sentiment (NewsAPI). Generated by daily_report.py
"""
    return subject, body

# ── send email ───────────────────────────────────────────────────────────────────
def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"]    = SENDER
    msg["To"]      = RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())

# ── main ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Fetching market data...")
    iko_hist = fetch("IKO.AX", "90d")
    mkt_hist = fetch("^AXJO", "90d")

    iko              = analyse_iko(iko_hist, mkt_hist) if iko_hist is not None else None
    asx_price, asx_pct = get_asx200(mkt_hist)
    btc_price, btc_pct = get_btc_price()

    print("Fetching Korean tech peers...")
    peers = get_korean_tech()

    print("Fetching news sentiment...")
    headlines = get_news()

    subject, body = build_email(iko, asx_price, asx_pct, btc_price, btc_pct, peers, headlines)

    print(body)
    print("Sending email...")
    send_email(subject, body)
    print(f"Report sent to {RECIPIENT}")
