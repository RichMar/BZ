import csv
import requests
import time
import math
import os
from cryptography.fernet import Fernet
import sys
from gpx_converter import Converter
import gpxpy.gpx
from datetime import date
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from math import radians, cos, sin, asin, sqrt
import shutil
from datetime import datetime

print("START:", datetime.utcnow())

def get_distance(lat_1, lng_1, lat_2, lng_2):  # vypocet vzdalenosti bodu
    lng_1, lat_1, lng_2, lat_2 = map(radians, [lng_1, lat_1, lng_2, lat_2])  # prevede uhly na radiany
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1

    a = sin(d_lat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(d_lng / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

def encrypt_file(ofile, klic):
    fernet = Fernet(klic)
    with open(ofile, 'rb') as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open('enc-' + ofile, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)
    os.remove(ofile)
    return

def decrypt_file(efile, klic):
    fernet = Fernet(klic)
    with open(efile, 'rb') as enc_file:
        encrypted = enc_file.read()
    decrypted = fernet.decrypt(encrypted)
    with open(efile[4:], 'wb') as dec_file:
        dec_file.write(decrypted)
    return

def gpxtrcktoway(efile):
    dgpx_file = open(efile, 'r')
    dgpx = gpxpy.parse(dgpx_file)
    dgpxnew = gpxpy.gpx.GPX()
    for track in dgpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                dgpxnew.waypoints.append(point)
    dfp = open(efile, 'w')
    dfp.write(dgpxnew.to_xml())
    dfp.close()
    return

# --- Klíč pro šifrování ---
key = ''
try:
    key = os.environ['REPO_SECRET']
except:
    print("Pristup k REPO_SECRET zamitnut")
finally:
    print('jedu dál')

try:
    with open('filekey.key', 'rb') as f:
        key = f.read()
except FileNotFoundError:
    print("Nemohu nacist filekey.key.")

if key == '':
    print('Hodnota KEY není nastavena! Končíme.')
    sys.exit()

pocetboducelkem = 0
body_les_seznam = []
body_overpass_seznam = []
body_les_seznam_bezref = []
vymazatz_body_overpass_seznam = []
chybejicibody_noref = []

import removedbz

if os.path.exists('enc-OSMchybejicibody.csv'):
    vstup = 'enc-OSMchybejicibody.csv'
    oddelovac = ','
    decrypt_file(vstup, key)
    vstup = 'OSMchybejicibody.csv'
    zapis = 'a'
elif os.path.exists('enc-Lesy_CR_komplet.csv'):
    vstup = 'enc-Lesy_CR_komplet.csv'
    oddelovac = ';'
    decrypt_file(vstup, key)
    vstup = 'Lesy_CR_komplet.csv'
    zapis = 'w'
else:
    vstup = 'Lesy_CR_komplet.csv'
    oddelovac = ';'
    zapis = 'w'

print('Vstupni soubor: ' + vstup)

# 1. Načtení vstupních bodů z lokálního CSV souboru
with open(vstup, encoding='cp852') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=oddelovac)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')
            line_count += 1
        else:
            row[0] = ''.join([i for i in row[0]]).replace(",", ".")
            row[1] = ''.join([i for i in row[1]]).replace(",", ".")
            row[2] = row[2].replace("\t", "").replace(" ", "")
            
            bod_les = [row[0], row[1], row[2]]
            body_les_seznam.append(bod_les)
            line_count += 1

print("Načteno {len(body_les_seznam)} bodů ze vstupního souboru.")

# 2. Stažení všech bodů z Overpass API najednou (pro celé Česko)
# Seznam ověřených Overpass endpointů (zrcadel)
overpass_urls = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.openstreetmap.fr/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

overpass_query = """
[out:csv(::lat, ::lon, "ref", name)][timeout:90];
area[name="Česko"]->.searchArea;
(
  node(area.searchArea)["highway"="emergency_access_point"];
  node(area.searchArea)["emergency"="access_point"];
);
out body;
"""

headers = {
    'User-Agent': 'RichMar-BZ-Bot/1.0 (gis-script@github-action)'
}

print("Stahuji všechny body z Overpass API pro celé Česko...")
response = None
uspech = False

# Procházíme jednotlivá zrcadla v seznamu
for overpass_url in overpass_urls:
    print(f"Zkouším server: {overpass_url}")
    for pokus in range(3): # 3 pokusy na jedno zrcadlo
        try:
            response = requests.post(
                overpass_url,
                data={'data': overpass_query},
                headers=headers,
                timeout=120
            )
            if response.status_code == 200:
                print(f"Úspěšně staženo z {overpass_url}")
                uspech = True
                break
            else:
                print(f"  Server vrátil status {response.status_code}, opakuji...")
                time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"  Chyba spojení ({e}), opakuji...")
            time.sleep(10)
    
    if uspech:
        break
    else:
        print(f"Server {overpass_url} selhal, zkouším další zrcadlo...")

# Pokud selhaly všechny servery, skript ukončíme
if not uspech:
    print("Nepodařilo se získat data z žádného Overpass API serveru.")
    sys.exit(1)

response.encoding = 'windows-1250'
data = [row.split('\t') for row in response.text.split('\n')]
print(f"Staženo řádků z Overpass: {len(data)}")

# Zpracování stažených dat z Overpass
for x in data:
    if len(x) >= 3 and x[0] != '@lat' and x[0].strip() != '':
        lat = x[0].replace(",", ".")
        lon = x[1].replace(",", ".")
        ref = x[2].strip() if len(x) > 2 else ""
        name = x[3].strip() if len(x) > 3 else ""
        
        bod_overpass = [lat, lon, ref]
        if ref != "":
            body_overpass_seznam.append(bod_overpass)
        else:
            body_les_seznam_bezref.append(bod_overpass)
        pocetboducelkem += 1

print(f"Pocet nalezenych bodu v OSM: {pocetboducelkem}")

# 3. Lokální porovnání dat
dist = open('dist.txt', 'a')
dist.write("Vzdalenost bodu nize je vetsi nez 100m:\n")
chybejicibody = body_les_seznam.copy()

for y in body_overpass_seznam:
    ref = y[2].replace(" ", "")
    index_les = [(i, element.index(ref)) for i, element in enumerate(body_les_seznam) if ref in element]
    
    if index_les:
        index_chybejici = [(i, element.index(ref)) for i, element in enumerate(chybejicibody) if ref in element]
        if index_chybejici:
            del chybejicibody[index_chybejici[0][0]]
            
        vzdalenost = get_distance(
            float(body_les_seznam[index_les[0][0]][0]),
            float(body_les_seznam[index_les[0][0]][1]),
            float(y[0]), float(y[1])
        ) * 1000  # převod na metry
        
        # Pokud je bod v OSM dál než 100m od bodu v LČR, má pravděpodobně špatnou pozici nebo ref
        if vzdalenost > 100:
            dist.write(ref + " " + str(vzdalenost) + '|LCR:' + str(body_les_seznam[index_les[0][0]][0]) + ','
                        + str(body_les_seznam[index_les[0][0]][1]) + '|OSM:' + str(y[0]) + ',' + str(y[1]) + "\n")
            print('Vzdálenost bodů: ' + str(vzdalenost), " ", y[2])
            # Tady patří body, které se liší pozicí/nesedí
            body_les_seznam_bezref.append(y)
            if vstup == 'OSMchybejicibody.csv':
                vymazatz_body_overpass_seznam.append(y)
    else:
        # Pokud ref z OSM vůbec není v LČR seznamu (nebo má chybějící ref)
        body_les_seznam_bezref.append(y)
        vymazatz_body_overpass_seznam.append(y)

# Přidáme sem i ty body z Overpassu, které už v surovém stahování neměly vyplněný ref
for y_noref in body_overpass_seznam_bezref if 'body_overpass_seznam_bezref' in locals() else []:
    if y_noref not in body_les_seznam_bezref:
        body_les_seznam_bezref.append(y_noref)

for s in vymazatz_body_overpass_seznam:
    ref = s[2]
    index_body_overpass_seznam = [(i, element.index(ref)) for i, element in enumerate(body_overpass_seznam) if ref in element]
    if index_body_overpass_seznam:
        del body_overpass_seznam[index_body_overpass_seznam[0][0]]

novyseznambodu = len(body_overpass_seznam)

if os.path.exists('OSMBZ.csv'):
    with open('OSMBZ.csv', newline='') as csvfileOSM:
        fileObject = csv.reader(csvfileOSM)
        puvodniseznambodu = sum(1 for row in fileObject)
else:
    puvodniseznambodu = 1

if not os.path.exists('statistika.csv'):
    with open('statistika.csv', 'w', newline='') as stat:
        wr = csv.writer(stat, delimiter=',')
        wr.writerow(['datum', 'narust', 'celkem'])

print('Původní počet bodů:' + str(puvodniseznambodu - 1) + "\n" + "Nový počet bodů: " + str(novyseznambodu))

# vymaze bod ktery je v BZneni.csv z Chybejicbody (OSMchybejicibody.csv)
if os.path.exists("BZneni.csv"):
    with open("BZneni.csv", "r", encoding="utf-8") as neni_file:
        csv_reader_neni = csv.reader(neni_file, delimiter=",")
        header_skipped = False
        for row_neni in csv_reader_neni:
            if not header_skipped:
                header_skipped = True
                continue
            if len(row_neni) >= 2 and row_neni[0].strip():
                try:
                    r_lat = float(row_neni[0].replace(",", "."))
                    r_lon = float(row_neni[1].replace(",", "."))
                    for rr in list(chybejicibody):
                        vzd = get_distance(float(rr[0]), float(rr[1]), r_lat, r_lon) * 1000
                        if vzd < 100:
                            if rr in chybejicibody:
                                chybejicibody.remove(rr)
                                print(f"Bod {rr} byl vymazan z chybejicibody.")
                except ValueError:
                    continue # Kdyby řádek nebyl číslo, bezpečně ho přeskočíme

today = date.today()
d1 = today.strftime("%d/%m/%Y")

if ((puvodniseznambodu - 1) < novyseznambodu and vstup == 'Lesy_CR_komplet.csv') or (novyseznambodu > 0 and vstup == 'OSMchybejicibody.csv'):
    if vstup == 'Lesy_CR_komplet.csv':
        nar = novyseznambodu - (puvodniseznambodu - 1)
        celk = novyseznambodu
    else:
        nar = novyseznambodu
        celk = puvodniseznambodu + nar

    with open('statistika.csv', 'a', newline='') as sta:
        wri = csv.writer(sta, delimiter=',')
        wri.writerow([d1, str(nar), celk])

    with open('OSMbodybezref.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['lat', 'lon'])
        chybejicibody_noref = [x[0:2] for x in chybejicibody]
        writer.writerows(chybejicibody_noref)

    Converter(input_file='OSMbodybezref.csv').csv_to_gpx(lats_colname='lat', longs_colname='lon', output_file='OSMbodybezref.gpx')

    gpx_file = open('OSMbodybezref.gpx', 'r')
    gpx = gpxpy.parse(gpx_file)
    gpxnew = gpxpy.gpx.GPX()

    data_csv = pd.read_csv('OSMbodybezref.csv')
    df = data_csv
    df['geometry'] = df.apply(lambda row: Point(float(row['lon']), float(row['lat'])), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.to_file('OSMbodybezref.geojson', driver='GeoJSON')

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                gpxnew.waypoints.append(point)

    fp = open('OSMbodybezref.gpx', 'w')
    fp.write(gpxnew.to_xml())
    fp.close()

    if os.path.exists('OSMBZ.csv'):
        src = 'OSMBZ.csv'
        dst = './archiv/OSMBZ' + str(today) + '.csv'
        os.makedirs('./archiv', exist_ok=True)
        shutil.copy(src, dst)

    with open('OSMBZ.csv', zapis, newline='') as f:
        writer = csv.writer(f, delimiter=',')
        if zapis == 'w':
            writer.writerow(['lat', 'lon', 'ref'])
        writer.writerows(body_overpass_seznam)

    with open('OSMchybejicibody.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon', 'ref'])
        writer.writerows(chybejicibody)
    encrypt_file('OSMchybejicibody.csv', key)

    with open('OSMbodychybejiciref.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon', 'ref'])
        writer.writerows(body_les_seznam_bezref)

    Converter(input_file='OSMbodychybejiciref.csv').csv_to_gpx(lats_colname='lat', longs_colname='lon', output_file='OSMbodychybejiciref.gpx')
    gpxtrcktoway('OSMbodychybejiciref.gpx')

    import wikipg

if os.path.exists('OSMchybejicibody.csv'):
    os.remove('OSMchybejicibody.csv')
    print("..........................")

if os.path.exists('Lesy_CR_komplet.csv'):
    encrypt_file('Lesy_CR_komplet.csv', key)
if os.path.exists('Lesy_CR_komplet.csv'):
    os.remove('Lesy_CR_komplet.csv')
