# phpBB Forum Scraper
Python-based scraper for phpBB forums.

Code requires: 

1. Python scraping library, [Scrapy](http://scrapy.org/).
    
2. Python HTML parsing library, [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).


## Scraper Output
Scrapes the following information from forum posts: 

	1. Username

	2. User post count

	3. Post date & time

	4. Post text
    
    5. Quoted text


Edit `phpBB.py` and specify:

1. `allowed_domains`
    
2. `start_urls`
    
3. `username` & `password`
    
4. `forum_login=False` or `forum_login=True`

## Instructions:
From within `/phpBB_scraper/`:

`scrapy crawl phpBB` to launch the crawler.

`scrapy crawl phpBB -o posts.csv` to launch the crawler and save results to CSV.

NOTE: Please adjust `settings.py` to throttle your requests.