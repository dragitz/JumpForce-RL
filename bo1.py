from helper_functions import *
from jumpforce_rl import *
import time
import math
import numpy as np
from data_type import ActionType, Vpad

REACTION_TIME_MS = 1 / 1000


def setVpad(value, mask):
    if value == 12345:
        value = 0
    
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

    # Default, no hijacking
    input = 12345
    
    # Frame perfect quick tp after holding the attack button
    if canChargeTp(my_state, rival_state):
        input = 0
    
    
    if canJumpHeavy(my_state, rival_state):
        input = setVpad(input, Vpad.HEAVY)

    if canGrab(my_state, rival_state):
        input = setVpad(input, Vpad.GRAB)


    my_state.sendInput(input)
    
    if rival_state.PLAYER_ACTION != 23 and my_state.PLAYER_ACTION != 23:
        print(getDistance(my_state, rival_state))
    #if my_state.PLAYER_ACTION != 122 and my_state.PLAYER_ACTION_PREVIOUS != 122:
    #    print(my_state.PLAYER_ACTION_FRAME)


"""    input = 0
    input = setVpad(input, Vpad.CHARGE)
    input = setVpad(input, Vpad.UNKNOWN)

    # Uses helper function to figure out when it can awaken
    if canAwaken(my_state, rival_state):
        input = setVpad(input, Vpad.AWAKEN)

    if canAttack(my_state, rival_state):
        input = setVpad(input, Vpad.LIGHT)
        input = setVpad(input, Vpad.HEAVY)"""
    
    
    #print(my_state.vpad_left_right)
    