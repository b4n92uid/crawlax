import codecs
import os
import sqlite3

database = sqlite3.connect('database.sqlite')
cur = database.cursor()
cur.execute('SELECT * from firms')

file = codecs.open('database.txt', 'w+', encoding='utf-8')

result = cur.fetchall()

for entry in result:
    line = ''
    line += entry[0].strip() + "\r\n"
    line += entry[1].strip() + "\r\n"
    line += entry[3].strip() + "\r\n"
    line += entry[4].strip() + "\r\n"
    line += ''.center(80, '-') + "\r\n"
    file.write(line)

print len(result), 'result printed !'

file.close()
cur.close()
