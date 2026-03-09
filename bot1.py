from helper_functions import *
from jumpforce_rl import *
import time
import math
import numpy as np
from data_type import ActionType, Vpad

REACTION_TIME_MS = 0.1 / 1000


def setVpad(value, mask):
    if value == 12345:
        value = 0
    
    return value | mask

def clearVpad(value, mask):
    return value & ~mask

MY_STATE = None
RIVAL_STATE = None

P1_PREV = None
P2_PREV = None

max_dist = 0
min_dist = 99
max_frame = 0
min_frame = 99

VALID_STATES = []

ACTION_BUFFER = []  # rolling history of recent actions
BUFFER_SIZE = 10

minX = -35
maxX = 35
minZ = -35
maxZ = 35

centerX = (minX + maxX) / 2
centerZ = (minZ + maxZ) / 2
radius  = (maxX - minX) / 2

print("Radius:",radius)

centerX = (minX + maxX) / 2.0
centerZ = (minZ + maxZ) / 2.0

print("Center: ", centerX, centerZ)

while True:

    # setup previous frame
    if MY_STATE != None:
        P1_PREV = MY_STATE.clone()
        P2_PREV = RIVAL_STATE.clone()

    time.sleep(REACTION_TIME_MS)

    if not PlayerStatus.isGameOn():
        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(0.5)
        continue

    MY_STATE = PlayerStatus(1)
    RIVAL_STATE = PlayerStatus(2)
    
    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, isBattleComplete, PauseTriggered, CombatTimer, WhoAmI = PlayerStatus.getGameStatus()

    distance = getDistance(MY_STATE, RIVAL_STATE)

    if P1_PREV == None:
        continue
    
    frame = P1_PREV.PLAYER_ACTION_FRAME
    changed = MY_STATE.PLAYER_ACTION != P1_PREV.PLAYER_ACTION

    print(getDistance(MY_STATE,RIVAL_STATE))

    if changed and ActionType(MY_STATE.PLAYER_ACTION) == ActionType.HighSpCounterAttack:
        
        #print(f"Action changed: {P1_PREV.PLAYER_ACTION} -> {MY_STATE.PLAYER_ACTION} (raw: {MY_STATE.PLAYER_ACTION})")
        
        if distance < min_dist:
            min_dist = distance
        if distance > max_dist:
            max_dist = distance
        if P1_PREV.PLAYER_ACTION_FRAME < min_frame:
            min_frame = P1_PREV.PLAYER_ACTION_FRAME
        if P1_PREV.PLAYER_ACTION_FRAME > max_frame:
            max_frame = P1_PREV.PLAYER_ACTION_FRAME

        print("Counter: ",min_dist, max_dist, min_frame, max_frame)

        if P1_PREV.PLAYER_ACTION not in VALID_STATES:
            VALID_STATES.append(P1_PREV.PLAYER_ACTION)
            print(f"New pre-counter state: {P1_PREV.PLAYER_ACTION} ({ActionType(P1_PREV.PLAYER_ACTION)})")

