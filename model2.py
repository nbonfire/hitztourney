from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Table, Text, create_engine, Column, Integer, String, PickleType, DateTime, func
from sqlalchemy.orm import relationship, backref, sessionmaker
import json, io, pickle, datetime, itertools, pprint, os

from sortedcollection import *
from trueskill import *

env=TrueSkill() # current season
overallenv=TrueSkill()
teamenv=TrueSkill() #current season
overallteamenv=TrueSkill()

currentseasonstartdate=datetime.datetime(2016,9,1)


RESET=0
SIGMA_CUTOFF=5.0
DB_FILENAME="hitz.sqlite"

Base = declarative_base()


class Hitter(Base):
	__tablename__='hitters'
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	#teams = relationship("Team", backref="hitter")
	overallrating = Column(PickleType)
	rating = Column(PickleType) # current season rating
	lastGamePlayed = Column(DateTime)
	def __init__(self, name,lastGamePlayed = datetime.datetime(2013,7,1),rating = env.Rating()):
		self.name = name
		self.lastGamePlayed = lastGamePlayed
		self.rating = rating
		self.overallrating=rating

	def hitzskill(self):
		return float(int((self.rating.mu - 3.0*self.rating.sigma)*100))/100.0
	def overallhitzskill(self):
		return float(int((self.overallrating.mu - 3.0*self.overallrating.sigma)*100))/100.0
	def recordstring(self, date=currentseasonstartdate):
		winninggames=0
		totalgames=0
		for team in self.teams:
			totalgames=totalgames+len(team.homegames)+len(team.awaygames)
			winninggames=winninggames+len(team.winninggames)
		return "%d - %d" %(winninggames, (totalgames-winninggames))
	def __repr__(self):
		return "<%s, %s, %s>" % (self.name, self.lastGamePlayed, str(self.rating.mu - 3.0*self.rating.sigma))
	def shortdict(self):
		return {
			'name':self.name,
			'record':self.recordstring(),
			'skill':self.hitzskill(),
			'overallskill':self.overallhitzskill()
		}



hitter_team_table = Table('hitter_team', Base.metadata,
	Column('team_id', Integer, ForeignKey('teams.id')),
	Column('hitter_id', Integer, ForeignKey('hitters.id'))

)

games_teams = Table('game_team', Base.metadata,
	Column('team_id', Integer, ForeignKey('teams.id')),
	Column('game_id', Integer, ForeignKey('games.id')))

class Team(Base):
	__tablename__='teams'
	id = Column(Integer,primary_key=True)
	name=Column(String)
	teamrating = Column(PickleType)
	overallteamrating = Column(PickleType)
	hitters = relationship("Hitter", secondary=hitter_team_table, backref='teams')

	def __init__(self):
		self.teamrating = teamenv.Rating()
		self.overallteamrating = overallteamenv.Rating()
	def __repr__(self):
		return "<%s, %s, %s last played: %s team rating: %s>" % (self.hitters[0].name, self.hitters[1].name, self.hitters[2].name, self.getdatelastplayed(),str(self.teamrating.mu - 3.0*self.teamrating.sigma))

	def tupleratings(self):
		ratingslist=[]
		for player in self.hitters:
			ratingslist.append(player.rating)

		return tuple(ratingslist)
	def tupleoverallratings(self):
		ratingslist=[]
		for player in self.hitters:
			ratingslist.append(player.overallrating)

		return tuple(ratingslist)
	def teamskill(self):
		return (self.teamrating.mu - 3.0*self.teamrating.sigma)
	def overallteamskill(self):
		return (self.overallteamrating.mu - 3.0*self.overallteamrating.sigma)
	def setdatelastplayed(self, datePlayed=datetime.datetime.today()):
		
		for player in self.hitters:
			if datePlayed > player.lastGamePlayed:
				player.lastGamePlayed =datePlayed
		
	def getdatelastplayed(self):
		comparedate=datetime.datetime.today()
		for player in self.hitters:
			if player.lastGamePlayed < comparedate:
				comparedate=player.lastGamePlayed
		return comparedate
	def listnames(self):
		return "%s, %s, %s"% (self.hitters[0].name, self.hitters[1].name, self.hitters[2].name)
	def listofnames(self):
		return [self.hitters[0].name, self.hitters[1].name, self.hitters[2].name]
	def getteamrating(self):
		sumindividual=0.0
		for player in self.hitters:
			sumindividual=sumindividual+player.hitzskill()
		avgindividual= sumindividual/len(self.hitters)
		
		if avgindividual>self.teamskill():
			return avgindividual
		else:
			return self.teamskill()
	def getoverallteamrating(self):
		sumindividual=0.0
		for player in self.hitters:
			sumindividual=sumindividual+player.overallhitzskill()
		avgindividual= sumindividual/len(self.hitters)
		
		if avgindividual>self.overallteamskill():
			return avgindividual
		else:
			return self.overallteamskill()

		

class Game(Base):
	__tablename__='games'
	id = Column(Integer, primary_key=True)

	teams = relationship("Team", secondary=games_teams, backref='games')

	#hometeam = ManyToOne('Teams', inverse='homegames')
	hometeam_id = Column(Integer, ForeignKey('teams.id'))
	hometeam = relationship("Team",
		primaryjoin=('games.c.hometeam_id==teams.c.id'),
		remote_side='Team.id',
		backref=backref('homegames', order_by=id))
	
	#awayteam = ManyToOne('Teams', inverse='awaygames')
	awayteam_id = Column(Integer, ForeignKey('teams.id'))
	awayteam = relationship("Team", 
		primaryjoin=('games.c.awayteam_id==teams.c.id'),
		remote_side='Team.id',
		backref=backref('awaygames', order_by=id))
	
	#winner = ManyToOne('Teams', inverse = 'winner')
	winner_id = Column(Integer, ForeignKey('teams.id'))
	winner = relationship('Team',
		primaryjoin=('games.c.winner_id==teams.c.id'),
		remote_side='Team.id', 
		backref=backref('winninggames', order_by=id))
	
	awaypoints = Column(Integer)
	homepoints = Column(Integer)
	#date = Field(DateTime, default=datetime.datetime.now())
	date = Column(DateTime)
	#event = Field(UnicodeText)
	event = Column(String)
	#gameNumber = Field(Integer)
	gameNumber = Column(Integer)
	def __init__(self, hometeam, awayteam, winner, homepoints=0,awaypoints=0, date = datetime.datetime.now() ):
		self.date = date
		self.hometeam = hometeam
		self.awayteam = awayteam
		self.teams = [hometeam,awayteam]
		self.winner = winner
		self.awaypoints = awaypoints
		self.homepoints = homepoints
	def winposition(self):
		if self.winner_id == self.hometeam_id:
			return "home"
		elif self.winner_id == self.awayteam_id:
			return "away"
		else:
			return "can't tell - winner: %s, home: %s, away: %s, names: %s" % (self.winner_id, self.hometeam_id, self.awayteam_id, self.winner.names())
	def __repr__(self):
		return "<%s -  %s vs %s - %s won>" %(self.date, self.awayteam, self.hometeam, self.winner)
	def _asdict(self):
		return {
			'id':self.id,
			'away':self.awayteam.listofnames(),
			'home':self.hometeam.listofnames(),
			'winner':self.winposition(),
			'date':datetime.datetime.strftime(self.date,'%Y-%m-%d'),
			'score':{
						'home':self.homepoints,
						'away':self.awaypoints
					}
		}




def get_or_create(session, model, **kwargs):
	instance = session.query(model).filter_by(**kwargs).first()
	if instance:
		return instance
	else:
		instance = model(**kwargs)
		session.add(instance)
		session.commit()
		return instance
	# myHitter = get_or_create(session, Hitter, name=hitterName)
def get_or_create_team(session, findplayers):
	#print findplayers
	create_team = session.query(Team).filter(Team.hitters.any(Hitter.name==findplayers[0])).filter(Team.hitters.any(Hitter.name==findplayers[1])).filter(Team.hitters.any(Hitter.name==findplayers[2])).first()
	#session.query(Team).filter(Team.players.in_()) session.query(Hitter).name.in_(session)
	if not create_team:
		#create_team = Team()
		hittersforthisteam = []
		for newplayer in findplayers:
			hittersforthisteam.append(session.query(Hitter).filter_by(name=newplayer).first())
		if len(hittersforthisteam)<3:
			print "invalid player in list: %s" % findplayers
			return False
		else:
			create_team = Team()
			create_team.hitters = hittersforthisteam
			session.add(create_team)
			session.commit()
	return create_team
def getGamesForHitter(session, player, date=currentseasonstartdate):
	return session.query(Game).join(Team.games).filter(Team.hitters.contains(player)).filter(Game.date>=date).order_by(Game.date.desc()).all()

def getRecordsBelowSigma(session, sigma=SIGMA_CUTOFF):
	records = session.query(Hitter).all()
	recordsbelowsigma = []
	#for record in records:
		#print "-" * 20
		#print record.name
	
	for record in records:
		if record.rating.sigma < sigma:
			recordsbelowsigma.append(record)
	recordsbelowsigma.sort(key=lambda player: player.rating.hitzskill())
	return recordsbelowsigma



def getStrength(session, homeNames,awayNames):
	#
	# AKA the draw probability. Return value is *10000 to make it easier for output on the page.
	# ({'name':'alice','rating':2.0},{'name':'bob','rating':1.4},{'name':'charlie','rating':3.2})
	#
	homeTeam=get_or_create_team(session, homeNames)
	awayTeam=get_or_create_team(session, awayNames)
	homeRatings = homeTeam.tupleoverallratings()
	awayRatings = awayTeam.tupleoverallratings()
	return int(env.quality([homeRatings,awayRatings])*10000)

def getWinProb(rA=env.Rating(), rB=env.Rating()):
	#
	# Using formula from https://github.com/sublee/trueskill/issues/1
	# Only working for 1v1 :( plus
	# Needs to be determined how accurate this is... does it need half the draw percent removed?
	deltaMu = rA.mu - rB.mu
	rsss = sqrt(rA.sigma**2 + rB.sigma**2)
	return trueskill.mathematics.cdf(deltaMu/rsss)

def jsonbackup(session):
	results = []
	names = []
	allgames = session.query(Game).all()
	allhitters=session.query(Hitter).all()
	for hitter in allhitters:
		names.append(hitter.name)

	for game in allgames:
		results.append(game._asdict())

	with io.open('playersbackup-%s.txt'% str(datetime.date.today()), 'w', encoding='utf-8') as fn:
		fn.write(unicode(json.dumps(names, ensure_ascii=False)))
	with io.open('gamesbackup-%s.txt'% str(datetime.date.today()), 'w', encoding='utf-8') as fg:
		fg.write(unicode(json.dumps(results, ensure_ascii=False)))
	return json.dumps(results)

def jsonrestore(namefile='playersbackup.txt', gamefile='gamesbackup.txt'):
	if not os.path.exists(DB_FILENAME):
		session=standaloneSetup()
		results=[]
		names=[]

		with io.open(namefile, 'r', encoding='utf-8') as fn:
			names=json.loads(fn.read())
		with io.open(gamefile, 'r', encoding='utf-8') as fg:
			results=json.loads(fg.read())
		#pprint.pprint(names)
		#pprint.pprint( results)
		
		for name in names:
			get_or_create(session, Hitter, name=name)
		for game in results:
			completeGame(session,game['home'], game['away'], game['winner'], game['score']['away'], game['score']['home'], datetime.datetime.strptime(game['date'], '%Y-%m-%d'))
		session.close()
	else:
		print "DB file "+DB_FILENAME+" already exists. Delete or move it before running this command."

def getLastPlayed(session, homeNames,awayNames):
	#
	# ({'name':'alice','dateplayed':"7/10/13"},{'name':'bob','dateplayed':"7/10/13"},{'name':'charlie','dateplayed':"7/10/13"})
	#
	homeTeam=get_or_create_team(session, homeNames)
	awayTeam=get_or_create_team(session, awayNames)
	homeDate = homeTeam.getdatelastplayed()
	awayDate = awayTeam.getdatelastplayed()
	if homeDate<awayDate:
		return homeDate
	else:
		return awayDate

def completeGame(session,homeTeam,awayTeam,winner,awaypoints=0,homepoints=0,datePlayed=datetime.datetime.today()):
	homers=get_or_create_team(session, homeTeam)
	awayers=get_or_create_team(session, awayTeam)
	homers.setdatelastplayed(datePlayed)
	awayers.setdatelastplayed(datePlayed)

	#print "\n----------\n%s vs %s  " % (awayers, homers)
	
	if winner=='home':
		winningteam=get_or_create_team(session, homeTeam)
		#team rating
		if (datePlayed>currentseasonstartdate):
			homers.teamrating,awayers.teamrating = rate_1vs1(homers.teamrating, awayers.teamrating)
			#individual ratings
			(awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating),(homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating) = rate([[awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating],[homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating]], ranks=[1,0])
		homers.overallteamrating,awayers.overallteamrating = rate_1vs1(homers.overallteamrating, awayers.overallteamrating)
		(awayers.hitters[0].overallrating, awayers.hitters[1].overallrating, awayers.hitters[2].overallrating),(homers.hitters[0].overallrating, homers.hitters[1].overallrating, homers.hitters[2].overallrating) = rate([[awayers.hitters[0].overallrating, awayers.hitters[1].overallrating, awayers.hitters[2].overallrating],[homers.hitters[0].overallrating, homers.hitters[1].overallrating, homers.hitters[2].overallrating]], ranks=[1,0])

			
	else:
		winningteam=get_or_create_team(session, awayTeam)
		

		if (datePlayed>currentseasonstartdate):
			#team ratings
		
			awayers.teamrating,homers.teamrating = rate_1vs1(awayers.teamrating, homers.teamrating)
			#individual ratings
			(awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating),(homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating) = rate([[awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating],[homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating]], ranks=[0,1])
		awayers.overallteamrating,homers.overallteamrating = rate_1vs1(awayers.overallteamrating, homers.overallteamrating)
			#individual ratings
		(awayers.hitters[0].overallrating, awayers.hitters[1].overallrating, awayers.hitters[2].overallrating),(homers.hitters[0].overallrating, homers.hitters[1].overallrating, homers.hitters[2].overallrating) = rate([[awayers.hitters[0].overallrating, awayers.hitters[1].overallrating, awayers.hitters[2].overallrating],[homers.hitters[0].overallrating, homers.hitters[1].overallrating, homers.hitters[2].overallrating]], ranks=[0,1])

	newgame = Game(hometeam=homers, awayteam=awayers, homepoints=homepoints, awaypoints=awaypoints, winner=winningteam,date=datePlayed)
	session.add(newgame)
	session.commit()

def newSeasonRatingRecalculation(session, newDate=datetime.datetime.today()):
	global currentseasonstartdate
	currentseasonstartdate = newDate
	games = session.query(Game).filter(Game.date>newDate).all()
	hitters = session.query(Hitter).all()
	teams = session.query(Team).all()
	#reset current ratings
	for team in teams:
		team.teamrating = env.Rating()
	for hitter in hitters:
		hitter.rating = env.Rating()

	#start calculating new rating
	for game in games:
		homers = game.hometeam
		awayers= game.awayteam
		winners = game.winner
		if homers == winners:
			homers.teamrating,awayers.teamrating = rate_1vs1(homers.teamrating, awayers.teamrating)
			#individual ratings
			(awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating),(homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating) = rate([[awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating],[homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating]], ranks=[1,0])

		elif awayers == winners:
			awayers.teamrating,homers.teamrating = rate_1vs1(awayers.teamrating, homers.teamrating)
			#individual ratings
			(awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating),(homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating) = rate([[awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating],[homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating]], ranks=[0,1])
		else:
			print "Something went wrong. Winners %s Home team %s Away Team %s" % (winners, homers, awayers)
	session.commit()

def getPlayersForTemplate(session, checkedPlayers=['Nick', 'Rosen', 'Magoo', 'White Rob', 'Ziplox', 'Ced']):
	players = session.query(Hitter).all()
	names = []

	for player in players:
		if player.name in checkedPlayers:
			isChecked=True
		else:
			isChecked = False
		names.append({'name':player.name, 'isChecked': isChecked, 'playerrank':player.hitzskill(), 'overallplayerrank':player.overallhitzskill()} )
	names.sort(key=lambda player: player['playerrank'], reverse=True)
	return names
def getUserList(session):
	players=sorted(session.query(Hitter).all())
	listofplayers=[]
	for player in players:
		listofplayers.append(player.shortdict())
	listofplayers.sort(key=lambda k: k['skill'], reverse=True)
	
	return listofplayers
	#return [item for sublist in session.query(Hitter.name).all() for item in sublist] 
def getGameHistoryForUser(session, hitterObject, date=datetime.datetime(2013,1,1)):
	gameids=session.query(Game.id).join(Game.awayteam).join(Team.hitters).filter(
		Team.hitters.contains(hitterObject)).filter(Game.date>date).distinct(
		).all() + session.query(Game.id).join(Game.hometeam).join(Team.hitters).filter(Team.hitters.contains(
		hitterObject)).filter(Game.date>date).distinct().all()
	gameslist = []
	for game in session.query(Game).filter(Game.id.in_(flatten(gameids))).all():
		gamedict=game._asdict()
		gamedict['record']=getTeamVsRecord(session, hitterObject, game.awayteam, game.hometeam)
		if hitterObject.name in gamedict[gamedict['winner']]:
			gamedict['winstatus']="win"
		else:
			gamedict['winstatus']='loss'
		gameslist.append(gamedict)
	gameslist.sort(key=lambda k: k['id'], reverse=True)
	return gameslist

def getTeamVsRecord(session, hitterObject, awayteam, hometeam):
	#	gamealias=aliased(Game)
	#	session.query(Game).join(Game.awayteam).join(gamealias.hometeam).filter(gamealias.hometeam = hometeam).filter(Game.awayteam = awayteam)
	
	homegames=flatten(session.query(Game.id).join(Game.hometeam).filter(Game.hometeam==hometeam).all())
	homegamesagainstsecondteam=flatten(session.query(Game.id).join(Game.awayteam).filter(Game.awayteam==awayteam).filter(Game.id.in_(homegames)).all())
	awaygames=flatten(session.query(Game.id).join(Game.awayteam).filter(Game.awayteam==hometeam).all())
	awaygamesagainstsecondteam=flatten(session.query(Game.id).join(Game.hometeam).filter(Game.hometeam==awayteam).filter(Game.id.in_(awaygames)).all())
	allgames=homegamesagainstsecondteam+awaygamesagainstsecondteam
	homewins=0
	awaywins=0
	for game in session.query(Game).filter(Game.id.in_(allgames)).all():
		if game.winner == awayteam:
			awaywins= awaywins+1 
		else:
			homewins = homewins+1
	percentage = float(int(float(awaywins*10000)/float(awaywins + homewins)))/100.0 
	return {'record':'%d - %d'%(awaywins, homewins), 'percentagewon':percentage}


def currentSeasonRecordString(session, hitterObject):
	gameids=session.query(Game.id).join(Game.awayteam).join(Team.hitters).filter(
		Team.hitters.contains(hitterObject)).filter(Game.date>currentseasonstartdate).distinct().all() + session.query(
		Game.id).join(Game.hometeam).join(Team.hitters).filter(
		Team.hitters.contains(hitterObject)).filter(Game.date>currentseasonstartdate).distinct().all()
	winninggames=0
	games=session.query(Game).filter(Game.id.in_(flatten(gameids))).all()
	for game in games:
		gamedict=game._asdict()
		if hitterObject.name in gamedict[gamedict['winner']]:
			winninggames = winninggames + 1
	totalgames=len(games)
	return "%d - %d" % (winninggames, (totalgames-winninggames))

def recordstring1v1(session, playername, opponentname):
	player=get_or_create(session, Hitter, name=playername)
	opponent=get_or_create(session, Hitter, name=opponentname)
	return record1v1(session, player, opponent)

def record1w1(session, player, partner):  # record for hitter player with hitter partner on the same team
	playerHomeGameids=session.query(Game.id).join(Hitter.teams).join(Team.homegames).filter(Game.date>currentseasonstartdate).filter(Team.hitters.contains(player)).filter(Team.hitters.contains(partner)).distinct().all()
	
	playerAwayGameids=session.query(Game.id).join(Hitter.teams).join(Team.awaygames).filter(Game.date>currentseasonstartdate).filter(Team.hitters.contains(player)).filter(Team.hitters.contains(partner)).distinct().all()
	playerWinninggamecount=len(flatten(session.query(Game.id).join(Hitter.teams).join(Team.winninggames).filter(Team.hitters.contains(player)).filter(Team.hitters.contains(partner)).filter(Game.id.in_(flatten(playerHomeGameids + playerAwayGameids))).distinct().all()))
	#playerWinninggamecount = len(flatten(session.query(Game.id).join(Hitter.teams).join(Team.winninggames).filter(Game.id.in_(flatten(playerHomegameids + playerAwaygameids))).filter(Team.hitters.contains(player)).filter(Team.hitters.contains(partner)).distinct().all()))
	playerTotalgamecount = len(flatten(playerHomeGameids + playerAwayGameids))
	#print (player.name, partner.name)
	#print playerWinninggamecount
	#print playerTotalgamecount
	#print (playerHomeGameids, playerAwayGameids)
	if playerTotalgamecount>0:
		percentagewon=float(int(float(playerWinninggamecount*10000)/float(playerTotalgamecount)))/100.0
	else:
		percentagewon=0
	return {'record':"%d - %d" %(playerWinninggamecount, (playerTotalgamecount-playerWinninggamecount)), 'percentagewon':percentagewon, 'partnersigma':partner.rating.sigma}

def record1v1(session, player, opponent): # record for hitter player against hitter partner (separate teams)
	
	playerHomeGameids=session.query(Game.id).join(Hitter.teams).join(Team.homegames).filter(Team.hitters.contains(player)).filter(Game.date>currentseasonstartdate).distinct().all()
	playerAwayGameids=session.query(Game.id).join(Hitter.teams).join(Team.awaygames).filter(Team.hitters.contains(player)).filter(Game.date>currentseasonstartdate).distinct().all()
	playerVsOpponenthomegameids=session.query(Game.id).join(Hitter.teams).join(Team.awaygames).filter(Team.hitters.contains(opponent)).filter(Game.id.in_(flatten(playerHomeGameids))).distinct().all()
	playerVsOpponentawaygameids=session.query(Game.id).join(Hitter.teams).join(Team.homegames).filter(Team.hitters.contains(opponent)).filter(Game.id.in_(flatten(playerAwayGameids))).distinct().all()
	playerVsOpponentwinninggamecount = len(flatten(session.query(Game.id).join(Hitter.teams).join(Team.winninggames).filter(Game.id.in_(flatten(playerVsOpponenthomegameids + playerVsOpponentawaygameids))).filter(Team.hitters.contains(player)).distinct().all()))
	#print playerVsOpponentwinninggamecount 
	#print flatten(playerVsOpponenthomegameids+playerVsOpponentawaygameids)
	playerVsOpponenttotalgamecount = len(flatten(playerVsOpponenthomegameids + playerVsOpponentawaygameids))
	#return playerVsOpponentwinninggamecount 
	if playerVsOpponenttotalgamecount>0:
		percentagewon=float(int(float(playerVsOpponentwinninggamecount)*10000/float(playerVsOpponenttotalgamecount)))/100.0
	else:
		percentagewon=0
	return {'record':"%d - %d" % (playerVsOpponentwinninggamecount, (playerVsOpponenttotalgamecount-playerVsOpponentwinninggamecount)), 'percentagewon':percentagewon, 'opponentsigma':opponent.rating.sigma, 'totalgames':playerVsOpponenttotalgamecount}


def flatten(listtoflatten):
	return [item for sublist in listtoflatten for item in sublist]

def bffs(session, hitterobject): 
	#
	# Something funky here, double check results.
	#
	bffs=session.query(Hitter).join(Hitter.teams).filter(Team.hitters.contains(hitterobject)).filter(
    	Hitter.name!=hitterobject.name).distinct().all()
	listofbffs=[]

	for bff in bffs:
		bffrecord = record1w1(session, hitterobject, bff)
		if bffrecord['partnersigma']<SIGMA_CUTOFF:
			listofbffs.append({
				'name':bff.name,
				'record':bffrecord,
				'skill':bff.hitzskill(),
				'overallskill':bff.overallhitzskill()
			})
	listofbffs.sort(key=lambda k: k['skill'], reverse=True)
	listofbffs.sort(key=lambda k: k['record']['percentagewon'], reverse=True)
	return listofbffs[:5]

def bestTeams(session, hitterobject):
	teams=sorted(session.query(Team, func.count(Game.id)).join(Team.winninggames).filter(
    	Team.hitters.contains(hitterobject)).group_by(Team).all(),
    	key=lambda x:x[1], reverse=True)
	listofteams=[]
	for besty in teams:
		team=besty[0]
		totalcount=flatten(session.query(Game.id).join(Game.hometeam).filter(
			Game.hometeam==team).all()) + flatten(session.query(Game.id).join(Game.awayteam).filter(
			Game.awayteam==team).all())
		print totalcount
		totalcount=len(totalcount)
		wincount=besty[1]
		if totalcount>0:
			wonpercentage=(float(int(float(wincount*10000)/float(totalcount)))/100.0)
		else:
			wonpercentage=0.0
		if wincount>1:
			listofteams.append({
				'names':team.listnames(),
				'teamskill':float(int(team.getteamrating()*100))/100.0,
				'overallteamskill':float(int(team.getoverallteamrating()*100))/100.0,
				'record':{'record':'%d - %d' % (wincount,totalcount-wincount), 
					'percentagewon':wonpercentage
				}
			})
	listofteams.sort(key=lambda k: k['teamskill'], reverse=True)
	listofteams.sort(key=lambda k: k['record']['percentagewon'], reverse=True)
	return listofteams[:5]

def outforbloods(session, hitterobject):
	
	ofbs=session.query(Hitter).filter(
    	Hitter.name!=hitterobject.name).distinct().all()
	listofofbs=[]
	for ofb in ofbs:
		ofbrecord=record1v1(session, hitterobject, ofb)
		if (ofbrecord['opponentsigma']<SIGMA_CUTOFF) and ((ofbrecord['percentagewon']<40.0) and (ofbrecord['totalgames']>0)):
			listofofbs.append({
				'name':ofb.name,
				'record':ofbrecord,
				'skill':ofb.hitzskill(),
				'overallskill':ofb.overallhitzskill()
			})
	listofofbs.sort(key=lambda k: k['skill'], reverse=True)
	listofofbs.sort(key=lambda k: k['record']['percentagewon'])
	return listofofbs[:5]

def rivals(session, hitterobject):
	
	rivals=session.query(Hitter).filter(
    	Hitter.name!=hitterobject.name).distinct().all()
	listofrivals=[]
	for rival in rivals:
		listofrivals.append({
				'name':rival.name,
				'record':record1v1(session, hitterobject, rival),
				'skill':rival.hitzskill(),
				'overallskill':rival.overallhitzskill()
			})
		#print "%s - %s"%(rival.name, record1v1(session, rival, hitterobject))
	listofrivals.sort(key=lambda k: k['skill'], reverse=True)

	listofrivals.sort(key=lambda k: (50-k['record']['percentagewon'])**2)
	return listofrivals[:5]


def standaloneSetup():
	engine = create_engine('sqlite:///'+DB_FILENAME)
	

	Session = sessionmaker(bind=engine)

	session = Session()
	Base.metadata.create_all(engine)
	return session


if __name__ == "__main__":
	
	if RESET==1:
		jsonrestore()
	#Base = declarative_base()
	engine = create_engine('sqlite:///'+DB_FILENAME)
	

	Session = sessionmaker(bind=engine)

	session = Session()
	Base.metadata.create_all(engine)

	#setup_all()
	#create_all()
	hitlist=[]
	players = ["Adi","Bader","Ced","Gio","James","Keedy","Jesse","Jon","Kent","Koplow","Magoo","Nick","Rosen","McGilloway","White Rob","Ziplox", 'Drew', 'Crabman'];
	for player in players:
		#Hitters.get_by_or_init(name=player)
		currentplayer=get_or_create(session, Hitter, name=player)
		session.add(currentplayer)
		hitlist.append(currentplayer)
	session.commit()
	
			
			
			
			

	
		#thisgame = Games.get_by_or_init(hometeam=homers, awayteam=awayers, winner=game['winner'], date=datetime.datetime.now)
	# --------------------------------------------------
	# Simple Queries
 
	# get all the records
	#records = Hitters.query.filter(Hitters.rating.sigma<8.0).all()
	records = session.query(Hitter).all()
	recordsbelowsigma = []
	#for record in records:
		#print "-" * 20
		#print record.name
	records.sort(key=lambda player: player.rating.sigma)
	for record in records:
		if record.rating.sigma < 8.0:
			recordsbelowsigma.append(record)
			print "\n\n %s - %s"% (record.name, str(record.hitzskill()))



	recordsbelowsigma.sort(key=lambda player: player.rating.mu)
	print "\n\n\n%s\n\n\n" % recordsbelowsigma
	allteams=session.query(Team).all()
	#for allteam in allteams:
		#print "-" * 20
		#print allteam.players
	allteams.sort(key=lambda team: (team.teamrating.mu - 3*team.teamrating.sigma))
	print allteams
 
	# find a specific record

	qry = session.query(Hitter, func.count(Team.winninggames)).filter_by(name=u'Nick').all()
	#record = qry.first()
	#nickteams = record.teams.winninggames
	
	#print len(record.teams)
	#print nickteams
	print qry
	#print "%s" % (record.hitzskill())
	gamesbackup=jsonbackup(session)
	print gamesbackup
	#collectionOfGames= generateGamePermutations([i.name for i in recordsbelowsigma], 20)
	#cls()
	#print list(collectionOfGames)
	# delete the record
	#record.delete()
	#session.commit()
