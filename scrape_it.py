
# import scrapy
# from urllib.parse import urlparse, urljoin
# import time
# import random
# import json

# class GeneralSpider(scrapy.Spider):
#     name = 'general'
#     page_count = 0
#     max_pages = 100
#     priority_urls = set()
#     output_file = 'website_content.json'
#     crawled_data = []

#     custom_settings = {
#         'DOWNLOAD_DELAY': 5,
#         'RANDOMIZE_DOWNLOAD_DELAY': True,
#         'RETRY_TIMES': 5,
#         'RETRY_HTTP_CODES': [429, 500, 502, 503, 504, 522, 524, 408, 400],
#     }

#     def __init__(self, start_url=None, *args, **kwargs):
#         super(GeneralSpider, self).__init__(*args, **kwargs)
#         if start_url is not None:
#             self.start_urls = [start_url]
#             self.allowed_domains = [urlparse(start_url).netloc]
        
#         # Highlight: Removed the file clearing at initialization

#     def get_retry_request(self, request, spider, reason):
#         retry_times = request.meta.get('retry_times', 0) + 1
#         backoff_delay = 2 ** retry_times
#         random_delay = random.uniform(0, 3)
#         total_delay = backoff_delay + random_delay
#         time.sleep(total_delay)
#         return request

#     # Highlight: Added method to save data incrementally
#     def save_data(self):
#         with open(self.output_file, 'w') as f:
#             json.dump(self.crawled_data, f, indent=4)
#         self.logger.info(f'Saved {len(self.crawled_data)} pages to {self.output_file}')

#     def closed(self, reason):
#         self.save_data()

#     def parse(self, response):
#         if self.page_count >= self.max_pages:
#             return

#         self.page_count += 1

#         # Extract content
#         content = {
#             'url': response.url,
#             'title': response.css('title::text').get(),
#             'h1': response.css('h1::text').getall(),
#             'h2': response.css('h2::text').getall(),
#             'h3': response.css('h3::text').getall(),
#             'paragraphs': response.css('p::text').getall(),
#             'list_items': [item.strip() for item in response.css('li::text, li *::text').getall() if item.strip()],
#         }

#         # Add the content to our list of crawled data
#         self.crawled_data.append(content)

#         # Highlight: Save data incrementally every 10 pages
#         if self.page_count % 5 == 0:
#             self.save_data()

#         self.logger.info(f'Crawled page {self.page_count}: {response.url}')

#         # Follow links
#         if response.url == self.start_urls[0]:
#             for href in response.css('a::attr(href)').getall():
#                 full_url = urljoin(response.url, href)
#                 if urlparse(full_url).netloc == self.allowed_domains[0]:
#                     self.priority_urls.add(full_url)

#         for href in response.css('a::attr(href)').getall():
#             full_url = urljoin(response.url, href)
#             if urlparse(full_url).netloc == self.allowed_domains[0]:
#                 # Highlight: Removed sleep here to respect Scrapy's built-in delay
#                 if full_url in self.priority_urls:
#                     yield response.follow(full_url, self.parse, priority=1)
#                 else:
#                     yield response.follow(full_url, self.parse)
# import scrapy
# from scrapy.http import Request
# from scrapy.crawler import CrawlerProcess
# from itemadapter import ItemAdapter
# from collections import deque
# from scrapy.exceptions import CloseSpider

# class GeneralSpider(scrapy.Spider):
#     name = 'general'
    
#     def __init__(self, start_url, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.start_urls = [start_url]
#         self.crawled_urls = set()  # To store unique URLs
#         self.queue = deque([start_url])  # Queue to manage URLs
#         self.max_urls = 100  # Limit to 100 URLs

#     def parse(self, response):
#         if len(self.crawled_urls) >= self.max_urls:
#             raise CloseSpider(reason="Reached URL limit of 100")

#         # Extract all links from the page and add them to the queue
#         page_links = response.css('a::attr(href)').getall()

#         for link in page_links:
#             # Normalize the link and check if it's already crawled
#             absolute_url = response.urljoin(link)
#             if absolute_url not in self.crawled_urls and len(self.crawled_urls) < self.max_urls:
#                 self.queue.append(absolute_url)

#         # Mark the current page as crawled
#         self.crawled_urls.add(response.url)

#         # Yield the page content or data for storage
#         yield {
#             'url': response.url,https://help.gohighlevel.com/support/solutions
#             'content': response.text,  # Storing the page content
#         }

#         # Crawl next URLs from the queue
#         if self.queue:
#             next_url = self.queue.popleft()
#             yield Request(next_url, callback=self.parse)

import scrapy
from scrapy.http import Request
from scrapy.crawler import CrawlerProcess
from itemadapter import ItemAdapter
from collections import deque
from scrapy.exceptions import CloseSpider
import json

class GeneralSpider(scrapy.Spider):
    name = 'general'
    
    def __init__(self, start_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.crawled_urls = set()  # To store unique URLs
        self.queue = deque([start_url])  # Queue to manage URLs
        self.max_urls = 100  # Limit to 100 URLs
        self.crawled_data = []  # To store crawled data

    def parse(self, response):
        if len(self.crawled_urls) >= self.max_urls:
            raise CloseSpider(reason="Reached URL limit of 100")

        # Extract all links from the page and add them to the queue
        page_links = response.css('a::attr(href)').getall()

        for link in page_links:
            # Normalize the link and check if it's already crawled
            absolute_url = response.urljoin(link)
            if absolute_url not in self.crawled_urls and len(self.crawled_urls) < self.max_urls:
                self.queue.append(absolute_url)

        # Mark the current page as crawled
        self.crawled_urls.add(response.url)

        # Store the page content or data
        data = {
            'url': response.url,
            'content': response.text,  # Storing the page content
        }
        self.crawled_data.append(data)

        # Save data to JSON file after every 10 pages
        if len(self.crawled_data) % 10 == 0:
            self.save_data()

        # Yield the data for Scrapy's processing
        yield data

        # Crawl next URLs from the queue
        if self.queue:
            next_url = self.queue.popleft()
            yield Request(next_url, callback=self.parse)

    def save_data(self):
        with open('crawled_data.json', 'w') as f:
            json.dump(self.crawled_data, f, indent=4)
        self.logger.info(f"Saved {len(self.crawled_data)} pages to crawled_data.json")

    def closed(self, reason):
        self.save_data()  # Save any remaining data when spider closes