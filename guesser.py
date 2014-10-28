import logging as logger
import os
from google.appengine.ext import ndb

import jinja2
import webapp2

from models import Game, Player, Turn, GameFactory


# class Game(ndb.Model):
#     """Models an individual game.
#     Each Game entity is the top of an entity group so a query across one game is consistent. """
#     min_num = ndb.IntegerProperty(indexed=False)
#     max_num = ndb.IntegerProperty(indexed=False)
#     selected_num = ndb.IntegerProperty(indexed=False)
#     max_turns = ndb.IntegerProperty(indexed=False)
#     date = ndb.DateTimeProperty(auto_now_add=True)
#     # TODO: change from string to player
#     winner_name = ndb.StringProperty()
#
#
# class Player(ndb.Model):
#     """Models a player of a specific game.
#     A specific game entity is the player's ancestor."""
#     name = ndb.StringProperty()
#     date = ndb.DateTimeProperty(auto_now_add=True)
#
#
# class Turn(ndb.Model):
#     """Models a turn of a specific player.
#     A specific player entity is the turn's ancestor."""
#     number = ndb.IntegerProperty(indexed=False)
#     date = ndb.DateTimeProperty(auto_now_add=True)
#
#
# class GameFactory:
#     @staticmethod
#     def create(min_num_str, max_num_str, max_turns_str):
#         """Creates a new game entity
#         :param min_num_str:
#         :param max_num_str:
#         :param max_turns_str:
#         :return: (new game entity, '') or (None, err_msg)
#         """
#         try:
#             min_num = int(min_num_str)
#             max_num = int(max_num_str)
#             max_turns = int(max_turns_str)
#         except ValueError:
#             return None, 'wrong input format'
#         if min_num >= max_num:
#             return None, 'min_num should be smaller than max_num'
#         if max_turns <= 0:
#             return None, 'max_turns should be positive'
#         new_game = Game(min_num=min_num, max_num=max_num,
#                         selected_num=random.randrange(min_num, max_num),
#                         max_turns=max_turns)
#         return new_game, ''


class GameHelper:
    @staticmethod
    def validate_guessed_number(game, number_str):
        try:
            number = int(number_str)
        except ValueError:
            return None, 'wrong number format'
        if number < game.min_num or number > game.max_num:
            return None, 'number out of allowed range for this game: {} to {}'.format(game.min_num, game.max_num)
        return number, ''


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
            # template_name = 'error.html'
            # template_values = {'err_msg': err_msg}
            render_error_template(self.response, err_msg)
            return
        new_game_key = new_game.put()
        url_string = new_game_key.urlsafe()
        logger.error("CreatePage.create_game(): new_game_key={}, urlString={}".format(new_game_key, url_string))
        # template_name = 'game_create_success.html'
        template_values = {'game_id': url_string}
        render_template(self.response, 'game_create_success.html', template_values)


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
    :param request:
    :param game_key:
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


def find_curr_turn(game):
    player_query = Player.query(ancestor=game.key).order(-Player.date)
    player_keys = player_query.fetch(keys_only=True)
    if len(player_keys) < PLAYERS_PER_GAME:
        # player not created yet, so need to wait for his turn
        return 0
    min_turns = game.max_turns + 10
    for player_key in player_keys:
        turn_query = Turn.query(ancestor=player_key).order(-Turn.date)
        min_turns = min(turn_query.count(), min_turns)
    return min_turns


class StatusHandler(webapp2.RequestHandler):
    # and e.g. /status?game_id=ag9kZXZ-eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDA7wgM
    def get(self):
        game, err_msg = get_game(self.request.get('game_id'))
        if game is None:
            logger.error("no game found. err_msg={}".format(err_msg))
            render_error_template(self.response, err_msg)
            return
        players_query = Player.query(ancestor=game.key).order(-Player.date)
        players = players_query.fetch(PLAYERS_PER_GAME)
        num_players = len(players)
        template_values = {
            'game': game,
            'num_players': num_players,
            'players': players,
        }
        render_template(self.response, 'status.html', template_values)


class TurnHandler(webapp2.RequestHandler):
    # TODO: change get to post
    # e.g. guess/?game_id=eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDArwoM&player=james&number=43
    def get(self):
        # try:
        #     game_key, game = get_game(self.request)
        # except Exception:
        #     render_template(self.response, 'error.html',
        #                     {'err_msg': 'game id does not exist'})
        #     return
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
            self.render_turn_template('Game is already over. The winner is {}'.format(game.winner_name))
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
            result_str = 'You are the winner. You found the right number ({}) after {} turns'\
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


application = webapp2.WSGIApplication([
    # ('/', MainPage),
    # ('/sign', Guestbook),
    ('/create', CreateHandler),  # e.g. /create?min_num=1&max_num=100&max_turns=5
    ('/status', StatusHandler),  # e.g. /status?game_id=ag9kZXZ-eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDA7woM
    ('/guess', TurnHandler),  # e.g. guess/?game_id=ag9kZXZ-eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDA7woM&player=james&number=43

], debug=True)