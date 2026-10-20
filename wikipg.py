import csv
import os
import fileinput
from pathlib import Path


def import_csv(csvfilemame):
    data = []
    row_index = 0
    r = 0
    with open(csvfilemame, 'r') as stat:
        stat_reader = csv.reader(stat, delimiter=',')
    # last_row = stat_reader[-1]
        for row in stat_reader:
            if row:  # avoid blank lines
                row_index += 1
                try:
                    columns = [str(row_index), row[0], row[1], row[2]]
                    r = 1
                except:
                    columns = [str(row_index), row[0], row[1]]
                    r = 2
                data.append(columns)
    return data, r

data = import_csv('statistika.csv')
r = data[1]
if r == 1:
    last_row = data[0][-1]
    datum = last_row[1]
    datum_str = str(datum)
    datum_cr = datum_str.replace('/','.')
    bodyvOSM = data[0][-1][3]
    chb = 2171 - int(bodyvOSM)
    prir = data[0][-1][2]

data1 = import_csv('OSMbodychybejiciref.csv')
proble = len(data1[0]) -1

# absolute_path = os.path.dirname(__file__)
# relative_path = "BZ.wiki\Home.md"
# full_path = os.path.join(absolute_path, relative_path)
# print(absolute_path)
# print(full_path)

print(Path.cwd())
found_home = False

for root, dirs, files in os.walk(Path.cwd()):
    for name in files:
        if name.endswith(("Home.md")):
            found_home = True
            full_path = os.path.join(root, name)

            print(f"Nalezen soubor: {full_path}")
            print(f"Aktuální hodnota 'proble' pro zápis: {proble}")
            
            for line in fileinput.input(full_path, inplace=True, encoding="utf-8"):
                if 'Chy' in line and r == 1:
                    # Pokud jde o textový řádek dole (ne v grafu)
                    if not line.strip().startswith('"'):
                        a = line.find(':') + 2
                        x = line.replace(line[a:], str(chb))
                        print('{}'.format(x + '\n'), end='')
                    else:
                        # Řádek v mermaid grafu: "Chybějící body" : 1305
                        parts = line.split(':')
                        x = parts[0].strip() + ' : ' + str(chb)
                        print('    {}'.format(x), end='\n')
                elif 'OSM' in line and 'pie' not in line and r == 1:
                    if not line.strip().startswith('"'):
                        a = line.find(':') + 2
                        x = line.replace(line[a:], str(bodyvOSM))
                        print('{}'.format(x + '\n'), end='')
                    else:
                        # Řádek v mermaid grafu: "Body záchrany v OSM" : 866
                        parts = line.split(':')
                        x = parts[0].strip() + ' : ' + str(bodyvOSM)
                        print('    {}'.format(x), end='\n')
                elif 'REF' in line:
                    if not line.strip().startswith('"'):
                        # Běžný textový řádek dole: Body s problémovou REF hodnotou : 19
                        a = line.find(':') + 2
                        x = line.replace(line[a:], str(proble))
                        print('{}'.format(x + '\n'), end='')
                    else:
                        # Řádek v mermaid grafu: "Body s problémovou REF hodnotou" : 19
                        parts = line.split(':')
                        x = parts[0].strip() + ' : ' + str(proble)
                        print('    {}'.format(x), end='\n')
                else:
                    # Všechny ostatní řádky (včetně ```mermaid a ```) necháme naprosto netknuté!
                    print('{}'.format(line), end='')

        if name.endswith(("Prirustky-bodu-zachrany-do-OSM.md")):
            full_path = os.path.join(root, name)
            print(f"Nalezen soubor přírůstků: {full_path}")
            
            # Nejdříve načteme celý obsah a zkontrolujeme, zda dnešní datum už v grafu není
            with open(full_path, 'r', encoding='utf-8') as f:
                obsah = f.read()
            
            # Pokud už dnešní datum v souboru je, přírůstek nepřidáváme znova
            if f"section {datum_cr}" in obsah:
                print(f"Záznam pro dnešní datum ({datum_cr}) už v grafu existuje, přeskakuji zápis.")
            else:
                with fileinput.input(full_path, inplace=True, encoding="utf-8") as f:
                    for line in f:
                        if '```' in line and not 'mermaid' in line:
                            x = ''
                            print('{}'.format(x), end='')
                            y = '    section ' + datum_cr + '\n' + '    ' + str(prir) + '    : 0, ' + str(prir) + '\n\n' + '```'
                            print('{}'.format(y + '\n'), end='')
                        else:
                            print('{}'.format(line), end='')
                print(f"Přidán nový záznam do sloupcového grafu pro datum: {datum_cr}")

if not found_home:
    print("VAROVÁNÍ: Soubor Home.md nebyl v prohledávaných složkách nalezen!")

# Generování stránky žebříčku uživatelů
uzivatele_csv = 'statistika_uzivatelu.csv'
if os.path.exists(uzivatele_csv):
        rows_uzivatele = []
        with open(uzivatele_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None) # přeskočíme hlavičku
            for r_row in reader:
                if len(r_row) >= 6:
                    rows_uzivatele.append(r_row)

        found_zebricek = False
        for root, dirs, files in os.walk(Path.cwd()):
            for name in files:
                if name == "Zebricek-uzivatelu.md":
                    found_zebricek = True
                    zeb_path = os.path.join(root, name)
                    
                    with open(zeb_path, 'w', encoding='utf-8') as zf:
                        zf.write("# Žebříček přispěvatelů do OSM podle operátorů\n\n")
                        zf.write("Tento žebříček automaticky sleduje přispěvatele bodů záchrany rozdělené podle správců.\n\n")
                        zf.write("| Pořadí | Uživatel | Lesy ČR | VLS | Městské lesy | NP & CHKO | KČT | Bez operátora | Ostatní | Celkem |\n")
                        zf.write("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
                        
                        for idx, row in enumerate(rows_uzivatele, 1):
                            # row[0]=Uzivatel, row[1]=Lesy ČR, row[2]=VLS, row[3]=Městské, row[4]=NP&CHKO, row[5]=KČT, row[6]=Bez operátora, row[7]=Ostatní, row[8]=Celkem
                            zf.write(f"| {idx} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | **{row[8]}** |\n")
                    print(f"Stránka žebříčku byla aktualizována: {zeb_path}")

        if not found_zebricek:
            for root, dirs, files in os.walk(Path.cwd()):
                if os.path.basename(root) == "wiki_folder":
                    new_zeb_path = os.path.join(root, "Zebricek-uzivatelu.md")
                    with open(new_zeb_path, 'w', encoding='utf-8') as zf:
                        zf.write("# Žebříček přispěvatelů do OSM podle operátorů\n\n")
                        zf.write("Tento žebříček automaticky sleduje přispěvatele bodů záchrany rozdělené podle správců.\n\n")
                        zf.write("| Pořadí | Uživatel | Lesy ČR | VLS | Městské lesy | NP & CHKO | KČT | Bez operátora | Ostatní | Celkem |\n")
                        zf.write("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
                        
                        for idx, row in enumerate(rows_uzivatele, 1):
                            # row[0]=Uzivatel, row[1]=Lesy ČR, row[2]=VLS, row[3]=Městské, row[4]=NP&CHKO, row[5]=KČT, row[6]=Bez operátora, row[7]=Ostatní, row[8]=Celkem
                            zf.write(f"| {idx} | {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} | **{row[8]}** |\n")
                    print(f"Byl vytvořen nový soubor žebříčku: {new_zeb_path}")
                    break

print("Konec wikipg")
