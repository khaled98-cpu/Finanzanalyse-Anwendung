import os
from mongoengine import connect, StringField, DateTimeField, DynamicDocument

mongo_host = os.environ.get('DB_HOST', 'localhost')
mongo_port = int(os.environ.get('DB_PORT', 27018))

print(f"Verbinde mit MongoDB unter: {mongo_host}:{mongo_port}")

connect(db='finanzanalyse', host=mongo_host, port=mongo_port)

class stockDaten(DynamicDocument):   # Yahoo finanz und Alpha Vantage
    date = DateTimeField(required=True)
    ticker = StringField(required=True)
    source = StringField(required=True)

class news_Daten(DynamicDocument):   # news API collection
    date = DateTimeField(required=True)
    title = StringField(required=True)
    source = StringField(required=True)
    query = StringField() 
    