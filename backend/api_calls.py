import requests
import os
import json
import yfinance as yf  
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()


def get_news_from_news_api(query: str, from_date: str,to_date=None, sprache="de"):

    from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
    today = datetime.now().date()

    if (today - from_date_obj).days > 29:
        print(f"Fehler: Startdatum ist älter als 30 Tage. Das erlaubt der Free-Plan leider nicht.")
        return None

    API_KEY = os.getenv("NEWS_API_KEY_1")
    if not API_KEY:
        print("Fehler: NEWS_API_KEY wurde nicht in der .env Datei gefunden.")
        return None

    url = "https://newsapi.org/v2/everything"

    # 2. Variablen für den "Date-Walker"
    current_to_date = datetime.now().isoformat()

    all_articles = []
    seen_titles = set()  # Set für schnelle Duplikat-Erkennung

    print(f"Starte Abruf für '{query}' ab {from_date}...")

    # 3. Die Schleife: Holt Daten, schiebt das Zeitfenster nach hinten
    while True:
        params = {
            'q': query,
            'searchIn': 'title',
            'from': from_date,  # Bleibt statisch (der Start des Zeitraums)
            'to': current_to_date,  # Wird dynamisch in die Vergangenheit geschoben
            'language': sprache,
            'pageSize': 100,  # Maximum pro Request
            'apiKey': API_KEY,
            'sortBy': 'publishedAt'  # Wichtig: Neueste zuerst
        }

        try:
            response = requests.get(url, params=params)


            if response.status_code != 200:
                print(f"API-Fehler bei Anfrage: {response.status_code} - {response.text}")
                break

            data = response.json()
            batch = data.get("articles", [])

            if not batch:
                print("Keine weiteren Artikel in diesem Zeitfenster gefunden.")
                break


            new_articles_count = 0
            for article in batch:
                title = article.get('title')
                # Nur hinzufügen, wenn wir den Titel noch nicht kennen
                if title and title not in seen_titles:
                    all_articles.append(article)
                    seen_titles.add(title)
                    new_articles_count += 1

            print(
                f"  -> Batch geladen: {len(batch)} Artikel erhalten, davon {new_articles_count} neu. (Gesamt: {len(all_articles)})")


            if len(batch) < 100:
                print("Ende der Ergebnisse erreicht (Batch < 100).")
                break

            last_article = batch[-1]
            last_date = last_article.get('publishedAt')


            if last_date == current_to_date:
                print("Warnung: Zeitstempel bewegt sich nicht mehr vorwärts. Abbruch um Loop zu verhindern.")
                break

            current_to_date = last_date

        except requests.exceptions.RequestException as e:
            print(f"Netzwerkfehler aufgetreten: {e}")
            break
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}")
            break

    if all_articles:
        print(f"Abruf erfolgreich beendet. {len(all_articles)} Artikel gesammelt.")
        return {
            "status": "ok",
            "totalResults": len(all_articles),
            "articles": all_articles
        }
    else:
        print("Keine Artikel gefunden oder Fehler beim Abruf.")
        return None

def get_stock_data_yfinance(thema: str, start_date: str, end_date: str):
    try:
        stock=yf.Ticker(thema)
        
        hist_data = stock.history(start=start_date, end=end_date)
        if hist_data.empty:
            print(f"Fehler (yfinance): Keine Daten für Ticker '{thema}' im Zeitraum gefunden.")
            return None
            
        print(f"API-Anfrage (yfinance) für '{thema}' erfolgreich.")
        return hist_data
    except Exception as e:
        print(f"Ein Fehler mit yfinance ist aufgetreten: {e}")
        return None
    
def get_stock_data_alpha_vantage(thema: str, start_date: str, end_date: str) -> dict | None:
    
    API_KEY = os.getenv("ALPHA_VANTAGE_KEY")
    
    if not API_KEY:
        print("Fehler: ALPHA_VANTAGE_KEY wurde nicht in der .env Datei gefunden.")
        return None
        
    url = "https://www.alphavantage.co/query"
    
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": thema,
        "outputsize": "full", # historische Daten
        "apikey": API_KEY,
        "datatype": "json"
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Fehler bei AlphaVantage-Anfrage: Status Code {response.status_code}")
            return None
            
        data = response.json()
        print(data)

        if "Error Message" in data:
            print(f"API-Fehler (AlphaVantage): {data['Error Message']}")
            return None
        if "Note" in data:
            print(f"API-Hinweis (AlphaVantage): {data['Note']} ")
            return None
        
        start_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        time_series_data = data.get("Time Series (Daily)", {})
        filtered_data = {}
        
        for date_str, values in time_series_data.items():
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if start_obj <= current_date <= end_obj:
                filtered_data[date_str] = values
                
        if not filtered_data:
            print(f"Fehler (AlphaVantage): Keine Daten für thema '{thema}' im Zeitraum {start_date} bis {end_date} gefunden.")
            return None
        
        return filtered_data

    except requests.exceptions.RequestException as e:
        print(f"Ein Fehler mit der Netzwerkverbindung ist aufgetreten: {e}")
        return None  
    
    


if __name__ == "__main__":
    # ---- test  news_api ----------
    print("TEST:  newsapi ")
    
    suchbegriff = "gold"
    start_date = "2025-11-01"

    news_data = get_news_from_news_api(suchbegriff, start_date)

    if news_data:
        
        total_results = news_data['totalResults']
        print(f"Gesamtzahl gefundener Artikel: {total_results}")

        articles_received = len(news_data['articles'])
        print(f"Anzahl der abgerufenen Artikel (Limit): {articles_received}")
        
        if articles_received > 0:
            if total_results > articles_received:
                print("(Hinweis: Mehr Artikel gefunden, als der kostenlose Plan zulässt.)")
                
            print("--- Erster Artikel  ---")
            
            article = news_data['articles'][0]
            print(article)
        
        else:
            print("Keine Artikel mit diesem Wort im Titel im Zeitraum gefunden.")
    
    else:
        print("Datenabruf fehlgeschlagen")


    # ----- test yfinance---------
    
    # print(" TEST: yfinance")
    
    # stock_ticker = "AAPLE" # für tesla
    # stock_start = "2025-10-01"
    # stock_end = "2025-11-10"
    
    # yf_data_frame = get_stock_data_yfinance(stock_ticker, stock_start, stock_end)
    
    # if yf_data_frame is not None:
        
        
    #     print(yf_data_frame)
        
    # ------------test Alpha 
    
    # print("--- test: Alpha  ---")
    
    # av_ticker = "AAPL"
    # stock_start = "2025-11-09" 
    # stock_end = "2025-11-10"   
    # av_data = get_stock_data_alpha_vantage(av_ticker, stock_start, stock_end)
    
    # if av_data:
    #     print(f"Daten für '{av_ticker}' gefunden ({len(av_data)} Einträge):")
    #     print(json.dumps(av_data, indent=2))
    
    # else:
    #     print("Alpha Vantage Test fehlgeschlagen. (Siehe Fehler oben)")
        
        
        