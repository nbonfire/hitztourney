hitztourney
===========

to use with docker, build the docker file with 
`docker build --no-cache -t hitztourney:latest .`

then run with 
`docker run -d -p 4011:4011 -v db:/db hitztourney`

the -v db:/db maps the folder 'db' in the current folder to the db folder in the container so you can backup the db.

You might also want to populate a new db from a gamesbackup.txt you have in your current folder, you can do that like this:

`docker run -d -v db:/db gamesbackup.txt:/hitztourney/gamesbackup.txt hitztourney -c 'from model import *; jsonrestore()'`
