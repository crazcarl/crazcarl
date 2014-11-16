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
		
		# If score is 0
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
		
		
	def finished(self,lb,result=0):
	
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
		setAr = [int(self.request.get('0')),int(self.request.get('1')),int(self.request.get('2'))]
		result = evaluate(setAr)
		array = {}
		if not result:
			array['result'] = 0
		else:
			score = self.getValidatedScore()
			score += 1
			self.response.headers.add_header('Set-Cookie', '%s=%s' % ('score',make_secure_val(score)))
			array['result']=1
			array['score']=score
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
		
		
		
def evaluate(setAr):
		
	success = True
	
	# evaluate fill
	if ((fill(setAr[0]) == fill(setAr[1]) and fill(setAr[1]) <> fill(setAr[2])) or 
		(fill(setAr[0]) <> fill(setAr[1]) and fill(setAr[1]) == fill(setAr[2])) or
		(fill(setAr[0]) == fill(setAr[2]) and fill(setAr[0]) <> fill(setAr[1]))):
		success = False
	
	# evaluate qty
	if ((qty(setAr[0]) == qty(setAr[1]) and qty(setAr[1]) <> qty(setAr[2])) or 
		(qty(setAr[0]) <> qty(setAr[1]) and qty(setAr[1]) == qty(setAr[2])) or 
		(qty(setAr[0]) == qty(setAr[2]) and qty(setAr[0]) <> qty(setAr[1]))):
		success = False
		
	# evaluate shape
	if ((shape(setAr[0]) == shape(setAr[1]) and shape(setAr[1]) <> shape(setAr[2])) or 
		(shape(setAr[0]) <> shape(setAr[1]) and shape(setAr[1]) == shape(setAr[2])) or
		(shape(setAr[0]) == shape(setAr[2]) and shape(setAr[0]) <> shape(setAr[1]))):
		success = False
	
	# evaluate color
	if ((color(setAr[0]) == color(setAr[1]) and color(setAr[1]) <> color(setAr[2])) or 
		(color(setAr[0]) <> color(setAr[1]) and color(setAr[1]) == color(setAr[2])) or
		(color(setAr[0]) == color(setAr[2]) and color(setAr[0]) <> color(setAr[1]))):
		success = False
	
	return success


# Notes on element values:
#  N <= 27           = Solid
#  N > 27 && <= 54   = Stripes
#  N > 54            = Blank
#  N % 3 == 1        = Qty 1
#  N % 3 == 2        = Qty 2
#  N % 3 == 0        = Qty 0
#  N % 9 == 1,2,3    = Red
#  N % 9 == 4,5,6    = Purple
#  N % 9 == 7,8,0    = Green
#  N % 27 == 1-9     = Squiggle
#  N % 27 == 10-18   = Diamond
#  N % 27 == 19-26,0 = Oval

def fill(val):
	if (val <= 27):
		return 1  # Solid
	if (val <= 54):
		return 2  # Stripes
	return 3	  # Blank


def qty(val):
	if (val % 3 == 1):
		return 1
	if (val % 3 == 2):
		return 2
	return 3


def shape(val):
	val = val % 27
	if (val >= 1 and val <= 9):
		return 1
	if (val >= 10 and  val <= 18):
		return 2
	return 3


def color(val):
	val = val % 9
	if (val >= 1 and val <= 3):
		return 1
	if (val >= 4 and  val <= 6):
		return 2
	return 3
		

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