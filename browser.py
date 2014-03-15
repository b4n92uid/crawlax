
import urllib
import urllib2
import cookielib
import urlparse
import logging

headers = {
    'Connection' : 'keep-alive',
    'Cache-Control' : 'max-age=0',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36',
    'Accept-Language' : 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4,ar;q=0.2',
}

class browser:

    def __init__(self):
        coukiejar = cookielib.CookieJar()
        cookieHandler = urllib2.HTTPCookieProcessor(coukiejar)

        self.opener = urllib2.build_opener(cookieHandler)

    def _request(self, url):
        request = urllib2.Request(url, None, headers)
        return request

    def post(self, url, data):

        urlcom = urlparse.urlparse(url)
        logging.info('POST %s?%s', urlcom.path, urlcom.query)

        resp = None

        try:
            data = urllib.urlencode(data)
            req = self._request(url)
            resp = self.opener.open(req, data)

        except urllib2.URLError as e:
            logging.error("Request error : %s", e.reason)

        except urllib2.HTTPError as e:
            logging.error("Server error %d %s", e.code, e.reason)

        return resp.read()

    def get(self, url):

        urlcom = urlparse.urlparse(url)
        logging.info('GET %s?%s', urlcom.path, urlcom.query)

        resp = None

        try:
            req = self._request(url)
            resp = self.opener.open(req)

        except urllib2.URLError as e:
            logging.error("Request error %s", e.reason)

        except urllib2.HTTPError as e:
            logging.error("Server error %d %s", e.code, e.reason)

        return resp.read()
