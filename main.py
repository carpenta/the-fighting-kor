# -*- coding: utf8 -*-

import sys, os
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2
import json

JINJA_ENVIRONMENT = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions=['jinja2.ext.autoescape'])

# Models
class Participant(ndb.Model):
	image = ndb.StringProperty()
	name = ndb.StringProperty()
	association = ndb.StringProperty()
	emblem = ndb.StringProperty()
	operator = ndb.UserProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)

class FightMatch(ndb.Model):
	section_num = ndb.StringProperty()
	match_num = ndb.StringProperty()
	participant1 = ndb.KeyProperty(kind=Participant)  
	participant2 = ndb.KeyProperty(kind=Participant)
	score = ndb.StringProperty()
	checklist = ndb.StringProperty(repeated=True)
	winner = ndb.KeyProperty(kind=Participant)
	result = ndb.StringProperty()
	operator = ndb.UserProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
	def get(self):
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			template_values = {'participants' : Participant.query()}
			template = JINJA_ENVIRONMENT.get_template('index.html') 
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class Process(webapp2.RequestHandler):
	def get(self):
		self.response.write("test");
	def post(self): 
		if users.get_current_user():	
			participant = Participant()
			participant.operator = users.get_current_user()
			participant.name = self.request.get('user_name', 'unknown')
			participant.image = "not yet"
			participant.association = "test"
			participant.emblem = "not yet"
			participant.put()
			self.response.write("<a href='/'>success</a>")
		else:
			self.response.write("fail")

class JsonPage(webapp2.RequestHandler):
	def get(self):
		data_set = []
		for p in Participant.query().fetch():
			data_map = p.to_dict()
			data_map['operator'] = p.operator.user_id() + ", " + p.operator.nickname()
			data_map['date'] = p.date.isoformat()
			data_set.append(data_map)

		self.response.write(json.dumps(data_set))

		#self.response.write(json.dumps([p.name for p in Participant.query().fetch()]))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/update', Process),
		('/json', JsonPage)
], debug=True)


