#hitztourney.py
#port 4579

import cherrypy

matchup = [];
players = ["Nick","Ziplox","Safa","Jeff","Magoo","Rosen","Ced","Rob","Adi","James","Bader","Koplow","Sean", "Arambula","Jesse"];
playerList = [];
for player in players:
  playerList.append({"name":player,"wins":0,"games":0});
tv=["Samsung","Sony"]
if len(players)==15:
	matchup.append( {"home":[2,10,8],"away":[14,1,5], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[15,12,9],"away":[11,3,7], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[3,6,9],"away":[15,2,1], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[11,13,10],"away":[12,4,8], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[4,7,10],"away":[11,3,2], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[12,14,6],"away":[13,5,9], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[5,8,6],"away":[12,4,3], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[13,15,7],"away":[14,1,10], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[1,9,7],"away":[13,5,4], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[14,11,8],"away":[15,2,6], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[7,11,6],"away":[10,1,5], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[4,15,9],"away":[2,14,12], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[8,12,7],"away":[6,2,1], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[5,11,10],"away":[3,15,13], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[9,13,8],"away":[7,3,2], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[1,12,6],"away":[4,11,14], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[10,14,9],"away":[8,4,3], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[2,13,7],"away":[5,12,15], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[6,15,10],"away":[9,5,4], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[3,14,8],"away":[1,13,11], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[8,15,1],"away":[12,9,10], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[13,2,14],"away":[6,3,5], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[9,11,2],"away":[13,10,6], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[14,3,15],"away":[7,4,1], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[10,12,3],"away":[14,6,7], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[15,4,11],"away":[8,5,2], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[6,13,4],"away":[15,7,8], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[11,5,12],"away":[9,1,3], "winners":[ ], "tv":tv[1]});
	matchup.append( {"home":[7,14,5],"away":[11,8,9], "winners":[ ], "tv":tv[0]});
	matchup.append( {"home":[12,1,13],"away":[10,2,4], "winners":[ ], "tv":tv[1]});
elif len(players)==16:
	#( 1  6  5 v 16  3  9)  (13 11  8 v 12  2  4)  (10 14  7 15)
	matchup.append( {"home":[1,6,5], "away":[16,3,9], "winners":[], "tv":tv[0]}); #10 14 7 15
	matchup.append( {"home":[13,11,8], "away":[12,2,4], "winners":[], "tv":tv[1]});
	#( 2  7  6 v  1  4 10)  (14 12  9 v 13  3  5)  (11 15  8 16)
	matchup.append( {"home":[2,7,6], "away":[1,4,10], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[14,12,9], "away":[13,3,5], "winners":[], "tv":tv[1]});
	#( 3  8  7 v  2  5 11)  (15 13 10 v 14  4  6)  (12 16  9  1) 
	matchup.append( {"home":[3,8,7], "away":[2,5,11], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[15,13,10], "away":[14,4,6], "winners":[], "tv":tv[1]});
	#( 4  9  8 v  3  6 12)  (16 14 11 v 15  5  7)  (13  1 10  2) 
	matchup.append( {"home":[4,9,8], "away":[3,6,12], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[16,14,11], "away":[15,5,7], "winners":[], "tv":tv[1]});
	#( 5 10  9 v  4  7 13)  ( 1 15 12 v 16  6  8)  (14  2 11  3) 
	matchup.append( {"home":[5,10,9], "away":[4,7,13], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[1,15,12], "away":[16,6,8], "winners":[], "tv":tv[1]});
	#( 6 11 10 v  5  8 14)  ( 2 16 13 v  1  7  9)  (15  3 12  4) 
	matchup.append( {"home":[6,11,10], "away":[5,8,14], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[2,16,13], "away":[1,7,9], "winners":[], "tv":tv[1]});
	#( 7 12 11 v  6  9 15)  ( 3  1 14 v  2  8 10)  (16  4 13  5) 
	matchup.append( {"home":[7,12,11], "away":[6,9,15], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[3,1,14], "away":[2,8,10], "winners":[], "tv":tv[1]});
	#( 8 13 12 v  7 10 16)  ( 4  2 15 v  3  9 11)  ( 1  5 14  6) 
	matchup.append( {"home":[8,13,12], "away":[7,10,16], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[4,2,15], "away":[3,9,11], "winners":[], "tv":tv[1]});
	#( 9 14 13 v  8 11  1)  ( 5  3 16 v  4 10 12)  ( 2  6 15  7) 
	matchup.append( {"home":[9,14,13], "away":[8,11,1], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[5,3,16], "away":[4,10,12], "winners":[], "tv":tv[1]});
	#(10 15 14 v  9 12  2)  ( 6  4  1 v  5 11 13)  ( 3  7 16  8) 
	matchup.append( {"home":[10,15,14], "away":[9,12,2], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[6,4,1], "away":[5,11,13], "winners":[], "tv":tv[1]});
	#(11 16 15 v 10 13  3)  ( 7  5  2 v  6 12 14)  ( 4  8  1  9) 
	matchup.append( {"home":[11,16,15], "away":[10,13,3], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[7,5,2], "away":[6,12,14], "winners":[], "tv":tv[1]});
	#(12  1 16 v 11 14  4)  ( 8  6  3 v  7 13 15)  ( 5  9  2 10) 
	matchup.append( {"home":[12,1,16], "away":[11,14,4], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[8,6,3], "away":[7,13,15], "winners":[], "tv":tv[1]});
	#(13  2  1 v 12 15  5)  ( 9  7  4 v  8 14 16)  ( 6 10  3 11) 
	matchup.append( {"home":[13,2,1], "away":[12,15,5], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[9,7,4], "away":[8,14,16], "winners":[], "tv":tv[1]});
	#(14  3  2 v 13 16  6)  (10  8  5 v  9 15  1)  ( 7 11  4 12) 
	matchup.append( {"home":[14,3,2], "away":[13,16,6], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[10,8,5], "away":[9,15,1], "winners":[], "tv":tv[1]});
	#(15  4  3 v 14  1  7)  (11  9  6 v 10 16  2)  ( 8 12  5 13) 
	matchup.append( {"home":[15,4,3], "away":[14,1,7], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[11,9,6], "away":[10,16,2], "winners":[], "tv":tv[1]});
	#(16  5  4 v 15  2  8)  (12 10  7 v 11  1  3)  ( 9 13  6 14) 
	matchup.append( {"home":[16,5,4], "away":[15,2,8], "winners":[], "tv":tv[0]});
	matchup.append( {"home":[12,10,7], "away":[11,1,3], "winners":[], "tv":tv[1]});
else: 
	print str(len(players));

for i in range(len(matchup)):
  print "Game "+ str(i+1) + " is " + playerList[matchup[i]["home"][0]-1]["name"] + ", " + playerList[matchup[i]["home"][1]-1]["name"] + ", and "+playerList[matchup[i]["home"][2]-1]["name"] +" against "+playerList[matchup[i]["away"][0]-1]["name"]+", "+playerList[matchup[i]["away"][1]-1]["name"]+", and " + playerList[matchup[i]["away"][2]-1]["name"] + " on the "+matchup[i]["tv"]+" TV"
