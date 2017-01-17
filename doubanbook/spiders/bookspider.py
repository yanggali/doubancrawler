# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from doubanbook.items import DoubanItem,BookLink,Comment
from scrapy.http import Request,FormRequest
from scrapy.selector import HtmlXPathSelector
from doubanbook.settings import *
import json
import codecs
import re
#爬取书本页面详细信息
class BooksSpider(CrawlSpider):
    name = "books"
    allowed_domains = ["book.douban.com"]
    def __init__(self):
      #从文件中获取初始的url
        with codecs.open('link.data','r') as ffile:
            count = 0
            while 1:
                lines = ffile.readlines(200000)
                if not lines:
                    break
                for line in lines:
                    try:
                        line = line.strip()
                        self.start_urls.append(line)
                    except:
                        pass
            self.logger.info('url read successfully!')
    rules = (
        # 列表页url
        Rule(LinkExtractor(allow=(r"https://book.douban.com/top250\?start=\d+"))),
        # 详情页url
        Rule(LinkExtractor(allow=(r"https://book.douban.com/subject/\d+")), callback="books_parse")
    )
    def Cookies_Get(self):
        with codecs.open(Cookies_PATH,'r') as fd:
            data = fd.readlines()
            fd.close()
            length = len(data)
            if self.Cookies_Index >= length:
                self.Cookies_Index = 0
            item = data[self.Cookies_Index]
            cookie = item.strip().split(';')
            dict = {}
            for f in cookie:
                ff = f.strip().split('=')
                # print ff[0],ff[1]
                dict[ff[0]] = ff[1]
            self.cookies = dict
        self.Cookies_Index = self.Cookies_Index + 1
    def start_requests(self):
        for url in self.start_urls:
            yield FormRequest(url,\
                      callback=self.books_parse)
    def books_parse(self, response):
        books = []
        sel = Selector(response)
        info = sel.xpath('//li[@class="subject-item"]')
        if len(info) == 0:
            raise CloseSpider('---------------------End Search!---------------')


        f = open('books.data','a')
        for site in info.xpath('div[@class="info"]'):
            book = DoubanItem()
            book['title'] = site.xpath('h2/a/@title').extract()[0].encode('utf-8')
            book['link'] = site.xpath('h2/a/@href').extract()[0].encode('utf-8')
            pub = site.xpath('div[@class="pub"]/text()').extract()[0].encode('utf-8')
            pub = pub.strip().split('/')

            book['author'] = pub[0]
            book['price'] = pub[-1]
            desc = site.xpath('p/text()').extract()
            book['desc'] =  desc[0].encode('utf-8') if (len(desc) != 0) else ''
            print('-----------------lALALALALALA----------------------------------------------')
            print(book['title'])
            print(book['link'])
            print(book['author'])
            print(book['price'])
            print(book['desc'])
            ss = "{'title': '" + book['title'] + "' , " + "'link': '" + book['link'] + "' , " + "'author': '" + book['author'] + "' , " + "'price': '" + book['price'] + "' , " + "'desc': '" + book['desc'] + "'}"
            print ss
            target = json.dumps(ss, ensure_ascii=False)
            print target
            f.write(target+'\n')
            print('-----------------lALALALALALA----------------------------------------------\n\n')
            books.append(book)
            yield book


        f.close()

        site = sel.xpath('//span[@class="next"]/a/@href').extract()[0]
        print('url: ' + response.url)
        print('site: ' + site)
        temp = response.url.split('/')
        new_url = temp[0]
        i = 1
        while i < len(temp)-2:
           new_url += '/' + temp[i]
           i += 1
        new_url += site
        new_url = new_url.encode('utf-8')
        print('url: ' + new_url)
        yield Request(new_url,\
                            callback=self.books_parse)


class BooksUrlSpider(CrawlSpider):
    name = "urls"
    allowed_domains = ["book.douban.com"]
    Cookies_Index = 0
    start_urls = (
        'https://book.douban.com/tag/%E7%A8%8B%E5%BA%8F',
    )
    
    def start_requests(self):
        for url in self.start_urls:
            yield FormRequest(url,\
                      callback=self.links_parse)
    def book_parse(self,response):
        sel = Selector(response)
        bookitem = DoubanItem()
        press = u"出版社:"
        price = u"定价:"
        bookitem['subject'] = re.findall("\d+",response.url)[0]
        if sel.xpath('//*[@id="wrapper"]/h1/span/text()'):
            bookitem['title'] = sel.xpath('//*[@id="wrapper"]/h1/span/text()').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[1]/a/text()'):
            bookitem['author'] = sel.xpath('//*[@id="info"]/span[1]/a/text()').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[1]/a/text()'):
            bookitem['author'] = sel.xpath('//*[@id="info"]/span[1]/a/text()').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[text()="'+press+'"]/following-sibling::text()[1]'):
            bookitem['press'] = sel.xpath('//*[@id="info"]/span[text()="'+press+'"]/following-sibling::text()[1]').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[text()="ISBN:"]/following-sibling::text()[1]'):
            bookitem['ISBN'] = sel.xpath('//*[@id="info"]/span[text()="ISBN:"]/following-sibling::text()[1]').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[text()="'+price+'"]/following-sibling::text()[1]'):
            bookitem['price'] = sel.xpath('//*[@id="info"]/span[text()="'+price+'"]/following-sibling::text()[1]').extract()[0].replace('CNY','').replace(u'元','').\
            replace('HK$','').replace('NT','').replace('$','').replace(u'新台币','').strip()
        else:
            pass
        if sel.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/span/text()'):
            bookitem['ratepeople'] = sel.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/span/text()').extract()[0]
        else:
            pass
        bookitem['url'] = response.url
        bookitem['rate'] = sel.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()').extract()[0]
        description = sel.xpath('//*[@id="link-report"]/div[1]/div')
        if sel.xpath('//*[@id="link-report"]/div/div[@class="intro"]'):
            bookitem['description'] = description[0].xpath('string(.)').extract()[0].strip()
        elif sel.xpath('//*[@id="link-report"]/span[@class="all hidden"]/div/div'):
            temp = sel.xpath('//*[@id="link-report"]/span[@class="all hidden"]/div/div')
            bookitem['description'] = temp[0].xpath('string(.)').extract()[0].strip()
        else:
            pass
        
        # authordesc = sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/div/div[@class="intro"]')
        # if sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/div/div[@class="intro"]'):
        #     bookitem['authordesc'] = authordesc[0].xpath('string(.)').extract()[0]
        # else:
        #     temp = sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/span[@class="all hidden "]/div')
        #     bookitem['authordesc'] = temp[0].xpath('string(.)').extract()[0]
        tags = sel.xpath('//*[@id="db-tags-section"]/div/span/a')
        tagstr=''
        for tag in tags:
            tagstr += tag.xpath('text()').extract()[0]+","
        bookitem['tags'] = tagstr
        return bookitem
    def links_parse(self, response):
        sel = Selector(response)
        info = sel.xpath('//li[@class="subject-item"]')
        if len(info) == 0:
            raise CloseSpider('---------------------End Search!---------------')

        f = open('links.data','a')
        for site in info.xpath('div[2]/h2/a'):
            booklink = BookLink()
            booklink['link'] = site.xpath('@href').extract()[0].encode('utf-8')
            print(booklink['link'])
            f.write(booklink['link']+'\n')
            yield Request(booklink['link'],\
                callback=self.book_parse)


        f.close()

        site = sel.xpath('//span[@class="next"]/a/@href').extract()[0]
        print('url: ' + response.url)
        print('site: ' + site)
        temp = response.url.split('/')
        new_url = temp[0]
        i = 1
        while i < len(temp)-2:
           new_url += '/' + temp[i]
           i += 1
        new_url += site
        new_url = new_url.encode('utf-8')
        print('url: ' + new_url)
        yield Request(new_url,\
                            callback=self.links_parse)

global all_urls
all_urls = []

#根据现有书本找相关书本
class BooksDepthSpider(CrawlSpider):
    name = "deepurls"
    allowed_domains = ["book.douban.com"]
    Cookies_Index = 0
       #保存已爬取的书目链接
    
    count = 0#计数，深度爬取了多少本书
    start_urls = []
    def __init__(self):
      #从文件中获取初始的url
        with codecs.open('deepbookurls.txt','r') as ffile:
            count = 0
            while 1:
                lines = ffile.readlines(200000)
                if not lines:
                    break
                for line in lines:
                    try:
                        line = line.strip()
                        self.start_urls.append(line)
                    except:
                        pass
            self.logger.info('url read successfully!')
    
    def start_requests(self):
        for url in self.start_urls:
            yield FormRequest(url,\
                      callback=self.deep_parse)
    def deep_parse(self,response):        
        global count
        count = 0
        sel = Selector(response)
        all_urls.append(response.url)
        relatedbooks = sel.xpath('//*[@id="db-rec-section"]/div/dl/dd/a')
        for relatedbook in relatedbooks:
            relatedbookurl = relatedbook.xpath('@href').extract()[0]
            if relatedbookurl in all_urls:
                pass
            else:
                print relatedbookurl
                all_urls.append(relatedbookurl)
                count = count+1
                if len(all_urls) < 1000:
                    yield FormRequest(relatedbookurl,\
                                    callback=self.deep_parse)
                else:
                    break
        for url in all_urls:
            yield FormRequest(url,callback=self.deep_detail_parse)
            

    def deep_detail_parse(self,response):
        sel = Selector(response)
        bookitem = DoubanItem()
        press = u"出版社:"
        price = u"定价:"
        bookitem['subject'] = re.findall("\d+",response.url)[0]
        if sel.xpath('//*[@id="wrapper"]/h1/span/text()'):
            bookitem['title'] = sel.xpath('//*[@id="wrapper"]/h1/span/text()').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[1]/a/text()'):
            bookitem['author'] = sel.xpath('//*[@id="info"]/span[1]/a/text()').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[1]/a/text()'):
            bookitem['author'] = sel.xpath('//*[@id="info"]/span[1]/a/text()').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[text()="'+press+'"]/following-sibling::text()[1]'):
            bookitem['press'] = sel.xpath('//*[@id="info"]/span[text()="'+press+'"]/following-sibling::text()[1]').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[text()="ISBN:"]/following-sibling::text()[1]'):
            bookitem['ISBN'] = sel.xpath('//*[@id="info"]/span[text()="ISBN:"]/following-sibling::text()[1]').extract()[0].strip()
        else:
            pass
        if sel.xpath('//*[@id="info"]/span[text()="'+price+'"]/following-sibling::text()[1]'):
            bookitem['price'] = sel.xpath('//*[@id="info"]/span[text()="'+price+'"]/following-sibling::text()[1]').extract()[0].replace('CNY','').replace(u'元','').replace('HK$','').strip()
        else:
            pass
        if sel.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/span/text()'):
            bookitem['ratepeople'] = sel.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/span/text()').extract()[0].strip()
        else:
            pass
        bookitem['url'] = response.url
        bookitem['rate'] = sel.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()').extract()[0]
        description = sel.xpath('//*[@id="link-report"]/div[1]/div')
        if sel.xpath('//*[@id="link-report"]/div/div[@class="intro"]'):
            bookitem['description'] = description[0].xpath('string(.)').extract()[0].strip()
        elif sel.xpath('//*[@id="link-report"]/span[@class="all hidden"]/div/div'):
            temp = sel.xpath('//*[@id="link-report"]/span[@class="all hidden"]/div/div')
            bookitem['description'] = temp[0].xpath('string(.)').extract()[0].strip()
        else:
            pass
        
        # authordesc = sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/div/div[@class="intro"]')
        # if sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/div/div[@class="intro"]'):
        #     bookitem['authordesc'] = authordesc[0].xpath('string(.)').extract()[0]
        # else:
        #     temp = sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/span[@class="all hidden "]/div')
        #     bookitem['authordesc'] = temp[0].xpath('string(.)').extract()[0]
        tags = sel.xpath('//*[@id="db-tags-section"]/div/span/a')
        tagstr=''
        for tag in tags:
            tagstr += tag.xpath('text()').extract()[0]+","
        bookitem['tags'] = tagstr
        return bookitem
        

#爬取书本页面详细信息
class BooksDetailSpider(CrawlSpider):
    name = "detail"
    allowed_domains = ["book.douban.com"]
    Cookies_Index = 0
    start_urls = []
    def __init__(self):
      #从文件中获取初始的url
        with codecs.open('details.txt','r') as ffile:
            count = 0
            while 1:
                lines = ffile.readlines(200000)
                if not lines:
                    break
                for line in lines:
                    try:
                        line = line.strip()
                        self.start_urls.append(line)
                    except:
                        pass
            self.logger.info('url read successfully!')
    
    def start_requests(self):
        for url in self.start_urls:
            yield FormRequest(url,\

                      callback=self.detail_parse)
    def detail_parse(self,response):
        sel = Selector(response)
        bookitem = DoubanItem()
        press = u"出版社:"
        price = u"定价:"
        bookitem['subject'] = re.findall("\d+",response.url)[0]
        print bookitem['subject']
        if sel.xpath('//*[@id="wrapper"]/h1/span/text()'):
            bookitem['title'] = sel.xpath('//*[@id="wrapper"]/h1/span/text()').extract()[0].strip()
        else:
            bookitem['title'] = 'null'
        print bookitem['title']
        if sel.xpath('//*[@id="info"]/span[1]/a/text()'):
            bookitem['author'] = sel.xpath('//*[@id="info"]/span[1]/a/text()').extract()[0].strip()
        else:
            bookitem['author'] = 'null'
        print bookitem['author']
        if sel.xpath('//*[@id="info"]/span[text()="'+press+'"]/following-sibling::text()[1]'):
            bookitem['press'] = sel.xpath('//*[@id="info"]/span[text()="'+press+'"]/following-sibling::text()[1]').extract()[0].strip()
        else:
            bookitem['press'] = 'null'
        print bookitem['press']
        if sel.xpath('//*[@id="info"]/span[text()="ISBN:"]/following-sibling::text()[1]'):
            bookitem['ISBN'] = sel.xpath('//*[@id="info"]/span[text()="ISBN:"]/following-sibling::text()[1]').extract()[0].strip()
        else:
            pass
        print bookitem['ISBN']
        if sel.xpath('//*[@id="info"]/span[text()="'+price+'"]/following-sibling::text()[1]'):
            bookitem['price'] = sel.xpath('//*[@id="info"]/span[text()="'+price+'"]/following-sibling::text()[1]').extract()[0].replace('CNY','').replace(u'元','').replace('HK$','').strip()
        else:
            bookitem['price'] = 'null'
        print bookitem['price']
        if sel.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/span/text()'):
            bookitem['ratepeople'] = sel.xpath('//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/span/text()').extract()[0].strip()
        else:
            bookitem['ratepeople'] = 'null'
        print bookitem['ratepeople']
        bookitem['url'] = response.url
        if sel.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()'):
            bookitem['rate'] = sel.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()').extract()[0]
        else:
            bookitem['rate'] = 'null'
        print bookitem['rate']
        description = sel.xpath('//*[@id="link-report"]/div[1]/div')
        if sel.xpath('//*[@id="link-report"]/div/div[@class="intro"]'):
            bookitem['description'] = description[0].xpath('string(.)').extract()[0].strip()
        elif sel.xpath('//*[@id="link-report"]/span[@class="all hidden"]/div/div'):
            temp = sel.xpath('//*[@id="link-report"]/span[@class="all hidden"]/div/div')
            bookitem['description'] = temp[0].xpath('string(.)').extract()[0].strip()
        else:
            bookitem['description'] = 'null'
        print bookitem['description']
        # authordesc = sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/div/div[@class="intro"]')
        # if sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/div/div[@class="intro"]'):
        #     bookitem['authordesc'] = authordesc[0].xpath('string(.)').extract()[0]
        # else:
        #     temp = sel.xpath('//*[@id="link-report"]/following-sibling::div[@class="indent"]/span[@class="all hidden "]/div')
        #     bookitem['authordesc'] = temp[0].xpath('string(.)').extract()[0]
        tags = sel.xpath('//*[@id="db-tags-section"]/div/span/a')
        tagstr=''
        for tag in tags:
            tagstr += tag.xpath('text()').extract()[0]+","
        if tagstr:
            bookitem['tags'] = tagstr
        else:
            bookitem['tags'] = 'null'
        print bookitem['tags']
        return bookitem


#爬取书本评论信息
class BooksCommentsSpider(CrawlSpider):
    name = "bookcomments"
    allowed_domains = ["book.douban.com"]
    Cookies_Index = 0
    start_urls = []
    def __init__(self):
      #从文件中获取初始的url
        with codecs.open('bookurls.txt','r') as ffile:
            count = 0
            while 1:
                lines = ffile.readlines(200000)
                if not lines:
                    break
                for line in lines:
                    try:
                        line = line.strip()
                        self.start_urls.append(line)
                    except:
                        pass
            self.logger.info('url read successfully!')
    
    def start_requests(self):
        for url in self.start_urls:
            yield FormRequest(url,\
                      callback=self.goto_comments_parse)
    def goto_comments_parse(self,response):
        sel = Selector(response)
        if sel.xpath('//*[@id="info"]/span[text()="ISBN:"]/following-sibling::text()[1]'):
            bookisbn = sel.xpath('//*[@id="info"]/span[text()="ISBN:"]/following-sibling::text()[1]').extract()[0].strip()
        else:
            bookisbn = "null"
        comment_page = response.url+"comments/"
        yield FormRequest(comment_page,callback=lambda response,temp=bookisbn:self.comments_parse(response,temp))

    def comments_parse(self,response,temp):
        sel = Selector(response)
        bookisbn = temp
        booksubject = re.findall("\d+",response.url)[0]
        commentlist = sel.xpath('//*[@id="comments"]/ul/li/div[@class="comment"]')
        for one in commentlist:
            comment = Comment()
            comment['booksubject'] = booksubject
            comment['bookisbn'] = temp
            if sel.xpath('//*[@id="content"]/h1/text()'):
                comment['bookname'] = sel.xpath('//*[@id="content"]/h1/text()').extract()[0].replace(u'短评','').strip()
            else:
                comment['bookname'] = re.findall("\d+",response.url)
            pattern = re.compile("people/(.*)")
            #//*[@id="comments"]/ul/li[1]/div[2]/h3/span[2]/a
            userurl = one.xpath('h3/span[2]/a/@href').extract()[0]
            res = pattern.search(userurl).groups()
            comment['userid'] = res[0].replace('/','')
            if one.xpath('h3/span[@class="comment-info"]/span[2]'):
                comment['stars'] = re.findall("\d+",one.xpath('h3/span[@class="comment-info"]/span[1]/@class').extract()[0])[0]
                comment['commenttime'] = one.xpath('h3/span[@class="comment-info"]/span[2]/text()').extract()[0]
            else:
                comment['stars'] = "null"
                comment['commenttime'] = one.xpath('h3/span[@class="comment-info"]/span/text()').extract()[0]
            comment['comment'] = one.xpath('p[@class="comment-content"]/text()').extract()[0].strip()
            comment['support'] = one.xpath('h3/span[@class="comment-vote"]/span[@class="vote-count"]/text()').extract()[0]
            yield comment
        if sel.xpath('//div[@class="paginator-wrapper"]/ul/li[3]/a'):
            next_page = 'https://book.douban.com/subject/'+booksubject+'/comments/'+sel.xpath('//div[@class="paginator-wrapper"]/ul/li[3]/a/@href').extract()[0]
            print next_page
            yield Request(next_page,callback=lambda response,temp=bookisbn:self.comments_parse(response,temp))
        else:
            return
