import pymem

#from helper_functions import *

# This changes everytime, make sure you put the right address
AddressList = 0x00007FF738F60000


pm = pymem.Pymem("JUMP_FORCE-Win64-Shipping.exe")


class PlayerStatus:
    def __init__(self, player_id=1):

        self.id = player_id

        PLY_PTR = pm.read_longlong(AddressList + 0x20)
        PLY_PTR = pm.read_longlong(PLY_PTR)
        
        if player_id == 2:
            PLY_PTR = pm.read_longlong(AddressList + 0x28)
            PLY_PTR = pm.read_longlong(PLY_PTR)

        self.current_character_id   = pm.read_int(PLY_PTR + 0x94)
        self.next_character_id      = pm.read_int(PLY_PTR + 0x98)
        self.hp                     = pm.read_float(PLY_PTR + 0x28)
        self.hp_max                 = pm.read_float(PLY_PTR + 0x2c)
        self.hp_percent             = self.hp / self.hp_max  # not normalized
        self.charge                 = pm.read_float(PLY_PTR + 0x30) # from 0 to 5000
        self.charge_max             = pm.read_float(PLY_PTR + 0x34) # constant 5000
        self.charge_percent         = self.charge / self.charge_max
        self.stamina                = pm.read_float(PLY_PTR + 0x38) # from 0 to 10000
        self.stamina_max            = pm.read_float(PLY_PTR + 0x3C) # constant 10000
        self.stamina_percent         = self.stamina / self.stamina_max
        self.awakening              = pm.read_float(PLY_PTR + 0x40) # from 0 to 10000
        self.awakening_max          = pm.read_float(PLY_PTR + 0x44) # constant 10000
        self.awakening_percent      = pm.read_float(PLY_PTR + 0x80) # from 0.0 to 1.0
        self.time_till_recovery     = pm.read_float(PLY_PTR + 0x54) # float value never bigger than 2.0 (usually around 0.5)
        self.tiredness              = pm.read_float(PLY_PTR + 0x5c) # big float value (from 0 to  8500 and above) limit not yet observed
        
        self.charge_level           = pm.read_float(PLY_PTR + 0x78) # Visual from 0.0 to 5.0
        self.combo                  = pm.read_int(PLY_PTR + 0x88)   # integer usually from 0 to 200, has no limit
        self.dmg_dealt              = pm.read_float(PLY_PTR + 0x8C) # float usually from 0 to 20000, has no limit
        
        self.isHalfAwakenON     = pm.read_int(PLY_PTR + 0xC4) # 0 or 1
        self.isFullAwakenON     = pm.read_int(PLY_PTR + 0xC8) # 0 or 1
        self.isGod              = pm.read_int(PLY_PTR + 0xDC) # 0 or 1 - can't be hit
        
        self.PLAYER_ACTION, self.PLAYER_ACTION_PREVIOUS, self.PLAYER_RAW_ACTION, self.PLAYER_RAW_ACTION_PREVIOUS = self.getAction()

        COORD_PTR = pm.read_longlong(AddressList + 0x40)
        if self.id == 2:
            COORD_PTR = pm.read_longlong(AddressList + 0x48)
        
        self.x = pm.read_float(COORD_PTR + 0x0)
        self.y = pm.read_float(COORD_PTR + 0x4)
        self.z = pm.read_float(COORD_PTR + 0x8)

        VPAD_PTR = pm.read_longlong(AddressList + 0x50)
        if self.id == 2:
            VPAD_PTR = pm.read_longlong(AddressList + 0x58)
        
        self.vpad = pm.read_short(VPAD_PTR + 0x8)

        

    # Function to retrieve the action of a given player
    # Raw action ids are the true id of the action, while non-raw are a "summary"
    # Eg. RAW: 41, 42 and 43 is a sequence of attacks that gets summaized into "10" meaning "Attacking"
    # "_PREVIOUS" will store the previous frame's action, given a potential delay, this would give hints on a previous state
    def getAction(self):
        
        PLAYER_ACTION = 0
        PLAYER_ACTION_PREVIOUS = 0
        PLAYER_RAW_ACTION = 0
        PLAYER_RAW_ACTION_PREVIOUS = 0
        
        if self.id == 1:
            ACTION_PTR = pm.read_longlong(AddressList + 0x10)
            
            PLAYER_ACTION = pm.read_int(ACTION_PTR + 0x00)
            PLAYER_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x08)
            PLAYER_RAW_ACTION = pm.read_int(ACTION_PTR + 0x10)
            PLAYER_RAW_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x1C)
        
        elif self.id == 2:
            ACTION_PTR = pm.read_longlong(AddressList + 0x18)
            
            PLAYER_ACTION = pm.read_int(ACTION_PTR + 0x00)
            PLAYER_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x08)
            PLAYER_RAW_ACTION = pm.read_int(ACTION_PTR + 0x10)
            PLAYER_RAW_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x1C)
        
        
        return PLAYER_ACTION, PLAYER_ACTION_PREVIOUS, PLAYER_RAW_ACTION, PLAYER_RAW_ACTION_PREVIOUS

    # Function that return variables about the game, wether or not some calculations can be performed.
    # Both InGame and Flows must be set to 100 in order to allow inputs
    def getGameStatus():
        STAT_PTR = pm.read_longlong(AddressList + 0x8)

        InGame = pm.read_int(STAT_PTR + 0x00)
        Flows = pm.read_int(STAT_PTR + 0x04)
        StartAllowed = pm.read_int(STAT_PTR + 0x8)
        StartAllowed2 = pm.read_int(STAT_PTR + 0xC)

        Paused = pm.read_int(STAT_PTR + 0x10)
        Paused2 = pm.read_int(STAT_PTR + 0x14)

        return InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2
    
    def killPlayer(self):
        
        PLY_PTR = pm.read_longlong(AddressList + 0x20)
        PLY_PTR = pm.read_longlong(PLY_PTR)
        
        if self.id == 2:
            PLY_PTR = pm.read_longlong(AddressList + 0x28)
            PLY_PTR = pm.read_longlong(PLY_PTR)
        
        pm.write_float(PLY_PTR + 0x28, 0.0)
        


    def sendInput(self, input=12345):

        CONTROLLER_PTR = pm.read_longlong(AddressList + 0x30)
        if self.id == 2:
            CONTROLLER_PTR = pm.read_longlong(AddressList + 0x38)
        
        #print(f"Player {self.id} Controller PTR: {hex(CONTROLLER_PTR)}")
        pm.write_int(CONTROLLER_PTR, input)

        


