from helper_functions import *
from jumpforce_rl import *
import time
import math
import numpy as np
from data_type import ActionType, Vpad

REACTION_TIME_MS = 1 / 1000


def setVpad(value, mask):
    return value | mask

def clearVpad(value, mask):
    return value & ~mask


while True:

    time.sleep(REACTION_TIME_MS)

    if not PlayerStatus.isGameOn():
        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(0.5)
        continue

    my_state = PlayerStatus(1)
    rival_state = PlayerStatus(2)

    input = 0

    # Uses helper function to figure out when it can awaken
    if canAwaken(my_state, rival_state):
        input = setVpad(input, Vpad.AWAKEN)

    input = Vpad.AWAKEN
    if ActionType(rival_state.PLAYER_ACTION) in [ActionType.UsingSkill, ActionType.Attacking]:
        input=4096
    

    
    my_state.sendInput(input)
    