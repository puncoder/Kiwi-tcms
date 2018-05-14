import csv
with open('data.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        print (row)