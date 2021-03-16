import json
import math

import scrapy

from scrapy.loader import ItemLoader

from ..items import BankofgreecegrItem
from itemloaders.processors import TakeFirst

base = 'https://www.bankofgreece.gr/_layouts/15/Proxy/Proxy.svc/Media?lang=el&category=ade0d8a8-de85-4a6a-a9a0-974b076d495f&year=2021&sorting=date&page={}'

class BankofgreecegrSpider(scrapy.Spider):
	name = 'bankofgreecegr'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)

		for post in data['data']:
			date = post['date']
			title = post['title']
			href = post['href']
			yield response.follow(href, self.parse_post, cb_kwargs={'date': date, 'title': title})

		total_pages = math.ceil(data['totalItems']/10)
		if self.page < total_pages:
			self.page += 1
			yield scrapy.Request(base.format(self.page), self.parse)

	def parse_post(self, response, date, title):
		description = response.xpath('//p//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BankofgreecegrItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
