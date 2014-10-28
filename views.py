import logging as logger
import os
from google.appengine.ext import ndb

import jinja2
import webapp2

from models import Player, Turn, GameFactory, GameHelper


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def render_template(response, template_name, template_values, template_dir='templates'):
    template = JINJA_ENVIRONMENT.get_template(template_dir+'/'+template_name)
    response.write(template.render(template_values))


def render_error_template(response, err_msg):
    render_template(response, 'error.html', {'err_msg': err_msg})


class CreateHandler(webapp2.RequestHandler):
    # TODO: change get to post
    # e.g. /create?min_num=1&max_num=100&max_turns=5
    def get(self):
        min_num_str = self.request.get('min_num')
        max_num_str = self.request.get('max_num')
        max_turns_str = self.request.get('max_turns')
        new_game, err_msg = GameFactory.create(min_num_str, max_num_str, max_turns_str)
        if new_game is None:
            render_error_template(self.response, err_msg)
            return
        new_game_key = new_game.put()
        url_string = new_game_key.urlsafe()
        logger.error("CreatePage.create_game(): new_game_key={}, urlString={}".format(new_game_key, url_string))
        render_template(self.response, 'game_create_success.html', {'game_id': url_string})


def get_game(game_url_str):
    try:
        game_key = ndb.Key(urlsafe=game_url_str)
        game = game_key.get()
        if game is None:
            return None, 'game does not exist'
    except BaseException:
        return None, 'game does not exist'
    return game, ''


PLAYERS_PER_GAME = 2


def get_create_player(game, player_name):
    """
    :return: (player, '') or (None, err_msg)
    """
    players_query = \
        Player.query(ancestor=game.key).filter(ndb.GenericProperty('name') == player_name).order(-Player.date)
    player = players_query.get()
    if player is not None:
        return player, ''
    # player not found in datastore
    players_query = Player.query(ancestor=game.key).order(-Player.date)
    if players_query.count() >= PLAYERS_PER_GAME:
        return None, 'Cannot create another player for this game. Game reached max players.'
    # create a new player
    player = Player(parent=game.key, name=player_name)
    player.put()
    return player, ''


def get_turns(player_key):
    turn_query = Turn.query(ancestor=player_key).order(-Turn.date)
    return turn_query.count()


def find_curr_turn(game):
    player_query = Player.query(ancestor=game.key).order(-Player.date)
    player_keys = player_query.fetch(keys_only=True)
    if len(player_keys) < PLAYERS_PER_GAME:
        # player not created yet, so need to wait for his turn
        return 0
    min_turns = game.max_turns + 10
    for player_key in player_keys:
        # turn_query = Turn.query(ancestor=player_key).order(-Turn.date)
        # min_turns = min(turn_query.count(), min_turns)
        min_turns = min(get_turns(player_key), min_turns)
    return min_turns


class StatusHandler(webapp2.RequestHandler):
    # and e.g. /status?game_id=ag9kZXZ-eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDA7wgM
    def get(self):
        game, err_msg = get_game(self.request.get('game_id'))
        if game is None:
            logger.error("no game found. err_msg={}".format(err_msg))
            render_error_template(self.response, err_msg)
            return
        game_over = False
        curr_turn = find_curr_turn(game)
        if curr_turn >= game.max_turns:
            game_over = True
        if game.winner_name:
            game_over = True
        players_query = Player.query(ancestor=game.key).order(-Player.date)
        players = players_query.fetch(PLAYERS_PER_GAME)
        num_players = len(players)
        extended_players = []
        for player in players:
            extended_player = dict(player=player)
            extended_player['turns'] = get_turns(player.key)
            extended_players.append(extended_player)

        template_values = {
            'game': game,
            'game_over': game_over,
            'num_players': num_players,
            'expected_players': PLAYERS_PER_GAME,
            'players': extended_players,
        }
        render_template(self.response, 'status.html', template_values)


class TurnHandler(webapp2.RequestHandler):
    # TODO: change get to post
    # e.g. guess/?game_id=eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDArwoM&player=james&number=43
    def get(self):
        game, err_msg = get_game(self.request.get('game_id'))
        if game is None:
            # render_template(self.response, 'error.html', {'err_msg': err_msg})
            logger.error("no game found. err_msg={}".format(err_msg))
            render_error_template(self.response, err_msg)
            return
        player, err_msg = get_create_player(game, self.request.get('player'))
        if player is None:
            # render_template(self.response, 'error.html', {'err_msg': err_msg})
            logger.error("no player found. err_msg={}".format(err_msg))
            render_error_template(self.response, err_msg)
            return
        number, err_msg = GameHelper.validate_guessed_number(game, self.request.get('number'))
        if number is None:
            logger.error("wrong number. err_msg={}".format(err_msg))
            render_error_template(self.response, err_msg)
            return
        self.make_turn(game, player, number)

    def render_turn_template(self, message):
        render_template(self.response, 'turn.html', {'msg': message})

    # TODO: replace the result strings with proper html templates
    def make_turn(self, game, player, number):
        turn_query = Turn.query(ancestor=player.key).order(-Turn.date)
        curr_player_num_past_turns = turn_query.count()
        logger.error("curr_player_num_past_turns is {}".format(curr_player_num_past_turns))
        if game.winner_name:
            self.render_turn_template('Game is already over. The winner is {}.'.format(game.winner_name))
            return
        if curr_player_num_past_turns >= game.max_turns:
            self.render_turn_template('You have no more turns (max turns = {}).'.format(game.max_turns))
            return
        game_curr_turn = find_curr_turn(game)
        logger.error("game_curr_turn is {}".format(game_curr_turn))
        if curr_player_num_past_turns > game_curr_turn:
            self.render_turn_template('This is not your turn. Please try later.')
            return
        curr_player_turn_num = curr_player_num_past_turns + 1
        if number == game.selected_num:
            game.winner_name = player.name
            game.put()
            result_str = 'You are the winner. You found the right number ({}) after {} turns.'\
                .format(number, curr_player_turn_num)
        elif number > game.selected_num:
            result_str = 'Your number ({}) is bigger than the target (turn {} / {}).'\
                .format(number, curr_player_turn_num, game.max_turns)
        else:
            result_str = 'Your number ({}) is smaller than the target (turn {} / {}).'\
                .format(number, curr_player_turn_num, game.max_turns)
        turn = Turn(parent=player.key, number=number)
        turn.put()
        self.render_turn_template(result_str)