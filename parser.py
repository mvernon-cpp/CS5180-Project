from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient

def main():
	print('connecting to database collection pages')

	# Connecting to the database
	db = connectDataBase()

	db["faculty_websites"].drop()

	# Creating a collection
	pages = db["pages"]    

	print('connecting to database collection faculty_websites')
	faculty_websites = db["faculty_websites"]

	#query for target page
	target_pages = findTargetPage(pages)

	for target_page in target_pages:
		if target_page is not None:
			html = target_page.get('html')
			url = target_page.get('url')

			parseFacultyWebsite(faculty_websites, html, url)
		else:
			print('Target page does not exist.')


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


# change to find all
# testing with find one for now
def findTargetPage(pages):
	return pages.find( {"targetPage": 1} )
	 

def parseFacultyWebsite(faculty_websites, html, url):
	bs = BeautifulSoup(html, 'html.parser')
	
	fac_main = bs.select('div.fac.main')
	fac_right = bs.select('aside.fac.rightcol')

	# print('='*100)
	# print(fac_main[0].get_text().strip())
	# print(fac_right[0].get_text().strip())

	storeFacultyWebsites(faculty_websites, url, fac_main[0].prettify(), fac_right[0].prettify() )


def storeFacultyWebsites(faculty_websites, url, fac_main, fac_right ):
	website = {
		  "url": url,
		  "fac_main": fac_main,
		  "fac_right": fac_right,
	 }
	
	faculty_websites.insert_one(website)
	print( "Stored:",url )
	print('='*100)


if __name__ == '__main__':
	main()