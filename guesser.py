import webapp2
from views import CreateHandler, StatusHandler, TurnHandler

application = webapp2.WSGIApplication([
    # e.g. /create?min_num=1&max_num=100&max_turns=5 ==> returns a new key to be used below
    ('/create', CreateHandler),
    # e.g. /status?game_id=ag9kZXZ-eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDA7woM
    ('/status', StatusHandler),
    # e.g. guess/?game_id=ag9kZXZ-eW91ci1hcHAtaWRyEQsSBEdhbWUYgICAgIDA7woM&player=james&number=43
    ('/guess', TurnHandler),
], debug=True)