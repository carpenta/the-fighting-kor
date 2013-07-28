# -*- coding: utf8 -*-

from google.appengine.ext import ndb

'''
TODO: 나중에 async 로 put 하는 부분과 
to_dict 메소드의 커스터마이징 버전을 Model 자체적으로 메소드를 가지게 바꾸는게 좋으듯...
ref - https://developers.google.com/appengine/docs/python/ndb/async
'''

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