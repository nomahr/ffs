import logging
import requests
from flask import Flask

# NOTE(omar): required in order to use requests lib in Google App Engine
# Use the App Engine Requests adapter. This makes sure that Requests uses URLFetch.
from requests_toolbelt.adapters import appengine
appengine.monkeypatch()

# init flask app
app = Flask( __name__ )

#
# NOTE(omar): URL for getting the scoreboard info
# http://games.espn.com/ffl/api/v2/scoreboard2?leagueId=212084&matchupPeriodId=4&includeTopScorer=true&rand=44868
#

def get_espn_ff_scores( in_league_id, in_week_id ):
	scoreboard_url = 'http://games.espn.com/ffl/api/v2/scoreboard2?leagueId={}&matchupPeriodId={}&includeTopScorer=false&rand=44868'.format( in_league_id, in_week_id )
	r = requests.post( scoreboard_url )

	json_raw = r.json()

	scores = ''

	for matchup in json_raw[ 'scoreboard'][ 'matchups' ]:
		for team in matchup[ 'teams' ]:
			scores += '{} {} scored {}\n'.format( team[ 'team' ][ 'teamLocation' ], team[ 'team' ][ 'teamNickname' ], team[ 'score' ] )
		scores += '\n'

	return '<pre>{}</pre>'.format( scores )

#
# endpoints
#
@app.route( '/' ) #, methods=[ 'POST' ] )
def index():
	# league_id = request.form[ 'league_id' ]
	# week_id = request.form[ 'week_id' ]
	return get_espn_ff_scores( 212084, 4 )

@app.errorhandler( 500 )
def server_error( e ):
	logging.exception( 'Error occurred during a request' )
	return 'Error occurred', 500


#
# test
#
if __name__ == '__main__':
	get_espn_ff_scores( 212084, 4 )

