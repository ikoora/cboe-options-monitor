from datetime import date, timedelta
from io import BytesIO, StringIO
import json

import pandas as pd
import requests


# Use yesterday's calendar date
dt = (date.today() - timedelta(days=1)).isoformat()

url = (
    "https://www.cboe.com/us/options/symboldir/"
    f"equity-index-options/download/?dt={dt}"
)

headers = {
    "User-Agent": "Mozilla/5.0"
}

print(f"Downloading Cboe directory for {dt}")
print(url)

response = requests.get(url, headers=headers, timeout=60)
response.raise_for_status()

raw = response.content

# Try CSV first, otherwise Excel
try:
    text = raw.decode("utf-8-sig")
    df = pd.read_csv(StringIO(text))
except Exception:
    df = pd.read_excel(BytesIO(raw))

# IMPORTANT: remove spaces around Cboe column names
df.columns = df.columns.astype(str).str.strip()

print("Detected columns:", list(df.columns))

if "Stock Symbol" not in df.columns:
    raise RuntimeError(
        f"'Stock Symbol' column not found. Columns: {list(df.columns)}"
    )

symbols = sorted(
    df["Stock Symbol"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.upper()
    .unique()
    .tolist()
)

output = {
    "source": "Cboe Equity & Index Options Symbol Directory",
    "date": dt,
    "count": len(symbols),
    "symbols": symbols
}

with open("cboe-options.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"Saved {len(symbols)} symbols to cboe-options.json")
