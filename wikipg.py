import csv
import os


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

data= import_csv('statistika.csv')
last_row = data[-1]

absolute_path = os.path.dirname(__file__)
relative_path = "BZ.wiki\Home.md"
full_path = os.path.join(absolute_path, relative_path)
with open(full_path, 'r+', encoding="utf-8") as home:
    for line in home:
        # print(line)
        if 'body" : ' in line:
            a = line.find('body" : ') + 8
            print(a)
            print(line[-5:])
            print(line[a:])



print("ahoj")
