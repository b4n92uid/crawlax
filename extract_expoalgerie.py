import lxml.html
import httplib
import sqlite3
import re

database = sqlite3.connect('expoalgerie.sqlite')
connection = httplib.HTTPConnection('expoalgerie.com')

cur = database.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS firms(
    name TEXT, address TEXT, category TEXT, phone TEXT, email TEXT, website TEXT, other TEXT
)
''')
database.commit()
cur.close()

def parsecat(html, category):

    dom = lxml.html.document_fromstring(html)

    for content in dom.cssselect('.contenu'):
        
        content = content.text_content()
        content = content.replace('tel : ', '\n')
        content = content.replace('e-mail : ', '\n')
        content = content.replace('fax : ', '\n')
        content = content.replace('site web : ', '\n')
        content = [x.strip() for x in content.split('\n') if x]
        
        name, address = content[:2]
        email = ''
        phone = ''
        other = list()
        
        for info in content[2:]:
            if not email and re.match('(.+)@(.+)', info):
                email = info
            elif not phone and re.match('\d+ ', info):
                phone = info
            else:
                other.append(info)
            
        print 'Name:', name
        print 'Address:', address
        print 'Phone:', phone
        print 'Email:', email
        print 'Other:', other

        #cur = database.cursor()
        #cur.('''INSERT INTO firms() VALUES()''')
        #database.commit()
        #cur.close()

def main():

    category_base = "/categorie/index.php?cat={0}"

    print 'Fetch index page...'

    connection.request("GET", '/')
    indexhtml = connection.getresponse().read()
    connection.close()

    for i in range(1,14) :

        print 'Parsing category', i

        url = category_base.format(i)
        connection.request("GET", url)
        reponse = connection.getresponse()
        html = reponse.read()

        dom = lxml.html.document_fromstring(indexhtml)
        cats = dom.cssselect('.categorie')
        category = re.match('\w+', cats[i-1].text_content()).group(0)
        
        result = re.findall("index\.php\?page=\d+", html)

        page_base = "/categorie/index.php?cat={0}&page={1}"

        for j,pagelink in enumerate(result) :

            print 'Parsing page', j
            
            pageurl = page_base.format(i, j)
            connection.request("GET", pageurl)
            reponse = connection.getresponse()
            
            parsecat(reponse.read(), category)

main()
