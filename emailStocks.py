# This script uses yahoo's finance page to gather stock information
# Simply enter your gmail info on lines 19 - 22
#
# The information is then emailed using info you must provide.
# Info: Stocks with quarterly resulsts being announced at the end of
#	today or before market open on the next business day (with positive EPS)
# You should be able to import and use the script elsewhere, but I have not tested
# If you wish to use multiple recipients, I believe you can do so by simply making
#	Taddr a list of strings instead of a single string.

import re
import urllib2
from bs4 import BeautifulSoup
import time
import datetime
import smtplib
from email.mime.text import MIMEText


Uname = 'gmail_username'
Pword = 'gmail_password'
Faddr = Uname + '@gmail.com'
Taddr = 'recipient@gmail.com'


def send_email(username, password, fromaddr, toaddr, msg):
	print 'Sending stock information to ' + toaddr
	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(fromaddr, toaddr, msg.as_string())
		server.quit()
	except:
		print 'Unable to send email'
	#In case you want to verify info in your terminal:
	#print 'Message:\n' + msg.as_string()

	

def get_stocks(url):
	print 'Retrieving stock information from ' + url
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page)
	
	source = str(soup.find_all('table')[5])
	table = re.findall('><td>(.*?)</td></tr>', source, re.S)
	
	stocks = []
	# Company name, link, symbol, eps, time
	pattern = r'(.+)</td><td><a href="(.+)">(.+)</a></td><td align="center">(.+)</td><td align="center"><small>([\w\s]+)</small>'
	for line in table:
		M = re.search(pattern, line)
		if M:
			stocks.append([M.group(1), M.group(2), M.group(3), M.group(4), M.group(5)])
	
	return stocks


def get_next_date():
	today = datetime.date.today()
	next = today + datetime.timedelta(days= 7-today.weekday() if today.weekday()>3 else 1)
	next = next.timetuple()

	y = str(next.tm_year)
	m = next.tm_mon
	if m <= 9:
		m = '0' + str(m)
	else:
		m = str(m)
	d = next.tm_mday
	if d <= 9:
		d = '0' + str(d)
	else:
		d = str(d)

	date = y + m + d
	return date


def screen_positive_eps(stocks):
	print 'Screening stocks for positive EPS...'
	positives = []
	for stock in stocks:
		if stock[3] != 'N/A' and float(stock[3]) > 0.0:
			positives.append(stock)
	return positives


def sort_today(stocks):
	print "Sorting today's stocks..."
	sorted = []
	for stock in stocks:
		if stock[4] == 'After Market Close':
			sorted.append(stock)
	for stock in stocks:
		if stock[4] == 'Time Not Supplied':
			sorted.append(stock)
	return sorted


def sort_tom(stocks):
	print "Sorting next business day's stocks..."
	sorted = []
	for stock in stocks:
		if stock[4] == 'Before Market Open':
			sorted.append(stock)
	for stock in stocks:
		if stock[4] == 'Time Not Supplied':
			sorted.append(stock)
	return sorted


def stocks_to_text(stocks):
	text = ''
	for stock in stocks:
		text += stock[0][:30]
		spaces = 30 - len(stock[0])
		if spaces < 0:
			spaces = 0
		text += ' ' * (spaces + 2)
		text += stock[2][:8]
		spaces = 8 - len(stock[2])
		if spaces < 0:
			spaces = 0
		text += ' ' * spaces
		text += stock[3][:4]
		spaces = 4 - len(stock[3])
		if spaces < 0:
			spaces = 0
		text += ' ' * (spaces+2)
		text += stock[4]
		spaces = 18 - len(stock[4])
		if spaces < 0:
			spaces = 0
		text += ' ' * (spaces+2)
		text += stock[1]
		text += '\n'
	return text


def email_stock_info(username, password, fromaddr, toaddr):
	today = 'http://biz.yahoo.com/research/earncal/today.html'
	stocks = get_stocks(today)
	stocks = screen_positive_eps(stocks)
	stocks = sort_today(stocks)
	
	email_msg = 'Today:\n'
	email_msg += stocks_to_text(stocks) + '\n'

	next_day = get_next_date()
	next_url = 'http://biz.yahoo.com/research/earncal/' + next_day + '.html'
	try:
		stocks = get_stocks(next_url)
	except:
		print 'Unable to open URL for next day.'
		email_msg += 'Unable to open URL for next day.'
	else:
		stocks = screen_positive_eps(stocks)
		stocks = sort_tom(stocks)
	
		email_msg += next_day + ':\n'
		email_msg += stocks_to_text(stocks)
	
	mime_msg = MIMEText(email_msg)
	mime_msg['Subject'] = "Stock Information"
	mime_msg['From'] = fromaddr
	mime_msg['To'] = toaddr
	send_email(username, password, fromaddr, toaddr, mime_msg)



if __name__ == "__main__":
	email_stock_info(Uname, Pword, Faddr, Taddr)
