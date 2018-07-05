import logging
import json
import requests

from flask import Flask
from flask import request as flask_request
from flask import make_response as flask_make_response

from ffs_config import valid_slack_token
from ffs_config import valid_slack_commands
from ffs_config import valid_url
from ffs_config import league_id 

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

	logging.info( r.status_code )
	logging.info( r.text )

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
basic_200_response = { 'response_type' : 'ephemeral', 'text' : 'huzzah' }
fail_response_message = { 'response_type' : 'ephemeral', 'text' : 'Invalid request' }
success_message = { 'response_type' : 'ephemeral', 'text' : 'Huzzah! Scores!!' }
help_message = { 'response_type' : 'ephemeral', 'text' : 'How to use /itoys', 'attachments' : [ { 'text' : '/itoys [command] [param1] ... [paramN]' } ] }

#
# slack command functions
#
def itoys_main( func, args ):
	logging.info( 'func={}, args={}'.format( func.__name__, args ) )
	if not args is None:
		args_list = args.split()
		return func( *args_list )
	else:
		return func()

def itoys_fail():
	response = flask_make_response( json.dumps( fail_response_message ) )
	response.headers[ 'Content-type' ] = 'application/json'
	return response

def itoys_help():
	return help_message

def itoys_reticlesonyateticles_scores( week_id, blah_param, param1 ):
	print 'week_id={}, blah_param={}, param1={}'.format( week_id, blah_param, param1 )
	scoreboard_url = valid_url.format( league_id, week_id )
	scores_text = scoreboard_url # get_espn_ff_scores( league_id, week_id )
	scores_message = { 'response_type' : 'ephemeral', 'text' : 'Scores for Week {}'.format( week_id ), 'attachments' : [ { 'text' : scores_text } ] }
	return scores_message 

#
# slack command mappings
#
itoys_commands = {
	'help' : { 'handler' : itoys_help, 'delayed_response' : False },
	'scores' : { 'handler' : itoys_reticlesonyateticles_scores, 'delayed_response' : True }
}

#
# endpoints
#
@app.route( '/' )
def index():
	response = flask_make_response( json.dumps( basic_200_response ) )
	response.headers[ 'Content-type' ] = 'application/json'
	return response

#
# Industrial Toys slack commands
#
# /itoys [command] [param1] ... [paramN]
@app.route( '/itoys', methods=[ 'POST' ] )
def itoys():
	# validate calling token
	token = flask_request.form[ 'token' ]
	if not token == valid_slack_token:
		return itoys_fail()

	# parse command ... remove the starting slash
	command = flask_request.form[ 'command' ]
	command = command[ 1 : ]
	if not command == 'itoys':
		return itoys_fail()

	# TODO(omar): initialize delayed response

	# parse arguments ... create a tuple from any args
	text = flask_request.form[ 'text' ]
	func_args = text.split()
	if len( func_args ) > 1:
		func_key, args = text.split( None, 1 )
		func_key = func_key.strip()
	else:
		func_key = func_args[ 0 ].strip()
		args = None

	func = itoys_commands[ func_key ][ 'handler' ]

	logging.info( 'text={}, key={}, func={}, args={}'.format( text, func_key, func.__name__, args ) )

	# call command with arguments
	response_message = itoys_main( func, args )
	response = flask_make_response( json.dumps( response_message ) )
	response.headers[ 'Content-type' ] = 'application/json'
	return response


@app.errorhandler( 500 )
def server_error( e ):
	logging.exception( 'Error occurred during a request' )
	return 'Error occurred', 500


#
# test
#
if __name__ == '__main__':
	print get_espn_ff_scores( 212084, 4 )

