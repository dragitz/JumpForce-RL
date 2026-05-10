from jumpforce_rl import PlayerStatus
from data_type import *
import math

def follow(direction=0):
    btn = 0

    if direction == 0:
        btn = Xinput.Follow | Xinput.Up
    elif direction == 1:
        btn = Xinput.Follow | Xinput.Down
    elif direction == 2:
        btn = Xinput.Follow | Xinput.Left
    elif direction == 3:
        btn = Xinput.Follow | Xinput.Right

    
    return btn

def walk(direction=0):
    
    if direction == 0:
        return Xinput.Up
    elif direction == 1:
        return Xinput.Down
    elif direction == 2:
        return Xinput.Left
    elif direction == 3:
        return Xinput.Right

    return Xinput.Idle

def parry(): return Xinput.Parry

def jump(): return Xinput.Jump

def attack(): return Xinput.Light

# thanks ai
def goTo(my_state:PlayerStatus, rival_state:PlayerStatus, target_coords):
    
    # angle to the target in world space
    dx_target = target_coords[0] - my_state.x
    dz_target = target_coords[2] - my_state.z
    angle_to_target = math.atan2(dz_target, dx_target)

    # angle to the rival
    dx_rival = rival_state.x - my_state.x
    dz_rival = rival_state.z - my_state.z
    angle_to_rival = math.atan2(dz_rival, dx_rival)

    # get the relative angle
    # subtracting camera angle from target angle "rotates" the world so rival is always 'Up'
    relative_angle = angle_to_target - angle_to_rival
    
    # normalize angle to be between -pi and pi
    relative_angle = (relative_angle + math.pi) % (2 * math.pi) - math.pi


    btn = Xinput.Idle
    
    # 45-degree buffer (pi/4) for each direction
    # Up is roughly 0 radians relative to the enemy
    if my_state.id == 1:
        if -math.pi/4 <= relative_angle <= math.pi/4:
            btn = Xinput.Up
        elif math.pi/4 < relative_angle <= 3*math.pi/4:
            btn = Xinput.Left
        elif -3*math.pi/4 <= relative_angle < -math.pi/4:
            btn = Xinput.Right
        else:
            btn = Xinput.Down
    else:
        if -math.pi/4 <= relative_angle <= math.pi/4:
            btn = Xinput.Down
        elif math.pi/4 < relative_angle <= 3*math.pi/4:
            btn = Xinput.Left
        elif -3*math.pi/4 <= relative_angle < -math.pi/4:
            btn = Xinput.Right
        else:
            btn = Xinput.Up

    return btn