import csv
from Consts import Const

headers = ['IMAGEID', 'N', 'col', 'row', 'longitude', 'latitude', 'T4', 'T11', 'pixel_poly', 'region']
with open('points.txt', 'r', encoding='UTF-8') as txt:
    line = eval(txt.readlines()[0])

with open(f'{Const.IMAGEID}_Dorene.csv', 'w', encoding='UTF-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(line)

print(f'{Const.IMAGEID}_Dorene.csv')
