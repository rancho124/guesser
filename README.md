<h1>Guesser</h1>
Sample python app for google app engine.
<br>This sample app is deployed on google app engine:
http://refined-byte-747.appspot.com/

<h2>Goal</h2>
A number guessing game for 2 players.


<h2>Steps</h2>

<h3>Create a new game</h3>
Supply the required range of numbers and a maximum number of turns.
<br>The service chooses randomly a number in the required range and returns a game id.
<br>In the next steps 2 players should take turns and guess the number.

Example url for creating a game:
<br>/create?min_num=1&max_num=100&max_turns=5

Example response:
<br>New game created successfully.
<br>id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM

<h3>Make a guessing turn</h3>
Supply the game id, player name and number guessed.
<br>Every player selects his own player name.
<br>The service responds weather the number is found, or is smaller/bigger.

Example url for guessing turn:
<br>/guess?game_id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM&player=jack&number=21

Example response:
<br>Your number (21) is smaller than the target (turn 1 / 5).


<h3>Get the game status</h3>
Supply the game id.

Example url for creating a game:
<br>/status?game_id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM

