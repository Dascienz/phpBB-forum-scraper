# phpBB Forum Scraper
Python-based scraper for phpBB forums.

Code requires: 

    1. Python scraping library, <a href="http://scrapy.org/" target="_blank">Scrapy</a>.
    
    2. Python HTML parsing library, <a href="ttps://www.crummy.com/software/BeautifulSoup/bs4/doc/" target="_blank">BeautifulSoup</a>.


## Scraper Output
Scrapes the following information from forum posts: 

	1. Username

	2. User post count

	3. Post date & time

	4. Post text
    
    5. Quoted text


allowed_domains = ['']
    start_urls = ['']
    username = ''
    password = ''
    form_login = False

Edit `phpBB.py` and specify:

    1. `allowed_domains`
    
    2. `start_urls`
    
    3. `username` & `password`
    
    4. `forum_login=False` or `forum_login=True`

## Instructions:
From within `/phpBB_scraper/`:

`scrapy crawl phpBB` to launch the crawler.

`scrapy crawl phpBB -o posts.csv` to launch the crawler and save results to CSV.