# -*- coding: utf-8 -*-

# Alien
# ==============================================================================
# A cool friend to get in touch wile coding.

"""
						 ___---------___
					   _".^ .^ ^.  '.. :"-_
					 /:            . .^  :.:\
				   /: .   .    .        . . .:\
				  /:               .  ^ .  . .:\
				 /.                        .  .:\
				|:                    .  .  ^. .:|
				||        .                . . !:|
				\(                           . :)/
				|. ######              .#######::|
				 |.#######           ..########:|
				 \ ########          :######## :/
				  \ ########       . ########.:/
				   \. #######       #######..:/
					 \           .   .   ..:/
					  \.       | |     . .:/
						\             ..:/
						 \.           .:/
						   \   ___/  :/
							\       :/
							 |\  .:/|
							 |  --.:|
							 "(  ..)"
							/  .  .::\
"""

# Imports
# ==============================================================================
# Import some cool component for the game.

from math import *
from random import *
from termcolor import *
from time import sleep #because everyone needs to rest.
from os import system

# Game
# ==============================================================================
# Create a new game and play it.

def is_game_continue(game_stats):
	"""
	Check if a player has won the game.

	Parameters
	----------
	game_stats : game before comand execution (dic)

	Return
	------
	True if the game is not over (no one has won yet), False if someone has won.

	Version
	-------
	specifications : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1) 24/2/2017
	implementation : Alisson Leist (v1) 24/2/2017 """

	not_loser = []

	# Checking playert thats have more than on ships
	for player in game_stats['players']:

		if player == 'none':
			continue

		if game_stats['players'][player]['nb_ships'] > 0:
			not_loser.append(player)

	# Check if the game continue.
	if not (len(not_loser)==1 or game_stats['nb_rounds'] >= game_stats['max_nb_rounds']):
		return True


	winners = {}
	for player in not_loser:
		winners[player] = calculate_value(player, game_stats)

	max_value = 0
	max_value_owners = []

	for player in winners:
		if winners[player] > max_value:

			max_value = winners[player]
			max_value_owners = []
			max_value_owners.append(player)

		elif winners[player] == max_value:
			max_value_owners.append(player)

	game_stats['winners'] = max_value_owners

	return False

def calculate_value(player, game_stats):
	"""
	calculate the total ship value of a player.

	Parameters
	----------
	player : name of the player to count value (str)
	game_stats : game before comand execution (dic)


	"""
	total_value = 0

	for ship in game_stats['ships']:
		if game_stats['ships'][ship]['owner'] == player:
			total_value += game_stats['model_ship'][game_stats['ships'][ship]['type']]['price']

	return total_value

def play_game(level_name, players_list):
	"""
	Main game function which runs the game loop.

	Parameters
	----------

	level_name: name of the level (str)
	players_list: list of the players(list)

	Version
	-------
	Specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Bayron Mahy, Nicolas Van Bossuyt (v1. 15/02/17)
	"""

	game_stats = new_game(level_name, players_list)

	# Players create their ships.
	for player in game_stats['players']:
		game_stats = command_buy_ships(get_game_input(player, True, game_stats), player, game_stats)

	# Game loop.
	while is_game_continue(game_stats):
		# Show the game board to the human player.
		show_game_board(game_stats)

		# Cleaning the pending_attack list.
		game_stats['pending_attack'] = []

		# getting players input.
		for player in game_stats['players']:
			if game_stats['players'][player]['nb_ships'] > 0:
				parse_command(get_game_input(player, False, game_stats), player, game_stats)
			else:
				if game_stats['players'][player]['type'] != 'none':
					game_stats['game_logs'].append(player + ' has lost all these ships, so he has nothing to do.')

		# Do ships moves.
		do_moves(game_stats)

		# Do Attack
		for pending_attack in game_stats['pending_attack']:
			command_attack(pending_attack[0], pending_attack[1], pending_attack[2])

def new_game(level_name, players_list):
	"""
	Create a new game from a '.cis' file.

	Parameters
	----------
	level_name : name of the path to .cis file (str).
	players_list : list of players (list).

	Return
	-------
	game_stats : new game stats (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)

	Implementation : Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/2017)
					 Bayron Mahy, Nicolas Van Bossuyt (v2. 13/02/2017)
					 Nicolas Van Bossuyt (v3. 23/02/17)
	"""

	# Create game_stats dictionary.
	game_file = parse_game_file(level_name)
	game_stats = {'board':{}, 'players':{},'model_ship':{}, 'ships': {},
				  'board_size': game_file['size'],'level_name': level_name,
				  'nb_rounds': 0, 'max_nb_rounds': 10*len(players_list),
				  'pending_attacks': [], 'game_logs': [], 'winners' : []}

	# Create ship specs sheet.
	game_stats['model_ship']['fighter'] = {'icon': u'F', 'max_heal':3, 'max_speed':5, 'damages':1, 'range':5, 'price':10}
	game_stats['model_ship']['destroyer'] = {'icon': u'D', 'max_heal':8, 'max_speed':2, 'damages':2, 'range':7, 'price':20}
	game_stats['model_ship']['battlecruiser'] = {'icon': u'B', 'max_heal':20, 'max_speed':1, 'damages':4, 'range':10, 'price':30}

	# Create the game board.
	for line in range(game_file['size'][0]):
		for column in range(game_stats['board_size'][1]):
			game_stats['board'][(line,column)] = []

	# Create players.
	game_stats['players']['none'] = {'name': 'none', 'money':0, 'nb_ships': 1,'type': 'none','color':None,\
									 'ships_starting_point': (0, 0),'ships_starting_direction': (0, 0)}

	# Place lost ships.
	for ships in game_file['ships']:
		game_stats['ships'][ships[2]]= { 'type':ships[3], 'heal_points':game_stats['model_ship'][ships[3]]['max_heal'],'direction':ships[4], 'speed':0, 'owner': 'none', 'position': (ships[0],ships[1]) }
		game_stats['board'][(ships[0],ships[1])].append(ships[2])

	index_player=1
	for player in players_list:
		# Set player type.
		if '_bot' in player:
			player_type = 'ai'
		elif player == 'distant':
			player_type = 'distant'
		else:
			player_type = 'human'

		# Create new player.
		if index_player==1:
			game_stats['players'][player] = {'name': player, 'money':100, 'nb_ships': 0,'type': player_type,'color':'red',
											  'ships_starting_point': (9, 9),'ships_starting_direction': (1, 1)}
		elif index_player==2:
			game_stats['players'][player] = {'name': player, 'money':100, 'nb_ships': 0,'type': player_type,'color':'blue',
											  'ships_starting_point': (game_stats['board_size'][0]-10, game_stats['board_size'][1]-10),'ships_starting_direction': (-1, -1)}
		elif index_player==3:
			game_stats['players'][player] = {'name': player, 'money':100, 'nb_ships': 0,'type': player_type,'color':'yellow',
											  'ships_starting_point': (game_stats['board_size'][0]-10, 9),'ships_starting_direction': (-1, 1)}
		elif index_player==4:
			game_stats['players'][player] = {'name': player, 'money':100, 'nb_ships': 0,'type': player_type,'color':'magenta',
											  'ships_starting_point': (9, game_stats['board_size'][1]-10),'ships_starting_direction': (1, -1)}
		else:
			game_stats['game_logs'].append('There is too many player the player %s is a loser he must be watch you playing' % (player))

		index_player+=1

	return game_stats

# Input
# ==============================================================================
# Get input from each player.

def get_game_input(player_name, buy_ship, game_stats):
	"""
	get input from a specified player.

	Parameters
	----------
	player_name : name of the player to get input (str).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implemetation : Niolas Van Bossuyt (V1. 15/02/17)
	"""
	player_input = ''

	if game_stats['players'][player_name]['type'] == 'human':
		# get input from the human player.
		player_input = get_human_input(player_name, buy_ship, game_stats)

	elif game_stats['players'][player_name]['type'] == 'ai':
		# get input from the ai.
		player_input = get_ai_input(player_name, buy_ship, game_stats)

	elif game_stats['players'][player_name]['type'] == 'distant':
		# Get input from the remote player.
		# TODO : remote player logic.
		# player_input = get_remote_input(player, game_stats)
		pass
	elif game_stats['players'][player_name]['type'] == 'none':
		# None player ignore it.
		pass

	return player_input

# Player
# ------------------------------------------------------------------------------
# Human player interaction with the game.

def get_human_input(player_name, buy_ship, game_stats):
	"""
	Get input from a human player.

	Parameters
	----------
	player_name : Name of the player to get input from (str).
	buy_ship : the player need to buy a ship (str).
	game_stats : stats of the game (dic).

	Returns
	-------
	player_input : input from the player (str).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implemetation : Nicolas Van Bosuyt (v1 22/02/17)
	"""

	cls()
	# Show header.
	c = create_canvas(190, 5)
	put_box(c, 0, 0, 190, 5, 'single')
	put_string(c, 3, 0, '[ It\'s %s\'s turn ]' % player_name)
	put_string(c, 3, 2, 'Yours command : /ship-list, /game-command, /show-game-board')
	print_canvas(c)

	while True:

		# Getting human player input.
		print ''
		player_input = raw_input(colored('< ' + player_name + ' > : ', game_stats['players'][player_name]['color']))
		print ''

		cls()

		# Run human player command.
		if '/' in player_input:

			if player_input == '/ship-list':
				show_ship_list(c, player_name, game_stats)

			elif player_input == '/help-game-command':
				show_help_game_command(c)
				print_canvas(c)
			elif player_input == '/show-game-board':
				show_game_board(game_stats)
			else:
				print 'Wrong input'
		else:
			return player_input

def show_ship_list(c, player_name, game_stats):
	c = create_canvas(106, 10 + len(game_stats['ships']) + len(game_stats['players']) * 4)
	put_box(c, 0, 0, c['size'][0], c['size'][1], 'double')
	put_string(c, 3, 0, '[ Spaceships ]')
	line_index = 0

	# Show ships models.
	put_string(c, 3, 2, '// Spaceships Models //')
	put_string(c, 1, 3, '-'*104)
	for ship_model_name in game_stats['model_ship']:
		ship_model = game_stats['model_ship'][ship_model_name]
		put_string(c, 3, 4 + line_index, '[%s] %s // heal : %spv ~ speed : %skm/s ~ damages : %spv ~ attack range : %skm ~ price : %sG$ ' % (ship_model['icon'], ship_model_name, ship_model['max_heal'], ship_model['max_speed'], ship_model['damages'], ship_model['range'], ship_model['price']))
		line_index+=1
	put_string(c, 1, 4 + line_index, '-'*104)

	for player in game_stats['players']:
		# Show Players's ships.

		line_index += 4

		if player == 'none':
			put_string(c, 3, 2 + line_index, '// Abandonned spaceships //')
		else:
			put_string(c, 3, 2 + line_index, '// %s\'s spaceships //' % (player), color=game_stats['players'][player]['color'])

		put_string(c, 1, 3 + line_index, '-'*104)

		if game_stats['players'][player]['nb_ships'] > 0:
			for ship_name in game_stats['ships']:
				ship = game_stats['ships'][ship_name]
				if ship['owner'] == player:
					put_string(c, 3, 4 + line_index, '[%s] %s // heal : %spv ~ speed : %skm/s ~ Facing : %s' % (game_stats['model_ship'][ship['type']]['icon'], ship_name, ship['heal_points'], ship['speed'], str(ship['direction'])))
					line_index+=1
		else:
			put_string(c, 3, 4 + line_index, 'Sorry no space ships :/')
			line_index+=1

		put_string(c, 1, 4 + line_index, '-'*104)

	print_canvas(c)
def show_game_board(game_stats, color = True):
	"""
	Show the game to the user screen.

	Parameter
	---------
	game_stats : game to show on screen (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/2017)
					 Nicolas Van Bossuyt (v2. 12/02/2017)
					 Nicolas Van Bossuyt (v3. 13/02/2017)
					 Nicolas Van Bossuyt (v4. 19/02/2017)
					 Nicolas Van Bossuyt (v5. 23/02/2017)
	"""
	# Create a new canvas.
	c = create_canvas(190, 50, color)

	# Put a cool artwork on the background.
	if randint(0, 1) == 1:
		put_ascii_art(c, c['size'][0] - 71, c['size'][1] - 40, 'alien', 'green')
	else:
		put_ascii_art(c, c['size'][0] - 76, c['size'][1] - 27, 'planet')

	# Create the board frame.
	game_board_size = (game_stats['board_size'][0]*3 + 5, game_stats['board_size'][1] + 3)
	put_box(c, 0, 0, game_board_size[0], game_board_size[1])
	put_string(c, 2, 0, u'[ Coder in space : %s ]' % (game_stats['level_name']))

	# Put copyright text.
	copyright_text = '[ CoderInSpace (c) 2017 - 3342 Groupe24-Corp ]'
	put_string(c, game_board_size[0] - len(copyright_text) - 2, game_board_size[1] - 1, copyright_text)

	# Put horizontal coordinate.
	coordinate_string = ''
	for i in range(1, game_stats['board_size'][0] + 1):
		value_string = str(i)
		if len(value_string) == 1:
			value_string = ' ' + value_string
		value_string += ' '
		coordinate_string += value_string

	put_string(c, 4, 1, coordinate_string, 1, 0, 'blue', 'white')

	# Put vertical coordinate.
	for i in range(1, game_stats['board_size'][1] +1):
		value_string = str(i)
		if len(value_string) == 1:
			value_string = ' ' + value_string
		put_string(c,1,i + 1,value_string + ' ', 1,0, 'blue', 'white')

	# Put game board.
	for x in range(game_stats['board_size'][0]):
		for y in range(game_stats['board_size'][1]):
			on_screen_board_tile = (x*3 + 4, y + 2)

			# Check how many ship there are in the board tile.
			if len(game_stats['board'][(x,y)]) == 0:
				# No space ship : put the cool background.
				void_char = ['.', '*', '\'']
				if randint(0, 20) == 0:
					put_string(c, on_screen_board_tile[0], on_screen_board_tile[1], ' ' + void_char[randint(0, 2)])


			elif len(game_stats['board'][(x,y)]) == 1:
				# When there are one, show somme information about.
				ship_name = game_stats['board'][(x,y)][0]
				ship_type = game_stats['ships'][ship_name]['type']
				ship_icon = game_stats['model_ship'][ship_type]['icon']
				ship_owner = game_stats['ships'][ship_name]['owner']

				# Print ship on gameboard.
				ship_owner_color = game_stats['players'][game_stats['ships'][ship_name]['owner']]['color']

				ship_direction = game_stats['ships'][ship_name]['direction']
				ship_speed = game_stats['ships'][ship_name]['speed']

				# Pur direction line.
				direction_char = '|'

				if ship_direction == (1, 1) or ship_direction == (-1, -1):
					direction_char = '\\'
				elif ship_direction == (1, -1) or ship_direction == (-1, 1):
					direction_char = '/'
				elif ship_direction == (1, 0) or ship_direction == (-1, 0):
					direction_char = u'─'

				put_string(c, on_screen_board_tile[0] + 1 + ship_direction[0], on_screen_board_tile[1]  + ship_direction[1], direction_char, 1, 0, 'white', ship_owner_color)
				put_string(c, on_screen_board_tile[0] + 1, on_screen_board_tile[1], ship_icon,1,0,'white', ship_owner_color)
			else:
				# in other case show how many ship there are in the tile.
				put_string(c, on_screen_board_tile[0], on_screen_board_tile[1], '!' + str(len(game_stats['board'][(x,y)])),1,0,'white', 'green')

	# Put players liste frame.
	players_bord_size = ((len(game_stats['players']) - 1) * 30 + 2, 7)
	put_box(c, 0, game_board_size[1], players_bord_size[0], players_bord_size[1])
	put_string(c, 1, game_board_size[1], u'[ Players ]')

	# Put players liste.
	player_count = 0
	for player in game_stats['players']:
		if game_stats['players'][player]['type'] != 'none':
			location = ((player_count * 30) + 1, game_board_size[1] + 1,)
			put_box(c, location[0], location[1], 30, 5, 'single')

			# Put player informations.
			put_string(c, location[0] + 2, location[1] , '[ ' + game_stats['players'][player]['name'] + ' ]', color=game_stats['players'][player]['color'])
			put_string(c, location[0] + 2, location[1] + 1, 'Type : ' + game_stats['players'][player]['type'])
			put_string(c, location[0] + 2, location[1] + 2, 'Money : ' + str(game_stats['players'][player]['money']) + '$')
			put_string(c, location[0] + 2, location[1] + 3, 'Spaceship count : ' + str(game_stats['players'][player]['nb_ships']))

			player_count += 1

	# Put Game Logs frame.
	logs_size = (c['size'][0] - players_bord_size[0], 7)
	logs_location = (players_bord_size[0], game_board_size[1])
	put_box(c, logs_location[0], logs_location[1], logs_size[0], logs_size[1])
	put_string(c, logs_location[0] + 1, logs_location[1],u'[ Game Logs ]')

	line_index = 1
	for line in game_stats['game_logs'][-5:]:
		put_string(c, logs_location[0] + 1, logs_location[1] + line_index, line)
		line_index +=1

	# Show the game board in the terminal.
	print_canvas(c)

# A.I.
# ------------------------------------------------------------------------------
# AI interactions

def get_ai_input(player_name, buy_ship, game_stats):
	"""
	Get the game input from the ai.

	Parameter
	---------
	player_name : name of the player (str).
	game_stats : game stat of the current game (dic).

	Return
	------
	ai_input : game input from the ai (str).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	"""

	if buy_ship:
		return 'StarBoby:fighter me:destroyer tamere:battlecruiser'

	action = ['faster', 'slower', 'left', 'right']

	ai_input = ''

	for ship in game_stats['ships']:
		if (game_stats['ships'][ship]['owner'] == player_name):
			ai_input += ship.replace(player_name + '_','') + ':' + action[randint(0, len(action) - 1 )] + ' '

	return ai_input[:-1]

# Remote player
# ------------------------------------------------------------------------------
# Handeling remote player command.

def get_remote_input():
	# Not implemented yet.
	pass
# Gui framework
# ==============================================================================
# framework for easy user interface creation.

# Canvas creation and printing.
# ------------------------------------------------------------------------------
# Create and print a canvas in the user console.

def create_canvas(width, height, enable_color = True):
	"""
	Create a new char canvas.

	Parameters
	----------
	height : height of the game view (int).
	width : width of the game view (int).
	enable_color : enable color in the game view (bool)

	Return
	------
	canva : new char canva (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 13/02/2017)
	"""

	# Initialize the canvas.
	canvas = {'size': (width, height), 'color': enable_color, 'grid': {}}

	# Create canvas's tiles.
	for x in range(width):
		for y in range(height):
			canvas['grid'][(x,y)] = {'color':None, 'back_color':None, 'char':' '}

	# Put debug informations.
	canvas_info = '| canvas size : %d, %d |' % (width, height)
	canvas = put_box(canvas, 0, 0, width, height, 'single')
	canvas = put_string(canvas, width - len(canvas_info) - 2, height - 1, canvas_info)

	return canvas

def print_canvas(canvas):
	"""
	Print the game view in the terminal.

	Parameter
	---------
	canvas : canvas to print on screen (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/2017)
	"""

	canvas_width = canvas['size'][0]
	canvas_height = canvas['size'][1]
	line = '\033[0;0H'
	for y in range(canvas_height):

		for x in range(canvas_width):
			grid_item = canvas['grid'][(x,y)]
			char = grid_item['char']
			color = grid_item['color']
			back_color = grid_item['back_color']

			if (canvas['color']):
				line = line + colored(char, color, back_color)
			else:
				line = line + char
		line += '\n'
	print line

# Canvas drawing.
# ------------------------------------------------------------------------------
# All tools and brush to draw on the canvas.

def put(canvas, x, y, char, color = None, back_color = None):
	"""
	Put the specified char in the canvas.

	Parameters
	----------
	canvas : game view to put the char in (dic).
	x, y : coordinate of were to put the char (int).
	char : char to put (str).
	color, back_color : color for the char (string).

	Return
	------
	canvas : canvas with the char put on it (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

	# Check if the coordinate is in the bound of the game view.
	if x < canvas['size'][0] and x>=0 and\
	y < canvas['size'][1] and y >= 0:

		# Put the char a the coordinate.
		canvas['grid'][(x,y)]['char'] = char
		canvas['grid'][(x,y)]['color'] = color

		# Add the 'on_' at the start of the back_color string.
		if not back_color == None:
			canvas['grid'][(x,y)]['back_color'] = 'on_' + back_color
		else:
			canvas['grid'][(x,y)]['back_color'] = None

	return canvas

def put_rectangle(canvas, x, y, width, height, char, color = None, back_color = None):
	"""
	Put and fill a rectangle in the canvas.

	Parameters
	----------
	x, y : coordinate of the rectangle (int).
	width, height : size of the rectangle (int).
	color, back_color : color for the char (string).

	Return
	------
	canvas : canvas whith the rectangle (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

	for w in range(width):
		for h in range(height):
			canvas = put(canvas, x + w, y + h, char, color, back_color)

	return canvas
def put_box(canvas, x, y, width, height, mode = 'double', color = None, back_color = None):
	"""
	Put a box in the canvas.

	Parameters
	----------
	x, y : coordinate of the rectangle (int).
	width, height : size of the rectangle (int).
	mode : double ou single line <'double'|'single'> (str).
	color, back_color : color for the char (string).

	Return
	------
	canvas : canvas whith the box (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/17)
	"""
	if mode == 'double':
		put_rectangle(canvas, x, y, width, height, u'═', color, back_color)
		put_rectangle(canvas, x, y + 1, width, height - 2,u'║', color, back_color)
		put(canvas, x, y, u'╔', color, back_color)
		put(canvas, x, y + height - 1, u'╚', color, back_color)
		put(canvas, x + width - 1, y, u'╗', color, back_color)
		put(canvas, x + width - 1, y + height - 1, u'╝', color, back_color)

	elif mode == 'single':
		put_rectangle(canvas, x, y, width, height, u'─', color, back_color)
		put_rectangle(canvas, x, y + 1, width, height - 2,u'│', color, back_color)

		put(canvas, x, y, u'┌', color, back_color)
		put(canvas, x, y + height - 1, u'└', color, back_color)
		put(canvas, x + width - 1, y, u'┐', color, back_color)
		put(canvas, x + width - 1, y + height - 1, u'┘', color, back_color)

	put_rectangle(canvas, x + 1 , y + 1, width - 2, height - 2, ' ')

	return canvas
def put_string(canvas, x, y, string, direction_x = 1, direction_y = 0, color = None, back_color = None):
	"""
	Put a specified string in the canvas.

	Parameter
	---------
	x, y : coordinate of the string (int).
	direction_x, direction_y : direction to draw the string (int).
	canvas : game view to put the string (dic).

	Return
	------
	canvas : game view with the new string (dic).

	Notes
	-----
	direction_x, direction_y : Muste be -1, 0 or 1.

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/17)
	"""

	for char in string:
		canvas = put(canvas, x, y, char, color, back_color)
		x += direction_x
		y += direction_y

	return canvas
def put_ascii_art(canvas, x, y, ascii_art_name, color = None, back_color = None, transparency_char = None):
	"""
	Put a ascii art in the in the canvas.

	Parameters
	----------
	x, y : coordinate to pute the art (int).
	ascii_art_name : name of the art file (string).
	canvas : game view to put the art on it (dic).
	transparency_char : ignored char.

	return
	------
	canvas : game view with te ascii art (dic).

	Version
	-------
	specification  : Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (V1. 15/02/17)
				     Nicolas Van Bossuyt (v2. 26/02/17)
	"""
	art_file = open('art/' + ascii_art_name + '.txt','r')

	index = 0

	for line in art_file:
		char_index = 0
		for char in line.replace('\n', ''):
			if char != transparency_char:
				put(canvas, x + char_index, y + line_index, char, color, back_color)

			char_index += 1
		index += 1

	art_file.close()

	return canvas

# Game commands
# ==============================================================================
# Game command parsing and execution.

# Command Parsing
# ------------------------------------------------------------------------------
# From a string to a game command.

def parse_command(commands, player_name, game_stats):
	"""
	Parse a command from a player and run it.

	Parameters
	----------
	command : command from the player (str).
	game_stats : stat of the game (dic).

	Return
	------
	game_stats : game stat after the command execution (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (V1. 10/02/17)
	"""

	commands = commands.split(' ')
	for cmd in commands:
		if cmd == '':
			continue

		try:
			sub_cmd = cmd.split(':')
			ship_name = player_name + '_' + sub_cmd[0]
			ship_action = sub_cmd[1]
		except:
			print 'Syntaxe error : ' + cmd + ' ":" is missing.'
			continue

		try:
			if ship_action == 'slower' or ship_action == 'faster':
				# Speed command :
				game_stats = command_change_speed(ship_name, ship_action, game_stats)
			elif ship_action == 'left' or ship_action == 'right':
				# Rotate command :
				game_stats = command_rotate(ship_name, ship_action, game_stats)
			else:
				# Attack command :
				coordinate_str = ship_action.split('-')
				coordinate = (int(coordinate_str[0]) - 1, int(coordinate_str[1]) - 1)
				game_stats['pending_attacks'].append((ship_name, game_stats['ships'][ship_name]['position'], coordinate))

		except Exception as e:
			print ship_action + ' is invalide action, please try : "faster, slower, left, right, or 42-24".'

	return game_stats

# Ship creation
# ------------------------------------------------------------------------------
# Buy and create a spaceship.

def command_buy_ships(ships, player, game_stats):
	"""
	Allow a player to buy some spaceships.

	Parameters
	----------
	ships : spaceships to buy (str).
	player : name of the player (str).
	game_stats : stat of the game (dic).

	Return
	------
	game_stats : game stats after the operation (dic).

	Version
	-------
	specification : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 14/02/17)
					 Nicolas Van Bossuyt (v2. 23/02/17)
	"""

	for ship in ships.split(' '):
		if ship == '':
			continue

		ship = ship.split(':')

		# Allow human player to dont have to write the full ship type name.
		if ship[1][0] == 'f':
			ship[1] = 'fighter'
		elif ship[1][0] == 'd':
			ship[1] = 'destroyer'
		elif ship[1][0] == 'b':
			ship[1] = 'battlecruiser'

		ship_price = game_stats['model_ship'][ship[1]]['price']

		if ship_price <= game_stats['players'][player]['money']:
			game_stats['players'][player]['money'] -= ship_price
			create_ship(player, '%s_%s' % (player, ship[0]), ship[1], game_stats)

	return game_stats
def create_ship(player_name, ship_name, ship_type, game_stats):
	"""
	Create and add a new ship.

	Parameters
	----------
	player_name : name of the owner of the ship (str).
	ship_name : Name of the ship (str).
	ship_type : Model of the ship (str).
	game_stats : stats of the game (str).

	Return
	------
	game_stats : stats after adding the new ship (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	implementation : Nicolas Van Bossuyt (v1. 15/02/2017)
	"""

	# Creatting the new space ship and add to the game_stats.
	game_stats['ships'][ship_name] = {'type':ship_type, 'heal_points':game_stats['model_ship'][ship_type]['max_heal'], 'direction':game_stats['players'][player_name]['ships_starting_direction'], 'speed':0, 'owner': player_name, 'position': game_stats['players'][player_name]['ships_starting_point']}
	game_stats['board'][game_stats['players'][player_name]['ships_starting_point']].append(ship_name)
	game_stats['players'][player_name]['nb_ships'] += 1

	return game_stats

# Move Command
# ------------------------------------------------------------------------------
# Make shipe move, rotate, and go faste and furiouse.

def command_change_speed(ship, change, game_stats):
	"""
	Increase the speed of a ship.

	Parameters
	----------
	ship : name of the ship to Increase the speed (str).
	change : the way to change the speed <"slower"|"faster"> (str).
	game_stats : stats of the game (dic).

	Returns
	-------
	game_stats : the game after the command execution (dic)

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Bayron Mahy (v1. 10/02/2017)
	"""
	type = game_stats['ships'][ship]['type']

	# Make the ship move faster.
	if change == 'faster' and game_stats['ships'][ship]['speed'] < game_stats['model_ship'][type]['max_speed']:
		game_stats['ships'][ship]['speed']+=1

	# Make the ship move slower.
	elif change == 'slower' and game_stats['ships'][ship]['speed'] > 0:
		game_stats['ships'][ship]['speed']-=1

	# Show a message when is a invalide change.
	else:
		game_stats['game_logs'].append('you cannot make that change on the speed of "' + ship + '"')

	return game_stats
def command_rotate(ship, direction, game_stats):
	"""
	Rotate the ship.

	Parameters
	----------
	ship : name of the ship to Increase the speed.
	direction : the direction to rotate the ship <"left"|"right">(str)
	game_stats : stats of the game (dic).

	Returns
	-------
	new_game_stats : the game after the command execution.

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/17)
					 Nicolas Van Bossuyt (v2. 22/02/17)
	"""
	v = (0, 0)
	if direction == 'left':
		v = rotate_vector_2D(game_stats['ships'][ship]['direction'], -45)
	elif direction == 'right':
		v = rotate_vector_2D(game_stats['ships'][ship]['direction'], 45)

	game_stats['ships'][ship]['direction'] = to_unit_vector(v)
	return game_stats
def do_moves(game_stats):
	"""
	Apply move to ships.

	Parameters
	----------
	game_stats : stats of the game (dic)

	Return
	------
	game_stats : stats of the game after the moves (dic)

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Alisson Leist (v1. 20/02/17)
					 Nicolas Van Bosuuyt (v2. 23/02/17)
	"""
	for element in game_stats['ships'] :

		position = game_stats['ships'][element]['position']

		# Compute new position of the ship.
		move_x = game_stats['ships'][element]['speed'] * game_stats['ships'][element]['direction'][0]
		move_y = game_stats['ships'][element]['speed'] * game_stats['ships'][element]['direction'][1]

		position_x = position[0] + move_x
		position_y = position[1] + move_y

		# Apply toric space.
		if position_x >= game_stats['board_size'][0]:
			position_x -= game_stats['board_size'][0]

		elif position_x < 0:
			position_x += game_stats['board_size'][0]

		if position_y >= game_stats['board_size'][1]:
			position_y -= game_stats['board_size'][1]

		elif position_y < 0:
			position_y += game_stats['board_size'][1]

		# Create new position.
		new_position = (position_x, position_y)

		# Move the ship.
		game_stats['board'][position].remove(element)
		game_stats['board'][new_position].append(element)
		game_stats['ships'][element]['position']=new_position
		if len(game_stats['board'][new_position]) >1 and game_stats['ships'][game_stats['board'][new_position][0]]['owner']=='none':
			take_abandonned_ship(game_stats)

	return game_stats

def take_abandonned_ship(game_stats):
	""" determine who become the owner of the abandonned ship.

	Parameters
	----------
	game_stats: state of the game before the call of this function (dico)

	Returns
	-------
	game_stats: state of the game after the call of this function (dico)

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Bayron Mahy (v.1 21/02/17)
					 Bayron Mahy (v.2 22/02/17)
	"""
	for location in game_stats['board']:
		ships_on_location= game_stats['board'][location]
		if ships_on_location != []:
			nb_good_ships = 1
			if len(ships_on_location) > 2:
				owner_to_test= game_stats['ships'][ships_on_location[1]]['owner']
				for ships in ships_on_location:
					if game_stats['ships'][ships]['owner'] == owner_to_test:
						nb_good_ships+=1
			if game_stats['ships'][ships_on_location[0]]['owner']=='none' and  (nb_good_ships == len(ships_on_location)-1):

				#change owner none by the owner of the other ships
				game_stats['ships'][ships_on_location[0]]['owner']=game_stats['ships'][ships_on_location[1]]['owner']
				#c/p of the dictionnary
				game_stats['ships'][game_stats['ships'][ships_on_location[0]]['owner']+'_'+ships_on_location[0]] = game_stats['ships'][ships_on_location[0]]

				#change the name of the ex- abandonned ship on the location
				game_stats['board'][location].append(game_stats['ships'][ships_on_location[1]]['owner']+'_'+ships_on_location[0])
				del game_stats['ships'][ships_on_location[0]]
				#remove the previous name of the ships from location
				game_stats['board'][location].remove(ships_on_location[0])
				game_stats['players'][game_stats['ships'][ships_on_location[0]]['owner']]['nb_ships']+=1

	return game_stats




# Attack Command
# ------------------------------------------------------------------------------
# Allow ship to attack each other.

def command_attack(ship, ship_coordinate, target_coordinate, game_stats):
	"""
	Determine if the attack works and do it.

	Parameters
	----------
	ship_location : coodinate of the first ship (tuple(int, int)).
	coordinate : coordinate of the tile to attack (tuple(int,int)).
	game_stats : stats of the game (dic).

	Return
	------
	new_game_stats : the game after the command execution (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/2/17)
	implementation : Alisson Leist (v1. 14/2/17)
	"""

	# Retriving information from game_stats.
	board_width=game_stats['board_size'][0]
	board_height=game_stats['board_size'][1]
	damages=game_stats['ships'][ship]['damages']

	# Getting distance between ship and taget.
	if abs(target_coordinate[0] - ship_coordinate[0]) > board_width/2:
		if target_coordinate[0] < ship_coordinate[0]:
			target_coordinate[0]+=board_width
		else:
			target_coordinate[0]+=board_width

	if abs(target_coordinate[1] - ship_coordinate[1]) > board_height/2:
		if target_coordinate[1] < ship_coordinate[1]:
			target_coordinate[1]+=board_height
		else:
			ship_coordinate[1]+=board_height

	if abs((target_coordinate[0] - ship_coordinate[0])) + abs((target_coordinate[1] - ship_coordinate[1])) <= game_stats ['ships'][ship]['range'] :
		if not game_stats['board'][target_coordinate] == []:
			game_stats['nb_rounds']=0
			# Give damages to all ship on targe coordinate.
			for target_ship in game_stats['board'][target_coordinate]:
				# Give damages to the taget ship.
				game_stats['ships'][target_ship]['heal_point']-=damages
				if game_stats['ships'][target_ship]['heal_point']<=0:
					# Remove the space ship.
					game_stats['board'][target_coordinate].remove(target_ship)
					game_stats['players'][game_stats['ships'][target_ship]['owner']]['nb_ships'] -=1

	return game_stats

# Utils
# ==============================================================================
# Somme use full function for a simple life. And also parse game file.

def rotate_vector_2D(vector, theta):
	"""
	Rotate a vector in a 2D space by a specified angle in radian.

	Parameters
	----------
	vector : 2D vector ton rotate (tuple(int,int)).
	radian : angle appli to the 2D vector (float).

	Return
	------
	vector : rotate vector 2d (tuple(int,int)).

	Version
	-------
	specification :  Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 10/02/17)
					 Nicolas Van Bossuyt (v2. 22/02/17)

	Source
	------
	Use code from https://gist.github.com/mcleonard/5351452 under MIT license.
	"""

	theta = radians(theta)
	# Just applying the 2D rotation matrix
	dc, ds = cos(theta), sin(theta)
	x, y = vector[0], vector[1]
	x, y = dc*x - ds*y, ds*x + dc*y
	return (x, y)
def to_unit_vector(vector):
	"""
	Convert a vector to a unit vector.

	Parameter
	---------
	vector : vector to convert (tuple(float, float)).

	Return
	------
	unit_vector : a unit vector between 1 and -1 (tuple(int, int)).
	"""

	def convert(value):
		if value > 0.25:
			return 1
		elif value < -0.25:
			return -1

		return 0

	return (convert(vector[0]), convert(vector[1]))
def direction_to_vector2D(direction):
	"""
	Convert a string direction to a vector2D.

	Parameter
	---------
	direction : direction to convert <up|down|left|right|up-left|up-right|down-left|down-right>(str).

	Return
	------
	vector : vector2D from direction (tuple(int, int)).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v1. 11/02/17)
	"""
	vector = ()

	if direction == 'up':
		vector = (0,1)

	elif direction == 'up-right':
		vector = (1,1)

	elif direction == 'right':
		vector = (1,0)

	elif direction == 'down-right':
		vector = (1,-1)

	elif direction == 'down':
		vector = (0,-1)

	elif direction == 'down-left':
		vector = (-1,-1)

	elif direction == 'left':
		vector = (-1,0)

	elif direction == 'up-left':
		vector = (-1,1)

	return vector
def parse_game_file(path):
	"""
	Parse a .cis file and returns its content.

	Parameter
	---------
	path : path of the .cis file (str).

	Return
	------
	parsed_data : data contained in the .cis file (dic).

	Version
	-------
	specification  : Alisson Leist, Bayron Mahy, Nicolas Van Bossuyt (v1. 10/02/17)
	implementation : Nicolas Van Bossuyt (v2. 15/02/2017)
	"""
	# Split file lines and remove '\n' chars.
	cis_file = open(path,'r')
	file_content = [line.strip() for line in cis_file]
	cis_file.close()

	# Get the size of the gameboard.
	size_str = file_content[0].split(' ')
	size = (int(size_str[0]),int(size_str[1]))

	# Get lost space ship in the new game.
	ships_list = []
	for line_index in range(len(file_content) - 1):
		try:
			ship_str = file_content[line_index + 1].split(' ')
			ship_name_and_type = ship_str[2].split(':')
			ship = (int(ship_str[0]), int(ship_str[1]), ship_name_and_type[0], ship_name_and_type[1], direction_to_vector2D(ship_str[3]))
			ships_list.append(ship)
		except:
			pass

	# Create parsed data dictionary and return it.
	parsed_data = {'size':size,'ships':ships_list}

	return parsed_data

def create_game_board(file_name, board_size, lost_ships_count):
	ship_type = ['fighter', 'destroyer', 'battlecruiser']
	ship_direction = ['up', 'up-left', 'up-right', 'left', 'right', 'down', 'down-left', 'down-right']

	f = open(file_name, 'w')

	print >>f, "%d %d" % (board_size[0], board_size[1])

	for i in range(lost_ships_count):
		# print line in the file.
		print >>f, '%d %d %s:%s %s' % (random.randint(0, board_size[0] - 1),\
		random.randint(0, board_size[1] - 1), 'ship_' + str(i),  ship_type[random.randint(0, len(ship_type) - 1)],\
		ship_direction[random.randint(0, len(ship_direction) - 1)])

	f.close()


def cls():
	system('cls' if os.name=='nt' else 'clear')

# (...)Ouais, ça va être bien, ça va être très bien même… Bon, bien sûr, y faut imaginer.
# - Jamel Debbouze, Astérix & Obélix : Mission Cléopâtre (2002), écrit par Alain Chabat, René Goscinny, Albert Uderzo
