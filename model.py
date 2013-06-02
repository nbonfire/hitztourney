from elixir import *
from trueskill import *

metadata.bind = "sqlite:///hitz.db"
metadata.bind.echo = True
env = TrueSkill(draw_probability=dynamic_draw_probability)
AWAY_TEAM=1
HOME_TEAM=0

class HitzPlayer(Entity):
	name = Field(Unicode(64), unique=True, required=True)
	login = Field(Unicode(18), unique=True, required=True)
	password = Field(Unicode(24), required=True)
	tags = OneToMany('Tag')
	photo = Field(Binary, deferred=True)
	rating = Field(PickleType, default=env.Rating())
	wins = Field(Integer, default=0)
	games = Field(Integer, default=0)
	teams = OneToMany('HitzTeam')

	#mu = 
	#sigma
	def __repr__(self):
        return '<Player "%s">' % self.name

class Tag(Entity):
	tagname = Field(Unicode(6))
	created_date = Field(DateTime, default=datetime.datetime.now)
	player = ManyToOne('Player')
	def __repr__(self):
		return '<Tag "%s" - %s >' % (self.tagname, self.player.name)

class HitzPickupMatch(Entity):
	awayTeam = ManyToOne('HitzTeam')
	homeTeam = ManyToOne('HitzTeam')
	winner = Field(Integer)
	date = Field(DateTime, default=datetime.datetime.now)
	event = Field(Unicode(64))

class HitzTeam(Entity):
	players = ManyToMany('HitzPlayer')