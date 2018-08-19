# -*- coding: utf-8 -*-
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request

class PhpbbSpider(scrapy.Spider):
    
    name = 'phpBB'
    allowed_domains = ['']
    start_urls = ['']
    username = ''
    password = ''
    form_login = False
    
    def parse(self, response):
        #LOGIN TO PHPBB BOARD AND CALL AFTER_LOGIN
        if self.form_login:
            formdata = {'username':self.username,'password':self.password}
            form_request = [scrapy.FormRequest.from_response(response,
                                                            formdata=formdata,
                                                            callback=self.after_login,
                                                            dont_click=True)]
            return form_request
        else:
            #REQUEST SUB-FORUM TITLE LINKS
            links = response.xpath('//a[@class="forumtitle"]/@href').extract()
            for link in links:
                yield scrapy.Request(response.urljoin(link),callback=self.parse_topics)

    def after_login(self, response):
        #CHECK LOGIN SUCCESS BEFORE MAKING REQUESTS
        if b'authentication failed' in response.body:
            self.logger.error('Login failed.')
            return
        else:
            #REQUEST SUB-FORUM TITLE LINKS
            links = response.xpath('//a[@class="forumtitle"]/@href').extract()
            for link in links:
                yield scrapy.Request(response.urljoin(link),callback=self.parse_topics)

    def parse_topics(self, response):
        #REQUEST TOPIC TITLE LINKS
        links = response.xpath('//a[@class="topictitle"]/@href').extract()
        for link in links:
            yield scrapy.Request(response.urljoin(link),callback=self.parse_posts)
        
        #IF NEXT PAGE EXISTS, FOLLOW
        Next = response.xpath("//li[@class='next']//a[@rel='next']/@href").extract_first()
        if Next:
            yield scrapy.Request(response.urljoin(Next),callback=self.parse_topics)   
    
    def clean_quote(self, string):
        #CLEAN HTML TAGS FROM POST TEXT, MARK QUOTES
        soup = BeautifulSoup(string,'lxml')
        blockQuotes = soup.find_all('blockquote')
        for i, quote in enumerate(blockQuotes):
            blockQuotes[i] = '<quote-%s>=' + str(i) + quote.get_text()
        text = ''.join(blockQuotes)
        return text
    
    def clean_text(self, string):
        #CLEAN HTML TAGS FROM POST TEXT, MARK REPLIES TO QUOTES
        tags = ['blockquote']
        soup = BeautifulSoup(string,'lxml')
        for tag in tags:
            for i, item in enumerate(soup.find_all(tag)):
                item.replaceWith('<reply-%s>=' + str(i))
        text = re.sub(' +',' ',soup.get_text())
        return text
      
    def parse_posts(self, response):
        #COLLECT FORUM POST DATA
        usernames = response.xpath('//p[@class="author"]//a[@class="username"]//text()').extract()
        postCounts = response.xpath('//dd[@class="profile-posts"]//a/text()').extract()
        postTimes = response.xpath('//p[@class="author"]/text()').extract()
        postTexts = response.xpath('//div[@class="postbody"]//div[@class="content"]').extract()
        postQuotes = [self.clean_quote(s) for s in postTexts]
        postTexts = [self.clean_text(s) for s in postTexts]

        #YIELD POST DATA
        for i in range(len(usernames)):
            yield {'User':usernames[i],'Count':postCounts[i],
                   'Time':postTimes[i],'Post Text':postTexts[i],'Quote Text':postQuotes[i]}
        
        #CLICK THROUGH NEXT PAGE
        Next = response.xpath("//li[@class='next']//a[@rel='next']/@href").extract_first()
        if Next:
            yield scrapy.Request(response.urljoin(Next),callback=self.parse_posts)