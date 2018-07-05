import requests
from ffs_config import valid_slack_token
from ffs_config import valid_slack_commands

url = 'http://localhost:9080/reticlesonyateticles'
itoys_url = 'http://localhost:9080/itoys'
data = { 'token' : valid_slack_token, 'command' : valid_slack_commands[0], 'text' : '4' }
itoys_data = { 'token' : valid_slack_token, 'command' : '/itoys', 'text' : 'help' }

def test_token( in_token ):
	invalid_token_data = data.copy()
	invalid_token_data[ 'token' ] = in_token
	r = requests.post( url, data=invalid_token_data )
	return r.text

def test_command( in_command ):
	invalid_command_data = data.copy()
	invalid_command_data[ 'command' ] = in_command
	r = requests.post( url, data=invalid_command_data )
	return r.text

def test_help():
	help_data = data.copy()
	help_data[ 'text' ] = 'help'
	r = requests.post( url, data=help_data )
	return r.text

def test_success():
	r = requests.post( url, data=data )
	return r.text

# itoys
def test_itoys_help():
	r = requests.post( itoys_url, data=itoys_data )
	return r.text

def test_itoys_scores():
	scores_data = itoys_data.copy()
	scores_data[ 'text' ] = 'scores 4 3 4'
	r = requests.post( itoys_url, data=scores_data )
	return r.text

def main():
	# print 'testing with valid token'
	# print test_token( valid_slack_token )
	# print 'testing with invalid token'
	# print test_token( 'asdf' )

	# print 'testing invalid command'
	# print test_command( '/blah' )
	# print 'testing valid command'
	# print test_command( valid_slack_commands[0] )

	# print 'testing help'
	# print test_help()

	# print 'testing success'
	# print test_success()

	print '\n\n testing itoys'
	print test_itoys_help()

	print 'testing itoys scores'
	print test_itoys_scores()


if __name__ == '__main__':
	main()
