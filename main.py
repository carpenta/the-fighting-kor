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
class Player(ndb.Model):
	name = ndb.StringProperty()
	association = ndb.StringProperty()
	weight = ndb.StringProperty()
	grade = ndb.StringProperty()
	group = ndb.StringProperty()
	#operator = ndb.UserProperty()
	#date = ndb.DateTimeProperty(auto_now_add=True)

class Tournament(ndb.Model):
	tournament_name = ndb.StringProperty()
	tournament_level = ndb.IntegerProperty()
	tournament_num = ndb.StringProperty()

class Fight(ndb.Model):
	tournament = ndb.KeyProperty(kind=Tournament)
	tournament_num = ndb.IntegerProperty()
	playground_num = ndb.IntegerProperty()
	player1 = ndb.KeyProperty(kind=Player)
	player2 = ndb.KeyProperty(kind=Player)
	status = ndb.StringProperty()
	winner = ndb.KeyProperty(kind=Player)

class PlayGround(ndb.Model):
	playground_num = ndb.IntegerProperty()
	fights = ndb.StructuredProperty(Fight, repeated=False)

class MainPage(webapp2.RequestHandler):
	def get(self):
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)

			playgrounds = PlayGround.query().order(PlayGround.playground_num).fetch()
			playground_fights = {}
			for pg in playgrounds:
				playground_fights[pg.playground_num] = Fight.query(Fight.playground_num == pg.playground_num).fetch()

			template_values = {
				'players' : Player.query(),
				'tournaments' : Tournament.query().order(Tournament.tournament_name),
				'playgrounds' : PlayGround.query().order(PlayGround.playground_num),
				'playground_fights' : playground_fights,
				'fights' : Fight.query(),
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
			player = Player()
			player.name = self.request.get('user_name', 'unknown')
			player.association = self.request.get('user_assoc', 'unknown')
			player.weight = self.request.get('user_weight', 'unknown')
			player.grade = self.request.get('user_grade', 'infinite')
			player.group = self.request.get('user_group', 'unknown')
			player.put()
			self.response.write("<a href='/?menu=player'>success</a>")
		else:
			self.response.write("fail")

class TournamentPage(webapp2.RequestHandler):
	def get(self):
		tournaments = []
		for t in Tournament.query().fetch():
			tournament = dictWithKey(t)
			tournaments.append(tournament)

		self.response.write(json.dumps(tournaments))	
		
	def post(self):
		tournament = Tournament()
		#tournament.tournament_num = self.request.get('tournament_num', 'error')
		tournament.tournament_name = self.request.get('tournament_name')
		tournament.tournament_level = int(self.request.get('tournament_level', '0'))
		tournament.put()
		self.response.write("<a href='/?menu=tournament'>success</a>")

class PlayGroundPage(webapp2.RequestHandler):
	def get(self):
		pgs = []
		for pg in PlayGround.query().fetch():
			playground = dictWithKey(pg)
			pgs.append(playground)

		self.response.write(json.dumps(pgs))

	def post(self):
		playground = PlayGround()
		playground.playground_num = int(self.request.get('playground_num'), 0)
		playground.put()
		self.response.write("<a href='/?menu=tournament'>success</a>")


class FightListPage(webapp2.RequestHandler):
	def get(self):
		fights = []
		ground = self.request.get('ground', 1)
		for f in Fight.query(Fight.playground_num == int(ground)).fetch():
			fights.append(f.key.urlsafe())

		self.response.write(json.dumps(fights))

class FightInfoPage(webapp2.RequestHandler):
	def get(self):
		fights = []
		ground = self.request.get('ground', 1)
		for fight in Fight.query(Fight.playground_num == int(ground)).fetch():
			fightdict = dictWithKey(fight)
			fightdict['tournament'] = dictWithKey(fight.tournament.get())
			fightdict['player1'] = dictWithKey(fight.player1.get())
			fightdict['player2'] = dictWithKey(fight.player2.get())
			if fight.winner != None:
				fightdict['winner'] = dictWithKey(fight.winner.get())
			fights.append(fightdict)

		self.response.write(json.dumps(fights))

class FightPage(webapp2.RequestHandler):
	def get(self):
		gid = self.request.get('gid', 1)
		fight = ndb.Key(urlsafe=gid).get()
		
		fightdict = dictWithKey(fight)
		fightdict['tournament'] = dictWithKey(fight.tournament.get())
		fightdict['player1'] = dictWithKey(fight.player1.get())
		fightdict['player2'] = dictWithKey(fight.player2.get())
		if fight.winner != None:
			fightdict['winner'] = dictWithKey(fight.winner.get())
		
		self.response.write(json.dumps(fightdict))

	def post(self):
		fight = Fight()
		fight.tournament = ndb.Key(urlsafe=self.request.get('tournament_id'))
		fight.tournament_num = int(self.request.get('tournament_num'))
		#fight.playground_num = self.request.get('playground_num')
		fight.player1 = ndb.Key(urlsafe=self.request.get('p1_id'))
		fight.player2 = ndb.Key(urlsafe=self.request.get('p2_id'))
		fight.status = "running"
		fight.put()
		self.response.write("<a href='/?menu=ground'>success</a>")


class FightUpdatePage(webapp2.RequestHandler):
	def post(self):
		fight = ndb.Key(urlsafe=self.request.get('fight')).get()
		fight.playground_num = int(self.request.get('playground_num'))
		fight.put()

		self.response.write("<a href='/?menu=ground'>success</a>")		

class JsonPage(webapp2.RequestHandler):
	def get(self):
		if self.request.get("key") :
			req_key = self.request.get("key")
			self.response.write(json.dumps(dictWithKey(ndb.Key(urlsafe=req_key).get())))
			return

		player = []
		for p in Player.query().fetch():
			player.append(dictWithKey(p))

		self.response.write(json.dumps(player))
		#self.response.write(json.dumps([p.name for p in Player.query().fetch()]))

class TestPage(webapp2.RequestHandler):
	def get(self):
		template = JINJA_ENVIRONMENT.get_template('kineticbox.html') 
		self.response.write(template.render({}))

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/player', PlayerPage),
	('/tournaments', TournamentPage),
	('/playground', PlayGroundPage),
	('/fights', FightListPage),
	('/fightinfo', FightInfoPage),
	('/fight', FightPage),
	('/fight/update', FightUpdatePage),
	('/json', JsonPage),
	('/test', TestPage)
], debug=True)


