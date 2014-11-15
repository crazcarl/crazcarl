from handlers.base import AppHandler
from google.appengine.ext import db
import json
import secret
import hmac

class SetHandler(AppHandler):
	def get(self):
		init_cookies(self)
		lb = LeaderBoard.all().order('-score').fetch(25)
		self.render('setgame.html',lb=lb)
		
	def post(self):

		score = self.getValidatedScore()
	
		try:
			score = int(score)
		except:
			return self.finished(lb,0)
		
		name = self.request.get('name')
		
		if not score:
			return self.finished(lb,0)
		
		
		lb = LeaderBoard.all().order('-score').fetch(25)
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
		return self.finished(lb,1,score)
		
		
	def finished(self,lb,result):
	
		if not lb:
			lb = LeaderBoard.all().order('-score').fetch(25)
	
		# sort leaderboard
		lb = sorted(lb, key=lambda x: -x.score)
		
		
		# convert to passable array
		inner_array = []
		for l in lb:
			inner_array.append([l.name,l.score])
			
		array = {'lb':inner_array,'result':result}
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(array))
		
	def checkSet(self):
		score = self.getValidatedScore()
		score += 1
		self.response.headers.add_header('Set-Cookie', '%s=%s' % ('score',make_secure_val(score)))
		array = {'score':score}
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(array))
		
		
	# Pass in score|hash. If valid, return score. Else, init cookies back to zero.
	def getValidatedScore(self):
		score = self.request.cookies.get('score')
		if not score:
			init_cookies(self)
			return 0
			
		# Validate it
		if not check_secure_val(score):
			init_cookies(self)
			return 0
		
		return int(score.split('|')[0])
		

# Function to help with cookie hashing
def hash_str(s):
	return hmac.new(secret.SECRET, s).hexdigest()
def check_secure_val(secure_val):
	val = secure_val.split('|')[0]
	if secure_val == make_secure_val(val):
		return val
def make_secure_val(val):
	return '%s|%s' % (val, hash_str(str(val)))
def init_cookies(self):
	init_score = make_secure_val(0)
	self.response.headers.add_header('Set-Cookie', '%s=%s' % ('score',init_score))
		
		

class LeaderBoard(db.Model):
	name = db.StringProperty(required = True)
	score = db.IntegerProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)