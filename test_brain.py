from helper_functions import *
from jumpforce_rl import *
import time


while True:

    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2 = PlayerStatus.getGameStatus(1)
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

    print( math.floor(getDistance(my_state, rival_state)) )
    #print(my_state.x)
    
    # test input, charge at interval
    time.sleep(0.150)
    #my_state.sendInput(player_id=1, input=12345)
    