Guesser sample python app for google app engine

Goal:
A number guessing game for 2 players.

This sample app is deployed on google app engine:
http://refined-byte-747.appspot.com/

Steps:
1. Create a new game, supplying a range of numbers and a maximum number of turns.
The service chooses randomly a number in the required range and returns a game id.
In the next steps 2 players should take turns and guess the number.

Example url for creating a game:
http://refined-byte-747.appspot.com/create?min_num=1&max_num=100&max_turns=5

Example response:
New game created successfully.
id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM

2. Make a guessing turn, supplying the game id, player name and number guessed.
Every player selects his own player name.
The service responds weather the number is found, or is smaller/bigger.

Example url for guessing turn:
http://refined-byte-747.appspot.com/guess?game_id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM&player=jack&number=21

Example response:
Your number (21) is smaller than the target (turn 1 / 5).


3. Get game status, supplying the game id:

Example url for creating a game:
http://refined-byte-747.appspot.com/status?game_id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM

