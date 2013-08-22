from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Table, Text, create_engine, Column, Integer, String, PickleType, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker
import json, io, pickle, datetime, itertools

from sortedcollection import *
from trueskill import *

env=TrueSkill() # current season
overallenv=TrueSkill()
teamenv=TrueSkill() #current season
overallteamenv=TrueSkill()

currentseasonstartdate=datetime.datetime(2013,4,21)


RESET=0
SIGMA_CUTOFF=8.0

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
	def __repr__(self):
		return "<%s, %s, %s>" % (self.name, self.lastGamePlayed, str(self.rating.mu - 3.0*self.rating.sigma))

hitter_team_table = Table('hitter_team', Base.metadata,
	Column('team_id', Integer, ForeignKey('teams.id')),
	Column('hitter_id', Integer, ForeignKey('hitters.id'))

)

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
	def getteamrating(self):
		sumindividual=0.0
		for player in self.hitters:
			sumindividual=sumindividual+player.hitzskill()
		avgindividual= sumindividual/len(self.hitters)
		
		if avgindividual>self.teamskill():
			return avgindividual
		else:
			return self.teamskill()
		

class Game(Base):
	__tablename__='games'
	id = Column(Integer, primary_key=True)
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
	# AKA the draw probability. Return value is *1000 to make it easier for output on the page.
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
	allgames = session.query(Game).all()

	for game in allgames:
		results.append({'away':game.awayteam.listnames(), 'home':game.hometeam.listnames(), 'winner': game.winposition(), 'score':{'away':game.awaypoints,'home':game.homepoints}, 'date': str(game.date)})

	with io.open('gamesbackup.txt', 'w', encoding='utf-8') as f:
		f.write(unicode(json.dumps(results, ensure_ascii=False)))
	return json.dumps(results)


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
	games = session.query(Game).filter(date>newDate)
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
	#defined in matchups.py
	#defaultPlayers = ['Nick', 'Ziplox', 'Rosen', 'Magoo', 'Ced', 'White Rob', 'Adi']
	for player in players:
		if player.name in checkedPlayers:
			isChecked=True
		else:
			isChecked = False
		names.append({'name':player.name, 'isChecked': isChecked, 'playerrank':player.hitzskill(), 'overallplayerrank':player.overallhitzskill()} )
	names.sort(key=lambda player: player['playerrank'], reverse=True)
	return names

if __name__ == "__main__":
	#Base = declarative_base()
	engine = create_engine('sqlite:///hitz.sqlite')
	

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
	
	if RESET==1:
		games = [
		{'away':['Nick','Ziplox','Ced'],'home':['Rosen','Crabman','Magoo'],'winner':'away', 'score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,13)},
		{'away':['Rosen','Ced','Magoo'],'home':['Nick','Ziplox','Crabman'],'winner':'away', 'score':{'away':0,'home':0},'date':datetime.datetime(2013,7,13)}, 
		{'home':['Rosen','Ced','Magoo'],'away':['Nick','Ziplox','Crabman'],'winner':'home', 'score':{'away':0,'home':0},'date':datetime.datetime(2013,7,13)},
		{'away':['Ziplox','Magoo','Nick'],'home':['Ced','Crabman','Rosen'],'winner':'away', 'score':{'away':0,'home':0},'date':datetime.datetime(2013,7,13)},
		{'away':['Ziplox','Rosen','Ced'],'home':['Nick','Magoo','Crabman'],'winner':'away', 'score':{'away':0,'home':0},'date':datetime.datetime(2013,7,13)}, 
		{'home':['Ziplox','Rosen','Ced'],'away':['Nick','Magoo','Crabman'],'winner':'home', 'score':{'away':0,'home':0},'date':datetime.datetime(2013,7,13)},
		{'home':['Ziplox','Rosen','Ced'],'away':['Nick','Magoo','Crabman'],'winner':'home', 'score':{'away':0,'home':0},'date':datetime.datetime(2013,7,13)},
		{'away':['Magoo','Crabman','Rosen'],'home':['Ziplox','Ced','Nick'],'winner':'home', 'score':{'away':0,'home':0},'date':datetime.datetime(2013,7,13)},
		{'home':['Ziplox','Rosen','Adi'],'away':['Crabman','Drew','White Rob'],'winner':'home','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['Ziplox','Nick','Adi'],'home':['Crabman','Drew','White Rob'],'winner':'away','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['Rosen','Crabman','White Rob'],'home':['Ziplox','Nick','Adi'],'winner':'home','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['Rosen','White Rob','Adi'],'home':['Ziplox','Nick','Drew'],'winner':'home','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},      
		{'away':['Rosen','White Rob','Crabman'],'home':['Ziplox','Nick','Drew'],'winner':'home','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['Drew','Adi','Crabman'],'home':['Rosen','Nick','Ziplox'],'winner':'away','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['Nick','White Rob','Rosen'],'home':['Drew','Adi','Crabman'],'winner':'home','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['Ziplox','White Rob','Rosen'],'home':['Drew','Adi','Crabman'],'winner':'away','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['White Rob','Drew','Adi'],'home':['Ziplox','Nick','Rosen'],'winner':'home','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['White Rob','Crabman','Adi'],'home':['Ziplox','Nick','Rosen'],'winner':'away','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},
		{'away':['Ziplox','Nick','Drew'],'home':['White Rob','Adi','Crabman'],'winner':'home','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},              
		{'away':['Ziplox','Rosen','Drew'],'home':['White Rob','Adi','Crabman'],'winner':'home','score':{'away':0,'home':0}, 'date':datetime.datetime(2013,7,27)},  
		{'away':['Bader','Magoo','Kent'],'home':['Adi','White Rob','Keedy'],'winner':'away', 'score':{'away':6,'home':5}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Rosen','Ziplox','Koplow'],'home':['Ced','Jon','Nick'],'winner':'away', 'score':{'away':6,'home':4}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Koplow','Ced','Jesse'],'home':['Ziplox','Adi','Bader'],'winner':'home', 'score':{'away':6,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Magoo','McGilloway','Nick'],'home':['Rosen','Gio','Kent'],'winner':'away', 'score':{'away':11,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Gio','Magoo','Jon'],'home':['Nick','Ced','Bader'],'winner':'away', 'score':{'away':14,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Koplow','McGilloway','Keedy'],'home':['White Rob','Rosen','Jesse'],'winner':'away', 'score':{'away':12,'home':10}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Keedy','Jesse','Kent'],'home':['Gio','Ced','Rosen'],'winner':'away', 'score':{'away':12,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Jon','McGilloway','Ziplox'],'home':['Magoo','Adi','White Rob'],'winner':'away', 'score':{'away':10,'home':9}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Adi','Koplow','Jon'],'home':['Gio','Keedy','McGilloway'],'winner':'home', 'score':{'away':2,'home':4}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Nick','White Rob','Kent'],'home':['Ziplox','Jesse','Bader'],'winner':'home', 'score':{'away':6,'home':13}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Nick','Jesse','Jon'],'home':['Magoo','Adi','Keedy'],'winner':'home', 'score':{'away':4,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Koplow','Gio','Ziplox'],'home':['Bader','Rosen','White Rob'],'winner':'away', 'score':{'away':12,'home':9}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Jon','Rosen','Kent'],'home':['Adi','Bader','Jesse'],'winner':'home', 'score':{'away':7,'home':9}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Magoo','Nick','Keedy'],'home':['Ziplox','Ced','McGilloway'],'winner':'away', 'score':{'away':9,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['McGilloway','Koplow','Kent'],'home':['Ced','Bader','Jon'],'winner':'home', 'score':{'away':6,'home':12}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Gio','Nick','White Rob'],'home':['Rosen','Jesse','Adi'],'winner':'away', 'score':{'away':10,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Magoo','Koplow','White Rob'],'home':['Ced','Gio','Kent'],'winner':'away', 'score':{'away':16,'home':5}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Jon','McGilloway','Bader'],'home':['Ziplox','Keedy','Rosen'],'winner':'home', 'score':{'away':8,'home':11}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Koplow','Gio','Keedy'],'home':['Magoo','Jesse','Ziplox'],'winner':'home', 'score':{'away':1,'home':15}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Ced','White Rob','Kent'],'home':['Nick','McGilloway','Adi'],'winner':'away', 'score':{'away':19,'home':4}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Ziplox','Adi','Kent'],'home':['Magoo','Rosen','Koplow'],'winner':'away', 'score':{'away':14,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Jesse','Ced','Keedy'],'home':['Bader','White Rob','McGilloway'],'winner':'away', 'score':{'away':13,'home':8}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Bader','Koplow','Nick'],'home':['Magoo','McGilloway','Jesse'],'winner':'home', 'score':{'away':5,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Ziplox','Ced','White Rob'],'home':['Adi','Gio','Jon'],'winner':'away', 'score':{'away':18,'home':1}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Rosen','Ced','Magoo'],'home':['Jesse','White Rob','Jon'],'winner':'away', 'score':{'away':18,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Ziplox','Gio','Nick'],'home':['Kent','Bader','Keedy'],'winner':'away', 'score':{'away':11,'home':7}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Jon','Ziplox','Kent'],'home':['Jesse','Gio','McGilloway'],'winner':'away', 'score':{'away':19,'home':5}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Rosen','Keedy','Nick'],'home':['Ced','Koplow','Adi'],'winner':'home', 'score':{'away':9,'home':10}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Jon','Keedy','White Rob'],'home':['Nick','Koplow','Kent'],'winner':'away', 'score':{'away':15,'home':11}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Rosen','McGilloway','Adi'],'home':['Magoo','Bader','Gio'],'winner':'home', 'score':{'away':3,'home':10}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Ziplox','Ced','Keedy'],'home':['Magoo','Jesse','Gio'],'winner':'away', 'score':{'away':16,'home':3}, 'date':datetime.datetime(2013,4,20)},
		{'away':['Magoo','Jesse','Gio'],'home':['Ziplox','Ced','Keedy'],'winner':'home', 'score':{'away':5,'home':12}, 'date':datetime.datetime(2013,4,20)},
		#{'away':['','',''],'home':['','',''],'winner':'', 'score':{'away':0,'home':0},'date':datetime.datetime(yyyy,mm,dd)},    
		]
		# Adding records
	
	
		for game in games:
			completeGame(session=session, homeTeam=game['home'],awayTeam=game['away'],winner=game['winner'],awaypoints=game['score']['away'],homepoints=game['score']['home'], datePlayed=game['date'])
			
			
			
			

	
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

	qry = session.query(Hitter).filter_by(name=u'Nick')
	record = qry.first()
	print "%s" % (record.hitzskill())
	gamesbackup=jsonbackup(session)
	print gamesbackup
	#collectionOfGames= generateGamePermutations([i.name for i in recordsbelowsigma], 20)
	#cls()
	#print list(collectionOfGames)
	# delete the record
	#record.delete()
	#session.commit()