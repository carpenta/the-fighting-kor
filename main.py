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
			self.redirect("/?menu=tournament")
		else:
			self.response.write("fail")


class TournamentHandler(webapp2.RequestHandler):
	def get(self):
		id = self.request.get('id',None)
		if id != None:
			self.response.write(tournamentService.getTournamentWithWinners(id))
		elif self.request.get('withDetail', None) != None:
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

class FightUpdateWinnerHandler(webapp2.RequestHandler):
	def post(self):
		fight_id = self.request.get('fight_id', None)
		winner = self.request.get('winner', None)

		if fightService.updateWinner(fight_id, winner):
			self.response.write("<a href='/'>success</a>")
		else:
			self.response.write("fail")

class FightStateToggleHandler(webapp2.RequestHandler):
	def post(self):
		if fightService.toggleState(self.request.get('fight')):
			self.response.write("<a href='/?menu=ground'>success</a>")
		else:
			self.response.write("fail")

class InitializeHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write("<h1>기존 데이터를 삭제합니다</h1>")
		# delete all players
		ndb.delete_multi([m.key for m in Player.query().fetch()])
		# delete all playgrounds
		ndb.delete_multi([g.key for g in PlayGround.query().fetch()])
		# delete all fights
		ndb.delete_multi([f.key for f in Fight.query().fetch()])
		# delete all tournaments
		ndb.delete_multi([t.key for t in Tournament.query().fetch()])
		self.response.write("<pre>")
		# insert players
		f = open('players.csv', 'r')
		line_count = 0
		players = []
		for line in f.xreadlines():
			line_count+=1
			if line_count == 1:
				continue # 첫번째 줄은 버린다.(컬럼명이 나온 부분임)
				
			row = line.split(",")
			#name = row[0]
			#assoc = row[1]
			#group = row[2]
			#weight = row[3]
			#grade = row[4]
			#infinite = row[5]	
			
			player = Player(
				name = str(row[0]), 
				association = str(row[1]), 
				weight = str(row[3]), 
				grade = str(row[4]), 
				group = str(row[2]), 
				isInfinite = row[5]!="")
			player.put()
			players.append(player.to_dict())	
		self.response.write("%d 명의 선수를 입력했습니다\n"%(line_count-1))

		# insert playgrounds
		ground_names = ["A","B","C","D"]
		for i in ground_names:
			playground = PlayGround(playground_name=i)
			playground.put()
		self.response.write("%d 개의 경기장을 생성했습니다\n"%(len(ground_names)))
		self.response.write("</pre>")


application = webapp2.WSGIApplication([
	('/', MainPage),
	('/player', PlayerHandler),
	('/playground', PlayGroundHandler),
	('/tournaments', TournamentHandler),
	('/fight', FightHandler),
	('/fight/update', FightUpdateGroundHandler),
	('/fight/updateWinner', FightUpdateWinnerHandler),
	('/fight/toggleState', FightStateToggleHandler),
	('/init', InitializeHandler)
], debug=True)
