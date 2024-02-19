import pytz
from influxdb_client import InfluxDBClient
from datetime import datetime, timezone
from dateutil import parser
import pytz
#apitoken = icZDRkYepFHRWLdP5HCzSPRC868TIfhQ4E8JguTQApWpKEpa6CBX1GXaIBKPNt44qQoHSRDJDvNeNMDtSpKq7Q==


token = "icZDRkYepFHRWLdP5HCzSPRC868TIfhQ4E8JguTQApWpKEpa6CBX1GXaIBKPNt44qQoHSRDJDvNeNMDtSpKq7Q=="
org = "my-org"
url = "http://192.168.0.230:8086"

client = InfluxDBClient(url=url, token=token, org=org)

query_api = client.query_api()

query = """from(bucket: "test")
 |> range(start: -10m)"""
tables = query_api.query(query, org="my-org")


for table in tables:
    print(table)
    for row in table.records:
        utc_timestamp = row.values["_time"]
        local_timezone = pytz.timezone('Europe/Berlin')
        # Umrechnung in lokale Zeit
        local_datetime = utc_timestamp.astimezone(local_timezone)
        #Entfernung UTC info
        local_datetime = local_datetime.replace(tzinfo=None)
        local_time = local_datetime.strftime('%Y-%m-%d %H:%M:%S')
        print(local_time, row.values["_value"])
