import logging
import json
import requests

from flask import Flask
from flask import request as flask_request
from flask import make_response as flask_make_response

from ffs_config import valid_slack_token
from ffs_config import valid_slack_commands
from ffs_config import valid_url

# NOTE(omar): required in order to use requests lib in Google App Engine
# Use the App Engine Requests adapter. This makes sure that Requests uses URLFetch.
if not __name__ == '__main__':
	from requests_toolbelt.adapters import appengine
	appengine.monkeypatch()

# init flask app
app = Flask( __name__ )

# the actual call to get scores
def get_espn_ff_scores( in_league_id, in_week_id ):
	scoreboard_url = valid_url.format( in_league_id, in_week_id )
	r = requests.post( scoreboard_url )

	json_raw = r.json()

	scores = ''

	for matchup in json_raw[ 'scoreboard'][ 'matchups' ]:
		for team in matchup[ 'teams' ]:
			scores += '{} {} scored {}\n'.format( team[ 'team' ][ 'teamLocation' ], team[ 'team' ][ 'teamNickname' ], team[ 'score' ] )
		scores += '\n'

	return scores

#
# useful response stuff
#
fail_response_message = { 'response_type' : 'ephemeral', 'text' : 'Invalid request. Can only be called from #reticlesonyateticles' }
fail_command_message = { 'response_type' : 'ephemeral', 'text' : 'Invalid command' }
success_message = { 'response_type' : 'ephemeral', 'text' : 'Huzzah! Scores!!' }
help_message = { 'response_type' : 'ephemeral', 'text' : 'How to use /ff', 'attachments' : [ { 'text' : '/ff [week] => returns the scores for that week' } ] }

#
# endpoints
#
@app.route( '/' )
def index():
	return 'hello there'

@app.route( '/reticlesonyateticles', methods=[ 'POST' ] )
def reticles():
	# validate request based on token
	requesting_slack_token = flask_request.form[ 'token' ]
	if not requesting_slack_token == valid_slack_token:
		fail_response = flask_make_response( json.dumps( fail_response_message ) )
		fail_response.headers[ 'Content-type' ] = 'application/json'
		return fail_response

	# validate command
	command = flask_request.form[ 'command' ]
	if not command in valid_slack_commands:
		fail_command_response = flask_make_response( json.dumps( fail_command_message ) )
		fail_command_response.headers[ 'Content-type' ] = 'application/json'
		return fail_command_response

	params = flask_request.form[ 'text' ].split()

	# help response
	if 'help' in params:
		help_response = flask_make_response( json.dumps( help_message ) )
		help_response.headers[ 'Content-type' ] = 'application/json'
		return help_response

	# actual response
	week_id = int( params[0] )
	success_response = flask_make_response( json.dumps( success_message ) )
	success_response.headers[ 'Content-type' ] = 'application/json'
	return success_response


@app.errorhandler( 500 )
def server_error( e ):
	logging.exception( 'Error occurred during a request' )
	return 'Error occurred', 500


#
# test
#
if __name__ == '__main__':
	print get_espn_ff_scores( 212084, 4 )

