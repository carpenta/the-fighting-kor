# -*- coding: utf8 -*-

import sys, os
import webapp2
import jinja2
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from TFKModel import *
from TFKService import *
from TFKUtil import *

JINJA_ENVIRONMENT = jinja2.Environment(
loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions=['jinja2.ext.autoescape'])

playerService = PlayerService()
playGroundService = PlayGroundService()
tournamentService = TournamentService()
fightService = FightService()

class MainPage(webapp2.RequestHandler):
	def get(self):
		if users.get_current_user():
			url = users.create_logout_url(self.request.uri)

			playgrounds = playGroundService.getGrounds()
			playground_fights = fightService.getGroundFightMap(playgrounds)
			
			template_values = {
				'players' : playerService.getPlayers(),
				'tournaments' : tournamentService.getTournaments(),
				'playgrounds' : playgrounds,
				'playground_fights' : playground_fights,
				'fights' : fightService.getFights(),
				'menu_context' : self.request.get("menu")
			}
			template = JINJA_ENVIRONMENT.get_template('views/index.html') 
			self.response.write(template.render(template_values))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class PlayerHandler(webapp2.RequestHandler):
	def get(self):
		req_player_id = self.request.get('id', None)
		self.response.write(playerService.getPlayerJson(req_player_id))
	def post(self):
		if users.get_current_user() and playerService.addPlayer(self.request):	
			self.response.write("<a href='/?menu=player'>success</a>")
		else:
			self.response.write("fail")

class PlayGroundHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write(playGroundService.getGroundsJson())

	def post(self):
		if playGroundService.addPlayGround(self.request):
			self.response.write("<a href='/?menu=tournament'>success</a>")
		else:
			self.response.write("fail")


class TournamentHandler(webapp2.RequestHandler):
	def get(self):
		if self.request.get('withDetail', None) != None:
			self.response.write(tournamentService.getTournamentWithFightJson())
		else:
			self.response.write(tournamentService.getTournamentJson())	
		
	def post(self):
		if tournamentService.addTournament(self.request):
			self.response.write("<a href='/?menu=tournament'>success</a>")
		else:
			self.response.write("fail")


class FightHandler(webapp2.RequestHandler):
	def get(self):
		ground = self.request.get('ground', None)
		gid = self.request.get('gid', None)
		if ground is not None:
			self.response.write(fightService.getFightsJson(int(ground)))
		elif gid is not None:
			self.response.write(fightService.getFightJson(gid))
		else:
			self.response.write("[]")

	def post(self):
		if fightService.addFight(self.request):
			self.response.write("<a href='/?menu=ground'>success</a>")
		else:
			self.response.write("fail")


class FightUpdateGroundHandler(webapp2.RequestHandler):
	def post(self):
		if fightService.updateFight(self.request.get('fight'), int(self.request.get('playground_num'))):
			self.response.write("<a href='/?menu=ground'>success</a>")
		else:
			self.response.write("fail")

class FightStateToggleHandler(webapp2.RequestHandler):
	def post(self):
		if fightService.toggleState(self.request.get('fight')):
			self.response.write("<a href='/?menu=ground'>success</a>")
		else:
			self.response.write("fail")

application = webapp2.WSGIApplication([
	('/', MainPage),
	('/player', PlayerHandler),
	('/playground', PlayGroundHandler),
	('/tournaments', TournamentHandler),
	('/fight', FightHandler),
	('/fight/update', FightUpdateGroundHandler),
	('/fight/toggleState', FightStateToggleHandler)
], debug=True)
