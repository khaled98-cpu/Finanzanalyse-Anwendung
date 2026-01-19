import mongoengine
from mongoengine import connect, DynamicDocument, ValidationError

try:
    connect(db='finanzanalyse', host='localhost', port=27018)
    print("Verbindung zur MongoDB erfolgreich")
except mongoengine.connection.ConnectionFailure as e:
    print(f"Fehler: Verbindung zur MongoDB fehlgeschlagen. Läuft der MongoDB-Server?\n{e}")
    exit()

class Test(DynamicDocument):
    pass


if __name__ == "__main__":
    try:

        neues_dokument = Test(
            name="test 2 ",
            anzahl=25,
            bewertung=4.5,
            ist_aktiv=True,
            tags=['python', 'mongoengine', 'database'],
            zusaetzliche_info="Das ist ein dynamischer Wert."
        )

        print("Speichere Dokument...")
        neues_dokument.save()
        print("Dokument gespeichert.")


    except ValidationError as e:
        print(f" Validierungsfehler erfolgreich abgefangen, wie erwartet:")
        print(f"   Fehlermeldung: {e}")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
