from flask import Flask, render_template, render_template_string, jsonify, request
from pyModbusTCP.client import ModbusClient
import time
import json


app = Flask(__name__)

@app.route("/")
def start():
    print("Start")

    return render_template('home.html')

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