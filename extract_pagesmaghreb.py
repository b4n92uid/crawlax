
import re
import os
import sys
import urllib
import sqlite3
import httplib
import hashlib
import lxml.html
import serializlist

base = 'http://www.lespagesmaghreb.com'

firmlist = serializlist.serializlist('pagesmaghreb.firm')
database = sqlite3.connect('pagesmaghreb.sqlite')
connection = httplib.HTTPConnection('lespagesmaghreb.com')

cur = database.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS firms(
    name TEXT, address TEXT, category TEXT, phone TEXT, email TEXT, website TEXT, other TEXT
)
''')
database.commit()
cur.close()


def parseSensibleInfo(firm):

    firstlink = firm['image']
    firm.pop('image')

    print 'Firm:', firm['name']

    path = urllib.url2pathname(firstlink)
    index = re.search(r"(\d+)\.png", path).group(1)
    index = int(index)

    skipcount = 0
    datacount = 0

    while True:

        nextlink = '/images/generated/contact_methods/{0}.png'.format(index)
        index += 1

        connection.request('GET', base + nextlink)
        response = connection.getresponse()

        if response.status != 200:

            skipcount += 1
            connection.close()

            if skipcount < 10:
                continue
            else:
                break
        else:

            skipcount = 0

        # ocr the sensible info and save theme

        file = open('info.png', 'wb+')
        file.write(response.read())
        file.close()

        os.system('tools/ocr.bat info.png')

        file = open("info.txt", "r")
        info = file.read().strip()
        file.close()

        os.remove('info.png');
        os.remove('info.txt');

        # detect what kind of info
        # if email data is detected break the loop

        print 'OCR info:', info

        if not firm['phone']:
            firm['phone'] = info

        elif re.match(r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]{2,}\.[a-zA-Z0-9_-]{2,}$', info):
            firm['email'] = info
            break

        else:
            firm['other'].append(info)

        connection.close()

        datacount += 1

        if datacount >= 10:
            break

def parsePage(html):

    firms = list()

    doc = lxml.html.document_fromstring(html)
    htmlfirms = doc.cssselect('#firms .main_box')

    # parse firm's block in a loop and start crawling
    # from the first image in purpose to find email

    for htmlfirm in htmlfirms:

        infos = dict()
        infos['name'] = htmlfirm.cssselect('.corporate-name')[0].text_content()
        infos['address'] = htmlfirm.cssselect('.main-address')[0].text_content()
        infos['website'] = htmlfirm.cssselect('.links li')[1].cssselect('a')[0].get('href')
        infos['category'] = htmlfirm.cssselect('.categories')[0].text_content()
        infos['image'] = htmlfirm.cssselect('.contact-phones img')

        if len(infos['image']) == 0:
            continue
        else:
            infos['image'] = infos['image'][0].get('src')

        infos['phone'] = ''
        infos['email'] = ''
        infos['other'] = list()

        firms.append(infos)

    curs = database.cursor()

    for firm in firms:

        if firm['name'] in firmlist:
            continue

        parseSensibleInfo(firm)

        firmlist.append(firm['name'])
        firmlist.update()

        try:
            curs.execute('''INSERT into
            firms(name, address, category, phone, email, website, other)
            VALUES(?, ?, ?, ?, ?, ?, ?)''',
                (firm['name'], firm['address'], firm['category'],
                firm['phone'], firm['email'], firm['website'], ', '.join(firm['other'])))
        except:
            print "Unexpected sql error:", sys.exc_info()[0]
            continue

    database.commit()
    curs.close()

    print len(firms), ' firms has been parsed !'
    print ''

def main():

    print ''.center(40, '-')
    print ' Welcome to the '.center(40, '-')
    print ' PagesMaghreb dumper '.center(40, '-')
    print ' (c) 2012 b4n92uid '.center(40, '-')
    print ''.center(40, '-')
    print ''

    searchpattern = '/firms?'
    keyword = raw_input('Keyword: ')
    searchpattern += 'search%5Bkeywords%5D=' + keyword
    searchpattern += '&search%5Bconditions%5D%5Brs%5D='
    searchpattern += '&search%5Bconditions%5D%5Bcategorie%5D='
    searchpattern += '&search%5Bconditions%5D%5Btag%5D='
    searchpattern += '&search%5Bconditions%5D%5Bcontact%5D='
    city = raw_input('City: ')
    searchpattern += '&search%5Bconditions%5D%5Bville%5D=' + city
    searchpattern += '&search%5Bconditions%5D%5Bwilaya%5D='
    searchpattern += '&search%5Bconditions%5D%5Bpays%5D='
    searchpattern += '&search%5Bconditions%5D%5Badresse%5D='
    searchpattern += '&select_gmap=0'
    searchpattern += '&search%5Bfilters%5D%5Bwith%5D%5B%5D=0'
    searchpattern += '&select_tel=0'
    searchpattern += '&search%5Bfilters%5D%5Bwith%5D%5B%5D=0'
    searchpattern += '&select_fax=0'
    searchpattern += '&search%5Bfilters%5D%5Bwith%5D%5B%5D=0'
    searchpattern += '&select_email=0'
    searchpattern += '&search%5Bfilters%5D%5Bwith%5D%5B%5D=0'
    searchpattern += '&select_mobile=0'
    searchpattern += '&search%5Bfilters%5D%5Bwith%5D%5B%5D=0'
    searchpattern += '&select_website=0'
    searchpattern += '&search%5Bfilters%5D%5Bwith%5D%5B%5D=0'
    searchpattern += '&commit='

    print 'Fetch index search page...'

    connection.request('GET', base + searchpattern)
    response = connection.getresponse()
    html = response.read()

    print 'Process pagnination links...'

    pageslink = list()
    doc = lxml.html.document_fromstring(html)

    for a in doc.cssselect('div.pagination a'):
        pageslink.append(a.get('href'))

    print (len(pageslink)+1), 'pages found for this query'

    print 'Parsing page', 1
    parsePage(html)

    # parse all pagination links

    for i, url in enumerate(pageslink):

        print 'Parsing page', (i+2)

        connection.request('GET', base + url)
        response = connection.getresponse()
        html = response.read()

        parsePage(html)

main()
