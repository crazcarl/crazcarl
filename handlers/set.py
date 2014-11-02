from handlers.base import AppHandler
from google.appengine.ext import db
from google.appengine.api import memcache
from main import root_dir
import os


class SetHandler(AppHandler):
	def get(self):
		self.render('setgame.html')