#!/usr/bin/env python3

#uses BeautifulSoup: http://www.crummy.com/software/BeautifulSoup
# installation: pip install beautifulsoup4
from bs4 import BeautifulSoup
from time import sleep
import requests
import os.path
from TwitterSession import TwitterSession

class TickerItem:
	def __init__(self):
		self.heading = ''
		self.body = ''
		self.urls = []

twitter_login = "NUTZERNAMEN HIER"
twitter_password = "PASSWORD HIER"
cache_file = 'tu-corona-ticker.txt'
corona_url = 'https://tu-dresden.de/tu-dresden/gesundheitsmanagement/information-regarding-covid-19-coronavirus-sars-cov-2/tud-corona-ticker'
response = requests.get(corona_url)

offset_main = response.text.find('<div id="content-core">')

ticker_list = []
if offset_main:
	offset_last = offset_main
	offset_heading = response.text.find('<h4>', offset_last)
	while -1 != offset_heading:
		offset_last = response.text.find('</h4>', offset_heading + 4)
		ticker_item = TickerItem()
		ticker_item.heading = response.text[offset_heading + 4:offset_last]

		offset_last = offset_last + 5
		offset_heading = response.text.find('<h4>', offset_last)
		if -1 != offset_heading \
		and ('<p>' in response.text[offset_last:offset_heading] \
		or '<div' in response.text[offset_last:offset_heading]):
			soup = BeautifulSoup(response.text[offset_last:offset_heading], 'html.parser')
			rawText = "{}".format(soup.text)
			textSansSpace = " ".join(rawText.split())
			ticker_item.body = textSansSpace
			for cur_link in soup.select('a'):
				if not cur_link.get('href') is None:
					link_url = "{}".format(cur_link.get('href'))
					ticker_item.urls.append(cur_link.get('href'))
			ticker_list.append(ticker_item)

blob_full = ""

for cur_item in ticker_list:
	blob_full = "{}{}\n".format(blob_full, cur_item.heading)

list_new_items = []

if os.path.isfile(cache_file):
	cache_contents = ""
	with open(cache_file, 'r') as file_handle:
		cache_contents = file_handle.read()

	for cur_item in ticker_list:
		if not cur_item.heading in cache_contents:
			list_new_items.append(cur_item)
else:
	# no cache file? no new entries!
	pass

with open(cache_file, 'w') as file_handle:
	file_handle.write(blob_full)

if 0 < len(list_new_items):
	session = TwitterSession()
	session.try_login(twitter_login, twitter_password)
	for cur_item in list_new_items:
		session.try_post("{} #tud #corona #update".format(cur_item.heading))
	session.try_logout()
