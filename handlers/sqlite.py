

import os
import sqlite3

class SqliteHandler():

  def __init__(self, filename, table, columns):

    initdb = os.path.exists(filename) == False

    self.database = sqlite3.connect(filename)
    self.table = table
    self.columns = columns

    if initdb:
      sql = 'CREATE TABLE IF NOT EXISTS %s(id INTEGER NOT NULL PRIMARY KEY DEFAULT "0", %s)'
      sql = sql % (self.table, ', '.join(['%s %s' % (k, v) for k, v in self.columns.items()]))

      cursor = self.database.cursor()
      cursor.execute(sql)
      self.database.commit()

  def buildSQL(self, data):
    holder = ['?' for i in range(len(data))]

    sql = 'INSERT into %s(%s) VALUES(%s)'
    sql = sql % (self.table, ', '.join(data.keys()), ', '.join(holder))

    return sql

  def dump(self, data):
    cursor = self.database.cursor()
    try:
      cursor.execute(self.buildSQL(data), data.values())
      self.database.commit()
      return True

    except sqlite3.Error as e:
      print e,
      return False

def get():
  return "sqlite", SqliteHandler
