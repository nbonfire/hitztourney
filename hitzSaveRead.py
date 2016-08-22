import binascii
import pprint
import os
import csv
import datetime

OFFSET = 8


FILENAME = 'BASLUS-20140NHLHitz'
PATH = '/media/pool/games/PlayStation 2/Saves/NHL Hitz 20-02/'
OUTPUTFILENAME = '/media/pool/games/PlayStation 2/Saves/NHL Hitz 20-02/output.csv'



# Converts the hex string to an integer value

def convert(hexString):  
    return int(binascii.hexlify(hexString),16)

def hitzSaveRead(filename, offset = OFFSET): 
    with open(filename,'rb') as fp:
        contents=fp.read()
        fp.close()

    #strip header
    contents=contents[offset:]

    players={}


    namelength=5
    gamesplayedPosition=10 
    shotsPosition=12
    goalsPosition=14
    assistsPosition=16
    onetimergoalsPosition=22
    onetimershotsPosition=24
    unknown01Position=26
    passesPosition=28
    unknown02Position=30
    hitsPosition=32
    winsPosition=34
    unknown03Position=36
    fightswonPosition=38
    p = lambda x,y: contents[x+y+1:x+y-1:-1] # get 2 bytes of data in reverse endianness
    for i in range(20): # there's a max of 20 users stored in a save

        startpos = i * 304
        name=contents[startpos:startpos+5].rstrip('\x00')
        gamesplayedhex=p(startpos,gamesplayedPosition)
        shotshex=p(startpos,shotsPosition) 
        goalshex = p(startpos,goalsPosition)
        assistshex = p(startpos,assistsPosition)
        onetimergoalshex = p(startpos,onetimergoalsPosition)
        onetimershotshex = p(startpos,onetimershotsPosition)
        unknown01hex = p(startpos,unknown01Position)
        passeshex = p(startpos,passesPosition)
        unknown02hex = p(startpos,unknown02Position)
        hitshex = p(startpos,hitsPosition)
        winshex = p(startpos,winsPosition)
        unknown03hex = p(startpos,unknown03Position)
        fightswonhex = p(startpos,fightswonPosition)

        gamesplayed = convert(gamesplayedhex)
        shots = convert(shotshex)
        goals = convert(goalshex)
        assists = convert(assistshex)
        onetimergoals = convert(onetimergoalshex)
        onetimershots = convert(onetimershotshex)
        unknown01 = convert(unknown01hex)
        passes = convert(passeshex)
        unknown02 = convert(unknown02hex)
        hits = convert(hitshex)
        wins = convert(winshex)
        unknown03 = convert(unknown03hex)
        fightswon = convert(fightswonhex)
        player={
                'id':'',
                'date':datetime.date.today(),
                'istournament':0,
                'playerid':'',
                'name':name,
                'assists':assists,
                'games_played':gamesplayed,
                'games_played_actual':gamesplayed,
                'goals':goals,
                'hits':hits,
                'one-timer_goals':onetimergoals,
                'one-timer_shots':onetimershots,
                'passes':passes,
                'shots':shots,
                'unknown01':unknown01,
                'unknown02':unknown02,
                'unknown03':unknown03,
                'wins':wins,
                'wins_actual':wins,
                'fights_won':fightswon
                }
        if name:
            players[name]=player
    return players


players = hitzSaveRead(os.path.join(PATH,FILENAME)) 
pprint.pprint(players)

# CSV output
# list of keys for first row of CSV
headings = ['id',
                'date',
                'istournament',
                'playerid',
                'name',
                'assists',
                'games_played',
                'games_played_actual',
                'goals',
                'hits',
                'one-timer_goals',
                'one-timer_shots',
                'passes',
                'shots',
                'unknown01',
                'unknown02',
                'unknown03',
                'wins',
                'wins_actual']# use list of keys to make sure CSV is in the same order
with open(OUTPUTFILENAME,'wb+') as fp:
    csvwriter=csv.writer(fp)
    csvwriter.writerow(headings)
    #pprint.pprint(players)
    for player in players.keys():
        #pprint.pprint(player)
        #playerdata=[players[player][heading] for heading in headings];pprint.pprint(playerdata)
        csvwriter.writerow([players[player][heading] for heading in headings])
