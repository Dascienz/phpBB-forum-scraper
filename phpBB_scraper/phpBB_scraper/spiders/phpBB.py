# -*- coding: utf-8 -*-
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request

class PhpbbSpider(scrapy.Spider):
    
    name = 'phpBB'
    #Domain only, no urls
    allowed_domains = ['']
    start_urls = ['']
    username = ''
    password = ''
    # False if you dont need to login, true if you do.
    form_login = False
    
    def parse(self, response):
        # LOGIN TO PHPBB BOARD AND CALL AFTER_LOGIN
        if self.form_login:
            formdata = {'username': self.username, 
                        'password': self.password}
            form_request = [scrapy.FormRequest.from_response(response,
                                                             formdata=formdata,
                                                             callback=self.after_login,
                                                             dont_click=True)]
            yield form_request
            return
        else:
            # REQUEST SUB-FORUM TITLE LINKS
            links = response.xpath('//a[@class="forumtitle"]/@href').extract()
            for link in links:
                yield scrapy.Request(response.urljoin(link), callback=self.parse_topics)

    def after_login(self, response):
        # CHECK LOGIN SUCCESS BEFORE MAKING REQUESTS
        if b'authentication failed' in response.body:
            self.logger.error('Login failed.')
            return
        else:
            # REQUEST SUB-FORUM TITLE LINKS
            links = response.xpath('//a[@class="forumtitle"]/@href').extract()
            for link in links:
                yield scrapy.Request(response.urljoin(link), callback=self.parse_topics)

    def parse_topics(self, response):
        # REQUEST TOPIC TITLE LINKS
        links = response.xpath('//a[@class="topictitle"]/@href').extract()
        for link in links:
            yield scrapy.Request(response.urljoin(link), callback=self.parse_posts)
        
        # IF NEXT PAGE EXISTS, FOLLOW
        next_link = response.xpath('//li[@class="next"]//a[@rel="next"]/@href').extract_first()
        if next_link:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_topics)   
    
    def clean_quote(self, string):
        # CLEAN HTML TAGS FROM POST TEXT, MARK QUOTES
        soup = BeautifulSoup(string, 'lxml')
        block_quotes = soup.find_all('blockquote')
        for i, quote in enumerate(block_quotes):
            block_quotes[i] = '<quote-%s>='%str(i+1) + quote.get_text()
        return ''.join(block_quotes)
    
    def clean_text(self, string):
        # CLEAN HTML TAGS FROM POST TEXT, MARK REPLIES TO QUOTES
        tags = ['blockquote']
        soup = BeautifulSoup(string, 'lxml')
        for tag in tags:
            for i, item in enumerate(soup.find_all(tag)):
                item.replaceWith('<reply-%s>='%str(i+1))
        return re.sub(r' +', r' ', soup.get_text())
      
    def parse_posts(self, response):
        # COLLECT FORUM POST DATA
        usernames = response.xpath('//p[@class="author"]//a[@class="username"]//text()').extract()
        post_counts = response.xpath('//dd[@class="profile-posts"]//a/text()').extract()
        post_times = response.xpath('//p[@class="author"]/text()').extract()
        post_texts = response.xpath('//div[@class="postbody"]//div[@class="content"]').extract()
        post_quotes = [self.clean_quote(s) for s in post_texts]
        post_texts = [self.clean_text(s) for s in post_texts]

        #YIELD POST DATA
        for i in range(len(usernames)):
            yield {'Username': usernames[i],
                   'PostCount': post_counts[i],
                   'PostTime': post_times[i],
                   'PostText': post_texts[i],
                   'QuoteText': post_quotes[i]}
        
        # CLICK THROUGH NEXT PAGE
        next_link = response.xpath('//li[@class="next"]//a[@rel="next"]/@href').extract_first()
        if next_link:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_posts)
