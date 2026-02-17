from helper_functions import *
from jumpforce_rl import *
import time
import math
import numpy as np
from data_type import ActionType


while True:

    time.sleep(0.05)

    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, isBattleComplete, PauseTriggered, CombatTimer = PlayerStatus.getGameStatus()
    #print(getGameStatus())

    # Simple system check to know if the game is ready to start (aka agent can fight)
    if InGame < 50 or StartAllowed == 0 or StartAllowed2 == 0 or Paused == 1 or isBattleComplete == 1: #or Flows < 100
        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(0.5)
        continue
    
    # 1 = player 1
    # 2 = player 2
    # Get player stats
    my_state = PlayerStatus(2)
    rival_state = PlayerStatus(1)

    #print(getDeltas(my_state, rival_state, Frame))


    print(rival_state.PLAYER_ACTION_FRAME, PauseTriggered)
    input = 4096
    if ActionType(rival_state.PLAYER_ACTION) in [ActionType.UsingSkill, ActionType.Attacking]:
        input=4096
    
    #if canGuardBreak(my_state, rival_state):
        #my_state.sendInput(17)
        #time.sleep(2.150)
    
    #print( math.floor(getDistance(my_state, rival_state)) )
    #print(my_state.x)
    
    # test input, charge at interval
    
    my_state.sendInput(input)
    