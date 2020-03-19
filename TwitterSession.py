#!/usr/bin/env python3

#uses BeautifulSoup: http://www.crummy.com/software/BeautifulSoup
# installation: pip install beautifulsoup4
from bs4 import BeautifulSoup
from time import sleep
import requests



class TwitterSession:
	def __init__(self):
		self.session = False
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language': 'de,en-US;q=0.7,en;q=0.3'
		}

	def store_response(self, filename, response):
		storage_file = open(filename, 'w')
		storage_file.write(response.text)
		storage_file.close()

	def try_login(self, paramUsername, paramPassword):
		url = "https://twitter.com/login"
		print(url)
		self.session = requests.Session()
		response = self.session.get(url, headers=self.headers)
		soup = BeautifulSoup(response.text, 'html.parser')
		formEle = soup.find('form')
		nextUrl = formEle.get('action')
		self.headers['Referer'] = url
		url = nextUrl

		sleep(2)
		print(url)
		response = self.session.post(url, headers=self.headers)
		self.store_response("login_confirm.html", response)
#		print("status_code: {}".format(response.status_code))
#		for header in response.headers:
#			print("{}: {}".format(header, response.headers[header]))
		soup = BeautifulSoup(response.text, 'html.parser')
		allFields = {}
		for curInput in soup.find_all("input"):
			curName = curInput.get('name')
			curValue = curInput.get('value')
			if 'password' == curInput.get('type'):
				curValue = paramPassword
			if 'text' == curInput.get('type') \
			and 'username' in curName:
				curValue = paramUsername
			allFields[curName] = curValue

		nextUrl = soup.form.get('action')
		if nextUrl.startswith('/'):
			nextUrl = "https://mobile.twitter.com{}".format(nextUrl)
		self.headers['Referer'] = url
		url = nextUrl

		sleep(3)
		print(url)
		response = self.session.post(url, headers=self.headers, data=allFields)
		self.store_response("login_attempt.html", response)

	def try_post(self, message):
		url = "https://mobile.twitter.com/compose/tweet"
		sleep(3)
		print(url)
		response = self.session.get(url, headers=self.headers)
		self.store_response("compose_tweet.html", response)
		soup = BeautifulSoup(response.text, 'html.parser')
		inputEles = soup.select('.tweetbox-container form input')
		allFields = {}
		for curInput in inputEles:
			allFields[curInput.get('name')] = curInput.get('value')
		textareaEle = soup.select('.tweetbox-container form textarea')
		allFields[textareaEle[0].get('name')] = message

		nextUrl = soup.select('.tweetbox-container form')[0].get('action')
		if nextUrl.startswith('/'):
			nextUrl = "https://mobile.twitter.com{}".format(nextUrl)
		url = nextUrl

		sleep(3)
		print(url)
		response = self.session.post(url, headers=self.headers, data=allFields)
		self.store_response("sent_tweet.html", response)

	def try_logout(self):
		url = "https://mobile.twitter.com/logout"

		sleep(3)
		print(url)
		response = self.session.get(url, headers=self.headers)
		self.store_response("logout_attempt.html", response)
		soup = BeautifulSoup(response.text, 'html.parser')
		formEle = soup.find('form')
		nextUrl = formEle.get('action')
		if nextUrl.startswith('/'):
			nextUrl = "https://mobile.twitter.com{}".format(nextUrl)
		allFields = {}
		for curInput in soup.find_all("input"):
			allFields[curInput.get('name')] = curInput.get('value')

		sleep(3)
		print(url)
		response = self.session.post(url, headers=self.headers, data=allFields)
		self.store_response("logout_finish.html", response)

