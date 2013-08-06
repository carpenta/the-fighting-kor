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
			players = Player.query().order(Player.name)
		else:
			players.append(ndb.Key(urlsafe=id).get())

		return players
	
	def getPlayerJson(self, id):
		players = []
		for p in self.getPlayer(id):
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
	
	def removePlayer(self, id):
		if id is None:
			return False
		player = ndb.Key(urlsafe=id).get()
		player.delete()
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
	
	def getTournamentWithWinners(self, id):
		if id is None:
			return False
		
		tournament = ndb.Key(urlsafe=id).get()
		if tournament is None:
			return False
		
		winner1 = None
		winner2 = None
		winner3 = None
		winner4 = None

		fight1 = Fight.query(Fight.tournament == tournament.key,
					Fight.fight_level == 2).fetch(1)
		fight2 = Fight.query(Fight.tournament == tournament.key,
					Fight.fight_level == 4,
					Fight.tournament_num == 1).fetch(1)
		fight3 = Fight.query(Fight.tournament == tournament.key,
					Fight.fight_level == 4,
					Fight.tournament_num == 2).fetch(1)
		if fight1 != None and len(fight1) > 0 and fight1[0] != None:
			fight = fight1[0]
			if fight.winner != None:
				winner1 = fight.winner.get()
				winner2 = fight.player1.get()
				if fight.player1 == fight.winner:
					winner2 = fight.player2.get()
		if fight2 != None and len(fight2) > 0 and fight2[0] != None:
			fight = fight2[0]
			if fight.winner != None:
				winner3 = fight.player1.get()
				if fight.player1 == fight.winner:
					winner3 = fight.player2.get()
		if fight3 != None and len(fight3) > 0 and fight3[0] != None: 
			fight = fight3[0]
			if fight.winner != None:
				winner4 = fight.player1.get()	
				if fight.player1 == fight.winner:
					winner4 = fight.player2.get()

		result = dictWithKey(tournament)
		result['winner1'] = dictWithKey(winner1)
		result['winner2'] = dictWithKey(winner2)
		result['winner3'] = dictWithKey(winner3)
		result['winner4'] = dictWithKey(winner4)
		return json.dumps(result)

	def getTournamentWithFightJson(self):
		tournaments = []
		for t in Tournament.query().fetch():
			tournament = dictWithKey(t)

			fights = {} 
			for f in Fight.query(Fight.tournament == t.key):
				fight = dictWithKey(f)
				del fight['tournament']
				if f.player1 is None:
					tmpPlayer = Player()
					tmpPlayer.name = "(wait ..)"
					fight['player1'] = tmpPlayer.to_dict()
				else:
					fight['player1'] = dictWithKey(f.player1.get())
				if f.player2 is None:
					tmpPlayer = Player()
					tmpPlayer.name = "(wait ..)"
					fight['player2'] = tmpPlayer.to_dict()
				else:
					fight['player2'] = dictWithKey(f.player2.get())
				if f.winner is not None:
					fight['winner'] = dictWithKey(f.winner.get())
				fights["%s:%d"%(f.fight_level,f.tournament_num)] = fight

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
		return Fight.query().order(Fight.tournament, Fight.fight_level, Fight.fight_level)

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
		fight.fight_level = fight.tournament.get().tournament_level
		fight.put()
		return True

	def updateFight(self, id, playground_num):
		if id is None or playground_num is None:
			return False
		fight = ndb.Key(urlsafe=id).get()
		fight.playground_num = playground_num
		fight.put()
		return True

	def updateNextFight(self, fight):
		if fight is None or fight.fight_level is None or fight.fight_level < 4:
			return False
		
		# 이미 입력되어 있는 토너먼트 찾기
		if fight.fight_level is None:
			fight.fight_level = fight.tournament.get().tournament_level
			fight.put()

		fights = Fight.query(Fight.fight_level == fight.fight_level/2, 
				Fight.tournament_num == self.nextNum(fight.tournament_num)).fetch(1)
		nextFight = None
		if len(fights) > 0:
			nextFight = fights[0]
		
		if nextFight is None:
			nextFight = Fight()
			nextFight.tournament = fight.tournament
			nextFight.tournament_num = self.nextNum(fight.tournament_num)
			nextFight.status = "running"
			nextFight.fight_level = fight.fight_level/2

		if(self.isFirstPlayer(fight.tournament_num)):
			nextFight.player1 = fight.winner
		else:
			nextFight.player2 = fight.winner
		nextFight.put()
		return True

	def updateWinner(self, fight_id, winner):
		if id is None or winner is None:
			return False
		fight = ndb.Key(urlsafe=fight_id).get()
		fight.winner = ndb.Key(urlsafe=winner)
		fight.status = "end"
		fight.put()
		
		self.updateNextFight(fight)
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
	
	def nextNum(self, num):
		return int((num+1) / 2.0)
	
	def isFirstPlayer(self, num):
		return (num % 2) != 0
