
import urllib
import urllib2
import cookielib

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5',
    'Accept' : 'text/html, image/jpeg, image/png, text/*, image/*, */*',
    'Accept-Language': 'fr-fr',
    'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Keep-Alive': '300',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}

class browser:

    def __init__(self):
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    def _request(self, url):
        request = urllib2.Request(url, None, headers)
        return request

    def post(self, url, data):
        data = urllib.urlencode(data)
        resp = self.opener.open(self._request(url), data)
        return resp.read()

    def get(self, url):
        resp = self.opener.open(self._request(url))
        return resp.read()
