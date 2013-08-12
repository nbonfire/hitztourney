from model import *
import itertools

SIGMA_CUTOFF = 8.0
defaultPlayers= ['Nick', 'Ziplox', 'Ced', 'Magoo', 'Rosen', 'White Rob', 'Adi']

def getRecordsBelowSigma(sigma):
	records = Hitters.query.all()
	recordsbelowsigma = []
    #for record in records:
        #print "-" * 20
        #print record.name
    
    for record in records:
        if record.rating.sigma < sigma:
            recordsbelowsigma.append(record)
    recordsbelowsigma.sort(key=lambda player: player.rating.score())
    return recordsbelowsigma


def generateGamePossibilities(listOfPlayers=defaultPlayers, numberOfGames=10, usesWebsocket = True):
	# 
    # output should be a list of games [{'home':team,'away':team, 'strength':float}] randomized, then sorted by strength
    #
    potentialGames=[]
    potentialGamesCollection=SortedCollection(key=lambda item:-item['strength'])
    
    """
    # first get a list of the potential combinations of 6 players
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
    lastupdate=begintime #when was the last time we printed the results?
    for home in itertools.combinations(players, 3):
        complete.add(home[0])
        remaining_players = players - set(home) - complete
        for away in itertools.combinations(remaining_players, 3):
            potentialGamesCollection.insert({'home':'%s, %s, %s' % (home[0],home[1],home[2]), 'away':'%s, %s, %s' % (away[0],away[1],away[2]), 'strength':getStrength(homeNames=home,awayNames=away)*100, 'lastPlayed':getLastPlayed(homeNames=home,awayNames=away)})
            #potentialGames.append( {'home':home, 'away':away, 'strength':getStrength(homeNames=home,awayNames=away), 'lastPlayed':getLastPlayed(homeNames=home,awayNames=away)})
            if len(potentialGamesCollection)>numberOfGames:
                potentialGamesCollection.removebyindex(numberOfGames)
            
            
            if usesWebsocket==True:
            	timenow=datetime.datetime.now()
            	difference=timenow-lastupdate
            	if difference.total_seconds()>2:
                	#cls()
                	#print list(potentialGamesCollection)
                	lastupdate=timenow
                	sendMessage(event='top10games', data={'games':list(potentialGamesCollection), 'isdone':"Working..."})

    if usesWebsocket == True:
	    sendMessage(event='top10games', data={'games':list(potentialGamesCollection), 'isdone':"Done"})
    	print 'Elapsed Time: %s seconds' % str((lastdisplay-timenow).total_seconds)
    	return True
    else:
    	return potentialGamesCollection


	