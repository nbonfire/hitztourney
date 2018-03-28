hitztourney
===========

NOTE: there is no index on purpose. go to http://yourhostname.whatever/games to see the main page. Yes, I know this is security by obscurity but I really only need to stop drunk gamers from padding their stats. I do a better job with security in the flask/heroku-based version at nbonfire/hitzapp by implementing social login.


to use with docker, download and build the docker file with 
`docker build --no-cache -t hitztourney:latest .`



You might first want to populate a new db from a gamesbackup.txt you have in your current folder, you can do that like this, make sure you have an empty db folder first though:

`docker run -v db:/db gamesbackup.txt:/hitztourney/gamesbackup.txt hitztourney -c "from model import *; jsonrestore()"`

then run with 
`docker run --name hitztourney -d -p 4011:4011 -v db:/db hitztourney`


the -v db:/db maps the folder 'db' in the current folder to the db folder in the container so you can backup the db.
