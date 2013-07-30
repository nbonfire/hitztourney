from model import *
import itertools

SIGMA_CUTOFF = 8.0
def getRecordsBelowSigma(sigma):
	records = Hitters.query.all()
	recordsbelowsigma = []
    #for record in records:
        #print "-" * 20
        #print record.name
    records.sort(key=lambda player: player.rating.sigma)
    for record in records:
        if record.rating.sigma < sigma:
            recordsbelowsigma.append(record)
    return recordsbelowsigma

def generateGamePermutations(listOfPlayers):
	# 
	# output should be a list of games [{'home':team,'away':team, 'strength':float}] sorted by strength
	#

	# first get a list of the potential combinations of 6 players
	if len(listOfPlayers==6):
		return generateGamePermutationsForExactly6(listOfPlayers)
	else:

		potentialmatchups = itertools.combinations(listOfPlayers,6)

		for matchup in potentialmatchups:
			potentialGames.append(generateGamePermutationsForExactly6(matchup))
	# next find the strongest matches for each group of 6 and create the list out of all games

		#allteams.sort(key=lambda team: team.teamrating.mu)
		potentialGames.sort(key = lambda game: game['strength'] )
		return potentialGames
	#return listOfGames

def generateGamePermutationsForExactly6(listOfPlayers):

if __name__ == '__main__':
	#get top 10 active players
	setup_all()
	create_all()

	potentialplayers = getRecordsBelowSigma(SIGMA_CUTOFF)
	games = generateGamePermutations(potentialplayers)

    #generate permutations
	