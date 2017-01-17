# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
#保存图书链接
class BookLink(scrapy.Item):
	link = scrapy.Field()
		
class DoubanItem(scrapy.Item):
    """ 定义需要抓取的字段名 """
    subject = scrapy.Field()                    # 书id
    title = scrapy.Field()                      # 书名
    author = scrapy.Field()                     # 作者
    ISBN = scrapy.Field()                       # ISBN号
    press = scrapy.Field()                      # 出版社
    price = scrapy.Field()                      # 价格
    url = scrapy.Field()                        # 链接
    rate = scrapy.Field()                       # 读者评分
    authordesc = scrapy.Field()                 # 作者简介
    description = scrapy.Field()                # 内容简介
    tags = scrapy.Field()                       # 详情页链接
    ratepeople = scrapy.Field()                 # 评价人数

#评论信息
class Comment(scrapy.Item):
	booksubject = scrapy.Field()   #书本id
	bookname = scrapy.Field()      #书本名称
	bookisbn = scrapy.Field()      #书本isbn
	userid = scrapy.Field()        #用户id
	stars = scrapy.Field()         #打星
	comment = scrapy.Field()       #评论
	commenttime = scrapy.Field()          #评论时间
	support = scrapy.Field()       #支持数
