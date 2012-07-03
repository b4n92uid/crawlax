
import re
import browser
import time
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
    name TEXT, address TEXT, category TEXT, phone TEXT, email TEXT, website TEXT, other TEXT
)
''')
database.commit()
cur.close()

def parsefirm(detail_html, category):

    patern = re.compile(r'=([\d.]+)')

    html = lxml.html.document_fromstring(detail_html)

    name = html.cssselect('.name')[0].text_content()
    address = ''
    phone = ''
    other = list()

    if name in firmlist:
        return

    print 'Parsing firm', name

    infos = html.cssselect('.style-content > p')

    for i in infos:

        key, value = i.text_content().split(':')

        key = key.strip()
        value = value.strip()

        if key == 'Nom de l\'entreprise':
            name = value

        elif key == 'Pay\xc3':
            address += value
        elif key == 'Addresse':
            address += value
        elif key == 'wilaya':
            address += value

        elif key == 'T\xe9l':

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

    cur.execute('INSERT INTO firms VALUES(?, ?, ?, ?, ?, ?, ?)',
    (name, address, category, phone, '', '', ', '.join(other)))

    database.commit()
    cur.close()

    firmlist.append(name)
    firmlist.update()

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

    for catelem in dom.cssselect('.iconne') :

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

            firmblocks = catdom.cssselect('#result-block')

            for firm in firmblocks :

                detail_url = firm.cssselect('.detailbutton')[0].get('href')
                detail_html = browser.get(detail_url)
                
                parsefirm(detail_html, categoy_name)
                
                time.sleep(2)

            print len(firmblocks), ' Frims has been parsed'

            next_elem = catdom.cssselect('.pagination a')[-1]

            if not 'Suivant' in next_elem.text_content():
                break;

            categoy_url = next_elem.get('href')
            curpage += 1

main()
