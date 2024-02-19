from influxdb_client import InfluxDBClient


token = "icZDRkYepFHRWLdP5HCzSPRC868TIfhQ4E8JguTQApWpKEpa6CBX1GXaIBKPNt44qQoHSRDJDvNeNMDtSpKq7Q=="
org = "my-org"
url = "http://192.168.0.230:8086"

client = InfluxDBClient(url=url, token=token, org=org)

query_api = client.query_api()

query = """from(bucket: "test")
  |> range(start: -1m)"""

tables = query_api.query(query, org="my-org")
for table in tables:
    for row in table.records:
        value = row.values["_value"]
        print(value)


