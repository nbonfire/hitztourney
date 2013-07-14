
from trueskill import *
import pickle



def setup(): #create env and save pickle
	env = TrueSkill(draw_probability=0.1)
	pickle.dump(env, open("env.p", "wb"))

if __name__ == "__main__":
	setup()