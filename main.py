# -*- coding: utf8 -*-

import sys, os
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions=['jinja2.ext.autoescape'])

# Models
class Participant(ndb.Model):
  image = ndb.StringProperty(indexed=False)
  name = ndb.StringProperty(indexed=False)
	association = ndb.StringProperty(indexed=False)
	emblem = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add=True)

class FightMatch(ndb.Model):
	section_num = ndb.StringProperty()
	match_num = ndb.StringProperty()
  participant1 = ndb.ReferenceProperty(Participant)  
	participant2 = ndb.ReferenceProperty(Participant)
	score = ndb.StringProperty()
	checklist = ndb.StringListProperty()
	winner = ndb.ReferenceProperty(Participant)
	result = ndb.StringProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            template_values = {}
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Schedule(webapp2.RequestHandler):
		def get(self):
			self.response.write("test");

    def post(self):
        if users.get_current_user():
            checkedScheduleJson = self.request.get('schedule', '')
            checkedPlaceJson = self.request.get('place', '')

            user = users.get_current_user()
            userId = user.user_id()
            userSchedule = UserCheckedSchedule(ndb.Key('UserCheckedSchedule', userId))

            userSchedule.checkedDateJson = checkedScheduleJson
            userSchedule.checkedPlaceJson = checkedPlaceJson
            userSchedule.put()
            self.response.write("success")
        else:
            self.response.write("fail")




application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/update', Schedule)
], debug=True)
