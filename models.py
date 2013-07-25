import datetime
import requests

from giotto import get_config
Base = get_config("Base")
from colour import Color
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Boolean, func, desc, PickleType

def color_range(color_start, color_end, value, max_value):
	c1 = Color(color_start)
	c2 = Color(color_end)
	color_range = list(c1.range_to(c2, 100))
	ratio = value / float(max_value) * 100
	if value >= max_value:
		ratio = 99
	return color_range[int(ratio)]

class Submission(Base):
	"""
	Represents a hacker news submission that has made it to
	the front page.
	"""
	hn_id = Column(Integer, primary_key=True) # id on hacker news
	date_created = Column(DateTime)
	peak_rank = Column(Integer)
	current_rank = Column(Integer)
	title = Column(String)
	url = Column(String)
	comments = Column(Integer)
	points = Column(Integer)
	submitter = Column(String)

	def __repr__(self):
		rank = "(#%s)" % self.current_rank if self.current_rank else ''
		return "<Submission %s:%s %s>" % (
			self.hn_id,
			rank,
			self.title.encode('ascii', 'replace')
		)

	@classmethod
	def all_update(cls, submissions):
		"""
		Passed in is a list of dicts representing the data crawled from
		the hacker news front page. Out is the number os new submissions found.
		This function updates the database tables and should be run on a regular
		schedule.
		"""
		new = 0
		session = get_config('db_session')
		session.query(Submission).update({'current_rank': None})
		for sub in submissions:
			try:
				submission = session.query(Submission).get(sub['hn_id'])
				submission.update_from_crawl(sub)
			except AttributeError:
				submission = Submission(date_created=datetime.datetime.now(), **sub)
				session.add(submission)
				new += 1

		session.commit()
		return new

	@property
	def age_color(self):
		"""
		Return a hex color representing the age of this submission. Green ==
		new, brown == old. 
		"""
		#return "#0F0"
		return color_range('green', 'brown', self.age, 24)

	@property
	def submitter_color(self):
		cache = get_config('cache_engine')
		key = "user/%s" % self.submitter
		json = cache.get(key)
		if not json:
			res = requests.get("http://hn-karma-tracker.herokuapp.com/user/%s.json" % self.submitter)
			if res.status_code != 200:
				return 'black'
			json = res.json()
			cache.set(key, json, 24 * 3600)
		
		percentile = float(json['month_data']['percentile']) * 100

		if percentile < 20:
			return 'lime'
		if percentile < 50:
			return 'green'
		if percentile < 80:
			return 'orange'
		
		return 'red'

	@property
	def points_color(self):
		#return "#093"
		return color_range('blue', 'red', self.points, 1000)

	@property
	def comments_color(self):
		if self.comments == 0:
			return 'lime'
		if self.comments < 20:
			return 'green'
		if self.comments < 100:
			return 'orange'
		if self.comments < 500:
			return 'crimson'
		if self.comments < 1000:
			return 'brown'

		return 'black'

	@property
	def age(self):
		"""
		How old this submission is. Returns a value in hours.
		"""
		return (datetime.datetime.now() - self.date_created).total_seconds() / 3600

	def update_from_crawl(self, data):
		"""
		Update this submission instance with the latest comment counts/points/rank/etc.
		"""
		self.comments = data['comments']
		self.points = data['points']
		self.current_rank = data['current_rank']
		if self.current_rank <= self.peak_rank or not self.peak_rank:
			self.peak_rank = self.current_rank
		
		session = get_config('db_session')
		session.add(self)
		session.commit()