import itertools
from elixir import *
from trueskill import *
import datetime
from sortedcollection import SortedCollection
from sys import stdout
import win32api,win32console

AWAY_TEAM=1
HOME_TEAM=0
RESET=0 #requires you to delete the db before running

env=TrueSkill(draw_probability=dynamic_draw_probability)

def cls():
     "Clear console screen"
     TopLeft = win32console.PyCOORDType(0,0)
     csb = win32console.GetStdHandle(win32api.STD_OUTPUT_HANDLE)
     csbi = csb.GetConsoleScreenBufferInfo()
     size = csbi['Size'].X * csbi['Size'].Y;
     csb.FillConsoleOutputCharacter(u' ', size, TopLeft)
     csb.FillConsoleOutputAttribute(csbi['Attributes'], size, TopLeft);
     csb.SetConsoleCursorPosition(TopLeft)

def get_by_or_init(cls, if_new_set={}, **params):
    """Call get_by; if no object is returned, initialize an object
    with the same parameters. If a new object was created,
    set any initial values."""
    result = cls.get_by(**params)
    if not result:
        result = cls(**params)
        result.set(**if_new_set)
    return result

Entity.get_by_or_init = classmethod(get_by_or_init)


metadata.bind = "sqlite:///hitz.sqlite"
#metadata.bind.echo = True
 
########################################################################
class Hitters(Entity):
    """
    Custom made bookmark example
    """
    name = Field(Unicode, unique = True)
    teams = ManyToMany('Teams')
    rating = Field(PickleType, default=env.Rating())
    lastGamePlayed = Field(DateTime, default=datetime.datetime(2013,7,1))
 
    #----------------------------------------------------------------------
    def __repr__(self):
        """"""
        return "<Hitter '%s' (%s)" % (self.name, self.rating)

class Teams(Entity):
    
    players = ManyToMany('Hitters')
    teamrating = Field(PickleType, default=env.Rating())
    homegames = OneToMany('Games', inverse='hometeam')
    awaygames = OneToMany('Games', inverse='awayteam')
    gameswon = OneToMany('Games', inverse='winner')
    def __repr__(self):
        return "<Teams '%s' , rating: %s>" % (self.players, self.teamrating)
    def tupleratings(self):
        ratings=[]
        for player in self.players:
            ratings.append(player.rating)

        return tuple(ratings)
    def setdatelastplayed(self, datePlayed=datetime.datetime.today()):
        
        for player in self.players:
            if datePlayed > player.lastGamePlayed:
                player.lastGamePlayed =datePlayed
        
    def getdatelastplayed(self):
        comparedate=datetime.datetime.today()
        for player in self.players:
            if player.lastGamePlayed < comparedate:
                comparedate=player.lastGamePlayed
        return comparedate


    
class Games(Entity):
    hometeam = ManyToOne('Teams', inverse='homegames')
    awayteam = ManyToOne('Teams', inverse='awaygames')
    winner = ManyToOne('Teams', inverse = 'winner')
    date = Field(DateTime, default=datetime.datetime.now())
    event = Field(UnicodeText)
    gameNumber = Field(Integer)
    def __repr__(self):
        return "<Game '%s' %s vs %s, %s won" % (self.date, self.awayteam,self.hometeam,self.winner)


def get_or_create_team(findplayers):
    #first check if a team exists

    createam=Teams.query.filter(Teams.players.any(name=findplayers[0])).filter(Teams.players.any(name=findplayers[1])).filter(Teams.players.any(name=findplayers[2])).first()
    #if it doesn't exist, create it
    if not createam:
            createam = Teams()
            for newplayer in findplayers:
                createam.players.append(Hitters.get_by_or_init(name=newplayer))
            session.commit()
    return createam
        
def generateGamePermutations(listOfPlayers, numberOfGames=10):
    # 
    # output should be a list of games [{'home':team,'away':team, 'strength':float}] randomized, then sorted by strength
    #
    potentialGames=[]
    potentialGamesCollection=SortedCollection(key=lambda item:-item['strength'])
    # first get a list of the potential combinations of 6 players
    """
    for potentialmatchups in list(itertools.combinations(listOfPlayers,6):
        for match in potentialmatchups:
            for a in range(len(match)/2):
                homeTeam=match[a]
                awayTeam=match[len(match)-a-1]
                potentialGames.append({'home': match[a],'away':match[len(match)-a-1]}, 'strength':getStrength(homeTuple=homeTeam,awayTuple=awayTeam), 'sigma':getTeamSigma())
    """

    players = set(listOfPlayers)
    complete = set()
    begintime=datetime.datetime.now()
    lastdisplay=begintime #when was the last time we printed the results?
    for home in itertools.combinations(players, 3):
        complete.add(home[0])
        remaining_players = players - set(home) - complete
        for away in itertools.combinations(remaining_players, 3):
            potentialGamesCollection.insert({'home':home, 'away':away, 'strength':getStrength(homeNames=home,awayNames=away), 'lastPlayed':getLastPlayed(homeNames=home,awayNames=away)})
            #potentialGames.append( {'home':home, 'away':away, 'strength':getStrength(homeNames=home,awayNames=away), 'lastPlayed':getLastPlayed(homeNames=home,awayNames=away)})
            if len(potentialGamesCollection)>numberOfGames:
                potentialGamesCollection.removebyindex(numberOfGames)
            
            timenow=datetime.datetime.now()
            difference=timenow-lastdisplay
            if difference.total_seconds()>2:
                cls()
                print list(potentialGamesCollection)
                lastdisplay=timenow

    print 'Elapsed Time: %s seconds' % str((lastdisplay-timenow).total_seconds)
    return potentialGamesCollection

def getStrength(homeNames,awayNames):
    #
    # ({'name':'alice','rating':2.0},{'name':'bob','rating':1.4},{'name':'charlie','rating':3.2})
    #
    homeTeam=get_or_create_team(homeNames)
    awayTeam=get_or_create_team(awayNames)
    homeRatings = homeTeam.tupleratings()
    awayRatings = awayTeam.tupleratings()
    return env.quality([homeRatings,awayRatings])
def getLastPlayed(homeNames,awayNames):
    #
    # ({'name':'alice','rating':2.0},{'name':'bob','rating':1.4},{'name':'charlie','rating':3.2})
    #
    homeTeam=get_or_create_team(homeNames)
    awayTeam=get_or_create_team(awayNames)
    homeDate = homeTeam.getdatelastplayed()
    awayDate = awayTeam.getdatelastplayed()
    if homeDate<awayDate:
        return homeDate
    else:
        return awayDate

def completeGame(homeTeam,awayTeam,winner,datePlayed=datetime.datetime.today()):
    homers=get_or_create_team(homeTeam)
    awayers=get_or_create_team(awayTeam)
    homers.setdatelastplayed(datePlayed)
    awayers.setdatelastplayed(datePlayed)

    print "\n----------\n%s vs %s  " % (awayers, homers)
    
    if winner=='home':
        winningteam=get_or_create_team(homeTeam)
        #team rating
        homers.teamrating,awayers.teamrating = rate_1vs1(homers.teamrating, awayers.teamrating)
        #individual ratings
        (awayers.players[0].rating, awayers.players[1].rating, awayers.players[2].rating),(homers.players[0].rating, homers.players[1].rating, homers.players[2].rating) = rate([[awayers.players[0].rating, awayers.players[1].rating, awayers.players[2].rating],[homers.players[0].rating, homers.players[1].rating, homers.players[2].rating]], ranks=[1,0])
            
    else:
        winningteam=get_or_create_team(awayTeam)
        #team ratings
        awayers.teamrating,homers.teamrating = rate_1vs1(awayers.teamrating, homers.teamrating)
        #individual ratings
        (awayers.players[0].rating, awayers.players[1].rating, awayers.players[2].rating),(homers.players[0].rating, homers.players[1].rating, homers.players[2].rating) = rate([[awayers.players[0].rating, awayers.players[1].rating, awayers.players[2].rating],[homers.players[0].rating, homers.players[1].rating, homers.players[2].rating]], ranks=[0,1])
    newgame = Games(hometeam=homers, awayteam=awayers, winner=winningteam,date=datePlayed)
    session.commit()

 
if __name__ == "__main__":
    from elixir import create_all, setup_all, session
    setup_all()
    create_all()
    players = ["Adi","Bader","Ced","Gio","James","Jeff","Jesse","Jon","Kent","Koplow","Magoo","Nick","Rosen","Sean","White Rob","Ziplox", 'Drew', 'Crabman'];
    for player in players:
        Hitters.get_by_or_init(name=player)
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
        {'home':['Ziplox','Rosen','Adi'],'away':['Crabman','Drew','Rob'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
        {'away':['Ziplox','Nick','Adi'],'home':['Crabman','Drew','Rob'],'winner':'away', 'date':datetime.datetime(2013,7,27)},
        {'away':['Rosen','Crabman','Rob'],'home':['Ziplox','Nick','Adi'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
        {'away':['Rosen','Rob','Adi'],'home':['Ziplox','Nick','Drew'],'winner':'home', 'date':datetime.datetime(2013,7,27)},      
        {'away':['Rosen','Rob','Crabman'],'home':['Ziplox','Nick','Drew'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
        {'away':['Drew','Adi','Crabman'],'home':['Rosen','Nick','Ziplox'],'winner':'away', 'date':datetime.datetime(2013,7,27)},
        {'away':['Nick','Rob','Rosen'],'home':['Drew','Adi','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
        {'away':['Ziplox','Rob','Rosen'],'home':['Drew','Adi','Crabman'],'winner':'away', 'date':datetime.datetime(2013,7,27)},
        {'away':['Rob','Drew','Adi'],'home':['Ziplox','Nick','Rosen'],'winner':'home', 'date':datetime.datetime(2013,7,27)},
        {'away':['Rob','Crabman','Adi'],'home':['Ziplox','Nick','Rosen'],'winner':'away', 'date':datetime.datetime(2013,7,27)},
        {'away':['Ziplox','Nick','Drew'],'home':['Rob','Adi','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,27)},              
        {'away':['Ziplox','Rosen','Drew'],'home':['Rob','Adi','Crabman'],'winner':'home', 'date':datetime.datetime(2013,7,27)},  
        #{'away':['','',''],'home':['','',''],'winner':''},    
        ]
        # Adding records
    
    
        for game in games:
            completeGame(game['home'],game['away'],game['winner'], game['date'])
            
            
            
            

    
        #thisgame = Games.get_by_or_init(hometeam=homers, awayteam=awayers, winner=game['winner'], date=datetime.datetime.now)
    # --------------------------------------------------
    # Simple Queries
 
    # get all the records
    #records = Hitters.query.filter(Hitters.rating.sigma<8.0).all()
    records = Hitters.query.all()
    recordsbelowsigma = []
    #for record in records:
        #print "-" * 20
        #print record.name
    records.sort(key=lambda player: player.rating.sigma)
    for record in records:
        if record.rating.sigma < 8.0:
            recordsbelowsigma.append(record)



    recordsbelowsigma.sort(key=lambda player: player.rating.mu)
    print "\n\n\n%s\n\n\n" % recordsbelowsigma
    allteams=Teams.query.all()
    #for allteam in allteams:
        #print "-" * 20
        #print allteam.players
    allteams.sort(key=lambda team: team.teamrating.mu)
    print allteams
 
    # find a specific record
    qry = Hitters.query.filter_by(name=u'Nick')
    record = qry.first()
    print "%s" % (record.rating.sigma)
    collectionOfGames= generateGamePermutations([i.name for i in recordsbelowsigma], 20)
    cls()
    print list(collectionOfGames)
    # delete the record
    #record.delete()
    #session.commit()