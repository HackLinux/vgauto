import csv


f = open('vpngateserver.csv', 'rb')
reader = csv.reader(f, delimiter=',', quotechar='|')

a = []
for row in reader:
	print row[0].strip()
