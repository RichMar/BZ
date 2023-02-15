import csv
import requests
import time
from multiprocessing.dummy import Pool
import json

# json.loads("")

with open('Lesy_CR_komplet.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """[out:csv(::lat, ::lon, "ref")];"""
    overpass_end = "\n out; \n"
    f = open("comm_wr.txt", "w")
    c = 1
    prvni = 0
    rad = 1
    timestr = time.strftime("%Y%m%d-%H%M%S")
    for row in csv_reader:

        # print("111" + row)
        if line_count == 0:
            print(f'Column names are {", ".join(row)}') #nazvy sloupcu csv
            line_count += 1
        else:
            #nahradi carku teckou v souradnicich
            row[0] = ''.join([i for i in row[0]]).replace(",", ".")
            row[1] = ''.join([i for i in row[1]]).replace(",", ".")
            #odstrani tab meyeru pred nazvem bodu
            row[2] = row[2].replace("\t", "")
            row[2] = row[2].replace(" ", "")
            dotaz_body = """node[highway=emergency_access_point](around:100,""" + row[0] + """, """ + row[1] + """);"""
            overpass_query = overpass_query + dotaz_body
            overpass_query = overpass_query + overpass_end
            print(f'x={row[0]}; y= {row[1]}; {row[2]}.')
            line_count += 1
            print(line_count)
            if line_count == c * 50:
                c = c + 1
                #zapise prikaz api overpaass do souboru txt }
                f.write(overpass_query + "\n")
                print("Overpass_query_ja:" + overpass_query)
                print(line_count)
                # pošle dotaz na overpass

                        #print(future.get())
                        #response = r.get()
                        # print("Blabla" + future.get())

                response = requests.get(overpass_url, params={'data': overpass_query})
                                    #print(type(response))
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
                osm_bz_resp = csv.writer(open("osm_bz_resp-" + timestr + ".csv", "a"))
                # vymaže dotaz
                overpass_query = ""
                overpass_query = """[out:csv(::lat, ::lon, "ref")];""" + "\n"
                #prvni = 3
                #osm_bz_resp.writerow(str(c*50))
                for x in data[:m]:
                    print("x: " + str(x))
                    if prvni == 0 and "lat" in str(x):
                        if not str(x) == "" and len(x) == 3:
                            osm_bz_resp.writerow(x)
                            #print(x)
                            prvni = 0
                    if prvni == 2 and not "lat" in str(x) and not "<" in str(x) and not "/" in str(x):
                        if not str(x) == "" and len(x) == 3:
                            #osm_bz_resp.writerow(str(rad))
                            #print("Sloupce: " + str(len(x)))

                            osm_bz_resp.writerow(x)
                            rad = rad + 1

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
            break

        # print(type(e))
        # print(x[2])
    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    # print("XXXCSV: " + response.text)
    # prevede response na neco citelneho
    # decoded_content = response.content.decode("utf-8")
    # cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    # my_list = list(cr)

    print(f"Processed {line_count} lines.")
