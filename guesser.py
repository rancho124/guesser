import logging as logger
import os
import random
from google.appengine.ext import ndb
# from uuid import uuid4

import jinja2
import webapp2


# def uniq_game_key():
#     """Constructs a unique Datastore key for a Game entity based on uuid."""
#     return ndb.Key('Game', str(uuid4()))


class Game(ndb.Model):
    """Models an individual game.
    Each Game entity is the top of an entity group so a query across one game is consistent. """
    min_num = ndb.IntegerProperty(indexed=False)
    max_num = ndb.IntegerProperty(indexed=False)
    selected_num = ndb.IntegerProperty(indexed=False)
    max_turns = ndb.IntegerProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class Player(ndb.Model):
    """Models a player of a specific game.
    A specific game entity is the player's ancestor."""
    name = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class Turn(ndb.Model):
    """Models a turn of a specific player.
    A specific player entity is the turn's ancestor."""
    selected_number = ndb.IntegerProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class GameFactory:
    @staticmethod
    def create(min_num_str, max_num_str, max_turns_str):
        """Creates a new game entity
        :param min_num_str:
        :param max_num_str:
        :param max_turns_str:
        :return: (new game entity, '') or (None, err_msg)
        """
        try:
            min_num = int(min_num_str)
            max_num = int(max_num_str)
            max_turns = int(max_turns_str)
        except ValueError:
            return None, 'wrong input format'
        if min_num >= max_num:
            return None, 'min_num should be smaller than max_num'
        if max_turns <= 0:
            return None, 'max_turns should be positive'
        new_game = Game(min_num=min_num, max_num=max_num,
                        selected_num=random.randrange(min_num, max_num),
                        max_turns=max_turns)
        return new_game, ''


PLAYERS_PER_GAME = 2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def render_template(response, template_name, template_values):
    template = JINJA_ENVIRONMENT.get_template(template_name)
    response.write(template.render(template_values))


class CreatePage(webapp2.RequestHandler):
    # TODO: should change to post
    # e.g. /create?min_num=1&max_num=100&max_turns=5
    def get(self):
        min_num_str = self.request.get('min_num')
        max_num_str = self.request.get('max_num')
        max_turns_str = self.request.get('max_turns')
        # new_game, err_msg = self.create_game(min_num_str, max_num_str, max_turns_str)
        new_game, err_msg = GameFactory.create(min_num_str, max_num_str, max_turns_str)
        if new_game is None:
            template_name = 'templates/error.html'
            template_values = {'err_msg': err_msg}
        else:
            new_game_key = new_game.put()
            url_string = new_game_key.urlsafe()
            logger.error("CreatePage.create_game(): new_game_key={}, urlString={}".format(new_game_key, url_string))
            template_name = 'templates/game_create_success.html'
            template_values = {'game_id': url_string}

        render_template(self.response, template_name, template_values)

        #
        # template = JINJA_ENVIRONMENT.get_template(template_name)
        # self.response.write(template.render(template_values))


class StatusPage(webapp2.RequestHandler):
    # and e.g. /status?game_id=ag9kZXZ-eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDA7wgM
    def get(self):
        game_url_str = self.request.get('game_id')
        try:
            game_key = ndb.Key(urlsafe=game_url_str)
            game = game_key.get()
        except Exception:
            render_template(self.response, 'templates/error.html', {'err_msg': 'game id does not exist'})
            # template = JINJA_ENVIRONMENT.get_template('templates/error.html')
            # self.response.write(template.render({'err_msg': 'game id does not exist'}))
            return

        # players_query = Player.query(ancestor=game_key).order(-Player.date)
        # players = players_query.fetch(PLAYERS_PER_GAME)
        # TODO: add exception handling / validation

        template_values = {
            'game': game,
            # 'players': players,
        }

        # template = JINJA_ENVIRONMENT.get_template('templates/status.html')
        # self.response.write(template.render(template_values))
        render_template(self.response, 'templates/status.html', template_values)


class TurnPage(webapp2.RequestHandler):
    # TODO: should change to post
    # e.g. guess/?game_id=eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDArwoM&player_id=james&number=20
    def get(self):
        min_num_str = self.request.get('min_num')
        max_num_str = self.request.get('max_num')
        max_turns_str = self.request.get('max_turns')


# DEFAULT_GUESTBOOK_NAME = 'default_guestbook'
#
# # We set a parent key on the 'Greetings' to ensure that they are all in the same
# # entity group. Queries across the single entity group will be consistent.
# # However, the write rate should be limited to ~1/second.
#
#
# def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
#     """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
#     return ndb.Key('Guestbook', guestbook_name)
#
#
# class Greeting(ndb.Model):
#     """Models an individual Guestbook entry."""
#     author = ndb.UserProperty()
#     content = ndb.StringProperty(indexed=False)
#     date = ndb.DateTimeProperty(auto_now_add=True)
#
#
# class MainPage(webapp2.RequestHandler):
#
#     def get(self):
#         guestbook_name = self.request.get('guestbook_name',
#                                           DEFAULT_GUESTBOOK_NAME)
#         greetings_query = Greeting.query(
#             ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
#         greetings = greetings_query.fetch(10)
#
#         if users.get_current_user():
#             url = users.create_logout_url(self.request.uri)
#             url_linktext = 'Logout'
#         else:
#             url = users.create_login_url(self.request.uri)
#             url_linktext = 'Login'
#
#         template_values = {
#             'greetings': greetings,
#             'guestbook_name': urllib.quote_plus(guestbook_name),
#             'url': url,
#             'url_linktext': url_linktext,
#         }
#
#         template = JINJA_ENVIRONMENT.get_template('index.html')
#         self.response.write(template.render(template_values))
#
#
# class Guestbook(webapp2.RequestHandler):
#     def post(self):
#         # We set the same parent key on the 'Greeting' to ensure each Greeting
#         # is in the same entity group. Queries across the single entity group
#         # will be consistent. However, the write rate to a single entity group
#         # should be limited to ~1/second.
#         guestbook_name = self.request.get('guestbook_name',
#                                           DEFAULT_GUESTBOOK_NAME)
#         greeting = Greeting(parent=guestbook_key(guestbook_name))
#
#         if users.get_current_user():
#             greeting.author = users.get_current_user()
#
#         greeting.content = self.request.get('content')
#         greeting.put()
#
#         query_params = {'guestbook_name': guestbook_name}
#         self.redirect('/?' + urllib.urlencode(query_params))

application = webapp2.WSGIApplication([
    # ('/', MainPage),
    # ('/sign', Guestbook),
    ('/create', CreatePage),  # e.g. /create?min_num=1&max_num=100&max_turns=5
    ('/status', StatusPage),  # e.g. /status?game_id=ag9kZXZ-eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDA7wgM
    ('/guess', TurnPage),  # e.g. guess/?game_id=eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDArwoM&player_id=james&number=20

], debug=True)