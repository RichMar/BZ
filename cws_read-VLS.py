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
# import pandas_geojson as pdg
# Original
# from pandas_geojson import to_geojson
# from pandas_geojson import write_geojson
from math import radians, cos, sin, asin, sqrt
import shutil


def get_distance(lat_1, lng_1, lat_2, lng_2):  # vypocet vzdalenosti bodu
    lng_1, lat_1, lng_2, lat_2 = map(radians, [lng_1, lat_1, lng_2, lat_2])  # prevede uhly na radiany
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1

    # temp = (
    #         math.sin(d_lat / 2) ** 2
    #         + math.cos(lat_1)
    #         * math.cos(lat_2)
    #         * math.sin(d_lng / 2) ** 2
    # )
    a = sin(d_lat / 2) ** 2 + cos(lat_1) * cos(lat_2) * sin(d_lng / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    # return 6371.0 * (2 * math.atan2(math.sqrt(temp), math.sqrt(1 - temp)))
    return c * r


def encrypt_file(ofile, klic):
    # using the generated key
    fernet = Fernet(klic)

    # opening the original file to encrypt
    with open(ofile, 'rb') as file:
        original = file.read()

    # encrypting the file
    encrypted = fernet.encrypt(original)

    # opening the file in write mode and
    # writing the encrypted data
    with open('enc-' + ofile, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

    os.remove(ofile)
    return


def decrypt_file(efile, klic):
    # using the generated key
    fernet = Fernet(klic)
    # opening the encrypted file
    with open(efile, 'rb') as enc_file:
        encrypted = enc_file.read()
    # decrypting the file
    decrypted = fernet.decrypt(encrypted)

    # using the key
    fernet = Fernet(key)

    # opening the encrypted file
    with open(efile, 'rb') as enc_file:
        encrypted = enc_file.read()

    # decrypting the file
    decrypted = fernet.decrypt(encrypted)

    # opening the file in write mode and
    # writing the decrypted data
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

   # print('Created GPX:', gpxnew.to_xml())
    dfp = open(efile, 'w')
    dfp.write(dgpxnew.to_xml())
    dfp.close()
    return
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# NEMAZAT!!!
# key generation
# key = Fernet.generate_key()



key = ''
# prevezme klic z Gitu
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

# key = ''
if key == '':
    print('Hodnota KEY není nastavena! Končíme.')
    sys.exit()
# key = ""
# string the key in a file
# with open('filekey.key', 'wb') as filekey:
#        filekey.write(key)

# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# json.loads("")
# encrypt_file("Lesy_CR_komplet_.csv", key )
pocetboducelkem = 0
body_les_seznam = []
body_overpass_seznam = []
body_les_seznam_bezref = []
vymazatz_body_overpass_seznam = []
chybejicibody_noref = []

import removedbz
if os.path.exists('enc-OSMchybejicibody-VLS.csv'):
    vstup = 'enc-OSMchybejicibody-VLS.csv'
    oddelovac = ','
    decrypt_file(vstup, key)
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # encrypt_file('OSMchybejicibody.csv', key)
    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    vstup = 'OSMchybejicibody-VLS.csv'
    zapis = 'a'

elif os.path.exists('enc-VLS-komplet.csv'):
    vstup = 'enc-VLS-komplet.csv'
    oddelovac = ';'
    decrypt_file(vstup, key)
    vstup = 'VLS-komplet.csv'
    zapis = 'w'
else:
    vstup = 'VLS-komplet.csv'
    oddelovac = ';'
    zapis = 'w'

# with open(vstup, encoding='cp852') as csv_file:
# with open(vstup[4:], encoding='cp852') as csv_file:
print('Vstupni soubor: ' + vstup)
f = open("comm_wr-VLS.txt", "w")
with open(vstup, encoding='cp852') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=oddelovac)
    line_count = 0
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """[out:csv(::lat, ::lon, "ref", name, ::count)]; \n ( \n"""
    overpass_end = "\n ); \n out; \n out count; \n"
   # f = open("comm_wr.txt", "w")
    c = 1
    prvni = 0
    rad = 1
    timestr = time.strftime("%Y%m%d-%H%M%S")

    for row in csv_reader:

        # print("111" + row)
        if line_count == 0:
            print(f'Column names are {", ".join(row)}')  # nazvy sloupcu csv
            line_count += 1
        else:
            # nahradi carku teckou v souradnicich
            row[0] = ''.join([i for i in row[0]]).replace(",", ".")
            row[1] = ''.join([i for i in row[1]]).replace(",", ".")
            # odstrani tab mezeru pred nazvem bodu
            row[2] = row[2].replace("\t", "")
            row[2] = row[2].replace(" ", "")
            # dotaz_body = """node[highway=emergency_access_point](around:100,""" + row[0] + """, """ + row[1] + """);"""
            dotaz_body = """node[highway=emergency_access_point](around:100,""" + row[0] + """, """ + row[1] + """);
                            node[emergency=access_point](around:100,""" + row[0] + """, """ + row[1] + """);"""
            overpass_query = overpass_query + dotaz_body
            # overpass_query = overpass_query + overpass_end
            print(f'x={row[0]}; y= {row[1]}; {row[2]}.')
            bod_les = [row[0], row[1], row[2]]
            # if not row[2] == "":
            body_les_seznam.append(bod_les)
            # else:
            #     body_les_seznam_bezref.append(bod_les)
            line_count += 1
            print(line_count)
            # c*xx - hodnta xx nastaví počet bodů v jednom požadavku na overpass
            if line_count == c * 20:
                overpass_query = overpass_query + overpass_end
                c = c + 1
                # zapise prikaz api overpaass do souboru txt }
                f.write(overpass_query + "\n")
                print("Overpass_query_ja:" + overpass_query)
                print(line_count)
                # posle dotaz na overpass

                # print(future.get())
                # response = r.get()
                # print("Blabla" + future.get())

                response = requests.get(overpass_url, params={'data': overpass_query})
                # print(type(response))
                print("encoding :" + response.encoding)
                # response.encoding = 'cp852'
                response.encoding = 'windows - 1250'
                print("encoding cov:" + response.encoding)
                data = [row.split('\t') for row in response.text.split('\n')]
                m = sum(1 for line in data)
                print("pocet radku m =" + str(m))
                n = 0
                while not m == n:
                    n = sum(1 for line in data)
                    print("pocet radku n =" + str(n))
                    time.sleep(0.5)
                    data = [row.split('\t') for row in response.text.split('\n')]
                    n = m
                    m = sum(1 for line in data)
                    print("pocet radku m =" + str(m))
                # osm_bz_resp = csv.writer(open("osm_bz_resp-" + timestr + ".csv", newline=""))
                # osm_bz_resp = csv.writer(open("osm_bz_resp-" + timestr + ".csv", "a", newline="", encoding='windows - 1250'))
                # osm_bz_resp = csv.writer(
                #     open("osm_bz.csv", "a", newline="", encoding='windows - 1250'))
                # windows - 1250
                # cp852
                # vymaže dotaz
                overpass_query = ""
                overpass_query = """[out:csv(::lat, ::lon, "ref", name, ::count)]; \n ( \n"""
                # prvni = 3
                # osm_bz_resp.writerow(str(c*50))

                for x in data[:m]:
                    try:
                        if x[2] == "NJ014" in str(x):
                            print("ref")
                    except:
                        print("An exception occurred")
                    print("x: " + str(x))
                    if prvni == 0 and "lat" in str(x):
                        if not str(x) == "" and len(x) == 5:
                            # osm_bz_resp.writerow(x)
                            # body_overpass_seznam.append('lat,lon,ref')
                            # print(x)
                            prvni = 0
                    if prvni == 2 and not "lat" in str(x) and not "<" in str(x) and not "/" in str(x):
                        if not str(x) == "" and len(x) == 5 and x[4] == "":
                            # osm_bz_resp.writerow(str(rad))
                            # print("Sloupce: " + str(len(x)))
                            bod_overpass = [x[0], x[1], x[2], x[3]]
                            # pokud bod v OSM nema hodntu REF zapise do seznamu bezref
                            if not x[2] == "" or not x[3] == "" :
                                body_overpass_seznam.append(bod_overpass)
                            else:
                                body_les_seznam_bezref.append(bod_overpass)
                            # osm_bz_resp.writerow(x)
                            rad = rad + 1

                    if len(x) == 5 and not x[4] == "" and not x[4] == "@count":
                        pocetbodu = int(x[4])
                        pocetboducelkem = pocetboducelkem + pocetbodu

                    prvni = 2
                    try:
                        e = str(x)
                        # e.strip()
                        # print(e)
                        # e = float(e)
                        print(e)
                        # print(type(e))
                    except:
                        print("chyba")
                prvni = 1
        print(f"Processed {line_count} lines.")

        if line_count == 2172:
            print("Pocet nalezenych bodu v OSM: " + str(pocetboducelkem))
            break

        # print(type(e))
        # print(x[2])
    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    dist = open('dis-VLSt.txt', 'a')
    dist.write("Vzdalenost bodu nize je vetsi nez 100m:" + "\n")
    chybejicibody = body_les_seznam.copy()

for y in body_overpass_seznam:
    if not "lat" in str(y):
        ref = y[2].replace(" ", "")
        index_les = [(i, element.index(ref)) for i, element in enumerate(body_les_seznam) if ref in element]
        # z kompletniho seznamu odstrani polozky, ktere jiz v oSM existuji.
        if index_les:
            index_chybejici = [(i, element.index(ref)) for i, element in enumerate(chybejicibody) if ref in element]
            if index_chybejici:
                del chybejicibody[index_chybejici[0][0]]
            # chybejicibody.remove(y)
            # print(index_les[0][0], index_les[0][1])
            # overeni vzdalenosti bodu v km se stejnym ref overpass a lesy
            vzdalenost = get_distance(float(body_les_seznam[index_les[0][0]][0]),
                                      float(body_les_seznam[index_les[0][0]][1]),
                                      float(y[0]), float(y[1]))
            # prevod na metry
            vzdalenost = vzdalenost * 1000
            if vzdalenost > 100:
                dist.write(ref + " " + str(vzdalenost) + '|VLS:' + str(body_les_seznam[index_les[0][0]][0]) + ','
                            + str(body_les_seznam[index_les[0][0]][1]) + '|OSM:' + str(y[0]) + ',' + str(y[1]) + "\n")
                print('Vzdálenost bodů: ' + str(vzdalenost), " ", y[2])
                body_les_seznam_bezref.append(y)
                if vstup == 'OSMchybejicibody-VLS.csv':
                    vymazatz_body_overpass_seznam.append(y)
        else:
            body_les_seznam_bezref.append(y)
            # body_overpass_seznam.remove(index_les[0][0])
            # body_overpass_seznam.remove(y)
            vymazatz_body_overpass_seznam.append(y)


print(f"Processed {line_count} lines.")
# f.close()
for s in vymazatz_body_overpass_seznam:
    if "lat" not in str(s):
        # ref = s[2].replace(" ", "")
        ref = s[2]
        index_body_overpass_seznam = [(i, element.index(ref)) for i, element in enumerate(body_overpass_seznam) if ref in element]
        if index_body_overpass_seznam:
            del body_overpass_seznam[index_body_overpass_seznam[0][0]]

# aktualni pocet bodu nalazenych v OSM
novyseznambodu = len(body_overpass_seznam)
# pocet bodu nalazenych v OSM pri minulem behu
if os.path.exists('OSMBZ-VLS.csv'):
    with open('OSMBZ-VLS.csv', newline='') as csvfileOSM:
        fileObject = csv.reader(csvfileOSM)
        puvodniseznambodu = sum(1 for row in fileObject)
else:
    puvodniseznambodu = 1

if not os.path.exists('statistika-VLS.csv'):
    with open('statistika-VLS.csv', 'w', newline='') as stat:
        wr = csv.writer(stat, delimiter=',')
        wr.writerow(['datum', 'narust', 'celkem'])
print('Původní počet bodů:' + str(puvodniseznambodu - 1) + "\n" + "Nový počet bodů: " + str(novyseznambodu))

# vymaze bod ktery je v BZneni.csv z Chybejicbody (OSMchybejicibody.csv)
neni = open("BZneni-VLS.csv", "r")
csv_reader_neni = csv.reader(neni, delimiter=",")
line_count = 0
for row in csv_reader_neni:
    if line_count == 0:
        line_count += 1
    else:
        for rr in chybejicibody:
            vzd = get_distance(float(rr[0]), float(rr[1]), float(row[0]), float(row[1]))
            vzd = vzd * 1000
            if vzd < 100:
                chybejicibody.remove(rr)
                print("Bod " + str(rr) + "byl vymazan z chybejicibody.")


if ((puvodniseznambodu - 1) < novyseznambodu and vstup == 'VLS-komplet.csv') or (novyseznambodu > 0 and vstup == 'OSMchybejicibody-VLS.csv'):
    today = date.today()
    # dd/mm/YY
    d1 = today.strftime("%d/%m/%Y")
    if vstup == 'VLS-komplet.csv':
        nar = novyseznambodu - (puvodniseznambodu - 1)
        celk = novyseznambodu
    else:
        nar = novyseznambodu
        celk = puvodniseznambodu + nar
    # vytvoří statistiku
    with open('statistika-VLS.csv', 'a', newline='') as sta:
        wri = csv.writer(sta, delimiter=',')
        wri.writerow([d1, str(nar), celk])

    # vytvoří seznam chbejicich bodu v OSM bez ref
    with open('OSMbodybezref-VLS.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(['lat', 'lon'])
        # chybejicibody_noref= []
        chybejicibody_noref = [x[0:2] for x in chybejicibody]
        writer.writerows(chybejicibody_noref)

    # https: // github.com / nidhaloff / gpx - converter
    Converter(input_file='OSMbodybezref-VLS.csv').csv_to_gpx(lats_colname='lat', longs_colname='lon', output_file='OSMbodybezref-VLS.gpx')

    # uprava gpx souboru na jednotlivé body (body jsou převedeny na waypoint)
    gpx_file = open('OSMbodybezref-VLS.gpx', 'r')
    gpx = gpxpy.parse(gpx_file)
    gpxnew = gpxpy.gpx.GPX()

    # PREVOD CSV NA GeoJSON
    data_csv = pd.read_csv('OSMbodybezref-VLS.csv')
    # Orig
    # geo_json = to_geojson(df=data_csv, lat='lat', lon='lon', properties=[])
    # 1.4.2024 oprava
    # geo_json = pdg.GeoJSON.from_dataframe(df=data_csv, lat='lat', lon='lon', properties=[])

    # Orig
    # write_geojson(geo_json, filename='OSMbodybezref.geojson', indent=4)
    # 1.4.2024 oprava 
    # pdg.save_geojson(geo_json, filename='OSMbodybezref.geojson', indent=4)
    # 2.4.2024 oprava
    df = data_csv
    df['geometry'] = df.apply(lambda row: Point(float(row['lon']), float(row['lat'])), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    gdf.to_file('OSMbodybezref-VLS.geojson', driver='GeoJSON')

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                gpxnew.waypoints.append(point)

    # print('Created GPX:', gpxnew.to_xml())
    fp = open('OSMbodybezref-VLS.gpx', 'w')
    fp.write(gpxnew.to_xml())
    fp.close()

    # zapise body zachrany, keré jsou v OSM
    if os.path.exists('OSMBZ-VLS.csv'):
        src = 'OSMBZ-VLS.csv'
        dst = './archiv/OSMBZ' + str(today) + '.csv'
        shutil.copy(src, dst)
    with open('OSMBZ-VLS.csv', zapis, newline='') as f:
        writer = csv.writer(f, delimiter=',')
        if zapis == 'w':
            writer.writerow(['lat', 'lon', 'ref'])
        writer.writerows(body_overpass_seznam)

    # vytvoří seznam chybejicich bodu v OSM s ref
    with open('OSMchybejicibody-VLS.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon', 'ref'])
        writer.writerows(chybejicibody)
    encrypt_file('OSMchybejicibody-VLS.csv', key)

    # vytvori seznam bodu v OSM ale s chybejici nebo chybnou hodnotou REF
    # body_les_seznam_bezref
    with open('OSMbodychybejiciref-VLS.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon', 'ref'])
        writer.writerows(body_les_seznam_bezref)

    # https: // github.com / nidhaloff / gpx - converter
    Converter(input_file='OSMbodychybejiciref-VLS.csv').csv_to_gpx(lats_colname='lat', longs_colname='lon',
                                                               output_file='OSMbodychybejiciref-VLS.gpx')
    gpxtrcktoway('OSMbodychybejiciref-VLS.gpx')


    # sousti wikipg.py
    import wikipg

# OSMchybejicibody.csv
if os.path.exists('OSMchybejicibody-VLS.csv'):
    os.remove('OSMchybejicibody-VLS.csv')
    print("..........................")

if os.path.exists('VLS-komplet.csv'):
     encrypt_file('VLS-komplet.csv', key)
if os.path.exists('VLS-komplet.csv'):
     os.remove('VLS-komplet.csv')

# /*
# This has been generated by the overpass-turbo wizard.
# The original search was:
# “emergency=access_point”
# */
# [out:json][timeout:25];
# // gather results
# (
#   // query part for: “emergency=access_point”
#   area[name="Česko"];
#   node(area)["emergency"="access_point"];
#   node(area)["highway"="emergency_access_point"];
# );
# // print results
# out body;
# >;
# out skel qt;
