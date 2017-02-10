# fleurs
import string

def new_game(path, list_players):
    """
    Create a new game from a '.cis' file.

    Parameters
    ----------
    path : to the cis file (str).
    list_players: list of players (list)

    Return
    -------
    game_stats : new game stats (dic).
	
	Version
    -------
    specification : Nicolas Van Bossuyt (v1. 09/02/2017)
					Bayron Mahy (v2. 10/02/2017)
    implementation : Bayron Mahy (v1. 10/02/2017)
    """
	game_stats = {'board':{}, 'players':{}, 'rounds': 0, 'max_nb_rounds': 10*len(list_players)}
	game_file= parse_game_file(path)
	for line in range(game_file['size'][0]):
            for column in range(game_file['size'][1]):
                game_stats['board'][(game_file['size'][0],game_file['size'][1])] = ''
	for player in range(list_players):
		if player == 'ai' or player == 'distant':
			type=player
		else:
			type= 'human'
		game_stats['players'][player]={'money':100, 'nb_ship': 0, 'type':type}
    raise NotImplementedError
	

def parse_game_file(path):
    """
    Parse a cis file give us his content.

    Parameter
    ---------
    path : path of the cis file (str).

    Return
    ------
    parsed_data : data containe in the cis file (dic).

    Version
    -------
    specification : Nicolas Van Bossuyt (v1. 09/02/2017)
    implementation : Nicolas Van Bossuyt (v1. 09/02/2017)
    """

    # Split file lines and remove '\n' chars.
    with file(path,'r') as f:
        file_content = [i.strip() for i in f]

    # Get the size of the gameboard.
    size_str = file_content[0].split(' ')
    size = (int(size_str[0]),int(size_str[1]))

    # Get lost space ship in the new game.
    ships_list = []
    for i in range(len(file_content)):
        ship_str = file_content[i].split(' ')
        ship = (int(ship_str[0]), int(ship_str[1]), ship_str[2])
        ships_list.append(ship)

    # Create parsed data dictionary and return it.
    parsed_data = {'size':size,'ships':ships_list}
    return parsed_data

def play_game():
    """
    Main game function thats run the game loop.
    """
    raise NotImplementedError

def show_board(game_stats):
    """
    Show the game to the user screen.

    Parameter
    ---------
    game_stats : game to show on screen (dic).
    """
    raise NotImplementedError