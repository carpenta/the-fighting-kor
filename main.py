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


def dictWithKey(model):
	result = model.to_dict()
	result['id'] = model.key.urlsafe()
	return result

# Models
class Participant(ndb.Model):
	name = ndb.StringProperty()
	association = ndb.StringProperty()
	weight = ndb.StringProperty()
	grade = ndb.StringProperty()
	#operator = ndb.UserProperty()
	#date = ndb.DateTimeProperty(auto_now_add=True)

class Tournament(ndb.Model):
	tournament_num = ndb.StringProperty()
	participant1 = ndb.KeyProperty(kind=Participant)
	participant2 = ndb.KeyProperty(kind=Participant)
	status = ndb.StringProperty()
	winner = ndb.KeyProperty(kind=Participant)

class MainPage(webapp2.RequestHandler):
	def get(self):
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)
			template_values = {
				'participants' : Participant.query(),
				'tournaments' : Tournament.query(),
				'menu_context' : self.request.get("menu")
			}
			template = JINJA_ENVIRONMENT.get_template('index.html') 
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class PlayerPage(webapp2.RequestHandler):
	def get(self):
		self.response.write("test")
	def post(self): 
		if users.get_current_user():	
			participant = Participant()
			participant.name = self.request.get('user_name', 'unknown')
			participant.association = self.request.get('user_assoc', 'unknown')
			participant.weight = self.request.get('user_weight', 'unknown')
			participant.grade = self.request.get('user_grade', 'infinite')
			participant.put()
			self.response.write("<a href='/?menu=player'>success</a>")
		else:
			self.response.write("fail")

class Ground(webapp2.RequestHandler):
	def get(self):
		ground_num = self.request.get("gid")
		
		self.response.write("test")
	def post(self):
		if users.get_current_user():
			fightmatch = FightMatch()
			fightmatch.section_num = self.request.get('section')
			fightmatch.match_num = self.request.get('match')
			fightmatch.put()
			self.response.write("<a href='/?menu=ground'>success</a>")
		else:
			self.response.write("fail")

class TournamentPage(webapp2.RequestHandler):
	def get(self):
		ground_num = self.request.get("ground")
		tournaments = []
		for t in Tournament.query().fetch():
			tournaments.append(dictWithKey(t))

		self.response.write(json.dumps(tournaments))	
		
	def post(self):
		tournament = Tournament()
		tournament.tournament_num = self.request.get('tournament_num', 'error')
		tournament.status = "running" #self.reqeust.get('status')
		tournament.participant1 = ndb.Key(urlsafe=self.request.get('p1_id'))
		tournament.participant2 = ndb.Key(urlsafe=self.request.get('p2_id'))
		#tournament.winner = Participant.query(self.request.get('winner_id')).get()
		tournament.put()
		self.response.write("<a href='/?menu=ground'>success</a>")

class JsonPage(webapp2.RequestHandler):
	def get(self):
		if self.request.get("key") :
			req_key = self.request.get("key")
			self.response.write(json.dumps(dictWithKey(ndb.Key(urlsafe=req_key).get())))
			return

		participants = []
		for p in Participant.query().fetch():
			participants.append(dictWithKey(p))

		self.response.write(json.dumps(participants))
		#self.response.write(json.dumps([p.name for p in Participant.query().fetch()]))

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/player', PlayerPage),
	('/ground', Ground),
	('/tournaments', TournamentPage),
	('/json', JsonPage)
], debug=True)


