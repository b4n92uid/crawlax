
# CRAWLAX
Powerful tool for Crawling And eXtracting data from web page

## Usage

```shell
usage: crawlax.py [-h] [-c COUNT] [-p] [-n] [-o OFFSET OFFSET]
                  [-l {DEBUG,INFO,WARNING,ERROR}]
                  crawlfile ...

Powerful tool for crawling and extraction data from web page

positional arguments:
  crawlfile             crawl file to describe crawling process
  args                  argument required for crawl process

optional arguments:
  -h, --help
      show this help message and exit

  -c COUNT, --count COUNT
      max extraction count

  -p, --print-only
      data will be printed only not dumped into handler

  -n, --no-cache
      do not cache extracted elem

  -o OFFSET OFFSET, --offset OFFSET OFFSET
      offset crawling from start

  -l {DEBUG,INFO,WARNING,ERROR}, --log {DEBUG,INFO,WARNING,ERROR}
      minimum log level
```

## Example of a crawling descriptor file

```json
{
  "base": "http:\/\/www.website.com",

  "crawl": {
    "id": "category",
    "selector": "#categories .category-links a:first-child",
    "attr": "href",
    "document": "page",

    "crawl": {
      "id": "products",
      "selector": "a.product_link",
      "attr": "href",
      "document": "page",
      "hash": "href",

      "extract": {
        "handler": "sqlite",
        "params": [
          "products.sqlite",
          "products",
          {
            "ref":"INTEGER", "title":"TEXT", "date":"DATETIME", "category":"TEXT",
            "description":"TEXT", "location":"TEXT", "phone":"TEXT", "email":"TEXT",
            "author":"TEXT", "photos":"TEXT"
          }
        ],

        "data":{
          "ref": {
            "selector": "#menu > div > span.idall",
            "pattern":"(\\d+)$",
            "dataformat": "{0}"
          },
          "title": "#Title",
          "date": {
            "selector": "#menu > div > span.date-depot",
            "pattern":"([0-9]{2})-([0-9]{2})-([0-9]{4}) à ([0-9:]+)",
            "dataformat": "{2}-{1}-{0} {3}"
          },
          "category": "#Catégorie > span",
          "description": "#GetDescription",
          "location": "#Annonceur p.Adresse",
          "phone": {
            "selector": "#Annonceur p.Phone > img",
            "attr": "src",
            "plugin": {"id":"ocr", "args":["{value}"]}
          },
          "email": {
            "selector": "#Annonceur p.Email > img",
            "attr": "src",
            "plugin": {"id":"ocr", "args":["{value}"]}
          },
          "author": "#store_name, #Annonceur p.Pseudo > a",
          "photo": {
            "selector":"#gallery > a",
            "attr":"href",
            "datatype":"json"
          }
        }
      },

      "pagination": {
        "selector": "#divPages > a.page_arrow",
        "attr": "href"
      }
    }
  }
}
```

### the `base` key

### the `login` key

### the `args` key

### the `crawl` instruction

  *  `id`
  *  `selector`
  *  `attr`
  *  `document`
  *  `hash`
  *  `pagination`

### the `extract` instruction

  * `handler`
  * `params`
  * `data`
