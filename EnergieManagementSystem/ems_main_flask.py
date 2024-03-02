from flask import Flask, render_template, render_template_string, jsonify, request
from pyModbusTCP.client import ModbusClient
import time
import json
from influxdb_client import InfluxDBClient
import pytz
from datetime import datetime

token = "icZDRkYepFHRWLdP5HCzSPRC868TIfhQ4E8JguTQApWpKEpa6CBX1GXaIBKPNt44qQoHSRDJDvNeNMDtSpKq7Q=="
org = "my-org"
url = "http://192.168.0.230:8086"

client = InfluxDBClient(url=url, token=token, org=org)


app = Flask(__name__)

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

@app.route("/modus")
def modus():
    return render_template('modus.html')

# Diese Funktion schickt ein Befehl an Modbus
# Beschreibe Modbusregister
# Lademodus
@app.route('/writeModbus_laden', methods=['POST'])
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
    result = "Lademodus gestartet"
    return jsonify({"result": result})

# default Modus (Automatik Sungrow)
@app.route('/writeModbus_default', methods=['POST'])
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
    result = "Lademodus beendet"
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)