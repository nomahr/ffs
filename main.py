import requests

#
# URL for getting the scoreboard info
# http://games.espn.com/ffl/api/v2/scoreboard2?leagueId=212084&matchupPeriodId=4&includeTopScorer=true&rand=44868

#
LEAGUE_ID = 212084
WEEK_ID = 4

def get_espn_ff_scores( in_league_id, in_week_id ):
	scoreboard_url = 'http://games.espn.com/ffl/api/v2/scoreboard2?leagueId={}&matchupPeriodId={}&includeTopScorer=true&rand=44868'.format( in_league_id, in_week_id )
	r = requests.post( scoreboard_url )

	json_raw = r.json()

	for matchup in json_raw[ 'scoreboard'][ 'matchups' ]:
		for T in matchup[ 'teams' ]:
			print( '{} {} scored {}'.format( T[ 'team' ][ 'teamLocation' ], T[ 'team' ][ 'teamNickname' ], T[ 'score' ] ) )
		print( '\n' )


if __name__ == '__main__':
	get_espn_ff_scores( LEAGUE_ID, WEEK_ID )

