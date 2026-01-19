import pandas as pd

def prepare_yahoo_data(df_raw: pd.DataFrame, ticker: str, source: str = "yahoo") -> pd.DataFrame:

    df = df_raw.copy()
    df = df[["Open", "High", "Low", "Close", "Volume"]]

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    df = df.reset_index()
    df = df.rename(columns={"Date": "date"})

    df["ticker"] = ticker
    df["source"] = source

    df["date"] = pd.to_datetime(df["date"])
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    df["adj_close"] = df["close"]

    df = df.sort_values("date").reset_index(drop=True)

    return df


def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()


    df = df.dropna(subset=["date", "close"])


    df = df.drop_duplicates(subset=["ticker", "date", "source"])


    df = df[df["close"] > 0]


    df = df.sort_values("date").reset_index(drop=True)

    return df

def prepare_alpha_data(raw_dict: dict, ticker: str, source: str = "alpha_vantage") -> pd.DataFrame:



    df = pd.DataFrame.from_dict(raw_dict, orient="index")


    df.index = pd.to_datetime(df.index)
    df = df.reset_index()
    df = df.rename(columns={"index": "date"})


    df = df.rename(columns={
        "1. open": "open",
        "2. high": "high",
        "3. low": "low",
        "4. close": "close",
        "5. volume": "volume"
    })


    df["adj_close"] = df["close"]


    df = df[["date", "open", "high", "low", "close", "adj_close", "volume"]]


    df["ticker"] = ticker
    df["source"] = source


    for col in ["open", "high", "low", "close", "adj_close", "volume"]:
        df[col] = df[col].astype(float)


    df = df.sort_values("date").reset_index(drop=True)

    return df


def prepare_news_data(news_json: dict, query: str) -> pd.DataFrame:


    articles = news_json.get("articles", [])

    if not articles:
        print("keine article bekommen.")
        return pd.DataFrame(columns=["date","title","description","content","source","query", "author", "url"])

    df = pd.DataFrame(articles)


    for col in ["publishedAt", "title", "description", "content", "source", "author", "url"]:
        if col not in df.columns:
            df[col] = None


    df = df.rename(columns={"publishedAt": "date"})


    df["source"] = df["source"].apply(
        lambda x: x.get("name") if isinstance(x, dict) and "name" in x else None
    )


    df["date"] = pd.to_datetime(df["date"], errors="coerce")


    df["query"] = query


    df = df.dropna(subset=["date", "title"])


    df = df.sort_values("date").reset_index(drop=True)

    return df


