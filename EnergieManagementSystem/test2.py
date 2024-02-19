import schedule
import time
import datetime
import sched

solarprognose = 1500
strompreise = 15
uhr1 = "22:00:00"

zeit = datetime.datetime.now()
print(zeit)

def start():
    print("Start")



if solarprognose < 10000:
    print("Solarertrag reicht niht aus, prüfe Ladung aus dem Netz")
    if strompreise < 20:
        print("Günstiges Preis endekt starte Ladevorgang aus dem Netz um " + uhr1)
    else:
        print("Strompreise sind über " + str(strompreise) + "€/kWh" + " ladevorgang ist nicht wirtschaftlich")
else:
    print("Solarertrag reicht aus um den Speicher zu laden")

if zeit == uhr1:
    print("Ladevorgang gestartet")




def anotherfunction():
    zeiten = strompreise()
    ladestart = zeiten[0]
    ladestop = zeiten[1]
    print("Ladestart" + ladestart, "Ladestop" +  ladestop)