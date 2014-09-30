#
# hitzSaveRead.py
#
# extract data from a PS2 NHL Hitz 20-02 save file (unknown if it works for xbox or GC saves)
#
 
import binascii
import pprint
 
FILENAME = 'hitzsave'
 
# Converts the hex string to an integer value

def convert(hexString):  
	return int(binascii.hexlify(hexString),16)

def hitzSaveRead(filename): 
    with open(filename,'rb') as fp:
        contents=fp.read()
        fp.close()
     
    #strip header
    contents=contents[8:]
     
    players={}
     
     
    namelength=5
    gamesplayedPosition=10 
    shotsPosition=12 # 2 bytes
    goalsPosition=14 # 2 bytes
    assistsPosition=16
    consecutivelossesPosition=20
    hitsPosition=32 # 2 bytes
    winsPosition=34
     
    for i in range(20): # there's a max of 20 users stored in a save
        
        startpos = i * 304
        name=contents[startpos:startpos+5].rstrip('\x00')
        gamesplayedhex=contents[startpos+gamesplayedPosition]
        shotshex=contents[startpos+shotsPosition+1:startpos+shotsPosition-1:-1]       # reversed to fix endianness
        goalshex = contents[startpos+goalsPosition+1:startpos+goalsPosition-1:-1]     # There's probably a better way to do this...
        hitshex = contents[startpos + hitsPosition + 1:startpos + hitsPosition-1:-1]
        winshex = contents[startpos + winsPosition]
        assistshex = contents[startpos+assistsPosition]
        consecutivelosseshex = contents[startpos+consecutivelossesPosition]
     
        gamesplayed=convert(gamesplayedhex)
        shots=convert(shotshex)
        goals = convert(goalshex)
        hits = convert(hitshex)
        wins = convert(winshex)
        assists = convert(assistshex)
        consecutivelosses = convert(consecutivelosseshex)
        player={'name':name,
                'gamesPlayed':gamesplayed,
                'shots':shots,
                'hits':hits,
                'wins':wins,
                'assists':assists,
                'consecutiveLosses':consecutivelosses
                }
        players[name]=player

if __name__ == '__main__':
    players = readsave(FILENAME) 
    pprint.pprint(players)