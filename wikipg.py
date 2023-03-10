import csv
import os
import fileinput

def import_csv(csvfilemame):
    data = []
    row_index = 0
    with open('statistika.csv', 'r') as stat:
        stat_reader = csv.reader(stat, delimiter=',')
    # last_row = stat_reader[-1]
        for row in stat_reader:
            if row:  # avoid blank lines
                row_index += 1
                columns = [str(row_index), row[0], row[1], row[2]]
                data.append(columns)
    return data

data = import_csv('statistika.csv')
last_row = data[-1]
boduvOSM = data[-1][3]
chb = 2171-int(boduvOSM)
b = data[-1][2]
absolute_path = os.path.dirname(__file__)
relative_path = "BZ.wiki\Home.md"
full_path = os.path.join(absolute_path, relative_path)


for line in fileinput.input(full_path, inplace=True, encoding="cp852"):
    if 'body" : ' in line:
        a = line.find('body" : ') + 8
        x = line.replace(line[a:], str(chb))
        print('{}'.format(x + '\n'), end='')
    elif 'v OSM" : ' in line:
        a = line.find('v OSM" : ') + 9
        x = line.replace(line[a:], str(b))
        print('{}'.format(x + '\n'), end='')
    else:
        print('{}'.format(line), end='')

print("ahoj wikipg")
