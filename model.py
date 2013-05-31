from elixir import *

metadata.bind = "sqlite:///hitz.db"
metadata.bind.echo = True


class HitzPlayer(Entity):
	name = Field(Unicode(64), unique=True, required=True)
	login = Field(Unicode(18), unique=True, required=True)
	password = Field(Unicode(24), required=True)
	tags = OneToMany('Tag')
	photo = Field(Binary, deferred=True)
	rating = Field(Integer, default=1200)
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

class HitzTeam(Entity):