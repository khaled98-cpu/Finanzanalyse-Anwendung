"""Flask application that exposes the API endpoints and renders the dashboard."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List

import pandas as pd  # für pd.isna Check
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from save_data import (
    fetch_and_store_stock_data,
    fetch_and_store_news_data
)


app = Flask(__name__, template_folder="frontend", static_folder="frontend/static")
CORS(app, resources={r"/api/*": {"origins": "*"}})

SUPPORTED_SYMBOLS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "TSLA": "Tesla",
    "NVDA": "NVIDIA",
    "META": "Meta",
}

MAX_PAST_DAYS = 365
MAX_FUTURE_DAYS = 31
MAX_NEWS_LOOKBACK = 30


def _parse_date(value: str | None, field_name: str) -> date:
    if not value:
        raise ValueError(f"Parameter '{field_name}' ist erforderlich")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Parameter '{field_name}' muss im Format YYYY-MM-DD sein") from exc


def _validate_range(start: date, end: date) -> None:
    today = date.today()
    if start > end:
        raise ValueError("Startdatum darf nicht nach dem Enddatum liegen")
    if (today - start).days > MAX_PAST_DAYS:
        raise ValueError("Zeitraum darf maximal ein Jahr in die Vergangenheit reichen")
    if (end - today).days > MAX_FUTURE_DAYS:
        raise ValueError("Zeitraum darf maximal einen Monat in die Zukunft reichen")


@app.route("/")
def index() -> str:
    return render_template("dashboard.html", symbols=SUPPORTED_SYMBOLS)


@app.route("/api/news")
def news_endpoint():
    query = request.args.get("query")
    from_param = request.args.get("from")

    if not query:
        return jsonify({"error": "Parameter 'query' ist erforderlich"}), 400

    try:
        start_date = _parse_date(from_param, "from")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    today = date.today()
    if (today - start_date).days > MAX_NEWS_LOOKBACK:
        return (
            jsonify({
                "error": "News können nur für die letzten 30 Tage abgerufen werden",
            }),
            400,
        )

    
    # kleine änderung an der alten Version : erst in der db prüfen 
    # Sie holt fehlende News, speichert sie und gibt alles aus der DB zurück
    result = fetch_and_store_news_data(query, start_date.isoformat())
    
    # Payload für das Frontend zusammenbauen
    articles = result.get("articles", [])
    payload = {
        "query": query,
        "from": start_date.isoformat(),
        "totalResults": result.get("totalResults", len(articles)),
        "articles": articles,
    }
    return jsonify(payload)


@app.route("/api/stocks/yf")
def stocks_yfinance_endpoint():
    symbol = request.args.get("symbol", "").upper()
    start_param = request.args.get("start")
    end_param = request.args.get("end")

    if symbol not in SUPPORTED_SYMBOLS:
        return jsonify({"error": "Ticker wird nicht unterstützt"}), 400

    try:
        start_date = _parse_date(start_param, "start")
        end_date = _parse_date(end_param, "end")
        _validate_range(start_date, end_date)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    # genau wie bei news_data
    frame = fetch_and_store_stock_data(symbol, start_date.isoformat(), end_date.isoformat(), source="yahoo")
    
    if frame is None or frame.empty:
        return jsonify({"error": "Kursdaten konnten nicht geladen werden"}), 502

    records: List[Dict[str, Any]] = []
    for _, row in frame.iterrows():
        d_val = row["date"]
        d_str = d_val.strftime("%Y-%m-%d") if isinstance(d_val, (date, datetime)) else str(d_val)
        
        records.append(
            {
                "date": d_str,
                "open": float(row["open"]),
                "close": float(row["close"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": int(row["volume"]),
            }
        )

    return jsonify({"symbol": symbol, "source": "yfinance", "data": records})


@app.route("/api/stocks/av")
def stocks_alpha_vantage_endpoint():
    symbol = request.args.get("symbol", "").upper()
    start_param = request.args.get("start")
    end_param = request.args.get("end")

    if not symbol:
        return jsonify({"error": "Parameter 'symbol' ist erforderlich"}), 400

    try:
        start_date = _parse_date(start_param, "start")
        end_date = _parse_date(end_param, "end")
        _validate_range(start_date, end_date)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    #  (Quelle: 'alpha_vantage') wird eher nicht genutzt wegen der Kosten 
    frame = fetch_and_store_stock_data(symbol, start_date.isoformat(), end_date.isoformat(), source="alpha_vantage")

    if frame is None or frame.empty:
        return jsonify({"error": "Alpha Vantage Daten konnten nicht geladen werden"}), 502

    data = []
    for _, row in frame.iterrows():
        d_val = row["date"]
        d_str = d_val.strftime("%Y-%m-%d") if isinstance(d_val, (date, datetime)) else str(d_val)
        
        # 'adj_close' sicher behandeln (falls leer)
        adj = row.get("adj_close")
        if pd.isna(adj):
            adj = 0.0

        data.append({
            "date": d_str,
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "adjusted_close": float(adj),
            "volume": int(row["volume"]),
        })

    return jsonify({"symbol": symbol, "source": "alpha_vantage", "data": data})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)