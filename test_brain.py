from helper_functions import *
from jumpforce_rl import *
import time
import math
import numpy as np



BRAIN_REACTION_TIME = 0.01

# How long the agent can hold information about a state + its associated reward
# Lower reaction times will lead to bigger memory sizes
MEMORY_SECONDS    = 10
MEMORY_SIZE_MAX   = int(MEMORY_SECONDS / BRAIN_REACTION_TIME)

# Fill memory with zeroes
MEMORY = {}


# Current game stats
TIME_PASSED = 0


def getSimpleReward(action):
    score = 0
    
    if action == 0:
        return -0.001
    
    # Simple reward
    if action >= 20 and action <= 24:
        score -= 0.005
    elif action >= 10 and action <= 19:
        score += 0.005
    elif action > 0:
        score += 0.001
    
    return round(score, 5)


def saveMemory(my_state:PlayerStatus, rival_state:PlayerStatus):
    mem_size = len(MEMORY)

    if mem_size >= MEMORY_SIZE_MAX:
        # remove oldest key
        oldest_key = next(iter(MEMORY))
        del MEMORY[oldest_key]

    new_key = max(MEMORY.keys(), default=-1) + 1
    
    MEMORY[new_key] = {
        0: [
            my_state.hp_percent, my_state.charge_percent, my_state.stamina_percent, my_state.awakening_percent,
            my_state.time_till_recovery, my_state.tiredness,
            my_state.combo, my_state.dmg_dealt,
            my_state.PLAYER_ACTION, my_state.PLAYER_ACTION_PREVIOUS, my_state.PLAYER_RAW_ACTION, my_state.PLAYER_RAW_ACTION_PREVIOUS,
            getSimpleReward(my_state.PLAYER_ACTION)
        ],
        1: [
            rival_state.hp_percent, rival_state.charge_percent, rival_state.stamina_percent, rival_state.awakening_percent,
            rival_state.time_till_recovery, rival_state.tiredness,
            rival_state.combo, rival_state.dmg_dealt,
            rival_state.PLAYER_ACTION, rival_state.PLAYER_ACTION_PREVIOUS, rival_state.PLAYER_RAW_ACTION, rival_state.PLAYER_RAW_ACTION_PREVIOUS,
            getSimpleReward(rival_state.PLAYER_ACTION)
        ],
        2: [TIME_PASSED, round(getDistance(my_state, rival_state), 2)]
    }

def computeAvgScore():
    global MEMORY
    score1 = 0
    score2 = 0
    for frame in MEMORY.values():
        score1 += frame[2][-1]
    
    return round(score1 / len(MEMORY), 1)
        
    

    

while True:

    # Simple system check to know if the game is ready to start (aka agent can fight)
    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2 = PlayerStatus.getGameStatus()
    if InGame < 50 or StartAllowed == 0 or StartAllowed2 == 0 or Paused == 1: #or Flows < 100
        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(0.5)
        continue

    # Time tracker
    TIME_PASSED += BRAIN_REACTION_TIME
    time.sleep(BRAIN_REACTION_TIME)
    

    # Get player stats
    my_state = PlayerStatus(1)
    rival_state = PlayerStatus(2)

    saveMemory(my_state, rival_state)
    #print(f"mem size: {len(MEMORY)}")
    #print(len(MEMORY["0"]))
    print(computeAvgScore())