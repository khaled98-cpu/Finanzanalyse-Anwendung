import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_news_content(title, description, topic):
    """
    Analysiert Nachrichten auf Sentiment und Relevanz bezüglich eines Tickers/Themas.
    """
    prompt = f"""
    Du bist ein Experte in der Finanzanalyse. 
    Analysiere die folgende Nachricht im Kontext des Themas '{topic}':
    Titel: {title}
    Beschreibung: {description}

    Regeln für deine Antwort:
    1. Ist die Nachricht relevant für das Thema '{topic}'? Falls nein, antworte NUR: "nicht relevant".
    2. Falls relevant: Bewerte, wie positiv oder negativ die Nachricht für den Aktienkurs ist (Skala 1 bis 10).
    3. Gib NUR das Vorzeichen (+ für positiv, - für negativ) gefolgt von der Zahl aus.
    
    Beispiele:
    - Sehr positiv: +9
    - Leicht negativ: -2
    - Kein Bezug zum Thema: nicht relevant
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg:
                print(f"Quota überschritten, warte 10s... (Versuch {attempt+1}/3)")
                time.sleep(10)
                continue
            print(f"KI-Fehler bei Analyse: {err_msg}")
            return "Analyse fehlgeschlagen"
    
    return "Limit erreicht"

if __name__ == "__main__":
    print(analyze_news_content(
        "Autoindustrie: BMW kommt besser durch die Krise", 
        "BMW hat seinen Gewinn im dritten Quartal verdreifacht",
        "BMW"
    ))
    
    
    # print(analyze_news_content(
    #     "Autoindustrie: BMW kommt besser durch die Krise", 
    #     "BMW hat seinen Gewinn im dritten Quartal nur um 10% verbessert",
    #     "BMW"
    # ))
    
    # print(analyze_news_content(
    #     "Autoindustrie: BMW kommt schlechter durch die Krise", 
    #     "BMW hat seinen Gewinn im dritten Quartal -30% verloren",
    #     "BMW"
    # ))