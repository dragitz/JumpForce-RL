from helper_functions import *
from jumpforce_rl import *
import time
import math
import numpy as np


# Configurable settings
MAX_MATCH_TIME      = 99
BRAIN_REACTION_TIME_MS = 0.1 / 1000


# How long the agent can hold information about a state + its associated reward
# Lower reaction times will lead to bigger memory sizes
MEMORY_SECONDS    = MAX_MATCH_TIME
MEMORY_SIZE_MAX   = int(MEMORY_SECONDS / BRAIN_REACTION_TIME_MS)

# Each frame contains 13 inputs for each player, plus 2 global ones, then it's multiplied by the total frames in memory
PLAYER_INPUT_FRAMES = 13
GLOBAL_INPUTS = 2
INPUTS = (PLAYER_INPUT_FRAMES * 2 + GLOBAL_INPUTS) * MEMORY_SIZE_MAX

# Setup and fill memory with zeroes
MEMORY = {}
print("memory setting up..")
for frame in range(MEMORY_SIZE_MAX):
    MEMORY[frame] = {
        0: [0.0] * PLAYER_INPUT_FRAMES,
        1: [0.0] * PLAYER_INPUT_FRAMES,
        2: [0.0] * GLOBAL_INPUTS
    }
print("memory ready!")
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

# Function analyzes tracked stats during the duration of the game
def analize():
    
    """
        Cause of death
        Track how many times a raw action has been seen
    """
    tracked_raw1 = {}
    tracked_raw2 = {}
    for frame in MEMORY.values():
        raw1 = frame[0][10]
        
        if frame[1][0] == 0 and frame[1][1] == 0:
            continue

        raw2 = frame[1][10]
        raw3 = frame[1][11]

        if raw1 not in tracked_raw1:
            tracked_raw1[raw1] = 1
        else:
            tracked_raw1[raw1] += 1

        if raw2 not in tracked_raw2:
            tracked_raw2[raw2] = 1
        else:
            tracked_raw2[raw2] += 1

        if raw3 not in tracked_raw2:
            tracked_raw2[raw3] = 1
        else:
            tracked_raw2[raw3] += 1

    
    print("---------------")
    for key in tracked_raw2.keys():
        print(f"{key}: {tracked_raw2[key]}")
    print("---------------")
    




TOTAL_GAMES = 0
MY_WINS = 0
RIVAL_WINS = 0
game_ended = False

while True:

    # Simple system check to know if the game is ready to start (aka agent can fight)
    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2 = PlayerStatus.getGameStatus()
    if InGame < 50 or StartAllowed == 0 or StartAllowed2 == 0 or Paused == 1: #or Flows < 100
        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(0.5)
        continue

    # Time tracker
    TIME_PASSED += BRAIN_REACTION_TIME_MS
    time.sleep(BRAIN_REACTION_TIME_MS)
    
    # Get player stats
    my_state = PlayerStatus(1)
    rival_state = PlayerStatus(2)

    # Force match end (if equal will wait till either has lower hp)
    if TIME_PASSED >= MAX_MATCH_TIME:
        if my_state.hp_percent < rival_state.hp_percent:
            my_state.killPlayer()
            game_ended = True
        elif rival_state.hp_percent < my_state.hp_percent:
            rival_state.killPlayer()
            game_ended = True
    elif my_state.hp_percent <= 0:
        game_ended = True
    elif rival_state.hp_percent <= 0:
        game_ended = True


    saveMemory(my_state, rival_state)

    if game_ended:
        
        # Stats
        TOTAL_GAMES += 1
        if rival_state.hp_percent <= 0:
            MY_WINS += 1
        else:
            RIVAL_WINS += 1

        analize()
        TIME_PASSED = 0
        game_ended = False
        
        time.sleep(2)

    #print(f"mem size: {len(MEMORY)}")
    #print(len(MEMORY["0"]))
    