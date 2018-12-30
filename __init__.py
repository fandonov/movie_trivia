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
	
def checkDB4movie(movie, query):
	LOG.info('MovieTrivia query for movie: %s' % movie)
	rows=[]
	try:
		conn=sqlite3.connect(dirname(__file__)+'/movies.db')
		curs=conn.cursor()
	except:
		LOG.info('MovieTriviaError: %s'%'error connecting to database')
	curs.execute(query % movie)
	row = curs.fetchone()		
	if row!=None:
		rows.append(row)
		for row in curs:
			rows.append(row)
	return rows
	
class MovieTriviaSkill(MycroftSkill):
	def __init__(self):
		super(MovieTriviaSkill, self).__init__(name="MovieTriviaSkill")
		self.count = 0

#how long is the movie?
#who is the screen writer of?
#how old was... in ...
#who wrote the music? (job_id=27)
#who plays #name in #movie

	@intent_handler(IntentBuilder("MovieComposerIntent").optionally("TellMe").require("Composer").optionally("Movie").require("MovieName"))
	def handle_movie_composer_intent(self, message):
		utterance = message.data['utterance']
		match = re.search(r'(tell me )*(the composer|who wrote the music|who composed the music|who is the composer|who is composer)( of| for)*( the movie)* (?P<MovieName>.*)', utterance)
		if match:
			movie = match.group('MovieName')
			query = ''' 
			select people.name from people, casts, movies where movies.name like "%s"
			and casts.movie_id=movies.id and casts.person_id=people.id 
			 and casts.job_id=27
			'''
			data={}
			data['movie']=movie
			rows=checkDB4movie(movie, query)
			LOG.info('MovieTrivia: rows len is %d'%len(rows))
			if len(rows)>0:
				for row in rows:
					if row:
						data['person'] = row[0]
						self.speak_dialog("composed.by",data)
						self.speak_dialog("movie.person",data)
			else:
				self.speak_dialog("dont.know.composer",data)


	@intent_handler(IntentBuilder("MovieDirectorIntent").optionally("TellMe").require("Director").optionally("Movie").require("MovieName"))
	def handle_movie_director_intent(self, message):
		utterance = message.data['utterance']
		match = re.search(r'(tell me )*(who is director|who is the director|who directed)( of| for)*( the movie)* (?P<MovieName>.*)', utterance)
		if match:
			movie = match.group('MovieName')
			query = ''' 
			select people.name from people, casts, movies where movies.name like "%s"
			and casts.movie_id=movies.id and casts.person_id=people.id 
			 and casts.job_id=21
			'''
			data={}
			data['movie']=movie
			rows=checkDB4movie(movie, query)
			LOG.info('MovieTrivia: rows len is %d'%len(rows))
			if len(rows)>0:
				for row in rows:
					if row:
						data['person'] = row[0]
						self.speak_dialog("directed.by",data)
						self.speak_dialog("movie.person",data)
			else:
				self.speak_dialog("dont.know.director",data)

	@intent_handler(IntentBuilder("LeadingActorsIntent").optionally("TellMe").require("PlayingIn").optionally("Movie").require("MovieName"))
	def handle_playing_in_intent(self, message):
		#~ movie = message.data.get('MovieName')
		utterance = message.data['utterance']
		match = re.search(r'(tell me )*(who plays in|the movie cast of|who stars in)( the movie)* (?P<MovieName>.*)', utterance)
		if match:
			movie = match.group('MovieName')
			query = ''' 
			select people.name, casts.role from people, casts,  movies where movies.name like "%s"
			and casts.movie_id=movies.id and casts.person_id=people.id and casts.position<9 
			and (casts.job_id=4 or casts.job_id=15)
			order by position
			limit 5
			'''			
			data={}
			data['movie']=movie
			rows=checkDB4movie(movie, query)
			if len(rows)>0:
				self.speak_dialog("in.the.movie",data)
				for row in rows:
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
