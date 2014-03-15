
import os
import re
import sys

import urllib
import urllib2

class OcrImg():

  def execute(self, url):

    try:

      response = urllib2.urlopen(url)

      with open('info.png', 'wb+') as f:
        f.write(response.read())

      location = os.path.dirname(sys.argv[0])

      cmd = '"{0}" info.png -resize 400% -unsharp 100 info.png > nul'
      cmd = cmd.format(os.path.join(location, 'plugins\\tools\\convert.exe'))
      os.system(cmd)

      cmd = '"{0}" info.png info > nul'
      cmd = cmd.format(os.path.join(location, 'plugins\\tools\\tesseract-ocr\\tesseract.exe'))
      os.system(cmd)

      with open("info.txt", "r") as f:
        info = f.read().strip()

    except IOError as e:
      print "/!\\", url, e
      return False

    except ValueError as e:
      print "/!\\", url, e
      return False

    except urllib2.HTTPError as e:
      print "/!\\", url, e.code, e.reason
      return False

    except urllib2.URLError as e:
      print "/!\\", url, e.reason
      return False

    finally:
      if os.path.exists('info.png'): os.remove('info.png')
      if os.path.exists('info.txt'): os.remove('info.txt')

    return info.strip().replace(' ', '')

def get():
  return "ocr", OcrImg
