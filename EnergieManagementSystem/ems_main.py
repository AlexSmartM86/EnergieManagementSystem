# Dieses Projekt soll automatisiert eine Datenabfrage bei forecastsolar und bei awattar machen und anhand der Daten
# entscheiden ob der Speicher geladen wird
import requests
import json
from datetime import datetime
import pandas as pd
import time
from pyModbusTCP.client import ModbusClient


# PV-Ertragsprognose
def pv_prognose():
    # Angeaben zur PV Anlage
    # allgemeine Angaben
    lat = "52.4233"
    lon = "7.0991"
    winkel = "15"
    kwp = "30"
    url = "https://api.forecast.solar/estimate/watthours/day/"
    # Himmelsrichtung
    az1 = "0"  # süden
    urldaten1 = url + lat + "/" + lon + "/" + winkel + "/" + az1 + "/" + kwp + "?time=utc"
    # Verarbeitung der Daten
    anfrage1 = requests.get(urldaten1).text
    parser1 = json.loads(anfrage1)
    result1 = parser1["result"]
    werte = []
    werte.append(result1)
    df = pd.DataFrame(werte)

    ertrag_heute = df.iloc[0:3, 0].sum()
    ertrag_morgen = df.iloc[0:3, 1].sum()

    print("Erwarteter Ertrag heute: ", ertrag_heute, "kWh" "\n" "Erwarteter Ertrag morgen: ", ertrag_morgen, "kWh")


# Strompreise von awattar über api
def strompreise():
    url = "https://api.awattar.de/v1/marketdata"
    anfrage = requests.get(url).text

    parser = json.loads(anfrage)
    daten = (parser["data"])

    liste = []

    for datensatz in daten:
        start_timestamp = datensatz['start_timestamp'] / 1000
        start_zeit = datetime.datetime.fromtimestamp(start_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        end_timestamp = datensatz['end_timestamp'] / 1000
        end_zeit = datetime.datetime.fromtimestamp(end_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        marketprice = datensatz['marketprice']
        unit = datensatz['unit']
        liste.append([start_zeit, end_zeit, marketprice, unit])

    df = pd.DataFrame(liste, columns=["Startzeit", "Endzeit", "Preis", "Währung"])

    bewertung = []
    for i in df["Preis"]:
        if i <= 0:
            bewertung.append("gut")
        else:
            bewertung.append("schlecht")

    df['Bewertung'] = bewertung

    print(df)

    # Umrechnung von float64 in int
    df["Preis"] = df["Preis"]
    minimum = df["Preis"].min()
    print("Der günstigster Preis beträgt ", minimum, "Eur/Mwh")

    # Sortierung erst nach Preis
    sort = df.sort_values(by=['Preis'])
    # wie viele Stunden sollen berücksichtigt werden (diese Variable soll über Dashboard eingegeben werden)
    ladedauer = 2
    sort_min_preis = sort.head(ladedauer)
    # Sortierung nach Zeit
    sort_zeit = sort_min_preis.sort_values(by=['Startzeit'])
    print(sort_zeit)

    uhr1 = sort_zeit["Startzeit"].iloc[0]  # Startzeit zum laden (erste Zeile in der Tabelle)
    uhr2 = sort_zeit["Endzeit"].iloc[-1]  # Endzeit zum laden (letzte Zeile in der Tabelle)

    print("Die günstigste Zeit zum Laden ist von ", uhr1, "bis ", uhr2)
    print("Soll der speicher von ", uhr1, "bis ", uhr2, "geladen werden?")


# Beschreibe Modbusregister
# Lademodus
def writeModbus_laden():
    # Erstelle einen Modbus TCP-Client
    host = "192.168.0.107"  # Variable für WR-Ip
    port = "10502"  # Variable für port
    client = ModbusClient(host=host, port=port)

    # Stelle eine Verbindung zum Server her
    if client.open():
        # schreibe Wert auf Modbus Register (13049 (default 0, 2=HandMode), 13050 (default 204, 170 Lademodus),
        # 13051 (default 0-5000, Ladeleistung in W))
        write_rh_13049 = client.write_single_register(13049, 2)
        time.sleep(1)
        write_rh_13050 = client.write_single_register(13050, 170)
        time.sleep(1)
        write_rh_13051 = client.write_single_register(13051, 5000)  # Ladeleistung vorgeben aus Dashboard?

        # Überprüfe, ob die Beschreibung erfolgreich war
        if write_rh_13049 and write_rh_13050 and write_rh_13051:
            # Zeige die geschriebenen Registerwerte an
            print("Register Beschrieben:")
            print(write_rh_13049, write_rh_13050, write_rh_13051)
        else:
            # Die Anfrage war nicht erfolgreich
            print("Fehler beim Beschreiben")
    else:
        # Verbindung zum Server fehlgeschlagen
        print("Fehler beim Verbinden zum Server")

    # Schließe die Verbindung zum Server
    client.close()


# default Modus (Automatik Sungrow)
def writeModbus_default():
    # Erstelle einen Modbus TCP-Client
    host = "192.168.0.107"  # Variable für WR-Ip
    port = "10502"  # Variable für port
    client = ModbusClient(host=host, port=port)

    # Stelle eine Verbindung zum Server her
    if client.open():
        # schreibe Wert auf Modbus Register (13049 (default 0, 2=HandMode), 13050 (default 204, 170 Lademodus),
        # 13051 (default 0-5000, Ladeleistung in W))
        write_rh_13049 = client.write_single_register(13049, 0)
        time.sleep(1)
        write_rh_13050 = client.write_single_register(13050, 204)

        # Überprüfe, ob die Beschreibung erfolgreich war
        if write_rh_13049 and write_rh_13050:
            # Zeige die geschriebenen Registerwerte an
            print("Register Beschrieben:")
            print(write_rh_13049, write_rh_13050)
        else:
            # Die Anfrage war nicht erfolgreich
            print("Fehler beim Beschreiben")
    else:
        # Verbindung zum Server fehlgeschlagen
        print("Fehler beim Verbinden zum Server")

    # Schließe die Verbindung zum Server
    client.close()


print("Wilkommen im Programm!")
print("Was möchtest du tun?")
print("folgende Möglichkeiten hast du: PV Prognose, Börsenpreise")
print("Eingabe: ")
eingabe = input()

if eingabe == "PV Prognose":
    pv_prognose()
if eingabe == "Börsenpreise":
    strompreise()
