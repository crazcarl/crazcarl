from handlers.base import AppHandler
from google.appengine.ext import db
import json
import secret
import hmac
from google.appengine.api import memcache
from random import randrange
import logging

class SetHandler(AppHandler):
	def get(self):
	
		# Create New Board
		board = self.generate_board()
		
		# Create New Game
		game = SetBoard(board = board)
		game.put()
		
		# Update Cookie with game ID
		self.response.headers.add_header('Set-Cookie', '%s=%s' % ('game',game.key().id()))
		
		lb = LeaderBoard.all().order('-score').fetch(25)
		self.render('setgame.html',lb=lb,board=board)
		
	# Leaderboard Submission
	def post(self):

		game = int(self.request.cookies.get('game'))
		if not game:
			return self.finished(lb,0)
			
		game = SetBoard.get_by_id(game)
		# If score is 0
		if not game.score:
			return self.finished(lb,0)
		
		name = self.request.get('name')
		
		score = game.score
		game.score = 0  # Reset Score
		game.put()
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
		# Get submitted elements
		setAr = [int(self.request.get('0')),int(self.request.get('1')),int(self.request.get('2'))]
		# Verify it is a set
		result = evaluate(setAr)		
		array = {}
		if not result:
			array['result'] = 0
		else:
			result = 0
			# Verify tiles are on board and Update SetBoard entity
			gameId = int(self.request.cookies.get('game'))
			if not gameId:
				return None;
			game = SetBoard.get_by_id(gameId)
			if game:
				newBoard = self.updateGame(game,setAr)
				if newBoard:
					score = game.score
					result = 1
				array['result'] = result
				array['score'] = score
				array['newBoard'] = newBoard
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(array))
		
	# updateGame
	# 1 Verifies set tiles are on board
	# 2 Updates SetBoard entity with new score
	# 3 Picks new tiles
	# 4 Updates SetBoard entity with new tiles
	# Returns new board if success. 0 if fail (for tiles not in board)
	def updateGame(self,game,tiles):
		
		if not game or not tiles:
			return 0
		
		# 1
		board = game.board
		for tile in tiles:
			if not tile in board:
				return 0
				
		# 2
		game.score += 1
		
		# 3
		newBoard = generRand(board,15)
		game.board = newBoard[:]
		game.board[game.board.index(tiles[0])] = newBoard[-3]
		game.board[game.board.index(tiles[1])] = newBoard[-2]
		game.board[game.board.index(tiles[2])] = newBoard[-1]
		game.board = game.board[0:12]
		
		game.put()
		
		return newBoard
		
		
	def generate_board(self,board = []):
		return generRand(board, 12)
		
	def repopulate_tiles(self):
		# get game Id
		gameId = int(self.request.cookies.get('game'))
		if not gameId:
			return None;
		game = SetBoard.get_by_id(gameId)
		
		# Create New Board
		board = self.generate_board()
		
		# Create New Game
		game.board = board
		
		# Reset Score
		rs = self.request.get('resetScore')
		if rs:
			game.score = 0;
			
		game.put()
		array = {}
		array['board'] = board
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(json.dumps(array))

		
def generRand(arr,cnt):
	if len(arr) == cnt:
		arr = []
	while len(arr) < cnt:
		randomnumber = randrange(80)+1
		found = False
		for i in arr:
			if i == randomnumber:
				found = True
				break
		if not found:
			arr.append(randomnumber)
	return arr		
		
		
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
		

		
		

class LeaderBoard(db.Model):
	name = db.StringProperty(required = True)
	score = db.IntegerProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	
class SetBoard(db.Model):
	board = db.ListProperty(required = True, item_type=int)
	score = db.IntegerProperty(required = True, default = 0)