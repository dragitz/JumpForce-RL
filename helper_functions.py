from jumpforce_rl import PlayerStatus
from data_type import ActionType
import math

def getDistance(my_state:PlayerStatus, rival_state:PlayerStatus):
    x1, y1, z1 = my_state.x, my_state.y, my_state.z
    x2, y2, z2 = rival_state.x, rival_state.y, rival_state.z
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def canGuardBreak(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    
    if getDistance(my_state, rival_state) <= 5 and (RIVAL_ACTION == ActionType.Guarding or RIVAL_ACTION == ActionType.SuccessfulGuard):
        return True

    return False

def canAwaken(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    
    if my_state.awakening_percent >= 0.5 and my_state.isHalfAwakenON == 0:
        if MY_ACTION in [ActionType.Attacking, ActionType.SwappedCharacter, 
                         ActionType.Follow, ActionType.Incoming, ActionType.Moving, ActionType.Nothing]:
            return True
    
    return False

def canAttack(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    
    dist = getDistance(my_state, rival_state)

    if dist > 15:
        return False
    
    if RIVAL_ACTION in [ActionType.GettingHit, ActionType.BrokenGuard]:
        return True
    
    return False

def canChargeTp(my_state:PlayerStatus, rival_state:PlayerStatus):

    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)

    frame = my_state.PLAYER_ACTION_FRAME

    if getDistance(my_state, rival_state) >= 25:
        return False

    if MY_ACTION == ActionType.ChargedAttack and MY_ACTION_PREVIOUS == ActionType.ChargedAttack and frame >= 8 and frame < 10:
        return True
    
    return False