import random
from google.appengine.ext import ndb


class Game(ndb.Model):
    """Models an individual game.
    Each Game entity is the top of an entity group so a query across one game is consistent. """
    min_num = ndb.IntegerProperty(indexed=False)
    max_num = ndb.IntegerProperty(indexed=False)
    selected_num = ndb.IntegerProperty(indexed=False)
    max_turns = ndb.IntegerProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    # TODO: change from string to player
    winner_name = ndb.StringProperty()


class Player(ndb.Model):
    """Models a player of a specific game.
    A specific game entity is the player's ancestor."""
    name = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class Turn(ndb.Model):
    """Models a turn of a specific player.
    A specific player entity is the turn's ancestor."""
    number = ndb.IntegerProperty(indexed=False)
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
