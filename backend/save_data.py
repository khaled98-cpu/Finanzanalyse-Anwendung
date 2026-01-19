import pandas as pd
from datetime import datetime, timedelta

from api_calls import (
    get_stock_data_yfinance,
    get_stock_data_alpha_vantage,
    get_news_from_news_api
)
from DatenBearbeiten import (
    prepare_yahoo_data,
    prepare_alpha_data,
    prepare_news_data,
    clean_stock_data
)
from database import stockDaten, news_Daten


def to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()


def run_yahoo_pipeline(ticker: str, start: str, end: str):
    raw = get_stock_data_yfinance(ticker, start, end)
    if raw is None: return None
    df_prepared = prepare_yahoo_data(raw, ticker)
    df_clean = clean_stock_data(df_prepared)
    return df_clean


def run_alpha_pipeline(ticker: str, start: str, end: str):
    raw = get_stock_data_alpha_vantage(ticker, start, end)
    if raw is None: return None
    df_prepared = prepare_alpha_data(raw, ticker)
    df_clean = clean_stock_data(df_prepared)
    return df_clean


def run_news_pipeline(query: str, from_date: str):
    raw = get_news_from_news_api(query, from_date)
    if raw is None: return None
    df_news = prepare_news_data(raw, query)
    return df_news


def _run_pipeline_and_save(ticker, start, end, source):
    if source == 'yahoo':
        df = run_yahoo_pipeline(ticker, start, end)
    else:
        df = run_alpha_pipeline(ticker, start, end)

    if df is not None and not df.empty:
        for _, row in df.iterrows():
            try:
                stockDaten(
                    date=row["date"],
                    ticker=row["ticker"],
                    source=row["source"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    adj_close=row.get("adj_close"),
                    volume=row["volume"]
                ).save()
            except Exception:
                pass


def fetch_and_store_stock_data(ticker: str, start_str: str, end_str: str, source: str):
    req_start = to_date(start_str)
    req_end = to_date(end_str)

    last_entry = stockDaten.objects(ticker=ticker, source=source).order_by('-date').first()

    fetch_start_date = req_start

    if last_entry:
        last_db_date = last_entry.date.date()
        if last_db_date < req_end:
            next_day = last_db_date + timedelta(days=1)
            fetch_start_date = max(req_start, next_day)

            if fetch_start_date <= req_end:
                _run_pipeline_and_save(ticker, fetch_start_date.isoformat(), end_str, source)
    else:
        _run_pipeline_and_save(ticker, start_str, end_str, source)

    qs = stockDaten.objects(
        ticker=ticker,
        source=source,
        date__gte=req_start,
        date__lte=req_end
    ).order_by('date')

    if not qs:
        return None

    data_list = [
        {
            "date": doc.date, "open": doc.open, "high": doc.high, "low": doc.low,
            "close": doc.close, "volume": doc.volume, "adj_close": doc.adj_close,
            "ticker": doc.ticker, "source": doc.source
        } for doc in qs
    ]
    return pd.DataFrame(data_list)


def fetch_and_store_news_data(query: str, from_date_str: str):
    req_start = to_date(from_date_str)
    today = datetime.now().date()

    last_entry = news_Daten.objects(query=query).order_by('-date').first()

    fetch_from = req_start

    if last_entry:
        last_db_date = last_entry.date.date()
        if last_db_date >= req_start:
            fetch_from = last_db_date

        if fetch_from > today:
            fetch_from = today

    if fetch_from <= today:
        df_news = run_news_pipeline(query, fetch_from.isoformat())

        if df_news is not None and not df_news.empty:
            for _, row in df_news.iterrows():
                exists = news_Daten.objects(title=row['title'], query=query).first()
                if not exists:
                    try:
                        news_Daten(
                            date=row["date"], title=row["title"],
                            description=row.get("description"), content=row.get("content"),
                            source=row.get("source"), query=row["query"],
                            author=row.get("author"), url=row.get("url")
                        ).save()
                    except Exception:
                        pass

    qs = news_Daten.objects(query=query, date__gte=req_start).order_by('-date')

    articles = [
        {
            "title": doc.title, "publishedAt": doc.date.isoformat(),
            "source": {"name": doc.source}, "description": doc.description,
            "url": doc.url, "author": doc.author, "content": doc.content
        } for doc in qs
    ]
    return {"articles": articles, "totalResults": len(articles)}


if __name__ == "__main__":
    print("Lade und speichere Testdaten")
    fetch_and_store_stock_data("MSFT", "2025-10-01", "2025-11-30", "yahoo")
    fetch_and_store_news_data("Microsoft", "2025-11-01")
    print("Fertig")
