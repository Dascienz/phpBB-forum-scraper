# -*- coding: utf-8 -*-
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy.http import Request

# TODO: Please provide values for the following variables
# Domains only, no urls
ALLOWED_DOMAINS = ['']
# Starting urls
START_URLS = ['']
# Is login required? True or False.
FORM_LOGIN = False
# Login username
USERNAME = ''
# Login password
PASSWORD = ''
# Login url
LOGIN_URL = ''


class PhpbbSpider(scrapy.Spider):
    
    name = 'phpBB'
    allowed_domains = ALLOWED_DOMAINS
    start_urls = START_URLS
    form_login = FORM_LOGIN
    if form_login is True:
        username = USERNAME
        password = PASSWORD
        login_url = LOGIN_URL
        start_urls.insert(0, login_url)

    username_xpath = '//p[contains(@class, "author")]//a[contains(@class, "username")]//text()'
    post_count_xpath = '//dd[@class="profile-posts" or not(@class)]//a/text()'
    post_time_xpath = '//div[@class="postbody"]//time/@datetime|//div[@class="postbody"]//p[@class="author"]/text()[2]'
    post_text_xpath = '//div[@class="postbody"]//div[@class="content"]'

    def parse(self, response):
        # LOGIN TO PHPBB BOARD AND CALL AFTER_LOGIN
        if self.form_login:
            formxpath = '//*[contains(@action, "login")]'
            formdata = {'username': self.username, 'password': self.password}
            form_request = scrapy.FormRequest.from_response(
                    response,
                    formdata=formdata,
                    formxpath=formxpath,
                    callback=self.after_login,
                    dont_click=False
            )
            yield form_request
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
            block_quotes[i] = '<quote-%s>=%s' % (str(i + 1), quote.get_text())
        return ''.join(block_quotes).strip()
    
    def clean_text(self, string):
        # CLEAN HTML TAGS FROM POST TEXT, MARK REPLIES TO QUOTES
        tags = ['blockquote']
        soup = BeautifulSoup(string, 'lxml')
        for tag in tags:
            for i, item in enumerate(soup.find_all(tag)):
                item.replaceWith('<reply-%s>=' % str(i + 1))
        return re.sub(r' +', r' ', soup.get_text()).strip()
      
    def parse_posts(self, response):
        # COLLECT FORUM POST DATA
        usernames = response.xpath(self.username_xpath).extract()
        n = len(usernames)
        if n > 0:
            post_counts = response.xpath(self.post_count_xpath).extract() or (n * [''])
            post_times = response.xpath(self.post_time_xpath).extract() or (n * [''])
            post_texts = response.xpath(self.post_text_xpath).extract() or (n * [''])
            post_quotes = [self.clean_quote(s) for s in post_texts]
            post_texts = [self.clean_text(s) for s in post_texts]

            # YIELD POST DATA
            for i in range(n):
                yield {'Username': str(usernames[i]).strip(), 'PostCount': str(post_counts[i]).strip(),
                       'PostTime': str(post_times[i]).strip(), 'PostText': post_texts[i], 'QuoteText': post_quotes[i]}

        # CLICK THROUGH NEXT PAGE
        next_link = response.xpath('//li[@class="next"]//a[@rel="next"]/@href').extract_first()
        if next_link:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse_posts)
