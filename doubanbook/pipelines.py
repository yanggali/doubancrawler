# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import log
from scrapy import signals
from twisted.enterprise import adbapi
from doubanbook.settings import *
import json
import codecs
from hashlib import md5
import MySQLdb
import MySQLdb.cursors

class DoubanbookPipeline(object):
	def __init__(self, dbpool):
		self.dbpool = dbpool
	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=MYSQL_HOST,
			db=MYSQL_DBNAME,
			user=MYSQL_USER,
			passwd=MYSQL_PASSWD,
			charset='utf8',
			cursorclass = MySQLdb.cursors.DictCursor,
			use_unicode= True,
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)
    #pipeline默认调用
	def process_item(self, item, spider):
		d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
		d.addErrback(self._handle_error)
		return item
    #将每行更新或写入数据库中
	def _do_upinsert(self, conn, item, spider):
		isbn = self._get_bookISBN(item)
		conn.execute("""
				select 1 from bookdetail where isbn = %s
			""", (isbn, ))
		ret = conn.fetchone()
		if ret:
			conn.execute("""UPDATE bookdetail SET
                subject=%s,title = %s,author = %s,isbn = %s,press = %s,price = %s,url = %s,rate = %s,description = %s,
                	tags = %s,ratepeople = %s where isbn = %s""",
                	(item['subject'],item['title'],item['author'],item['ISBN'],item['press'],
                    item['price'],item['url'],item['rate'],item['description'],
                    item['tags'],item['ratepeople'],isbn))
		else:
			conn.execute("""INSERT INTO bookdetail
                (subject,title,author,isbn,press,price,url,rate,description,
                	tags,ratepeople)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                 """,(item['subject'],item['title'],item['author'],item['ISBN'],item['press'],
                    item['price'],item['url'],item['rate'],item['description'],
                    item['tags'],item['ratepeople']))
    #获取注册编码
	def _get_bookISBN(self, item):
        #url进行md5处理，为避免重复采集设计
		return item['ISBN']
    #异常处理
	def _handle_error(self,e):
		log.err(e)

#将评论信息保存至数据库
class BookcommentPipeline(object):
	def __init__(self, dbpool):
		self.dbpool = dbpool
	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=MYSQL_HOST,
			db=MYSQL_DBNAME,
			user=MYSQL_USER,
			passwd=MYSQL_PASSWD,
			charset='utf8',
			cursorclass = MySQLdb.cursors.DictCursor,
			use_unicode= True,
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)
    #pipeline默认调用
	def process_item(self, item, spider):
		d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
		d.addErrback(self._handle_error)
		return item
    #将每行更新或写入数据库中
	def _do_upinsert(self, conn, item, spider):
		bookname = self._get_bookname(item)
		userid = self._get_userid(item)
		conn.execute("""
				select 1 from bookcomments where bookname = %s and userid = %s
			""", (bookname, userid,))
		ret = conn.fetchone()
		if ret:
			pass
		else:
			conn.execute("""INSERT INTO bookcomments
                (bookisbn,booksubject,bookname,userid,stars,comment,commenttime,support)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                 """,(item['bookisbn'],item['booksubject'],item['bookname'],item['userid'],item['stars'],item['comment'],
                    item['commenttime'],item['support']))
    #获取书名
	def _get_bookname(self, item):
        #url进行md5处理，为避免重复采集设计
		return item['bookname']
	#获取用户名
	def _get_userid(self, item):
        #url进行md5处理，为避免重复采集设计
		return item['userid']
    #异常处理
	def _handle_error(self,e):
		log.err(e)
