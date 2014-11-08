from handlers.base import AppHandler
from google.appengine.ext import db
import json

class SetHandler(AppHandler):
	def get(self):
		lb = LeaderBoard.all().order('-score').fetch(25)
		self.render('setgame.html',lb=lb)
		
	def post(self):
		score = self.request.get('score')
		
		lb = LeaderBoard.all().order('-score').fetch(25)
		try:
			int(score)
			score = int(score)
		except:
			return self.finished(lb,0)
		
		name = self.request.get('name')
		
		
		
		# First 25, add to LB
		if len(lb) < 25:
			entry = LeaderBoard(name=name,
								score=score)
			entry.put()
			lb.append(entry)
			return self.finished(lb,1)
			
		# Not good enough
		if lb[-1].score > score:
			return self.finished(lb,0)
		
		
		entry = LeaderBoard(name=name,
							score=score)
		entry.put()
		
		# Get rid of last (lowest score) entry
		lb.pop()
		
		lb.append(entry)
		return self.finished(lb,1)
		
		
	def finished(self,lb,result):
		# sort leaderboard
		lb = sorted(lb, key=lambda x: -x.score)
		
		# convert to passable array
		inner_array = []
		for l in lb:
			inner_array.append([l.name,l.score])
			
		array = {'lb':inner_array,'result':result}
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(array))
		
		

class LeaderBoard(db.Model):
	name = db.StringProperty(required = True)
	score = db.IntegerProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)