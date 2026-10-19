import csv
import requests
import sys

def stahni_body_s_poskozenou_tabulkou():
    seznam = []
    # Seznam ověřených zrcadel s https://
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.openstreetmap.fr/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    
    # Dotaz na body, které mají v OSM označenou chybějící/poškozenou fyzickou ceduli (tabulku)
    overpass_query = """
    [out:csv(::lat, ::lon, "ref", name)][timeout:90];
    area[name="Česko"]->.searchArea;
    (
      node(area.searchArea)["removed:highway"="emergency_access_point"];
      node(area.searchArea)["removed:emergency"="access_point"];
    );
    out body;
    """

    headers = {
        'User-Agent': 'RichMar-BZ-Bot/1.0 (gis-script@github-action)'
    }

    response = None
    uspech = False

    for overpass_url in overpass_urls:
        try:
            response = requests.post(
                overpass_url,
                data={'data': overpass_query},
                headers=headers,
                timeout=120
            )
            if response.status_code == 200:
                uspech = True
                break
        except requests.exceptions.RequestException:
            continue

    if not uspech or response is None:
        print("Nepodařilo se stáhnout body s poškozenou tabulkou z žádného Overpass serveru.")
        with open('BZneni.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['lat', 'lon', 'ref'])
        return

    response.encoding = 'utf-8'
    data = [row.split('\t') for row in response.text.split('\n')]
    
    for x in data:
        if len(x) >= 3 and "lat" not in str(x) and x[0].strip() != "" and not "<" in str(x):
            lat = x[0].replace(",", ".")
            lon = x[1].replace(",", ".")
            ref = x[2].strip()
            seznam.append([lat, lon, ref])

    with open('BZneni.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon', 'ref'])
        writer.writerows(seznam)
    
    print(f"Staženo {len(seznam)} bodů s poškozenou/chybějící tabulkou do BZneni.csv.")

# Spuštění při importu modulu
stahni_body_s_poskozenou_tabulkou()
