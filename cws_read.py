import csv
import requests
import time
import math
import os
from cryptography.fernet import Fernet
from multiprocessing.dummy import Pool
import json


def get_distance(lat_1, lng_1, lat_2, lng_2): #vypocet vdalenosti bodu
    lng_1, lat_1, lng_2, lat_2 = map(math.radians, [lng_1, lat_1, lng_2, lat_2]) #prevede uhly na radiany
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1

    temp = (
            math.sin(d_lat / 2) ** 2
            + math.cos(lat_1)
            * math.cos(lat_2)
            * math.sin(d_lng / 2) ** 2
    )

    return 6373.0 * (2 * math.atan2(math.sqrt(temp), math.sqrt(1 - temp)))


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


#mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
#NEMAZAT!!!
# key generation
# key = Fernet.generate_key()

#prevezme klic y Gitu
key = os.environ['REPO_SECRET']
# key = ""
# string the key in a file
# with open('filekey.key', 'wb') as filekey:
#     filekey.write(key)

#mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# json.loads("")
#encrypt_file("Lesy_CR_komplet_.csv", key )
pocetboducelkem = 0
body_les_seznam = []
body_overpass_seznam = []
body_les_seznam_bezref = []
chybejicibody_noref= []
if os.path.exists('enc-Lesy_CR_komplet100.csv'):
    vstup = 'enc-Lesy_CR_komplet100.csv'
    oddelovac = ';'
    decrypt_file(vstup, key)
else:
    vstup = 'enc-OSMchybejicibody.csv'
    oddelovac = ','
    vystup = 'enc-OSMchybejicibody_bezref.csv'
    decrypt_file(vstup, key)


# with open(vstup, encoding='cp852') as csv_file:
with open(vstup[4:], encoding='cp852') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=oddelovac)
    line_count = 0
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """[out:csv(::lat, ::lon, "ref", name, ::count)]; \n ( \n"""
    overpass_end = "\n ); \n out; \n out count; \n"
    f = open("comm_wr.txt", "w")
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
                            bod_overpass = [x[0], x[1], x[2]]
                            #pokud bod v OSM nema hodntu REF yapise do seznamu bezref
                            if not x[2] == "":
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
    f.write("Vzdalenost bodu nize je vetsi nez 100m:" + "\n")
    chybejicibody = body_les_seznam

for y in body_overpass_seznam:
    if not "lat" in str(y):
        ref = y[2].replace(" ", "")
        index_les = [(i, element.index(ref)) for i, element in enumerate(body_les_seznam) if ref in element]
        # y kompletniho seznamu odstrani polozky, ktere jiz v oSM existuji.
        del chybejicibody[index_les[0][0]]
        # print(index_les[0][0], index_les[0][1])
        # overeni vzdalenosti bodu v km se stejnym ref overpass a lesy
        vzdalenost = get_distance(float(body_les_seznam[index_les[0][0]][0]),
                                  float(body_les_seznam[index_les[0][0]][1]),
                                  float(y[0]), float(y[1]))
        # prevod na metry
        vzdalenost = vzdalenost * 1000
        if vzdalenost > 100:
            f.write(ref + " " + str(vzdalenost) + "\n")
        print(vzdalenost, " ", y[2])

        print(f"Processed {line_count} lines.")
# vytvoří seznam chbejicich bodu v OSM bez ref
with open('OSMchybejicibody_bezref.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['lat', 'lon', 'ref'])
    # chybejicibody_noref= []
    chybejicibody_noref = [x[0:2] for x in chybejicibody]
    writer.writerows(chybejicibody_noref)

# zapise body zachrany, keré jsou v OSM
with open('OSMBZ.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(['lat', 'lon', 'ref'])
    writer.writerows(body_overpass_seznam)


# vytvoří seznam chybejicich bodu v OSM s ref
with open('OSMchybejicibody.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['lat', 'lon'])
    writer.writerows(chybejicibody)
encrypt_file('OSMchybejicibody.csv', key)

# vytvori seznam bodu v OSM ale s chybejici hodnotou REF
# body_les_seznam_bezref
with open('OSMbodybezref.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['lat', 'lon'])
    writer.writerows(body_les_seznam_bezref)

if os.path.exists('Lesy_CR_komplet.csv'):
    os.remove('Lesy_CR_komplet.csv')
