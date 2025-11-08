import pymem
import time

from helper_functions import *

# This changes everytime, make sure you put the right address
AddressList = 0x00007FF700040000


pm = pymem.Pymem("JUMP_FORCE-Win64-Shipping.exe")


class PlayerStatus:
    def __init__(self, player_id=1):

        PLY_PTR = pm.read_longlong(AddressList + 0x20)
        PLY_PTR = pm.read_longlong(PLY_PTR)
        
        if player_id == 2:
            PLY_PTR = pm.read_longlong(AddressList + 0x28)
            PLY_PTR = pm.read_longlong(PLY_PTR)

        self.current_character_id   = pm.read_int(PLY_PTR + 0x94)
        self.next_character_id      = pm.read_int(PLY_PTR + 0x98)
        
        self.hp                     = pm.read_float(PLY_PTR + 0x28)
        self.hp_max                 = pm.read_float(PLY_PTR + 0x2c)
        self.hp_percent             = self.hp / self.hp_max
        self.charge                 = pm.read_float(PLY_PTR + 0x30)
        self.charge_max             = pm.read_float(PLY_PTR + 0x34)
        self.stamina                = pm.read_float(PLY_PTR + 0x38)
        self.stamina_max            = pm.read_float(PLY_PTR + 0x3C)
        self.awakening              = pm.read_float(PLY_PTR + 0x40)
        self.awakening_max          = pm.read_float(PLY_PTR + 0x44)
        self.awakening_percent      = pm.read_float(PLY_PTR + 0x80)
        self.time_till_recovery     = pm.read_float(PLY_PTR + 0x54)
        self.tiredness              = pm.read_float(PLY_PTR + 0x5c)
        
        self.charge_level           = pm.read_float(PLY_PTR + 0x78)
        self.combo                  = pm.read_float(PLY_PTR + 0x88)
        self.dmg_dealt              = pm.read_float(PLY_PTR + 0x8C)
        
        self.isHalfAwakenON     = pm.read_int(PLY_PTR + 0xC4)
        self.isFullAwakenON     = pm.read_int(PLY_PTR + 0xC8)
        self.isGod              = pm.read_int(PLY_PTR + 0xDC)
        
        self.PLAYER_ACTION, self.PLAYER_ACTION_PREVIOUS, self.PLAYER_RAW_ACTION, self.PLAYER_RAW_ACTION_PREVIOUS = self.getAction(player_id)

        COORD_PTR = pm.read_longlong(AddressList + 0x40)
        if player_id == 2:
            COORD_PTR = pm.read_longlong(AddressList + 0x48)
        
        self.x = pm.read_float(COORD_PTR + 0x0)
        self.y = pm.read_float(COORD_PTR + 0x4)
        self.z = pm.read_float(COORD_PTR + 0x8)

    # Function to retrieve the action of a given player
    # Raw action ids are the true id of the action, while non-raw are a "summary"
    # Eg. RAW: 41, 42 and 43 is a sequence of attacks that gets summaized into "10" meaning "Attacking"
    # "_PREVIOUS" will store the previous frame's action, given a potential delay, this would give hints on a previous state
    def getAction(self, player_id=1):
        
        PLAYER_ACTION = 0
        PLAYER_ACTION_PREVIOUS = 0
        PLAYER_RAW_ACTION = 0
        PLAYER_RAW_ACTION_PREVIOUS = 0
        
        if player_id == 1:
            ACTION_PTR = pm.read_longlong(AddressList + 0x10)
            
            PLAYER_ACTION = pm.read_int(ACTION_PTR + 0x00)
            PLAYER_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x08)
            PLAYER_RAW_ACTION = pm.read_int(ACTION_PTR + 0x10)
            PLAYER_RAW_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x1C)
        
        elif player_id == 2:
            ACTION_PTR = pm.read_longlong(AddressList + 0x18)
            
            PLAYER_ACTION = pm.read_int(ACTION_PTR + 0x00)
            PLAYER_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x08)
            PLAYER_RAW_ACTION = pm.read_int(ACTION_PTR + 0x10)
            PLAYER_RAW_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x1C)
        
        return PLAYER_ACTION, PLAYER_ACTION_PREVIOUS, PLAYER_RAW_ACTION, PLAYER_RAW_ACTION_PREVIOUS

    # Function that return variables about the game, wether or not some calculations can be performed.
    # Both InGame and Flows must be set to 100 in order to allow inputs
    def getGameStatus(self):
        STAT_PTR = pm.read_longlong(AddressList + 0x8)

        InGame = pm.read_int(STAT_PTR + 0x00)
        Flows = pm.read_int(STAT_PTR + 0x04)
        StartAllowed = pm.read_int(STAT_PTR + 0x8)
        StartAllowed2 = pm.read_int(STAT_PTR + 0xC)

        Paused = pm.read_int(STAT_PTR + 0x10)
        Paused2 = pm.read_int(STAT_PTR + 0x14)

        return InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2

    def sendInput(self, player_id=1, input=12345):

        CONTROLLER_PTR = pm.read_longlong(AddressList + 0x30)
        if player_id == 2:
            CONTROLLER_PTR = pm.read_longlong(AddressList + 0x38)
        
        pm.write_int(CONTROLLER_PTR, input)

        


