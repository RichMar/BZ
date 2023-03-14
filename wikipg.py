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
    bodyvOSM = data[0][-1][3]
    chb = 2171 - int(bodyvOSM)
    b = data[0][-1][2]
data1 = import_csv('OSMbodychybejiciref.csv')
proble = len(data1[0]) -1
# absolute_path = os.path.dirname(__file__)
# relative_path = "BZ.wiki\Home.md"
# full_path = os.path.join(absolute_path, relative_path)
# print(absolute_path)
# print(full_path)

print(Path.cwd())
for root, dirs, files in os.walk(Path.cwd()):
    for name in files:
        if name.endswith(("Home.md")):
            full_path = os.path.join(root, name)
            # print(root)
            # print(dirs)
            # print(files)
            print(full_path)
            for line in fileinput.input(full_path, inplace=True, encoding="cp852"):
                if 'body" : ' in line and r == 1:
                    a = line.find('body" : ') + 8
                    x = line.replace(line[a:], str(chb))
                    print('{}'.format(x + '\n'), end='')
                elif 'v OSM" : ' in line and r == 1:
                    a = line.find('v OSM" : ') + 9
                    x = line.replace(line[a:], str(bodyvOSM))
                    print('{}'.format(x + '\n'), end='')
                elif 'otou" : ' in line:
                    a = line.find('otou" : ') + 8
                    x = line.replace(line[a:], str(proble))
                    print('{}'.format(x + '\n'), end='')
                else:
                    print('{}'.format(line), end='')

print("ahoj wikipg")
