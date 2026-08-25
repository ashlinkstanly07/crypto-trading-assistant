"""A personal crypto research and trade-journal dashboard.

This app is for education and planning. It reads public market data and never
connects to an exchange or places orders.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


st.set_page_config(page_title="Crypto Compass", page_icon="🧭", layout="wide")

API_BASE = "https://api.coingecko.com/api/v3"
JOURNAL_PATH = Path("data/trade_journal.csv")

COINS = {
    "Bitcoin (BTC)": "bitcoin",
    "Ethereum (ETH)": "ethereum",
    "Solana (SOL)": "solana",
    "Chainlink (LINK)": "chainlink",
    "Polygon (POL)": "polygon-ecosystem-token",
}


@st.cache_data(ttl=60, show_spinner=False)
def get_market_data(coin_ids: list[str]) -> list[dict]:
    """Fetch current public market data from CoinGecko."""
    response = requests.get(
        f"{API_BASE}/coins/markets",
        params={
            "vs_currency": "usd",
            "ids": ",".join(coin_ids),
            "price_change_percentage": "24h",
        },
        timeout=12,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=300, show_spinner=False)
def get_price_history(coin_id: str) -> pd.DataFrame:
    """Fetch seven days of hourly-ish USD prices."""
    response = requests.get(
        f"{API_BASE}/coins/{coin_id}/market_chart",
        params={"vs_currency": "usd", "days": 7, "interval": "hourly"},
        timeout=12,
    )
    response.raise_for_status()
    prices = response.json()["prices"]
    frame = pd.DataFrame(prices, columns=["timestamp", "price_usd"])
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], unit="ms")
    return frame.set_index("timestamp")


def load_journal() -> pd.DataFrame:
    columns = ["date", "coin", "side", "entry_price", "quantity", "stop_loss", "notes"]
    if not JOURNAL_PATH.exists():
        return pd.DataFrame(columns=columns)
    return pd.read_csv(JOURNAL_PATH)


def save_trade(trade: dict) -> None:
    JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    journal = load_journal()
    journal = pd.concat([journal, pd.DataFrame([trade])], ignore_index=True)
    journal.to_csv(JOURNAL_PATH, index=False)


def usd(value: float | int | None) -> str:
    if value is None:
        return "—"
    if value >= 1:
        return f"${value:,.2f}"
    return f"${value:,.6f}"


st.title("🧭 Crypto Compass")
st.caption("Personal market research, risk planning, and trade journaling — not financial advice.")

with st.sidebar:
    st.header("Watchlist")
    selected_labels = st.multiselect(
        "Coins",
        options=list(COINS),
        default=["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"],
    )
    st.caption("Prices refresh at most once a minute to respect the free public API.")

if not selected_labels:
    st.info("Choose at least one coin in the sidebar to start.")
    st.stop()

selected_ids = [COINS[label] for label in selected_labels]

try:
    markets = get_market_data(selected_ids)
except requests.RequestException as error:
    st.error("Market data is unavailable right now. Please try again in a minute.")
    st.caption(f"Technical detail: {error}")
    st.stop()

st.subheader("Market snapshot")
market_columns = st.columns(len(markets))
for column, coin in zip(market_columns, markets):
    with column:
        change = coin.get("price_change_percentage_24h")
        st.metric(
            f"{coin['name']} ({coin['symbol'].upper()})",
            usd(coin.get("current_price")),
            f"{change:+.2f}%" if change is not None else "—",
        )
        st.caption(f"24h volume: {usd(coin.get('total_volume'))}")

st.divider()
left, right = st.columns([1.35, 1])

with left:
    st.subheader("Seven-day price trend")
    chart_label = st.selectbox("Chart coin", selected_labels)
    try:
        history = get_price_history(COINS[chart_label])
        st.line_chart(history, y="price_usd", use_container_width=True)
        first_price = history["price_usd"].iloc[0]
        latest_price = history["price_usd"].iloc[-1]
        trend = (latest_price / first_price - 1) * 100
        st.caption(f"Seven-day change: {trend:+.2f}%")
    except (requests.RequestException, KeyError, IndexError) as error:
        st.warning("The price chart is unavailable right now.")
        st.caption(f"Technical detail: {error}")

with right:
    st.subheader("Risk planner")
    st.caption("Use this before placing a trade. It calculates a maximum position from your risk limit.")
    account_size = st.number_input("Account size (USD)", min_value=0.0, value=1_000.0, step=100.0)
    risk_percent = st.number_input("Risk per trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    entry_price = st.number_input("Planned entry price (USD)", min_value=0.000001, value=100.0, step=1.0, format="%.6f")
    stop_price = st.number_input("Stop-loss price (USD)", min_value=0.000001, value=95.0, step=1.0, format="%.6f")

    if stop_price >= entry_price:
        st.warning("For a long trade, the stop-loss must be below the entry price.")
    else:
        max_loss = account_size * (risk_percent / 100)
        risk_per_coin = entry_price - stop_price
        quantity = max_loss / risk_per_coin
        position_value = quantity * entry_price
        st.metric("Maximum planned loss", usd(max_loss))
        st.metric("Maximum position size", usd(position_value))
        st.caption(f"Quantity: {quantity:,.6f} coins · Stop distance: {(risk_per_coin / entry_price) * 100:.2f}%")

st.divider()
st.subheader("Trade journal")
st.caption("Record your decisions so you can review the process—not just the outcome.")

with st.form("trade_journal", clear_on_submit=True):
    form_left, form_middle, form_right = st.columns(3)
    with form_left:
        trade_date = st.date_input("Date", value=date.today())
        coin = st.selectbox("Coin", selected_labels)
        side = st.selectbox("Side", ["Buy / long", "Sell / short"])
    with form_middle:
        journal_entry = st.number_input("Entry price (USD)", min_value=0.0, value=0.0, step=0.01, format="%.6f")
        journal_quantity = st.number_input("Quantity", min_value=0.0, value=0.0, step=0.01, format="%.6f")
    with form_right:
        journal_stop = st.number_input("Stop-loss (USD)", min_value=0.0, value=0.0, step=0.01, format="%.6f")
        notes = st.text_input("Why this trade?", placeholder="Setup, thesis, and invalidation")
    submitted = st.form_submit_button("Save journal entry")

if submitted:
    if journal_entry <= 0 or journal_quantity <= 0:
        st.error("Enter an entry price and quantity greater than zero.")
    else:
        save_trade(
            {
                "date": trade_date.isoformat(),
                "coin": coin,
                "side": side,
                "entry_price": journal_entry,
                "quantity": journal_quantity,
                "stop_loss": journal_stop,
                "notes": notes,
            }
        )
        st.success("Journal entry saved on your computer.")

journal = load_journal()
if journal.empty:
    st.info("No journal entries yet. Add your first planned trade above.")
else:
    journal["position_value_usd"] = journal["entry_price"] * journal["quantity"]
    st.dataframe(journal.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    st.download_button(
        "Download journal as CSV",
        data=journal.to_csv(index=False).encode("utf-8"),
        file_name="trade_journal.csv",
        mime="text/csv",
    )

st.divider()
st.caption("Educational tool only. Crypto assets are volatile; do your own research and never risk money you cannot afford to lose.")
