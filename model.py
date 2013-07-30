from elixir import *
from trueskill import *
import datetime

AWAY_TEAM=1
HOME_TEAM=0

env=TrueSkill(draw_probability=dynamic_draw_probability)

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
    
class Games(Entity):
    hometeam = ManyToOne('Teams', inverse='homegames')
    awayteam = ManyToOne('Teams', inverse='awaygames')
    winner = ManyToOne('Teams', inverse = 'winner')
    date = Field(DateTime, default=datetime.datetime.now)
    event = Field(UnicodeText)
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
        
        

 
if __name__ == "__main__":
    from elixir import create_all, setup_all, session
    setup_all()
    create_all()
    players = ["Adi","Bader","Ced","Gio","James","Jeff","Jesse","Jon","Kent","Koplow","Magoo","Nick","Rosen","Sean","White Rob","Ziplox", 'Drew', 'Crabman'];
    """games = [
        {'away':['Nick','Ziplox','Ced'],'home':['Rosen','Crabman','Magoo'],'winner':'away'},
        {'away':['Rosen','Ced','Magoo'],'home':['Nick','Ziplox','Crabman'],'winner':'away'}, 
        {'home':['Rosen','Ced','Magoo'],'away':['Nick','Ziplox','Crabman'],'winner':'home'},
        {'away':['Ziplox','Magoo','Nick'],'home':['Ced','Crabman','Rosen'],'winner':'away'},
        {'away':['Ziplox','Rosen','Ced'],'home':['Nick','Magoo','Crabman'],'winner':'away'}, 
        {'home':['Ziplox','Rosen','Ced'],'away':['Nick','Magoo','Crabman'],'winner':'home'},
        {'home':['Ziplox','Rosen','Ced'],'away':['Nick','Magoo','Crabman'],'winner':'home'},
        {'away':['Magoo','Crabman','Rosen'],'home':['Ziplox','Ced','Nick'],'winner':'home'},
        {'home':['Ziplox','Rosen','Adi'],'away':['Crabman','Drew','Rob'],'winner':'home'},
        {'away':['Ziplox','Nick','Adi'],'home':['Crabman','Drew','Rob'],'winner':'away'},
        {'away':['Rosen','Crabman','Rob'],'home':['Ziplox','Nick','Adi'],'winner':'home'},
        {'away':['Rosen','Rob','Adi'],'home':['Ziplox','Nick','Drew'],'winner':'home'},      
        {'away':['Rosen','Rob','Crabman'],'home':['Ziplox','Nick','Drew'],'winner':'home'},
        {'away':['Drew','Adi','Crabman'],'home':['Rosen','Nick','Ziplox'],'winner':'away'},
        {'away':['Nick','Rob','Rosen'],'home':['Drew','Adi','Crabman'],'winner':'home'},
        {'away':['Ziplox','Rob','Rosen'],'home':['Drew','Adi','Crabman'],'winner':'away'},
        {'away':['Rob','Drew','Adi'],'home':['Ziplox','Nick','Rosen'],'winner':'home'},
        {'away':['Rob','Crabman','Adi'],'home':['Ziplox','Nick','Rosen'],'winner':'away'},
        {'away':['Ziplox','Nick','Drew'],'home':['Rob','Adi','Crabman'],'winner':'home'},              
        {'away':['Ziplox','Rosen','Drew'],'home':['Rob','Adi','Crabman'],'winner':'home'},  
        #{'away':['','',''],'home':['','',''],'winner':''},    
        ]"""
    # Adding records
    for player in players:
        Hitters.get_by_or_init(name=player)
    session.commit()
    
    """for game in games:
        
        homers=get_or_create_team(game['home'])
        awayers=get_or_create_team(game['away'])
        winningteam=get_or_create_team(game[game['winner']])
        print "\n----------\n%s vs %s  " % (awayers, homers)
        newgame = Games(hometeam=homers, awayteam=awayers, winner=winningteam)
        if game['winner']=='home':
            #team rating
            homers.teamrating,awayers.teamrating = rate_1vs1(homers.teamrating, awayers.teamrating)
            #individual ratings
            (awayers.players[0].rating, awayers.players[1].rating, awayers.players[2].rating),(homers.players[0].rating, homers.players[1].rating, homers.players[2].rating) = rate([[awayers.players[0].rating, awayers.players[1].rating, awayers.players[2].rating],[homers.players[0].rating, homers.players[1].rating, homers.players[2].rating]], ranks=[1,0])
            
        else:
            #team ratings
            awayers.teamrating,homers.teamrating = rate_1vs1(awayers.teamrating, homers.teamrating)
            #individual ratings
            (awayers.players[0].rating, awayers.players[1].rating, awayers.players[2].rating),(homers.players[0].rating, homers.players[1].rating, homers.players[2].rating) = rate([[awayers.players[0].rating, awayers.players[1].rating, awayers.players[2].rating],[homers.players[0].rating, homers.players[1].rating, homers.players[2].rating]], ranks=[0,1])
            
        print newgame
        print homers.teamrating
        print awayers.teamrating
        session.commit()

    """
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
 
    # delete the record
    #record.delete()
    #session.commit()