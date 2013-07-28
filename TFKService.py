# -*- coding: utf8 -*-
import json

from google.appengine.ext import ndb
from TFKModel import *
from TFKUtil import *

class PlayerService():
	def getPlayers(self):
		return self.getPlayer(None)

	def getPlayer(self, id):
		players = []
		if id is None:
			players = Player.query()
		else:
			players.append(ndb.Key(urlsafe=id).get())

		return players
	
	def getPlayerJson(self, id):
		players = []
		for p in self.getPlayer(self, id):
			players.append(dictWithKey(p))
		return json.dumps(players)


	def addPlayer(self, request):
		if request is None:
			return False

		player = Player()
		player.name = request.get('user_name', 'unknown')
		player.association = request.get('user_assoc', 'unknown')
		player.weight = request.get('user_weight', 'unknown')
		player.grade = request.get('user_grade', 'infinite')
		player.group = request.get('user_group', 'unknown')
		player.put()
		return True


class PlayGroundService():
	def getGrounds(self):
		return PlayGround.query().order(PlayGround.playground_num).fetch()

	def getGroundsJson(self):
		pgs = []
		for pg in self.getGrounds():
			playground = dictWithKey(pg)
			pgs.append(playground)
		return json.dumps(pgs)

	def addPlayGround(self, request):
		if request is None:
			return False

		playground = PlayGround()
		playground.playground_num = int(request.get('playground_num'), 0)
		playground.put()
		return True
		


class TournamentService():
	def getTournaments(self):
		return Tournament.query().order(Tournament.tournament_name)

	def getTournamentJson(self):
		tournaments = []
		for t in Tournament.query().fetch():
			tournament = dictWithKey(t)
			tournaments.append(tournament)
		return json.dumps(tournaments)

	def getTournamentWithFightJson(self):
		tournaments = []
		for t in Tournament.query().fetch():
			tournament = dictWithKey(t)

			fights = {} 
			for f in Fight.query(Fight.tournament == t.key):
				fight = dictWithKey(f)
				print fight
				del fight['tournament']
				fight['player1'] = dictWithKey(f.player1.get())
				fight['player2'] = dictWithKey(f.player2.get())
				if f.winner != None:
					fight['winner'] = dictWithKey(f.winner.get())
				fights[f.tournament_num] = fight

			tournament['fights'] = fights
			tournaments.append(tournament)
		return json.dumps(tournaments);
		

	def addTournament(self, request):
		if request is None:
			return False

		tournament = Tournament()
		#tournament.tournament_num = request.get('tournament_num', 'error')
		tournament.tournament_name = request.get('tournament_name')
		tournament.tournament_level = int(request.get('tournament_level', '0'))
		tournament.put()
		return True


class FightService():
	def getFights(self):
		return Fight.query()

	def getFightJson(self, id):
		if id is None:
			return None

		fight = ndb.Key(urlsafe=id).get()
		
		fightdict = dictWithKey(fight)
		fightdict['tournament'] = dictWithKey(fight.tournament.get())
		fightdict['player1'] = dictWithKey(fight.player1.get())
		fightdict['player2'] = dictWithKey(fight.player2.get())
		if fight.winner != None:
			fightdict['winner'] = dictWithKey(fight.winner.get())
		
		return json.dumps(fightdict)

	def getFightKeyListJson(self, ground_num):
		fights = []
		for f in Fight.query(Fight.playground_num == ground_num).fetch():
			fights.append(f.key.urlsafe())

		return json.dumps(fights)

	def getFightsJson(self, ground_num):
		fights = []
		for fight in Fight.query(Fight.playground_num == ground_num).fetch():
			fightdict = dictWithKey(fight)
			fightdict['tournament'] = dictWithKey(fight.tournament.get())
			fightdict['player1'] = dictWithKey(fight.player1.get())
			fightdict['player2'] = dictWithKey(fight.player2.get())
			if fight.winner != None:
				fightdict['winner'] = dictWithKey(fight.winner.get())
			fights.append(fightdict)

		return json.dumps(fights)

	def getGroundFightMap(self, playgrounds):
		playground_fights = {}
		for pg in playgrounds:
			playground_fights[pg.playground_num] = Fight.query(Fight.playground_num == pg.playground_num, Fight.status == 'running').fetch()
		return playground_fights

	def addFight(self, request):
		if request is None:
			return False

		fight = Fight()
		fight.tournament = ndb.Key(urlsafe=request.get('tournament_id'))
		fight.tournament_num = int(request.get('tournament_num'))
		#fight.playground_num = self.request.get('playground_num')
		fight.player1 = ndb.Key(urlsafe=request.get('p1_id'))
		fight.player2 = ndb.Key(urlsafe=request.get('p2_id'))
		fight.status = "running"
		fight.put()
		return True

	def updateFight(self, id, playground_num):
		if id is None or playground_num is None:
			return False
		fight = ndb.Key(urlsafe=id).get()
		fight.playground_num = playground_num
		fight.put()
		return True

	def toggleState(self, id):
		if id is None:
			return False
		fight = ndb.Key(urlsafe=id).get()

		if fight.status == "running":
			fight.status = "end"
		else:
			fight.status = "running"
		fight.put()
		return True
