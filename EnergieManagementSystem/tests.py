# Dieses Projekt soll automatisiert eine Datenabfrage bei forecastsolar und bei awattar machen und anhand der Daten
# entscheiden ob der Speicher geladen wird
import requests
import json
import datetime
import pandas as pd
import time
from pyModbusTCP.client import ModbusClient
import schedule

# PV-Ertragsprognose
def prognose():
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

    print("Erwarteter Ertrag heute: ", ertrag_heute/1000, "kWh" "\n" "Erwarteter Ertrag morgen: ", ertrag_morgen/1000, "kWh")

    return ertrag_morgen



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


    # Sortierung erst nach Preis
    sort = df.sort_values(by=['Preis'])
    # wie viele Stunden sollen berücksichtigt werden (diese Variable soll über Dashboard eingegeben werden)
    ladedauer = 1
    sort_min_preis = sort.head(ladedauer)
    # Sortierung nach Zeit
    sort_zeit = sort_min_preis.sort_values(by=['Startzeit'])


    uhr1 = sort_zeit["Startzeit"].iloc[0]  # Startzeit zum laden (erste Zeile in der Tabelle)
    uhr2 = sort_zeit["Endzeit"].iloc[-1]  # Endzeit zum laden (letzte Zeile in der Tabelle)


    return minimum, uhr1, uhr2

# Beschreibe Modbusregister
# Lademodus
def writeModbus_laden():
    # Erstelle einen Modbus TCP-Client
    host = "192.168.0.105"  # Variable für WR-Ip
    port = 10502  # Variable für port
    client = ModbusClient(host=host, port=port)

    # Stelle eine Verbindung zum Server her
    if client.open():
        # schreibe Wert auf Modbus Register (13049 (default 0, 2=HandMode), 13050 (default 204, 170 Lademodus),
        # 13051 (default 0-5000, Ladeleistung in W))
        write_rh_13049 = client.write_single_register(0, 2)
        time.sleep(1)
        write_rh_13050 = client.write_single_register(1, 170)
        time.sleep(1)
        write_rh_13051 = client.write_single_register(2, 5000)  # Ladeleistung vorgeben aus Dashboard?

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
    host = "192.168.0.105"  # Variable für WR-Ip
    port = 10502  # Variable für port
    client = ModbusClient(host=host, port=port)

    # Stelle eine Verbindung zum Server her
    if client.open():
        # schreibe Wert auf Modbus Register (13049 (default 0, 2=HandMode), 13050 (default 204, 170 Lademodus),
        # 13051 (default 0-5000, Ladeleistung in W))
        write_rh_13049 = client.write_single_register(0, 0)
        time.sleep(1)
        write_rh_13050 = client.write_single_register(1, 204)

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


def main_function():
    prognose()
    ertrag = prognose()
    if ertrag < 150000:
        print("PV-Ertrag reicht nicht aus um den Speicher zu laden. Prüfe Ladung aus dem Netz")
        netzdaten = strompreise()
        strompreis = float(netzdaten[0])
        ladestart_str = netzdaten[1]
        ladestop_str = netzdaten[2]
        ladestart_date = datetime.datetime.strptime(ladestart_str, '%Y-%m-%d %H:%M:%S')
        ladestop_date = datetime.datetime.strptime(ladestop_str, '%Y-%m-%d %H:%M:%S')
        ladestart = datetime.datetime.strftime(ladestart_date, '%H:%M:%S')
        ladestop = datetime.datetime.strftime(ladestop_date, '%H:%M:%S')
        if strompreis < 70.5:
            print("Günstiges Preis zum Laden entdekt " + str(strompreis) + " am " + str(ladestart_str))
            print("Starte Ladevorgang am " + str(ladestart_str))

            def task_startladen():
                writeModbus_laden()
                print("Ladevorgang gestartet am " + str(ladestart_str) + "um ", datetime.datetime.now())
                return schedule.CancelJob

            schedule.every().day.at(ladestart).do(task_startladen)

            while True:
                schedule.run_pending()
                if not schedule.jobs:
                    break
                time.sleep(1)

            def task_stopladen():
                writeModbus_default()
                print("Ladevorgang beendet am " + str(ladestop_str) + "um " + ladestop)
                return schedule.CancelJob

            schedule.every().day.at(ladestop).do(task_stopladen) # das könnte man abhängig von SOC Battery beenden

            while True:
                schedule.run_pending()
                if not schedule.jobs:
                    break
                time.sleep(1)
        else:
            print("Strom aus dem Netz ist zu teuer " + str(strompreis))
    else:
        print("PV-Ertrag reicht aus um den Speicher zu laden " + str(ertrag))



if __name__ == "__main__":
    main_function()
