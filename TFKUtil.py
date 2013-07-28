# -*- coding: utf8 -*-

from google.appengine.ext import ndb

def dictWithKey(model):
	result = model.to_dict()
	result['id'] = model.key.urlsafe()
	return result