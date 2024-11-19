import re
from urllib.error import HTTPError
import urllib.parse
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient

class Frontier:
	def __init__(self, startingUrl):
		self.urls = []
		self.urls.append(startingUrl)
		self.current_index = 0
		self.end = len(self.urls)

	def done(self):
		if self.current_index == self.end:
			return True
		else:
			return False

	def nextURL(self):
		current_url = self.urls[self.current_index]
		self.current_index += 1
		return current_url

	def clear(self):
		print('clearing frontier')
		self.current_index = 0
		self.end = 0
		self.urls.clear()

	def addURL(self, url):
		#check url does not exist in list
		if url not in self.urls:
			self.urls.append(url)
			self.end += 1


def main():
	
	print('connecting to database collection pages')

	# Connecting to the database
	db = connectDataBase()

	# Drop existing pages collection
	pages = db["pages"]    
	pages.drop()
	
	# Creating a collection
	pages = db["pages"]    

	frontier = Frontier('https://www.cpp.edu/engineering/ce/index.shtml')
	# frontier = Frontier('https://www.cpp.edu/engineering/ce/faculty.shtml')
	# frontier = Frontier('https://www.cpp.edu/faculty/yongpingz/')
	
	num_target = 25
	crawlerThread(frontier, pages, num_target)



def retieveHTML(url):
	try:
		html = urlopen( url )
	except HTTPError as e:
		return ''
	try:
		bs = BeautifulSoup(html.read(), 'html.parser')
	except AttributeError as e:
		return ''
	return bs.prettify()

def connectDataBase():
	# Creating a database connection object using pymongo

	DB_NAME = "CPPCivilEngineering"
	DB_HOST = "localhost"
	DB_PORT = 27017

	try:
		client = MongoClient(host=DB_HOST, port=DB_PORT)
		db = client[DB_NAME]

		return db
	except:
		print("Database not connected successfully")


def storePage(pages, url, html):
	page = {
		  "url": url,
		  "html": html,
		  "targetPage": 0
	 }
	
	pages.insert_one(page)


def targetPage(html):
	# Stop criteria 
	# <div class="fac-info">

	bs = BeautifulSoup(html, 'html.parser')

	fac_info = True if bs.find(attrs={'class':'fac-info'}) else False
	
	# if fac_info:
	# 	print( bs.find(attrs={'class':'fac-info'}).get_text().strip() )
	return fac_info
		
def flagTargetPage(pages, url):
	page = { "$set": {
		  "targetPage": 1
	 }}
	
	pages.update_one({"url": url}, page)

def findURLS(html):
	ce_base = 'https://www.cpp.edu/engineering/ce/'
	cpp_base = 'http://www.cpp.edu'
	cpp_base_secure = 'https://www.cpp.edu'

	urls = []
	sanitized_found_urls = []
	bs = BeautifulSoup(html, 'html.parser')
	contains_hrefs = bs.find_all(href=True)

	file_types = ['.pdf', '.docx', '.doc', '.ppt','.pptx', '.png', '.jpg', '.jpeg', '.ai', '.xlsx']
	
	for hrefs in contains_hrefs:
		href = hrefs['href'].replace(" ", "")

		# print('href:', href)

		if any(ele in href for ele in file_types):
			continue
			# print('skip, file extension', href)
		elif 'mailto' in href:
			continue
			# print('skip, mailto', href)
		elif cpp_base_secure in href or cpp_base in href:
			# print('vaild', href)
			urls.append( href )
		elif 'http' in href and cpp_base_secure not in href:
			continue
			# print('skip, http not cpp', href)
		elif cpp_base_secure not in href:
			# print('urljoin', href)
			urls.append( urllib.parse.urljoin(ce_base, href) )
		else:
			continue
			# print('skipping non cpp websites', href)
		
		sanitized_found_urls = [url for url in urls if re.search(cpp_base_secure,url)]
		
	return sanitized_found_urls



def crawlerThread(frontier, pages, num_targets):
	print('Starting crawler thread')

	targets_found = 0
	while not frontier.done():

		url = frontier.nextURL()
		print('current url:', url)

		html = retieveHTML(url)

		storePage(pages, url, html)

		if targetPage(html):
			print('target met, add flag')
			flagTargetPage(pages, url)
			targets_found = targets_found + 1
		if targets_found == num_targets:
			frontier.clear()
		else:
			print('targets_found', targets_found)

			found_urls = findURLS(html)
			
			for url in found_urls:
				frontier.addURL(url)
	
	print('==========\nFinished crawler thread. Check mongoDB.\n==========')



	'''
	PSUEDOCODE (strictly follow):

	procedure crawlerThread (frontier, num_targets) 
		targets_found = 0 
		while not frontier.done() do 
			url <— frontier.nextURL() 
			html <— retrieveURL(url) 
			storePage(url, html) 
			if target_page (parse (html))  
				targets_found = targets_found + 1 
			if targets_found = num_targets 
				clear_frontier() 
			else 
				for each not visited url in parse (html) do 
					frontier.addURL(url) 
				end for 
			end if-else
		end while 
	end procedure
	'''

if __name__ == '__main__':
	main()