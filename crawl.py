import re

import requests
from bs4 import BeautifulSoup
from models import Submission

def parse_out_title(text):
	"""
	In comes a title directly from the hacker news html page
	This function removes the domain in parenthesis, and returns
	both the domain and the full title
	in -> "title (domain.com)"
	out-> ("title", "domain.com")
	"""
	match = re.search(r'\([\d\w\.]+\)$', text)
	just_domain = match.group()[1:-1]
	title = text[:(len(just_domain)+2) * -1].strip()
	return title, just_domain

def parse_front_page(html):
	"""
	In comes the HTML of the hacker news front page,
	out is the list of submissions in a nice list of dicts
	format.
	"""
	soup = BeautifulSoup(html)

	titles = []
	urls = []
	domains = []
	for tag in soup.find_all('td', class_='title'):
		if not tag.text.endswith('.') and "(" in tag.text:
			# ignore when there is a peroid present, (that is the rank, not relevent here)
			# and ignore when no parenthesis (the "More" link)
			title = tag.text.strip()
			just_title, domain = parse_out_title(title)
			titles.append(just_title)
			urls.append(tag.a['href'])
			domains.append(domain)

	data = []
	for tag in soup.find_all('td', class_='subtext'):
		points = tag.span and tag.span.text[:-7] # ignore trailing " points"
		submitter = tag('a') and tag('a')[0].text
		if submitter and points:
			data.append([points, submitter])
		
	ids = []
	comment_counts = []
	for tag in soup.find_all(href=re.compile("item\?id=(\d){7,8}")):
		# go through each link that looks like a comments link.
		if tag.text == "discuss":
			text = 0
		elif tag.text == '1 comment':
			text = 1
		else:
			text = int(tag.text[:-9])

		comment_counts.append(text)
		id = int(tag['href'][8:])
		ids.append(id)

	submissions = []
	for i in range(len(comment_counts)):
		submission = {
			'current_rank': i + 1,
			'title': titles[i].encode('ascii', 'xmlcharrefreplace'),
			'url': unicode(urls[i]),
			'domain': domains[i],
			'comments': comment_counts[i],
			"submitter": unicode(data[i][1]),
			"points": unicode(data[i][0]),
			'hn_id': ids[i],
		}
		submissions.append(submission)

	return submissions

def get_submissions():
	"""
	Crawls the front page of hacker news and returns a list of all
	submissions.
	"""
	front = requests.get("https://news.ycombinator.com/").text
	#front = open("html/front.html").read()
	return parse_front_page(front)

def crawl():
	"""
	Fetch the lastest front page from HN, and then update the tables
	"""
	Submission.all_update(get_submissions())














