from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Table, Text, create_engine, Column, Integer, String, PickleType, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker
import datetime

import itertools
from sortedcollection import *
from trueskill import *

env=TrueSkill(draw_probability=dynamic_draw_probability)

RESET=0
SIGMA_CUTOFF=8.0

Base = declarative_base()


class Hitter(Base):
	__tablename__='hitters'
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	#teams = relationship("Team", backref="hitter")
	rating = Column(PickleType)
	lastGamePlayed = Column(DateTime)
	def __init__(self, name,lastGamePlayed = datetime.datetime(2013,7,1),rating = env.Rating()):
		self.name = name
		self.lastGamePlayed = lastGamePlayed
		self.rating = rating
	def hitzskill(self):
		return (self.rating.mu - 3.0*self.rating.sigma)
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
	hitters = relationship("Hitter", secondary=hitter_team_table, backref='teams')

	def __init__(self):
		self.teamrating = env.Rating()
	def __repr__(self):
		return "<%s, %s, %s last played: %s team rating: %s>" % (self.hitters[0].name, self.hitters[1].name, self.hitters[2].name, self.getdatelastplayed(),str(self.teamrating.mu - 3.0*self.teamrating.sigma))

	def tupleratings(self):
		ratingslist=[]
		for player in self.hitters:
			ratingslist.append(player.rating)

		return tuple(ratingslist)
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
	

	#date = Field(DateTime, default=datetime.datetime.now())
	date = Column(DateTime)
	#event = Field(UnicodeText)
	event = Column(String)
	#gameNumber = Field(Integer)
	gameNumber = Column(Integer)
	def __init__(self, hometeam, awayteam, winner, date = datetime.datetime.now() ):
		self.date = date
		self.hometeam = hometeam
		self.awayteam = awayteam
		self.winner = winner
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
		create_team = Team()
		for newplayer in findplayers:
			create_team.hitters.append(get_or_create(session,Hitter,name=newplayer))
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
	# ({'name':'alice','rating':2.0},{'name':'bob','rating':1.4},{'name':'charlie','rating':3.2})
	#
	homeTeam=get_or_create_team(session, homeNames)
	awayTeam=get_or_create_team(session, awayNames)
	homeRatings = homeTeam.tupleratings()
	awayRatings = awayTeam.tupleratings()
	return int(env.quality([homeRatings,awayRatings])*10000)

def jsonbackup(session):
	results = []
	allgames = session.query(Game).all()

	for game in allgames:
		results.append({'away':game.awayteam.listnames(), 'home':game.hometeam.listnames(), 'winner': game.winposition(), 'date': game.date})

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

def completeGame(session,homeTeam,awayTeam,winner,datePlayed=datetime.datetime.today()):
	homers=get_or_create_team(session, homeTeam)
	awayers=get_or_create_team(session, awayTeam)
	homers.setdatelastplayed(datePlayed)
	awayers.setdatelastplayed(datePlayed)

	#print "\n----------\n%s vs %s  " % (awayers, homers)
	
	if winner=='home':
		winningteam=get_or_create_team(session, homeTeam)
		#team rating
		homers.teamrating,awayers.teamrating = rate_1vs1(homers.teamrating, awayers.teamrating)
		#individual ratings
		(awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating),(homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating) = rate([[awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating],[homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating]], ranks=[1,0])
			
	else:
		winningteam=get_or_create_team(session, awayTeam)
		#team ratings
		awayers.teamrating,homers.teamrating = rate_1vs1(awayers.teamrating, homers.teamrating)
		#individual ratings
		(awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating),(homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating) = rate([[awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating],[homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating]], ranks=[0,1])
	newgame = Game(hometeam=homers, awayteam=awayers, winner=winningteam,date=datePlayed)
	session.add(newgame)
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
		names.append({'name':player.name, 'isChecked': isChecked} )
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
	players = ["Adi","Bader","Ced","Gio","James","Jeff","Jesse","Jon","Kent","Koplow","Magoo","Nick","Rosen","Sean","White Rob","Ziplox", 'Drew', 'Crabman'];
	for player in players:
		#Hitters.get_by_or_init(name=player)
		hitlist.append(get_or_create(session, Hitter, name=player))
	session.commit()

	if RESET==1:
		games = [
		{'away':['Nick','Ziplox','Ced'],'home':['Rosen','Crabman','Magoo'],'winner':'away', 'date':datetime.datetime(2013,7,13)},
		{'away':['Rosen','Ced','Magoo'],'home':['Nick','Ziplox','Crabman'],'winner':'away', 'date':datetime.datetime(2013,7,13)}, 
		{'home':['Rosen','Ced','Magoo'],'away':['Nick','Ziplox','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,13)},
		{'away':['Ziplox','Magoo','Nick'],'home':['Ced','Crabman','Rosen'],'winner':'away', 'date':datetime.datetime(2013,7,13)},
		{'away':['Ziplox','Rosen','Ced'],'home':['Nick','Magoo','Crabman'],'winner':'away', 'date':datetime.datetime(2013,7,13)}, 
		{'home':['Ziplox','Rosen','Ced'],'away':['Nick','Magoo','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,13)},
		{'home':['Ziplox','Rosen','Ced'],'away':['Nick','Magoo','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,13)},
		{'away':['Magoo','Crabman','Rosen'],'home':['Ziplox','Ced','Nick'],'winner':'home', 'date':datetime.datetime(2013,7,13)},
		{'home':['Ziplox','Rosen','Adi'],'away':['Crabman','Drew','White Rob'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
		{'away':['Ziplox','Nick','Adi'],'home':['Crabman','Drew','White Rob'],'winner':'away', 'date':datetime.datetime(2013,7,27)},
		{'away':['Rosen','Crabman','White Rob'],'home':['Ziplox','Nick','Adi'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
		{'away':['Rosen','White Rob','Adi'],'home':['Ziplox','Nick','Drew'],'winner':'home', 'date':datetime.datetime(2013,7,27)},      
		{'away':['Rosen','White Rob','Crabman'],'home':['Ziplox','Nick','Drew'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
		{'away':['Drew','Adi','Crabman'],'home':['Rosen','Nick','Ziplox'],'winner':'away', 'date':datetime.datetime(2013,7,27)},
		{'away':['Nick','White Rob','Rosen'],'home':['Drew','Adi','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
		{'away':['Ziplox','White Rob','Rosen'],'home':['Drew','Adi','Crabman'],'winner':'away', 'date':datetime.datetime(2013,7,27)},
		{'away':['White Rob','Drew','Adi'],'home':['Ziplox','Nick','Rosen'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
		{'away':['White Rob','Crabman','Adi'],'home':['Ziplox','Nick','Rosen'],'winner':'away', 'date':datetime.datetime(2013,7,27)},
		{'away':['Ziplox','Nick','Drew'],'home':['White Rob','Adi','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,27)},              
		{'away':['Ziplox','Rosen','Drew'],'home':['White Rob','Adi','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,27)},  
		#{'away':['','',''],'home':['','',''],'winner':''},    
		]
		# Adding records
	
	
		for game in games:
			completeGame(session, game['home'],game['away'],game['winner'], game['date'])
			
			
			
			

	
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
	allteams.sort(key=lambda team: team.teamrating.mu)
	print allteams
 
	# find a specific record

	qry = session.query(Hitter).filter_by(name=u'Nick')
	record = qry.first()
	print "%s" % (record.hitzskill())
	#collectionOfGames= generateGamePermutations([i.name for i in recordsbelowsigma], 20)
	#cls()
	#print list(collectionOfGames)
	# delete the record
	#record.delete()
	#session.commit()