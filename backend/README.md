# Backend

Dieses Verzeichnis enthält den gesamten Backend-Code für die Finanzanalyse-Anwendung. Das Backend ist eine Flask-Anwendung, die Daten von verschiedenen APIs abruft, verarbeitet und über eine API bereitstellt.

## Dateien

- **`app.py`**: Die Haupt-Flask-Anwendung. Sie definiert die API-Endpunkte zum Abrufen von Nachrichten- und Aktiendaten und rendert das Frontend-Dashboard.
- **`api_calls.py`**: Enthält Funktionen zum Abrufen von Daten von externen APIs:
    - NewsAPI (für Nachrichten)
    - Yahoo Finance (für Aktiendaten)
    - Alpha Vantage (für Aktiendaten)
- **`database.py`**: Definiert die MongoDB-Datenbankmodelle mit `mongoengine`. Es gibt zwei Hauptmodelle: `stockDaten` für Aktiendaten und `news_Daten` für Nachrichten.
- **`DatenBearbeiten.py`**: Enthält Funktionen zur Aufbereitung und Bereinigung der von den APIs abgerufenen Rohdaten, bevor sie in der Datenbank gespeichert werden.
- **`save_data.py`**: Implementiert die Datenverarbeitungspipelines. Diese Skripte rufen Daten über `api_calls.py` ab, verarbeiten sie mit `DatenBearbeiten.py` und speichern sie in der MongoDB-Datenbank.
- **`test_db.py`**: Ein einfaches Skript zum Testen der Verbindung zur MongoDB-Datenbank.
- **`requirements.txt`**: Listet alle Python-Abhängigkeiten auf, die für das Backend erforderlich sind.
- **`Dockerfile`**: Konfiguriert den Docker-Container für das Backend.

## Endpunkte

- `GET /`: Zeigt das Dashboard an
- `GET /api/news`: Holt Nachrichten zu einem Suchbegriff.
- `GET /api/stocks/yf`: Holt Aktienkurse von Yahoo Finance.
- `GET /api/stocks/av`: Holt Aktienkurse von Alpha Vantage.

