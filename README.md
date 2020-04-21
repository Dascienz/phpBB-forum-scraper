# phpBB Forum Scraper

Python-based web scraper for phpBB forums. Project can be used as a template for building your own
custom Scrapy spiders or for one-off crawls on designated forums. Please keep in mind that aggressive crawls
can produce significant strain on web servers, so please throttle your request rates.


## Requirements: 

1. Python web scraping library, [Scrapy](http://scrapy.org/).   
2. Python HTML/XML parsing library, [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).


## Scraper Output

The phpBB.py spider scrapes the following information from forum posts:
1. Username
2. User Post Count
3. Post Date & Time
4. Post Text
5. Quoted Text

If you need additional data scraped, you will have to create additional spiders or edit the existing spider.


## Edit `phpBB.py` and Specify:

1. `allowed_domains`
2. `start_urls` 
3. `username` & `password`
4. `forum_login=False` or `forum_login=True`


## Running the Scraper:
```bash
cd phpBB_scraper/
scrapy crawl phpBB
# scrapy crawl phpBB -o posts.csv
```
NOTE: Please adjust `settings.py` to throttle your requests.