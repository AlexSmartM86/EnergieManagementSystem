from datetime import datetime
from dateutil import parser

timestamp_str = '2024-02-11 13:40:12.190000+00:00'
timestamp = parser.isoparse(timestamp_str)

# Zeitzone ändern
local_timestamp = timestamp.astimezone()
print(local_timestamp)
# In das gewünschte Format konvertieren
local_timestamp_str = local_timestamp.strftime('%Y-%m-%d %H:%M:%S')

print(local_timestamp_str)