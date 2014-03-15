
import argparse
import crawler
import signal
import glob
import sys
import os
import re

print
print ' CRAWLAX (c) 2014 b4n92uid '.center(56, '-')
print '''

                       .--.  .--.
                      /    \/    \\
                     /   .-.  .-. |
                    /   |  _\|  _\|
              .----'    |/` ||/` ||
            _/    ,--    \_0/ \_0/|
         .-'     / `)              \       .-""""""--.
        /          /              .-'-----/           \\
       /          /`\                          () ()  /
      /          |   '-.___.                          |
     ;           \      |/ `\                         /
    /             |.---.`.-. '.___              ___.-'
  /'              |     \   \ \ |/`'-.,____..-``|/
                  \  ,   \   \ \`,       |/     `
                   \/|    \   \ /|       `
                    \/     `   ;-`'.   ,
 jgs                 `'-.   ,   '.  '-/|    ,
                         './|     '-. ``;--/|-.
                           '`'--.,___) /|.-'"` )
                      '--._          `"`    .-'
                         .-`'-._          .'
                       .'       ``''---''`

'''
print ''.center(56, '-')
print

parser = argparse.ArgumentParser(description='Powerful tool for crawling and extraction data from web page')
parser.add_argument('-c', '--count', type=int, help='max extraction count')
parser.add_argument('-p', '--print-only', action='store_true', help='data will be printed only not dumped into handler')
parser.add_argument('-n', '--no-cache', action='store_true', help='do not cache extracted elem')
parser.add_argument('-o', '--offset', nargs=2, help='offset crawling from start')
parser.add_argument('-l', '--log', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='minimum log level')
parser.add_argument('crawlfile', help='crawl file to describe crawling process')
parser.add_argument('args', nargs=argparse.REMAINDER, help='argument required for crawl process')

params = parser.parse_args()

# SIGINT Handle
def signal_handler(signum, frame):
  res = raw_input("Would you like to interrupte crawling (y/n) ? ")

  if res[0].lower() == 'y':
    print 'Crawling interrupted !'
    quit(0)

signal.signal(signal.SIGINT, signal_handler)

# App init
app = crawler.Crawler(params.crawlfile)

app.setPrintOnly(params.print_only)
app.setExtractCount(params.extract_cout)
app.setLogLevel(params.log)
app.setCacheEnabled(not params.no_cache)
app.setOffset(params.offset[0], params.offset[1])

# Plugin and Handler loading
location = os.path.dirname(sys.argv[0])

for files in glob.glob(os.path.join(location, 'plugins/*.py')):
  app.registerPlugin(files)

for files in glob.glob(os.path.join(location, 'handlers/*.py')):
  app.registerHandler(files)

# Prompt for required args
crawler_args = app.getRequiredArgs()

for i, arg in enumerate(crawler_args):

  if i < len(params.args):
    value = params.args[i]
    print '> value for {0} : {1}'.format(arg, value)
  else:
    value = raw_input('Enter value for {0} : '.format(arg))

  app.setArg(arg, value)

# Start Crawling
app.start()
