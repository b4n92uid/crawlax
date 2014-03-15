
import time
import sys
import re
import os

import browser

import lxml.html

import hashlib
import logging
import json
import imp

class CrawlingCountReach(BaseException):
  def __init__(self):
    super(CrawlingCountReach, self).__init__()

class Crawler():

  def __init__(self, scriptfile):

    logging.basicConfig(
      format='%(asctime)s - %(levelname)s : %(message)s',
      datefmt='%m/%d/%Y %I:%M:%S',
      level=logging.INFO
    )

    self.scriptfile = scriptfile

    with open(self.scriptfile) as f:
      content = f.read()
      content = re.sub(r'/\*(.|\n)+\*/', r'\n', content)
      content = re.sub(r'//[^\n]+', r'\n', content)

      self.script = json.loads(content)

    self.browser = browser.browser()
    self.baseurl = dict()
    self.args = dict()
    self.handlers = dict()
    self.plugins = dict()
    self.hashtable = list()

    self.printonly = False
    self.extractcount = -1
    self.loglevel = logging.INFO
    self.cache = True
    self.offset = None

  def __del__(self):
    if self.cache:
      with open(self.cachefile, 'w+') as f:
        json.dump(self.hashtable, f)

  def _initUrl(self):

    if type(self.script['base']) is dict:
      host = self.script['base']['host']
      path = self.script['base']['path']

      query = self.script['base']['query']
      params = []

      for k, v in query.items():

        for ak,av in self.args.items():
          v = v.replace('{%s}'%ak, av)

        params.append(k+'='+v)

      self.baseurl['host'] = host.rstrip('/')
      self.baseurl['index'] = '/' + path.lstrip('/') + '?' + '&'.join(params)

    else:
      self.baseurl['host'] = self.script['base'].rstrip('/')
      self.baseurl['index'] = '/'

  def _initCache(self):

    if not self.cache:
      return

    root, ext = os.path.splitext(self.scriptfile)
    self.cachefile = root + '.cache'

    if os.path.exists(self.cachefile):
      with open(self.cachefile) as f:
        self.hashtable = json.load(f)

  def _login(self):

    if 'login' in self.script :
      logging.info('login process...')

      self.browser.post(
        self.baseurl['host'] + self.script['login']['action'],
        self.script['login']['post']
      )

  def _extract(self, extract, fragment):

    logging.info('extracting...')

    data = dict()

    for k, v in extract['data'].items():

      selector, attr, pattern, plugin, datatype, dataformat = None, None, None, None, None, None

      if type(v) is dict:
        selector = v['selector']
        attr = v['attr'] if 'attr' in v else None
        pattern = v['pattern'] if 'pattern' in v else None
        plugin  = v['plugin'] if 'plugin' in v else None
        datatype  = v['datatype'] if 'datatype' in v else 'raw'
        dataformat  = v['dataformat'] if 'dataformat' in v else None

      else:
        selector = v
        datatype = 'raw'

      elems = fragment.cssselect(selector)

      if not elems:
        logging.warning('elems `%s` not found', selector)
        continue

      dataValues = list()

      for elem in elems:

        value = elem.get(attr) if attr else elem.text_content()

        if value == None:
          continue

        # Pattern match
        matches = None

        if pattern:
          matches = re.search(pattern, value)

          if not matches:
            logging.warning('pattern mimatch `%s` `%s`', selector, pattern)
            continue

        # Data format
        if dataformat:

          value = dataformat.replace('{value}', value)

          if matches:
            try:
              value = dataformat.format(*matches.groups())
            except IndexError as e:
              logging.warning('%s', e)

        # Plugin execution
        if plugin:

          plugin['args'] = map(lambda a: a.replace('{value}', value), plugin['args'])

          if matches :
            plugin['args'] = map(lambda a: a.format(*matches.groups()), plugin['args'])

          pluginInstance = self.plugins[plugin['id']]()

          value = pluginInstance.execute(*plugin['args'])

          if not value:
            continue

        dataValues.append(value.strip())

      if datatype == 'json':
        data[k] = json.dumps(dataValues)
      else:
        data[k] = " ".join(dataValues)

    # Handling data

    if self.printonly:
      print json.dumps(data, sort_keys=True, indent=2, separators=('', ':'))
      return True

    else:
      try:
        handler = self.handlers[extract['handler']](*extract['params'])
        result = handler.dump(data)

        if not result:
          logging.warning('unable to dump data, handler return false')

      except TypeError as e:
        logging.error('Handle error: %s', e)
        return False

      return result

  def _crawl(self, process, fragment):

    selector = process['selector']
    document =  process['document']

    done = False

    while not done:

      logging.info('crwaling `%s`', process['id'])
      logging.debug('foreach `%s`', selector)

      extractionDone = 0
      extractionSkip = 0

      for elem in fragment.cssselect(selector) :

        if self.offset:
          if process['id'] == self.offset['id'] and self.offset['count'] > 0:
            logging.info('skiped element %d', self.offset['count'])
            self.offset['count'] -= 1
            continue

        elemhash = None

        # Cache handle
        if self.cache:

          if 'hash' in process:
            if process['hash'] == '@text':
              hashdata =  elem.text_content().encode('utf-8')
            else:
              hashdata =  elem.get(process['hash'])

            if hashdata:
              elemhash = hashlib.sha1(hashdata).hexdigest()

          if elemhash in self.hashtable:
            logging.info('skiped')
            extractionSkip += 1
            continue

        # Root document is page
        if document == 'page':
          attr =  process['attr'] if 'attr' in process else None
          target = elem.get(attr) if attr else elem.text_content()

          if target :

            target_html = self.browser.get(target)

            dom = lxml.html.fromstring(target_html)
            dom.make_links_absolute(self.baseurl['host'])

            extractionDone += self._process(process, dom)

          else:
            logging.warning('attribute `%s` not found', attr)

        # Root document is element
        elif document == 'elem':
          extractionDone += self._process(process, elem)

        # Append to hashtable for caching
        if self.cache:
          self.hashtable.append(elemhash)

      logging.info('end crwaling %s (%d done, %d skiped)',
        process['id'],
        extractionDone,
        extractionSkip
      )

      if 'pagination' in process:

        pagination = process['pagination']

        selector = pagination['selector'];
        attr = pagination['attr'];

        for elem in fragment.cssselect(selector):

          target = elem.get(attr)

          if target:

            if 'pattern' in pagination and re.match(pagination['pattern'], target) or True:

              target_html = self.browser.get(target)

              fragment = lxml.html.fromstring(target_html)
              fragment.make_links_absolute(self.baseurl['host'])
              continue

      done = True

  def _process(self, process, fragment):

    if 'extract' in process:
      result = self._extract(process['extract'], fragment)

      if result:
        self.extractcount -= 1

      if self.extractcount == 0:
        raise CrawlingCountReach()

      return result

    elif 'crawl' in process:
      return self._crawl(process['crawl'], fragment)

    else:
      logging.warning('no action for processing')

    return False

  def setPrintOnly(self, var):
    self.printonly = var

  def setExtractCount(self, var):
    self.extractcount = var

  def setLogLevel(self, var):
    self.loglevel = var

    level = {
      'DEBUG': logging.DEBUG,
      'INFO': logging.INFO,
      'WARNING': logging.WARNING,
      'ERROR': logging.ERROR
    }

    logging.getLogger().setLevel(level[var])

  def setCacheEnabled(self, var):
    self.cache = var

  def setOffset(self, id, count):
    self.offset = {
      'id': id,
      'count': int(count),
    }

  def setArg(self, arg, value):
    self.args[arg] = value

  def getRequiredArgs(self):
    if 'args' in self.script:
      return self.script['args']
    else:
      return []

  def registerPlugin(self, filename):
    base, ext = os.path.splitext(filename)
    module = imp.load_source(base, filename)
    id, instance = module.get()
    self.plugins[id] = instance
    logging.debug('Plugin `%s` registred !', id)

  def registerHandler(self, filename):
    base, ext = os.path.splitext(filename)
    module = imp.load_source(base, filename)
    id, instance = module.get()
    self.handlers[id] = instance
    logging.debug('Handler `%s` registred !', id)

  def start(self):

    self._initUrl()
    self._initCache()

    logging.info('Crawling <%s>', self.baseurl['host'])

    try:
      self._login()

      html = self.browser.get(self.baseurl['host'] + self.baseurl['index'])

      dom = lxml.html.fromstring(html)
      dom.make_links_absolute(self.baseurl['host'])

      self._process(self.script, dom)
      logging.info('all crawling is done !')

    except CrawlingCountReach as e:
      logging.info('max crawling count reach !')

