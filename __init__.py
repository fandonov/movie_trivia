# TODO: Add an appropriate license to your skill before publishing.  See
# the LICENSE file for more information.

# Below is the list of outside modules you'll be using in your skill.
# They might be built-in to Python, from mycroft-core or from external
# libraries.  If you use an external library, be sure to include it
# in the requirements.txt file so the library is installed properly
# when the skill gets installed later by a user.

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import LOG
import sqlite3
from os.path import join, abspath, dirname
import re

class MovieTriviaSkill(MycroftSkill):
	def __init__(self):
		super(MovieTriviaSkill, self).__init__(name="MovieTriviaSkill")
		self.count = 0

#how long is the movie?
#who is the director?
#who is the screen writer?
#how old was... in ...
	@intent_handler(IntentBuilder("LeadingActorsIntent").optionally("TellMe").require("PlayingIn").optionally("Movie").require("MovieName"))
	def handle_playing_in_intent(self, message):
		#~ movie = message.data.get('MovieName')
		utterance = message.data['utterance']
		match = re.search(r'(tell me )*(who plays in|the movie cast of|who stars in)( the movie)* (?P<MovieName>.*)', utterance)
		if match:
			LOG.info(match.group('MovieName'))
			movie = match.group('MovieName')
			LOG.info('MovieTrivia query for movie: %s' % movie)
			data={}
			data['movie']=movie
			try:
				conn=sqlite3.connect(dirname(__file__)+'/movies.db')
				curs=conn.cursor()
			except:
				LOG.info('MovieTriviaError: %s'%'error connecting to database')
			query = ''' 
			select people.name, casts.role from people, casts,  movies where movies.name like "%s"
			and casts.movie_id=movies.id and casts.person_id=people.id and casts.position<9 
			and (casts.job_id=4 or casts.job_id=15)
			order by position
			limit 5
			''' % movie
			curs.execute(query)
			row = curs.fetchone()
			if row!=None:
				data['lead'] = row[0]
				data['role'] = row[1]
				self.speak_dialog("in.the.movie",data)
				self.speak_dialog("movie.cast",data)
				for row in curs:
					data['lead']=row[0]
					data['role']=row[1]
					self.speak_dialog("movie.cast",data)
			else:
				self.speak_dialog("i.dont.know",data)

    # The "stop" method defines what Mycroft does when told to stop during
    # the skill's execution. In this case, since the skill's functionality
    # is extremely simple, there is no need to override it.  If you DO
    # need to implement stop, you should return True to indicate you handled
    # it.
    #
    # def stop(self):
    #    return False

def create_skill():
	return MovieTriviaSkill()
