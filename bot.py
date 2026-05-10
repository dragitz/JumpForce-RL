from helper_functions import *
from jumpforce_rl import *
from data_type import *
from helper_actions import *

import time
import math
import numpy as np



# target reaction time at 60fps
REACTION_MS      = 10

# 4 = 240fps, 5 = 300fps, 6 = 360fps, 10 = 600fps, 15 = 900fps
SPEED_MULTIPLIER = 1       
STEP_DELAY       = (REACTION_MS / 1000) / SPEED_MULTIPLIER


TICK = 0
MIN_ACTION_TICK = 6
MAX_ACTION_TICK = 120


# Brain must always return an input
def Brain(my_state:PlayerStatus, rival_state:PlayerStatus):
    global TICK, MIN_ACTION_TICK, MAX_ACTION_TICK

    # 
    btn = 0

    TICK += 1
    if TICK > MAX_ACTION_TICK:
        TICK = 0
        return btn

    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    MY_FRAME = my_state.PLAYER_ACTION_FRAME
    RIVAL_FRAME = rival_state.PLAYER_ACTION_FRAME

    distance = getDistance(my_state, rival_state)

    # Must act after a short delay

    target_coords = [rival_state.x, rival_state.y, rival_state.z]
    #btn = goTo(my_state, rival_state, target_coords)

    if my_state.charge < 2000:
        return Xinput.Charge
    
    if MY_ACTION == ActionType.Nothing:
        btn = Xinput.SKILL_3

    #

    return btn


while True:

    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, isBattleComplete, PauseTriggered, CombatTimer, WhoAmI = PlayerStatus.getGameStatus()

    # Simple system check to know if the game is ready to start (aka agent can fight)
    if InGame < 50 or StartAllowed == 0 or StartAllowed2 == 0 or Paused == 1 or isBattleComplete == 1 \
        or PlayerStatus(1).hp_percent <= 0.0 or PlayerStatus(2).hp_percent <= 0.0:

        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(0.5)
        continue
    

    # Get player stats
    my_state = PlayerStatus(2)
    rival_state = PlayerStatus(1)

    btn = Brain(my_state, rival_state)
    print(btn)

    my_state.sendXinput(btn)
    time.sleep(STEP_DELAY)
    
    


