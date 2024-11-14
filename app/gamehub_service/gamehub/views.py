from django.http import JsonResponse, HttpResponse
import random
import string
import redis
import json
import logging
from .utils import get_current_round, get_longest_winstreak, tournament_string, round_completed, set_match_data, set_online_match, match_lobby_string, multiple_lobby_string, set_winner_multiple
from channels.layers import get_channel_layer
from django.core.exceptions import ObjectDoesNotExist
from .models import GameStatsUser, OnlineMatch, TournamentResults
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
from .custom_permissions import IsInternalContainer, IsInternalContainerFactory

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

redis = redis.Redis(host='redis', port=6379, db=0)

def lobby_name_generator():
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))

@api_view(['PUT', 'POST'])
def gamestatsuser(request):
	data = json.loads(request.body)
	if request.method == 'POST':
		try:
			uid = (int)(data.get('user_id'))
			logger.debug(f"{type(uid)} + 'uid = ' {uid}")
			username = data.get('username')
			gamestatsuser = GameStatsUser.objects.create(user_id=uid, username=username)
			if not gamestatsuser:
				return JsonResponse({'type': 'error', 'message': 'Create GameStatsUser model failed.'}, status=400)
			return JsonResponse({'type': 'success'}, status=200)
		except Exception as e:
			logger.debug(f"Error: {e}")
			return JsonResponse({'type': 'error', 'message': 'Create GameStatsUser model failed.'}, status=400)
	elif request.method == 'PUT':
		user_id = data.get('user_id')
		username = data.get('username')
		try:
			gamestatsuser = GameStatsUser.objects.get(user_id=user_id)
			gamestatsuser.username = username
			gamestatsuser.save()
			return JsonResponse({'status': 'success'})
		except GameStatsUser.DoesNotExist:
			return JsonResponse({'status': 'error', 'message': 'GameStatsUser not found'}, status=404)
	return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)



@permission_classes([IsAuthenticated])
@api_view(['GET'])
def create_lobby(request):
	user = request.user
	type = request.GET.get('type')
	if redis.sismember('user_lobbies', user.id):
		return JsonResponse({
			'type': 'error',
			'message': 'You can\'t create multiple lobbies'
		})
	lobby_id = lobby_name_generator()
	if type == 'online':
		redis.set(match_lobby_string(lobby_id), "")
	elif type == 'tournament':
		redis.set(lobby_id, "")
	elif type == 'multiple':
		redis.set(multiple_lobby_string(lobby_id), "")
	else:
		return JsonResponse({
			'type': 'error',
			'message': 'Query "type" missing in request!'
		})
	redis.sadd('user_lobbies', user.id)
	return JsonResponse({
		'type': 'success',
		'lobby': {
			'id': lobby_id,
			'role': 'admin',
		}
	})
#Not used anymore, now we have one join_lobby!
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def join_match_lobby(request, lobby_id):
	user = request.user
	if (redis.exists(match_lobby_string(lobby_id))):
		lobby_data_json = redis.get(match_lobby_string(lobby_id))
		if not lobby_data_json: 
			return (JsonResponse({'type': 'error', 'message': 'No data in redis.'}))
		lobby_data = json.loads(lobby_data_json)
		member_username = str(lobby_data.get('member_username'))
		if (member_username == "" or member_username == user.username):
			return(JsonResponse({'type': 'success'}))
		else: 
			return (JsonResponse({'type': 'error', 'message': 'Lobby already full.'}))
	else: 
		return(JsonResponse({'type': 'error', 'message': 'Lobby does not exist.'}))
	

@api_view(['POST'])
@permission_classes([IsInternalContainerFactory(['daphne_gameloop'])])
def update_match(request):
	data = json.loads(request.body)
	if data is None:
		return HttpResponse(status=400)
	if not data['lobby_id'] or not data['type']:
		return HttpResponse(status=400)
	if data['type'] == 'match':
		if data['home_username'] == None or data['away_username'] == None or data['home_score'] == None or data['away_score'] == None:
			return HttpResponse(status=400)
		if not isinstance(data['home_score'], int) or not isinstance(data['away_score'], int):
			return HttpResponse(status=400)
		try:
			data['home'] = GameStatsUser.objects.get(username=data['home_username'])
			data['away'] = GameStatsUser.objects.get(username=data['away_username'])
		except:
			return HttpResponse(status=400)
		set_online_match(data, data['lobby_id'])
	elif data['type'] == 'tournament':
		if not data['match_id'] or not data['home_score'] or not data['away_score'] or not data['status']:
			return HttpResponse(status=400)
		if not isinstance(data['home_score'], int) or not isinstance(data['away_score'], int):
			return HttpResponse(status=400)
		set_match_data(data['lobby_id'], data['match_id'], data['home_score'], data['away_score'], data['status'])
	elif data['type'] == 'multiple':
		if not data['winner_username']:
			return HttpResponse(status=400)
		set_winner_multiple(data['lobby_id'], data.winner_username)
	else:
		return HttpResponse(status=400)
	return HttpResponse(status=200)
	

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def join_lobby(request, lobby_id):
	type = request.GET.get('type')
	if type == 'tournament':
		if redis.exists(tournament_string(lobby_id)):
			return(JsonResponse({'type': 'error', 'message': 'Tournament already started.'}))
		elif redis.exists(lobby_id):
			return(JsonResponse({'type': 'success'}))
	elif type == 'multiple':
		if redis.exists(multiple_lobby_string(lobby_id)):
			data = redis.get(multiple_lobby_string(lobby_id))
			if data:
				data = json.loads(data)
				if data['status'] == 'pending':
					return(JsonResponse({'type': 'success'}))
				else:
					return(JsonResponse({'type': 'error', 'message': 'Match already started.'}))
	elif type == 'online':
		user = request.user
		if (redis.exists(match_lobby_string(lobby_id))):
			lobby_data_json = redis.get(match_lobby_string(lobby_id))
			if not lobby_data_json: 
				return (JsonResponse({'type': 'error', 'message': 'No data in redis.'}))
			lobby_data = json.loads(lobby_data_json)
			member_username = str(lobby_data.get('member_username'))
			if (member_username == "" or member_username == user.username):
				return(JsonResponse({'type': 'success'}))
			else: 
				return (JsonResponse({'type': 'error', 'message': 'Lobby already full.'}))
	return(JsonResponse({'type': 'error', 'message': 'Lobby does not exist.'}))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lobby_data(request, lobby_id):
	type = request.GET.get('type')
	if type == 'match':
		online_match_json = redis.get(match_lobby_string(lobby_id))
		if (not online_match_json):
			return (JsonResponse({'type': 'error', 'message': 'No data in redis.'}))
		channel_layer = get_channel_layer()
		(async_to_sync)(channel_layer.group_send)(
			match_lobby_string(lobby_id),
			{
				'type': 'send_online_match_list',
			}
		)
		(async_to_sync)(channel_layer.group_send)(
			match_lobby_string(lobby_id),	
			{
				'type': 'send_online_lobby_user',
			}
		)
	elif type == 'tournament':
		return get_tournament_lobby_data(lobby_id)
	elif type == 'multiple':
		multiple_data_json = redis.get(multiple_lobby_string(lobby_id))
		if (not multiple_data_json):
			return (JsonResponse({'type': 'error', 'message': 'No data in redis.'}))
		channel_layer = get_channel_layer()
		(async_to_sync)(channel_layer.group_send)(
			multiple_lobby_string(lobby_id),
			{
				'type': 'send_multiple_match_list',
			}
		)
		(async_to_sync)(channel_layer.group_send)(
			multiple_lobby_string(lobby_id),	
			{
				'type': 'send_multiple_lobby_users',
			}
		)
	return (JsonResponse({'type': 'success'}))

def get_tournament_lobby_data(lobby_id):
	tournament = redis.get(tournament_string(lobby_id))
	if tournament is None:
		return JsonResponse({'type': 'error', 'message': 'Tournament not found.'})
	tournament_dic = json.loads(tournament)
	round, start = get_current_round(tournament_dic['matches'])
	channel_layer = get_channel_layer()
	(async_to_sync)(channel_layer.group_send)(
		lobby_id,
		{
			'type': 'match_list',
		}
	)
	(async_to_sync)(channel_layer.group_send)(
		lobby_id,
		{
			'type': 'send_tournament_users',
		}
	)
	round -= 1
	if round == -1:
		round = 0
	status, tournament_finished = round_completed(tournament_dic['matches'], round)
	if status and not tournament_finished:
		(async_to_sync)(channel_layer.group_send)(
			lobby_id,
			{
				'type': 'send_round_completed'
			}
		)
	elif status and tournament_finished:
		(async_to_sync)(channel_layer.group_send)(
			lobby_id,
			{
				'type': 'send_tournament_finished',
			}
		)
	return JsonResponse({'type': 'success'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def start_tournament_round(request, lobby_id):
	tournament_matches_json = redis.get(tournament_string(lobby_id))
	if not tournament_matches_json:
		return (JsonResponse({'type': 'error', 'message': 'Tournament not found'}))
	tournament_matches = json.loads(tournament_matches_json)
	matches = tournament_matches['matches']
	round, start = get_current_round(matches)
	if round != -1 or start != -1:
		channel_layer = get_channel_layer()
		for match in matches[start:]:
			if match['round'] > round:
				break
			if match['status'] == 'pending':
				(async_to_sync)(channel_layer.group_send)(
					lobby_id,
					{
						'type': 'start_tournament_match',
						'match_id': 'tournament_' + lobby_id + '_loop_' + str(match['match_id']),
						'user1': match['home'],
						'user2': match['away'],
					}
				)
	else: 
		return JsonResponse({'type': 'error', 'message': 'No round founded'})
	return JsonResponse({'type': 'success'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def start_group_tournament(request, lobby_id):
	results_json = redis.get(lobby_id)
	if (not results_json):
		return (JsonResponse({'type': 'error', 'message': 'No data in redis.'}))
	results = json.loads(results_json)
	if (len(results) % 2 != 0):
		results.append({'user_id': -1})
	num_rounds = len(results) - 1
	num_matches_per_round = len(results) // 2
	tournament_dict = {'tournament_id': lobby_id, 'matches': []}
	match_id = 1
	for round in range(num_rounds):
		for match in range(num_matches_per_round):
			home = (round + match) % (len(results) - 1)
			away = (len(results) - 1 - match + round) % (len(results) - 1)
			if match == 0:
				away = len(results) - 1
			new_match = {
				'match_id': match_id,
				'round': round + 1,
				'score_home': 0,
				'score_away': 0,
				'status': 'pending',
			}
			if results[home]['user_id'] == -1: 
				new_match['player_home'] = 'Free from play'
				new_match['home'] = -1
				new_match['player_away'] = results[away]['player']
				new_match['away'] = results[away]['user_id']
				new_match['status'] = 'freegame'
			elif results[away]['user_id'] == -1:
				new_match['player_home'] = results[home]['player']
				new_match['home'] = results[home]['user_id']
				new_match['player_away'] = 'Free from play'
				new_match['away'] = -1
				new_match['status'] = 'freegame'
			else:
				new_match['player_home'] = results[home]['player']
				new_match['home'] = results[home]['user_id']
				new_match['player_away'] = results[away]['player']
				new_match['away'] = results[away]['user_id']
			match_id += 1

			tournament_dict['matches'].append(new_match)
	tournament_json = json.dumps(tournament_dict)
	redis.set(tournament_string(lobby_id), tournament_json)
	channel_layer = get_channel_layer()
	(async_to_sync)(channel_layer.group_send)(
		lobby_id,
		{
			'type': 'match_list',
		}
	)
	return (JsonResponse(tournament_dict))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def set_tournament_match(request):
	data = json.loads(request.body)
	tournament_id = data.get('tournament_id')
	match_id = data.get('match_id')
	score_home = data.get('score_home')
	score_away = data.get('score_away')
	if await set_match_data(tournament_id, match_id, score_home, score_away, 'finished'):
		return (JsonResponse({'type': 'success'}))
	else:
		return (JsonResponse({'type': 'error'}))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def start_game_loop(request, lobby_id):
	type = request.GET.get('type')
	if type == 'match':
		channel_layer = get_channel_layer()	
		(async_to_sync)(channel_layer.group_send)(
			match_lobby_string(lobby_id),
			{
				'type': 'send_online_start_match',
			}
		)
	elif type == 'multiple':
		channel_layer = get_channel_layer()	
		(async_to_sync)(channel_layer.group_send)(
			multiple_lobby_string(lobby_id),
			{
				'type': 'send_multiple_start_match',
			}
		)
	return (JsonResponse({'type': 'success'}))


def get_last_tournament_data(user_game_stats):
	try:
		tournaments = TournamentResults.objects.filter(user=user_game_stats).order_by('-tournament_id__date').all()

		if not tournaments:
			return None, 0
		last_tournament_result = tournaments.first()
		
		if not last_tournament_result:
			return None, 0

		last_tournament = last_tournament_result.tournament_id

		# Retrieve all results for that tournament using related_name
		tournament_results = last_tournament.all_results.all()

		# Process tournament results as needed
		results_data = []
		for result in tournament_results:
			results_data.append({
				'player': result.user.username,
				'rank': result.rank,
				'games': result.games,
				'wins': result.won,
				'losses': result.lost,
				'goals_for': result.goals_for,
				'goals_against': result.goals_against,
				'diff': result.diff,
				'points': result.points,
			})

		return (results_data, len(tournaments))

	except ObjectDoesNotExist:
		return None, 0
   

def get_match_data(user_game_stats):
	home_matches = OnlineMatch.objects.filter(home=user_game_stats)
	away_matches = OnlineMatch.objects.filter(away=user_game_stats)
	all_matches = home_matches.union(away_matches)	
	matches_data = []
	highest_win = {}
	highest_loss = {}
	form = ""	
	for match in all_matches:
		match_data = {
			'player_home': match.home.username if match.home else None,
			'player_away': match.away.username if match.away else None,
			'score_home': match.home_score,
			'score_away': match.away_score,
			'winner': match.winner.username if match.winner else None,
			'date': match.created_at.strftime('%d-%m-%Y %H:%M'),
			'modus': match.modus,
		}
		if (match.winner == user_game_stats):
			form += ('W')
			if (match.winner == match.home): #user wins at home
				if (not highest_win or abs(highest_win['score_home'] - highest_win['score_away']) < abs(match_data['score_home'] - match_data['score_away'])):
					highest_win = match_data
			else: #(match.winner is match_data['away']): #user wins away
				if (not highest_win or abs(highest_win['score_away'] - highest_win['score_home']) < abs(match_data['score_away'] - match_data['score_home'])):
					highest_win = match_data

		else:
			form += ('L')
			if (user_game_stats == match.home):
				if (not highest_loss or abs(highest_loss['score_away'] - highest_loss['score_home']) < abs(match_data['score_away'] - match_data['score_home'])):
					highest_loss = match_data
			else:
				if (not highest_loss or abs(highest_loss['score_home'] - highest_loss['score_away']) < abs(match_data['score_home'] - match_data['score_away'])):
					highest_loss = match_data
		matches_data.append(match_data)
	return matches_data, highest_win, highest_loss, form

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_data(request):
	user = request.user
	try:
		user_game_stats = GameStatsUser.objects.get(username=user.username)
	except ObjectDoesNotExist:
		return JsonResponse({'type': 'error', 'message': 'User does not exist in GameStats Object'})

	all_matches, highest_win, highest_loss, form = get_match_data(user_game_stats)
	tournament_data, tournaments_played = get_last_tournament_data(user_game_stats)

	data = {
		'type': 'success',
		'wins': user_game_stats.wins,
		'losses': user_game_stats.losses,
		'goals_for': user_game_stats.goals_for,
		'goals_against': user_game_stats.goals_against,
		'username': user_game_stats.username,
		'tournament_wins': user_game_stats.tournament_wins,
		'form': 'WLWWLW', #muss noch gebaut werden
		'matches': all_matches,
		'last_tournament': tournament_data,
		'highest_win': highest_win if highest_win else None,
		'biggest_loss': highest_loss if highest_loss else None,
		'form': form,
		'tournaments_played': tournaments_played,
		'registered': user_game_stats.created_at.strftime('%d-%m-%Y %H:%M'),
		'winstreak': get_longest_winstreak(form),
		'avatar_url': user_game_stats.avatar.url,
	}
	return JsonResponse(data)
	#

# BLOCKCHAIN-SERVICE

def bc_update_score(request):
	user_id = request.user.id
	data = json.loads(request.body)
	new_score = data.get('newScore')
	
	response = requests.post('http://blockchain:5000/update_user_score', json={'userId': user_id, 'newScore': new_score})
	return JsonResponse(response.json(), status=response.status_code)

def bc_get_score(request):
	user_id = request.user.id
	response = requests.get(f'http://blockchain:5000/get_user_score?userId={user_id}')
	return JsonResponse(response.json(), status=response.status_code)

def bc_delete_score(request):
	user_id = request.user.id
	
	response = requests.get(f'http://blockchain:5000/delete_user_score?userId={user_id}')
	return JsonResponse(response.json(), status=response.status_code)