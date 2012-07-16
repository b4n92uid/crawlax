
import re
import glob
import sqlite3

# INIT -------------------------------------------------------------------------

firms = dict()

mainfn = 'database.sqlite'

if os.path.exists(mainfn):
    os.remove(mainfn)

maindb = sqlite3.connect(mainfn)

cur = maindb.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS firms(
    id INTEGER NOT NULL PRIMARY KEY DEFAULT "0",
    name TEXT, address TEXT, category TEXT, phone TEXT, email TEXT, website TEXT, other TEXT
)
''')
maindb.commit()
cur.close()

# GLOB -------------------------------------------------------------------------

for filename in glob.glob('*.sqlite'):

    if filename == mainfn:
        continue

    print '>', filename

    database = sqlite3.connect(filename)

    cur = database.cursor()
    cur.execute('SELECT * FROM firms')

    for entry in cur:

        name = entry[1].lower().strip()

        try:
            name = re.sub(u'[ÀÁÂÃÄÅàáâãäå]', 'a', name)
            name = re.sub(u'[ÒÓÔÕÖØòóôõöø]', 'o', name)
            name = re.sub(u'[ÈÉÊËèéêë]', 'e', name)
            name = re.sub(u'[Çç]', 'c', name)
            name = re.sub(u'[ÌÍÎÏìíîï]', 'i', name)
            name = re.sub(u'[ÙÚÛÜùúûü]', 'u', name)
            name = re.sub(u'[Ññ]', 'n', name)
            name = re.sub(u'[ÿ]', 'y', name)
            name = re.sub(u'[^a-zA-Z0-9]+', '-', name)

        except:
            pass

        if not name in firms.keys():
            firms[name] = entry

        print name

# INSERT -----------------------------------------------------------------------

mcur = maindb.cursor()

for f in firms.values():

    mcur.execute('''INSERT INTO firms(name, address, category, phone, email, website, other)
                    VALUES(?, ?, ?, ?, ?, ?, ?)''',
                    (f['name'], f['address'], f['category'], f['phone'], f['email'], f['website'], f['other']))


maindb.commit()
mcur.close()

os.system('pause')
