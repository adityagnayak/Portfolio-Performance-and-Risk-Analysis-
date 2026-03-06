# Portfolio Performance & Risk Analysis

A Streamlit app that evaluates whether portfolio returns come from **skill (alpha)** or **market movement (beta)**.

---

## Setup (one-time)

### 1. Install Python
Make sure you have Python 3.10+ installed: https://www.python.org/downloads/

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Run the app

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## How to use

1. **Enter tickers** in the sidebar (comma-separated)
   - Indian stocks: use `.NS` suffix (e.g. `RELIANCE.NS`, `TCS.NS`)
   - US stocks: just the symbol (e.g. `AAPL`, `MSFT`)
2. **Set benchmark**: `^NSEI` for NIFTY 50, `^GSPC` for S&P 500
3. **Choose date range** (default: last 3 years)
4. **Set weights**: equal or custom per stock
5. Click **Run Analysis**

---

## What each metric means

| Metric | Meaning |
|--------|---------|
| **Annual Return** | Total return annualised |
| **Volatility** | Annualised standard deviation of daily returns |
| **Sharpe Ratio** | Return per unit of total risk (>1 = good, >2 = excellent) |
| **Sortino Ratio** | Like Sharpe but only penalises downside risk |
| **Max Drawdown** | Worst peak-to-trough loss in the period |
| **Beta** | How much the portfolio moves per 1% market move |
| **Alpha** | Excess return after adjusting for market risk — the "skill" component |

---

## Ticker examples

| Stock | Ticker |
|-------|--------|
| Reliance Industries | `RELIANCE.NS` |
| TCS | `TCS.NS` |
| Infosys | `INFY.NS` |
| HDFC Bank | `HDFCBANK.NS` |
| ICICI Bank | `ICICIBANK.NS` |
| NIFTY 50 (benchmark) | `^NSEI` |
| Apple | `AAPL` |
| S&P 500 (benchmark) | `^GSPC` |
