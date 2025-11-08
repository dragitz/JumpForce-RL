from helper_functions import *
from jumpforce_rl import *
import time

boot = False

while True:

    time.sleep(0.01)

    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2 = PlayerStatus.getGameStatus()
    #print(getGameStatus())

    # Simple system check to know if the game is ready to start (aka agent can fight)
    if InGame < 100 or StartAllowed == 0 or StartAllowed2 == 0 or Paused == 1: #or Flows < 100
        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(1)
        continue
    
    # Get player stats
    my_state = PlayerStatus(1)
    rival_state = PlayerStatus(2)

    
    #my_state.sendInput(player_id=1, input=65)
    if canGuardBreak(my_state, rival_state):
        my_state.sendInput(17)
        time.sleep(2.150)
    
    #print( math.floor(getDistance(my_state, rival_state)) )
    #print(my_state.x)
    
    # test input, charge at interval
    
    my_state.sendInput(input=12345)
    