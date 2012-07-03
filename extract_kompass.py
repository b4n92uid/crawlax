import serializlist
import lxml.html
import urlparse
import sqlite3
import urllib
import re

baseurl = 'http://directory.kompass.com/';
firmlist = serializlist.serializlist('kompass.firm')

database = sqlite3.connect('kompass.sqlite')
database.text_factory = str
cur = database.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS firms(
    name TEXT, address TEXT, category TEXT, phone TEXT, email TEXT, website TEXT, other TEXT
)
''')
database.commit()
cur.close()

def parsefirm(firm_link):

    firm_dom = lxml.html.parse(firm_link).getroot()

    name = firm_dom.cssselect('.description_company .title_h2')[0].text_content().strip()
    address = firm_dom.cssselect('.color_gris')[0].text_content()
    address = re.sub("\s{2,}", "", address).strip()
    phone = ''
    other = list()

    for phone_elem in firm_dom.cssselect('#telBlockOne li') :

        value = phone_elem.text_content().split(':')[1].strip()

        if not phone:
            phone = value
        else:
            other.append(value)


    cur = database.cursor()
    cur.execute('INSERT INTO firms VALUES(?, ?, ?, ?, ?, ?, ?)',
    (name.encode('iso-8859-15'), address, '', phone, '', '', ', '.join(other)))

    database.commit()
    cur.close()

def main():

    print 'Fetch index page...'

    link = baseurl + 'fr/Alg%C3%A9rie/dir.php'

    dom = lxml.html.parse(link).getroot()
    dom.make_links_absolute(link)

    for wilaya_a in dom.cssselect('#list a') :

        wilaya_name = wilaya_a.text_content()
        wilaya_link = wilaya_a.get('href')

        print '> Parsing wilaya', wilaya_name

        wilaya_dom = lxml.html.parse(wilaya_link).getroot()
        wilaya_dom.make_links_absolute(wilaya_link)

        for commune_a in wilaya_dom.cssselect('#list a') :

            commune_name = commune_a.text_content()
            commune_link = commune_a.get('href')

            print '> Parsing commune', commune_name

            commune_dom = lxml.html.parse(commune_link).getroot()
            commune_dom.make_links_absolute(commune_link)

            for firm in commune_dom.cssselect('#list a'):

                print 'Parsing firm', firm.text_content()

                try:
                    firm_link = firm.get('href')

                    if not firm_link in firmlist:
                        parsefirm(firm_link)
                        firmlist.append(firm_link)

                except:
                    pass

if __name__ == '__main__':
    main()
