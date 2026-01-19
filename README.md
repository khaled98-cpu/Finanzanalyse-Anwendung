# Finanzanalyse-Anwendung

Dieses Repository enthält das Projekt Finanzanalyse-Anwendung, welches im Rahmen einer universitären Veranstaltung entwickelt wurde.
Ziel des Projekts ist die Erfassung, Speicherung, Analyse und Visualisierung von Daten über eine API-basierte Backend-Architektur mit angebundenem Frontend.

📌 Projektübersicht

Hauptbestandteile:

  Backend
    Python-basierte API (Flask)
    Datenverarbeitung & Analyse
    Persistente Speicherung in einer Datenbank
  
  Frontend:
    Einfache HTML-/CSS-basierte Benutzeroberfläche
    Darstellung von Analyseergebnissen
  Infrastruktur:
    Docker & Docker Compose für reproduzierbare Ausführung

⚙️ Technologien & Tools

    Programmiersprache: Python 3
    Web-Framework: Flask
    Datenbank: MongoDB (über Docker)
    Frontend: HTML, CSS 
    Containerisierung: Docker, Docker Compose

🚀 Installation & Ausführung
Voraussetzungen

Docker

Docker Compose

Projekt starten
docker-compose up --build
🔍 Backend-Funktionalitäten

Abruf externer Daten über APIs

Verarbeitung und Strukturierung der Rohdaten

Speicherung in der Datenbank

Analyse und Aufbereitung für das Frontend

Bereitstellung der Ergebnisse über REST-Endpunkte

📊 Frontend

Das Frontend dient zur:

Anzeige von Analyseergebnissen

Übersichtlichen Darstellung der verarbeiteten Daten

Demonstration der API-Funktionalität

🧪 Tests

Datenbanktests sind in backend/test_db.py enthalten

Weitere Tests können modular ergänzt werden
