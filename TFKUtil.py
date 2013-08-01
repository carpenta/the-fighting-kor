# -*- coding: utf8 -*-

from google.appengine.ext import ndb

def dictWithKey(model):
	if model is None:
		return {}

	result = model.to_dict()
	result['id'] = model.key.urlsafe()
	return result
