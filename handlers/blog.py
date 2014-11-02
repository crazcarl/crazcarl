from handlers.base import AppHandler
from google.appengine.ext import db
from google.appengine.api import memcache
from main import root_dir
import os
bp_dir = os.path.join(root_dir, 'bps')


class BlogHandler(AppHandler):
	def get(self):
		bps = self.getFP()
		people = Player.all().fetch(100)
		self.render('base.html',bps=bps,people=people)
	def getFP(self,newpost = []):
		bps = memcache.get("frontpage")
		if not bps:
			bps = BlogPost.all().order('-created').fetch(20)
			bps = list(bps)
			memcache.set("frontpage",bps)
		if newpost:
			bps = newpost + bps
			if len(bps) > 20:
				bps.pop()
			memcache.set("frontpage",bps)
		return bps

class PersonHandler(BlogHandler):
	#show person screen
	def person(self,player):
		p = Player.all().filter('name =', player).get()
		if not p:
			self.redirect_to('blog')
			return None
		priorities = Priorities.all().filter('player =', p).get()
		self.render('person.html',player=p,priorities=priorities)
		
	#show create screen
	def get(self):
		self.render('create_player.html')
	
	#create new user
	def post(self):
		user = self.request.get('username')
		password = self.request.get('password')
		
		if not user or not password:
			self.render('create_player.html',error="failed")
			return None
			
		# check for dup user
		players = db.GqlQuery("Select * from Player")
		
		for p in players:
			if user == p:
				self.render('create_player.html',error="failed")
				return None
		
		# add new user
		u = Player(name=user)
		u.put()
		self.render('create_player.html',error="success")

#For Updating Progress
class ProgressHandler(BlogHandler):	
	def get(self,player):
		#get priorities
		p = Player.all().filter('name =', player).get()
		if not p:
			self.redirect_to('update', player=player)
			return None
		priorities = Priorities.all().filter('player =', p).get()
		bricks = p.progress
		self.render('update.html',player=player,priorities=priorities,bricks=bricks)
		
	def post(self,player):
		pw = self.request.get('password')
		if pw <> "asdf":
			self.redirect_to('person',player=player)
			return None
		priorities=self.request.get('priorities')
		progress=self.request.get('progress')
		bricks=self.request.get('bricks')
		
		if not progress and not priorities:
			self.redirect_to('person',player=player)
			return None
			
		p = Player.all().filter('name =', player).get()
		if not p:
			self.redirect_to('update',player=player)
			return None
		
		if progress:
			# Add to progress
			prog_note = ProgressNote(content=progress, player=p)
			prog_note.put()
		if priorities:
			# Update priorities
			pt = Priorities.all().filter('player =',p).get()
			if not pt:
				pt = Priorities(content=priorities,player=p)
			else:
				pt.content = priorities
			pt.put()
		if bricks:
			p.progress = int(bricks)
			p.put()
		self.redirect_to('person',player=player)
	
class NewPostHandler(BlogHandler):
	def get(self):
		self.render('newpost.html')
		
	def post(self):
		file = self.request.get('datafile')
		file = os.path.join(bp_dir,file)
		file = os.path.abspath(file)
		message = ""
		content = ""
		pw = self.request.get('pw')
		if not pw or pw != "asdf":
			message += "Wrong pw try again. "
		if os.path.isfile(file):
			content = open(file, 'r')
		if not content:
			message += "The file selected contains no content. "
			message += str(file)
		title = self.request.get('title')
		if not title:
			message += " Please enter a title. "
		author = self.request.get('author')
		if not author:
			message += " Please enter an author. "
		tags = self.request.get('tags').split(',')
		if message:
			self.render('newpost.html',message=message)		
			return None
		else:
			content = content.read()
			bp = BlogPost(content=content,title=title,author=author,tags=tags)
			bp.put()
			x = self.getFP(newpost = [bp])
		self.redirect_to('blog')
		
class BlogPost(db.Model):
	title = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	author = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	tags = db.StringListProperty()

class Player(db.Model):
	name = db.StringProperty(required = True)
	progress = db.IntegerProperty()
	
class ProgressNote(db.Model):
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty (auto_now_add = True)
	player = db.ReferenceProperty(Player)

class Priorities(db.Model):
	content = db.TextProperty(required = True)
	player = db.ReferenceProperty(Player)
