from flask import Flask, render_template, jsonify, request
from pyModbusTCP.client import ModbusClient
import time
import json
from influxdb_client import InfluxDBClient
import pytz
from datetime import datetime
import requests
import pandas as pd
import schedule

# Verbindung zu InfluxDB
token = "icZDRkYepFHRWLdP5HCzSPRC868TIfhQ4E8JguTQApWpKEpa6CBX1GXaIBKPNt44qQoHSRDJDvNeNMDtSpKq7Q=="
org = "my-org"
url = "http://192.168.0.230:8086"

client = InfluxDBClient(url=url, token=token, org=org)


app = Flask(__name__)

# Homepage
@app.route("/")
def start():
    print("Start")

    return render_template('home.html')

@app.route("/data") #Chart
def data():
    query_pv = '''from(bucket: "test")
    |> range(start: -2h)
    |> filter(fn: (r) => r["_measurement"] == "pv.leistung")'''
    tables_pv = client.query_api().query(query=query_pv)

    query_bezug = '''from(bucket: "test")
    |> range(start: -2h)
    |> filter(fn: (r) => r["_measurement"] == "strom.bezug")'''
    tables_fromgrid = client.query_api().query(query=query_bezug)

    query_einspeisung = '''from(bucket: "test")
    |> range(start: -2h)
    |> filter(fn: (r) => r["_measurement"] == "strom.einspeisung")'''
    tables_togrid = client.query_api().query(query=query_einspeisung)

    # Daten für den Chart vorbereiten
    timestamps = []
    values_pv = []
    values_fromgrid = []
    values_togrid = []

    for table in tables_pv:
        for row in table.records:
            utc_timestamp = row.values["_time"]
            local_timezone = pytz.timezone('Europe/Berlin')
            # Umrechnung in lokale Zeit
            local_datetime = utc_timestamp.astimezone(local_timezone)
            # Entfernung UTC info
            local_datetime = local_datetime.replace(tzinfo=None)
            local_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
            # es darf nur ein Timestamp existieren, deswegen nur hier
            timestamps.append(local_time)
            values_pv.append(row.values["_value"])

    for table in tables_fromgrid:
        for row in table.records:
            utc_timestamp = row.values["_time"]
            local_timezone = pytz.timezone('Europe/Berlin')
            # Umrechnung in lokale Zeit
            local_datetime = utc_timestamp.astimezone(local_timezone)
            # Entfernung UTC info
            local_datetime = local_datetime.replace(tzinfo=None)
            local_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
            values_fromgrid.append(row.values["_value"])

    for table in tables_togrid:
        for row in table.records:
            utc_timestamp = row.values["_time"]
            local_timezone = pytz.timezone('Europe/Berlin')
            # Umrechnung in lokale Zeit
            local_datetime = utc_timestamp.astimezone(local_timezone)
            # Entfernung UTC info
            local_datetime = local_datetime.replace(tzinfo=None)
            local_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
            values_togrid.append(row.values["_value"])

    data = [timestamps, values_pv, values_fromgrid, values_togrid]
    # Daten an javascript html übergeben
    return jsonify(data)

#Update für Chart
@app.route('/update_chart', methods=['POST'])
def update_chart():
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    # String in ein datetime-Objekt konvertieren
    timestamp_start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
    timestamp_end = datetime.strptime(end_date, "%Y-%m-%dT%H:%M")

    # Parameter für query
    p = {"_start": timestamp_start,
         "_end": timestamp_end
         }

    # Daten aus der InfluxDB abrufen
    query_pv = '''from(bucket: "test")
    |> range(start: _start, stop: _end)
    |> filter(fn: (r) => r["_measurement"] == "pv.leistung")'''
    tables_pv = client.query_api().query(query=query_pv, params=p)

    query_bezug = '''from(bucket: "test")
    |> range(start: _start, stop: _end)
    |> filter(fn: (r) => r["_measurement"] == "strom.bezug")'''
    tables_fromgrid = client.query_api().query(query=query_bezug, params=p)

    query_einspeisung = '''from(bucket: "test")
    |> range(start: _start, stop: _end)
    |> filter(fn: (r) => r["_measurement"] == "strom.einspeisung")'''
    tables_togrid = client.query_api().query(query=query_einspeisung, params=p)

    # Daten für den Chart vorbereiten
    timestamps = []
    values_pv = []
    values_fromgrid = []
    values_togrid = []

    for table in tables_pv:
        for row in table.records:
            utc_timestamp = row.values["_time"]
            local_timezone = pytz.timezone('Europe/Berlin')
            # Umrechnung in lokale Zeit
            local_datetime = utc_timestamp.astimezone(local_timezone)
            # Entfernung UTC info
            local_datetime = local_datetime.replace(tzinfo=None)
            local_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
            # es darf nur ein Timestamp existieren, deswegen nur hier
            timestamps.append(local_time)
            values_pv.append(row.values["_value"])

    for table in tables_fromgrid:
        for row in table.records:
            utc_timestamp = row.values["_time"]
            local_timezone = pytz.timezone('Europe/Berlin')
            # Umrechnung in lokale Zeit
            local_datetime = utc_timestamp.astimezone(local_timezone)
            # Entfernung UTC info
            local_datetime = local_datetime.replace(tzinfo=None)
            local_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
            values_fromgrid.append(row.values["_value"])

    for table in tables_togrid:
        for row in table.records:
            utc_timestamp = row.values["_time"]
            local_timezone = pytz.timezone('Europe/Berlin')
            # Umrechnung in lokale Zeit
            local_datetime = utc_timestamp.astimezone(local_timezone)
            # Entfernung UTC info
            local_datetime = local_datetime.replace(tzinfo=None)
            local_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
            values_togrid.append(row.values["_value"])

    data = [timestamps, values_pv, values_fromgrid, values_togrid]
    return jsonify(data)

#Livedaten aus InfluxDB
@app.route("/pv-leistung")
def pvleistung():
    global value
    query = """from(bucket: "test")
      |> range(start: -1m)
      |> filter(fn: (r) => r["_measurement"] == "pv.leistung")"""

    tables = client.query_api().query(query, org="my-org")
    for table in tables:
        for row in table.records:
            value = row.values["_value"]

    return jsonify(value)

@app.route("/bezug")
def bezug():
    global value
    query = """from(bucket: "test")
      |> range(start: -1m)
      |> filter(fn: (r) => r["_measurement"] == "strom.bezug")"""

    tables = client.query_api().query(query, org="my-org")
    for table in tables:
        for row in table.records:
            value = row.values["_value"]

    return jsonify(value)

@app.route("/einspeisung")
def einspeisung():
    global value
    query = """from(bucket: "test")
      |> range(start: -1m)
      |> filter(fn: (r) => r["_measurement"] == "strom.einspeisung")"""

    tables = client.query_api().query(query, org="my-org")
    for table in tables:
        for row in table.records:
            value = row.values["_value"]

    return jsonify(value)


@app.route("/verbrauch")
def verbrauch():
    pass


#Config Seite
@app.route("/config", methods=['POST', 'GET'])
def config():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        winkel = request.form['winkel']
        kwp = request.form['kwp']
        azimuth = request.form['azimuth']
        modbus_host = request.form['modbus_host']
        modbus_port = int(request.form['modbus_port'])

        data = {}
        data["latitude"] = latitude
        data["longitude"] = longitude
        data["winkel"] = winkel
        data["kwp"] = kwp
        data["azimuth"] = azimuth
        data["Modbus_host"] = modbus_host
        data["Modbus_port"] = modbus_port

        with open("config.json", "w") as write_file:
            json.dump(data, write_file)

    return render_template('config.html')

#Modus Seite
@app.route("/modus")
def modus():
    return render_template('modus.html')


#Mainfunction automatische Abfrage von Einstrahlungsprognose, Strompreise und Entscheidung
# PV-Ertragsprognose
def prognose():
    # Angeaben zur PV Anlage
    # allgemeine Angaben

    with open("config.json", "r") as read_file:
        config_data = json.load(read_file)

    lat = config_data["latitude"]
    lon = config_data["longitude"]
    winkel = config_data["winkel"]
    kwp = config_data["kwp"]
    url = "https://api.forecast.solar/estimate/watthours/day/"
    # Himmelsrichtung
    az1 = config_data["azimuth"]
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
        start_zeit = datetime.fromtimestamp(start_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        end_timestamp = datensatz['end_timestamp'] / 1000
        end_zeit = datetime.fromtimestamp(end_timestamp).strftime('%Y-%m-%d %H:%M:%S')
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


# Diese Funktion schickt ein Befehl an Modbus
# Beschreibe Modbusregister
# Lademodus
@app.route('/writeModbus_laden', methods=['POST'])
def writeModbus_laden():
    # Erstelle einen Modbus TCP-Client
    with open("config.json", "r") as read_file:
        config_data = json.load(read_file)

    host = config_data["Modbus_host"]  # Variable für WR-Ip
    port = config_data["Modbus_port"]  # Variable für port
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
    result = "Lademodus gestartet"
    return jsonify({"result": result})

# default Modus (Automatik Sungrow)
@app.route('/writeModbus_default', methods=['POST'])
def writeModbus_default():
    # Erstelle einen Modbus TCP-Client
    with open("config.json", "r") as read_file:
        config_data = json.load(read_file)

    host = config_data["Modbus_host"]  # Variable für WR-Ip
    port = config_data["Modbus_port"]  # Variable für port
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
    result = "Lademodus beendet"
    return jsonify({"result": result})

def main_function():
    prognose()
    ertrag = prognose()
    if ertrag < 150000:
        print("PV-Ertrag reicht nicht aus um den Speicher zu laden. Prüfe Ladung aus dem Netz")
        netzdaten = strompreise()
        strompreis = float(netzdaten[0])
        ladestart_str = netzdaten[1]
        ladestop_str = netzdaten[2]
        ladestart_date = datetime.strptime(ladestart_str, '%Y-%m-%d %H:%M:%S')
        ladestop_date = datetime.strptime(ladestop_str, '%Y-%m-%d %H:%M:%S')
        ladestart = datetime.strftime(ladestart_date, '%H:%M:%S')
        ladestop = datetime.strftime(ladestop_date, '%H:%M:%S')
        if strompreis < 70.5:
            print("Günstiges Preis zum Laden entdekt " + str(strompreis) + " am " + str(ladestart_str))
            print("Starte Ladevorgang am " + str(ladestart_str))

            def task_startladen():
                writeModbus_laden()
                print("Ladevorgang gestartet am " + str(ladestart_str) + "um ", datetime.now())
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
    app.run(debug=True)