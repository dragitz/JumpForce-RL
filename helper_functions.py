from jumpforce_rl import PlayerStatus
from data_type import ActionType
import math

def getDistance(my_state:PlayerStatus, rival_state:PlayerStatus):
    x1, y1, z1 = my_state.x, my_state.y, my_state.z
    x2, y2, z2 = rival_state.x, rival_state.y, rival_state.z
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def getArenaDistance(my_state:PlayerStatus):
    
    sides = []

    x1, y1, z1 = my_state.x, my_state.y, my_state.z
    
    x2, y2, z2 = 35, 0, 0
    sides.append(math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2))

    x2, y2, z2 = -35, 0, 0
    sides.append(math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2))

    x2, y2, z2 = 0, 0, 35
    sides.append(math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2))

    x2, y2, z2 = 0, 0, -35
    sides.append(math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2))

    return sides



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

    distance = getDistance(my_state, rival_state)

    # We just got hit, can't do this
    if MY_ACTION == ActionType.GettingHit and my_state.PLAYER_ACTION_FRAME <= 7:
        return False

    if RIVAL_ACTION_PREVIOUS in [ActionType.HighSpDodge, ActionType.HighSpCounterAttack]:
        return True
    
    # Normal situations
    if MY_ACTION in [ActionType.Guarding, ActionType.SuccessfulGuard, 
                     ActionType.Nothing, ActionType.Moving, ActionType.Charging, 
                     ActionType.HighSpCombatEscape, ActionType.GettingHit]: #  and RIVAL_ACTION in [ActionType.UsingSkill, ActionType.Attacking]
        return True

    # Parry those
    if RIVAL_ACTION in [ActionType.JumpHeavyAttack, ActionType.JumpHeavyAttackCharged, 
                        ActionType.JumpLightAttack, ActionType.JumpLightAttackCharged,
                        ActionType.ChargedAttack] and distance < 10:
        return True
    
    # Vanish
    if my_state.stamina_percent >= 0.1:
        if MY_ACTION in [ActionType.GettingHit, ActionType.HighSpCombatEscape, 
                     ActionType.HighSpCounterAttack, ActionType.HighSpDodge, 
                     ActionType.Thrown, ActionType.StandingUp] or RIVAL_ACTION in [ActionType.HighSpCounterAttack, ActionType.HighSpDodge]:
            return True
    
    # Cancel incoming
    if MY_ACTION in [ActionType.Incoming, ActionType.Follow] and distance < 30:
        return True
    
    if MY_ACTION in [ActionType.SwappedCharacter] or RIVAL_ACTION in [ActionType.SwappedCharacter]:
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
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    dist = getDistance(my_state, rival_state)
    my_frame = my_state.PLAYER_ACTION_FRAME
    rival_frame = my_state.PLAYER_ACTION_FRAME

    # Too late to attack, enemy can parry
    if RIVAL_ACTION in [ActionType.Attacking, ActionType.ChargedAttack] and rival_frame >= 60:
        return False

    # If I'm attacking (spamming it) and enemy just dodged (both on ground), then stop attacking
    if MY_ACTION == ActionType.Attacking and my_frame >= 40:
        if RIVAL_ACTION == ActionType.HighSpDodge or RIVAL_ACTION_PREVIOUS == ActionType.HighSpDodge:
            return False 

    # Counter values
    if MY_ACTION_PREVIOUS in [ActionType.Incoming, ActionType.Thrown,
                              ActionType.GettingHit, ActionType.Nothing, 
                              ActionType.Jumping, ActionType.GuardDodge, 
                              ActionType.ChargedAttack, ActionType.Attacking]: # UsingSkill detected, maybe bug
        if dist >= 0.6 and dist < 7 and my_frame >= 8 and my_frame < 172:
            return True
    
    # No spam
    if dist > 10.5 or my_frame <= 10:
        return False
    
    # Generic actions
    if RIVAL_ACTION in [ActionType.UsingSkill]:
        return False
    
    if RIVAL_ACTION in [ActionType.GettingHit, ActionType.BrokenGuard, ActionType.HighSpDodge, 
                        ActionType.HighSpCounterAttack, ActionType.Attacking, ActionType.SwappedCharacter, ActionType.StandingUp]:
        return True
    
    if MY_ACTION in [ActionType.Attacking, ActionType.Nothing, ActionType.ChargedAttack, ActionType.Jumping]:
        return True

    if RIVAL_ACTION_PREVIOUS in [ActionType.GettingHit]:
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

    
    if getDistance(my_state, rival_state) >= 3.5 or frame >= 60: #4.01 3.5 is safer
        return False

    # Those can't be grabbed
    if RIVAL_ACTION in [ActionType.JumpHeavyAttack, ActionType.JumpHeavyAttackCharged, 
                        ActionType.JumpLightAttack, ActionType.JumpLightAttackCharged]:
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
    
    # Situations where it is not possible
    if MY_ACTION == ActionType.GettingHit:
        return False
    
    #print(MY_ACTION)

    return True


# This is a generic function, must be combined with (eg) my_state.canUseSkillUlt
# Note: this function ignores super
def canUseSKills(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    if MY_ACTION in [ActionType.GettingHit, ActionType.UsingSkill, 
                     ActionType.Thrown, ActionType.Awakening, 
                     ActionType.Attacking, ActionType.Follow, ActionType.Incoming, ActionType.StandingUp]:
        return False
    
    if my_state.charge < 1000:
        return False
    
    if (my_state.canUseSkillCircle + my_state.canUseSkillSquare + my_state.canUseSkillTriangle) == 0:
        return False
    
    # Check if enemy can guard
    if RIVAL_ACTION in [ActionType.Nothing, ActionType.Guarding, ActionType.Moving, 
                        ActionType.Follow, ActionType.Incoming, ActionType.SuccessfulGuard, ActionType.HighSpCombatEscape]:
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

    # Make ai not spam raw supers
    if my_state.isHalfAwakenON == 0 and (my_state.hp_percent > 0.5 or rival_state.hp_percent > 0.3) :
        return False

    # Check if enemy can guard
    if RIVAL_ACTION in [ActionType.Nothing, ActionType.Guarding, ActionType.Moving, 
                        ActionType.Follow, ActionType.Incoming, ActionType.SuccessfulGuard, 
                        ActionType.HighSpCombatEscape,ActionType.StandingUp, ActionType.OnGround]:
        return False
    
    # Enemy can guard?
    if RIVAL_ACTION_PREVIOUS in [ActionType.Incoming, ActionType.Follow]:
        return False
    

    # At some point (aka frames) opponent can guard regardless of current and previous state
    # observation is at 188 frames
    if rival_state.PLAYER_ACTION_FRAME >= 100:
        return False

    # Check if we can exploit frames
    if RIVAL_ACTION in [ActionType.VulnerableFramePerfect, ActionType.VulnerableSecondFrame]:
        return True
    

    # Some generic states where it is impossible to use it
    if MY_ACTION in [ActionType.GettingHit, ActionType.Awakening, ActionType.BrokenGuard]:
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
    
    distance = getDistance(my_state, rival_state)

    # Disallow in some situations
    if RIVAL_ACTION in [ActionType.UsingSkill, ActionType.Awakening, ActionType.Attacking,
                        ActionType.Nothing, ActionType.Guarding, ActionType.SuccessfulGuard, ActionType.GuardDodge]:
        return False

    # Should not do it
    if RIVAL_ACTION in [ActionType.JumpHeavyAttack, ActionType.JumpHeavyAttackCharged, 
                        ActionType.JumpLightAttack, ActionType.JumpLightAttackCharged] and distance < 15:
        return False
    
    # Escape counter
    if RIVAL_ACTION == ActionType.HighSpCombatEscape and RIVAL_ACTION_PREVIOUS == ActionType.GettingHit and rival_state.PLAYER_ACTION_FRAME <= 20:
        return True

    # Enemy is grabbing
    if canGrab(rival_state, my_state) and RIVAL_ACTION in [ActionType.VulnerableFramePerfect, ActionType.VulnerableSecondFrame]:
        return True
    
    # Follow after throw or combo started
    if MY_ACTION in [ActionType.ComboStarted] or RIVAL_ACTION in [ActionType.Thrown]:
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
    if RIVAL_ACTION in [ActionType.UsingSkill, ActionType.Incoming, 
                        ActionType.SwappedCharacter, ActionType.StandingUp,
                        ActionType.VulnerableFramePerfect, ActionType.VulnerableSecondFrame]:
        return False


    if MY_ACTION in [ActionType.Moving, ActionType.Nothing, ActionType.Charging]:
        return True

    
    return False


def canJump(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    if RIVAL_ACTION in [ActionType.Guarding, ActionType.SuccessfulGuard] or getDistance(my_state, rival_state) > 30:
        return False
    
    if MY_ACTION in [ActionType.OnGround, ActionType.StandingUp, ActionType.Nothing]: #, ActionType.Jumping , ActionType.Moving when moving for some reason it doesn't jump?
        return True
    
    return False

def canSwap(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    # Time is probably frozen
    if my_state.PLAYER_ACTION_FRAME == 0 or rival_state.PLAYER_ACTION_FRAME == 0:
        return False
    
    # Useless moment to swap
    if RIVAL_ACTION in [ActionType.Charging]:
        return False
    
    if MY_ACTION == ActionType.GettingHit:
        return False
    
    if my_state.switchCharacterTimer1 == 0:
        return True
    
    return False


# TODO: Eg when enemy attacks at close range, don't move? 
# has to be added to the mask
def canMove(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = ActionType(my_state.PLAYER_ACTION)
    MY_ACTION_PREVIOUS = ActionType(my_state.PLAYER_ACTION_PREVIOUS)
    RIVAL_ACTION = ActionType(rival_state.PLAYER_ACTION)
    RIVAL_ACTION_PREVIOUS = ActionType(rival_state.PLAYER_ACTION_PREVIOUS)

    dist = getDistance(my_state, rival_state)
        
    if MY_ACTION == ActionType.Nothing and RIVAL_ACTION in [ActionType.Attacking, ActionType.UsingSkill] and dist < 15:
        return False
    
    return True