from jumpforce_rl import PlayerStatus
import math

def getDistance(my_state:PlayerStatus, rival_state:PlayerStatus):
    x1, y1, z1 = my_state.x, my_state.y, my_state.z
    x2, y2, z2 = rival_state.x, rival_state.y, rival_state.z
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

"""def canGuardBreak(my_state:PlayerStatus, rival_state:PlayerStatus):
    MY_ACTION = 
    if getDistance(my_state, rival_state) <= 20 and 
    pass

local function canGuardBreak(my_state, rival_state)
    local MY_ACTION = my_state.current_action_simple
    local RIVAL_ACTION = rival_state.current_action_simple

    -- 6.88 is too low as it doesn't allow for the quick tp trick, increasing it to 20
    if getDistance2(my_state, rival_state) <= 20 and (RIVAL_ACTION == ActionType.Guarding or RIVAL_ACTION == ActionType.SuccessfulGuard)then
      return true
    end
    return false
end"""