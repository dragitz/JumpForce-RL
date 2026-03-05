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

def canGuard(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    
    if MY_ACTION in [ActionType.Guarding, ActionType.SuccessfulGuard, ActionType.Nothing, ActionType.Moving]:
        return True
    
    if MY_ACTION in [ActionType.GettingHit, ActionType.HighSpCombatEscape, ActionType.HighSpCounterAttack, ActionType.HighSpDodge, ActionType.Thrown]:
        return True
    
    if RIVAL_ACTION in [ActionType.UsingSkill, ActionType.Attacking]:
        return True

    if RIVAL_ACTION in [ActionType.JumpHeavyAttack, ActionType.JumpHeavyAttackCharged, ActionType.JumpLightAttack, ActionType.JumpLightAttackCharged]:
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

    if dist > 10.5:
        return False
    
    if RIVAL_ACTION in [ActionType.GettingHit, ActionType.BrokenGuard]:
        return True
    
    if MY_ACTION in [ActionType.Attacking, ActionType.Nothing]:
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

def canJumpHeavy(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    # Ensure enemy can be hit
    if RIVAL_ACTION not in [ActionType.Nothing, ActionType.Moving, ActionType.Attacking, ActionType.Follow]:
        return False

    frame = my_state.PLAYER_ACTION_FRAME

    if getDistance(my_state, rival_state) >= 6 or MY_ACTION != ActionType.Jumping or frame <= 20:
        return False
    
    # Ensure enemy can be hit
    if RIVAL_ACTION in [ActionType.Awakening, ActionType.UsingSkill]:
        return False
    
    return True

def canGrab(my_state:PlayerStatus, rival_state:PlayerStatus):
    
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)
    
    frame = rival_state.PLAYER_ACTION_FRAME

    
    if getDistance(my_state, rival_state) >= 3.5: #4.01 3.5 is safer
        return False

    # Ensure I can grab
    if MY_ACTION not in [ActionType.Nothing, ActionType.Moving, ActionType.Incoming]:
        return False
    
    # Ensure enemy can be grabbed
    if RIVAL_ACTION not in [ActionType.Nothing, ActionType.Moving, ActionType.UsingSkill, 
                            ActionType.Attacking, ActionType.StandingUp, ActionType.GettingHit,
                            ActionType.Guarding, ActionType.SuccessfulGuard]:
        return False

    # Edge case, when someone uses an ultimate, both players will get teleported really close
    # which will return true, we force it to false (frame counter is a useful metric)
    if RIVAL_ACTION == ActionType.UsingSkill and frame < 5:
        return False
    
    return True


# This is a generic function, must be combined with (eg) my_state.canUseSkillUlt
# Note: this function ignores super
def canUseSKills(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    if MY_ACTION in [ActionType.GettingHit, ActionType.UsingSkill, ActionType.Thrown, ActionType.Awakening, ActionType.Attacking]:
        return False
    
    if my_state.charge < 1000:
        return False
    
    if (my_state.canUseSkillCircle + my_state.canUseSkillSquare + my_state.canUseSkillTriangle) == 0:
        return False
    
    # Check if enemy can guard
    if RIVAL_ACTION in [ActionType.Nothing, ActionType.Guarding, ActionType.Moving, ActionType.Follow, ActionType.Incoming, ActionType.SuccessfulGuard, ActionType.HighSpCombatEscape]:
        return False

    # Other states where the enemy can't be hit
    if RIVAL_ACTION in [ActionType.Awakening] or rival_state.isGod == 1:
        return False
    
    return True

def canUseUlt(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    # Basic condition
    if my_state.canUseSkillUlt == 0:
        return False
    
    # Check if we can exploit frames
    if RIVAL_ACTION in [ActionType.VulnerableFramePerfect, ActionType.VulnerableSecondFrame]:
        return True
    
    # Make ai not spam raw supers
    if my_state.hp_percent > 0.5 and my_state.isHalfAwakenON == 0 and rival_state.hp_percent > 0.3:
        return False

    # Some generic states where it is impossible to use it
    if MY_ACTION in [ActionType.GettingHit, ActionType.Awakening, ActionType.BrokenGuard]:
        return False

    # Check if enemy can guard
    if RIVAL_ACTION in [ActionType.Nothing, ActionType.Guarding, ActionType.Moving, ActionType.Follow, ActionType.Incoming, ActionType.SuccessfulGuard, ActionType.HighSpCombatEscape]:
        return False

    return True

def canHighSpeedCounter(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)
    
    my_frame = my_state.PLAYER_ACTION_FRAME
    rival_frame = rival_state.PLAYER_ACTION_FRAME

    dist = getDistance(my_state, rival_state)

    if dist >= 10.0:
        return False
    
    if RIVAL_ACTION != ActionType.HighSpCounterAttack:
        return False
    
    if my_frame <= 10 or rival_frame <= 10:
        return False
    
    if my_state.stamina_percent <= 0.05:
        return False
    
    return True


def canHighSpeedDodge(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)
    
    my_frame = my_state.PLAYER_ACTION_FRAME
    rival_frame = rival_state.PLAYER_ACTION_FRAME

    dist = getDistance(my_state, rival_state)


    if dist <= 0.60 or dist > 0.61:
        return False
    
    if RIVAL_ACTION != ActionType.HighSpDodge or MY_ACTION == ActionType.Thrown:
        return False
    
    # We can't use frames (bug?)
    #if my_frame <= 10 or rival_frame <= 10:
    #    return False
    
    # Enter stamina conserve mode
    if my_state.stamina_percent <= 0.2:
        return False
    
    return True


# Important note: since the escape and follow button is the same, we have to ensure the rules are properly set to not interact with each other
# Eg. the escape would be a waste, but follow is allowed therefore the ai learns to exploit that condition.

def canEscape(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)
    
    # I must be getting hit
    if MY_ACTION != ActionType.GettingHit:
        return False
    
    # Don't waste stamina, unless your health is low
    if (my_state.stamina_percent <= 0.1 or my_state.stamina_percent >= 0.8) and my_state.hp_percent >= 0.5:
        return False

    # Disallow if rival is far and not using a skill
    if getDistance(my_state, rival_state) >= 20 and RIVAL_ACTION != ActionType.UsingSkill:
        return False


    return True


def canFollow(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    # nope, would interfere too much
    #if not canEscape(my_state, rival_state) :
    #    return False
    
    # Disallow in some situations
    if RIVAL_ACTION in [ActionType.UsingSkill, ActionType.Awakening, ActionType.Attacking, ActionType.Nothing]:
        return False

    # Escape counter
    if RIVAL_ACTION == ActionType.HighSpCombatEscape and RIVAL_ACTION_PREVIOUS == ActionType.GettingHit and rival_state.PLAYER_ACTION_FRAME <= 20:
        return True

    # Enemy is grabbing
    if canGrab(rival_state, my_state) and RIVAL_ACTION in [ActionType.VulnerableFramePerfect, ActionType.VulnerableSecondFrame]:
        return True
    
    # Generic moments
    if MY_ACTION in [ActionType.Jumping, ActionType.Nothing, ActionType.Moving]:
        return True

    return False


def canCharge(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    # Generally charging is better done at further distances, also don't spend time charging
    if getDistance(my_state, rival_state) < 15 or my_state.charge >= 4000:
        return False
    

    # Rival is doing or about to behave aggressively
    if RIVAL_ACTION in [ActionType.UsingSkill, ActionType.Incoming, ActionType.SwappedCharacter]:
        return False


    if MY_ACTION in [ActionType.Moving, ActionType.Nothing, ActionType.Charging]:
        return True

    
    return False


def canJump(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    if MY_ACTION in [ActionType.OnGround, ActionType.StandingUp, ActionType.Nothing, ActionType.Moving, ActionType.Jumping]:
        return True

    return False

def canSwap(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    if my_state.switchCharacterTimer1 == 0:
        return True
    
    return False

