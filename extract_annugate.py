
import re
import time
import random
import browser
import sqlite3
import urlparse
import lxml.html
import serializlist

baseurl = 'http://annugate.com/';
firmlist = serializlist.serializlist('annugate.firm')
database = sqlite3.connect('annugate.sqlite')
browser = browser.browser()

cur = database.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS firms(
    id INTEGER NOT NULL PRIMARY KEY DEFAULT "0",
    name TEXT, address TEXT, category TEXT, phone TEXT, email TEXT, website TEXT, other TEXT
)
''')
database.commit()
cur.close()

def parsefirm(detail_html, category):

    patern = re.compile(r'=([\d.]+)')

    html = lxml.html.document_fromstring(detail_html)

    name = html.cssselect('.name')[0].text_content()
    address = list()
    other = list()
    phone = ''

    print 'Parsing firm', name

    infos = html.cssselect('.style-content > p')

    for i in infos:

        key, value = i.text_content().split(':')

        key = key.strip()
        value = value.strip()

        if key == 'Nom de l\'entreprise':
            name = value

        elif key == u'Pay\xc3':
            address.append(value)
        elif key == 'Addresse':
            address.append(value)
        elif key == 'wilaya':
            address.append(value)

        elif key == u'T\xe9l':

            imgelem = i.cssselect('img')

            if imgelem:
                phone = patern.search(imgelem[0].get('src')).group(1)
            else:
                phone = value

        else:

            imgelem = i.cssselect('img')

            if imgelem:
                imgelem = patern.search(imgelem[0].get('src')).group(1)
            else:
                other.append(value)


    cur = database.cursor()

    address = ', '.join(address)
    other = ', '.join(other)

    cur.execute('INSERT INTO firms VALUES(?, ?, ?, ?, ?, ?, ?)',
    (name, address, category, phone, '', '', other))

    database.commit()
    cur.close()

def shuffle(list):
    random.shuffle(list)
    return list

def main():

    print 'Login...'

    browser.post(baseurl + "connexion.php", {
        'login' : 'tajepyjecymiqucu@tempomail.fr',
        'mdp' : 'jhondoe'
    })

    html = browser.get(baseurl)

    print 'Fetch index page...'

    dom = lxml.html.document_fromstring(html)
    dom.make_links_absolute(baseurl)

    for catelem in  shuffle(dom.cssselect('.iconne')):

        elem_a = catelem.cssselect('a')[0]

        categoy_name = elem_a.text_content()
        categoy_url = elem_a.get('href')
        curpage = 1

        print 'Parsing category', categoy_name

        while True:

            print 'Parsing page', curpage

            try:
                html = browser.get(categoy_url)
                catdom = lxml.html.document_fromstring(html)
                catdom.make_links_absolute(baseurl)
            except:
                break

            firmblocks = shuffle(catdom.cssselect('#result-block'))

            for firm in firmblocks :

                detail_url = firm.cssselect('.detailbutton')[0].get('href')
                detail_html = browser.get(detail_url)
                
                if 'images/stop.png' in detail_html :
                    raise Exception('*** Access denied to the site ! ***')
                
                try:
                    if detail_url in firmlist:
                        continue

                    parsefirm(detail_html, categoy_name)
                    firmlist.append(detail_html)
                    firmlist.update()
                    time.sleep(2)
                except:
                    pass

            print len(firmblocks), ' Frims has been parsed'

            next_elem = catdom.cssselect('.pagination a')[-1]

            if not 'Suivant' in next_elem.text_content():
                break;

            categoy_url = next_elem.get('href')
            curpage += 1

try:
    main()
except Exception as e:
    print e
