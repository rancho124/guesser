<h1>Guesser</h1>
Sample python game for google app engine.
<br>Deployed on:
http://refined-byte-747.appspot.com/

<h2>Goal</h2>
A number guessing game for 2 players.


<h2>Steps</h2>

<h3>Create a new game</h3>
Required parameters: range of numbers and a maximum number of turns.
<br>The service chooses randomly a number in the required range and returns a game id.
<br>In the next steps 2 players should take turns and guess the number.

<b>Sample url for creating a game</b>
<br>/create?min_num=1&max_num=100&max_turns=5

<b>Sample response</b>
<br>New game created successfully.
<br>id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM

<h3>Make a guessing turn</h3>
Required parameters: the game id, player name and number guessed.
<br>Every player selects his own player name.
<br>The service responds weather the number is found, or is smaller/bigger.

<b>Sample url for guessing turn</b>
<br>/guess?game_id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM&player=jack&number=21

<b>Sample response</b>
<br>Your number (21) is smaller than the target (turn 1 / 5).


<h3>Get the game status</h3>
Required parameters: the game id.

<b>Sample url for creating a game</b>
<br>/status?game_id=ahJzfnJlZmluZWQtYnl0ZS03NDdyEQsSBEdhbWUYgICAgICAgAoM

