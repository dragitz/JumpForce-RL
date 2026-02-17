import pymem
#from helper_functions import *

"""
-- Controller inputs for sendInput()
local AWAKEN         = 0x8000
local ESCAPE         = 0x4000
local FOLLOW         = 0x2000
local GUARD          = 0x1000
local ULTIMATE       = 0x0800
local SKILL_CIRCLE   = 0x0400
local SKILL_TRIANGLE = 0x0200
local SKILL_SQUARE   = 0x0100
local SWAP           = 0x0080
local CHARGE         = 0x0040
local HEAVY          = 0x0020
local LIGHT          = 0x0010
local GRAB           = 0x0008
local JUMP           = 0x0004
local MOVE           = 0x0002
local UNKNOWN        = 0x0001
"""



pm = pymem.Pymem("JUMP_FORCE-Win64-Shipping.exe")

module = pymem.process.module_from_name(
    pm.process_handle,
    "JUMP_FORCE-Win64-Shipping.exe"
)

BASE = module.lpBaseOfDll
ADDRESSLIST_OFFSET = 0x1ECB482
AddressList = BASE + ADDRESSLIST_OFFSET
AddressList = pm.read_longlong(AddressList)
print("JumpForce AddressList memory: ",hex(AddressList))

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
        if self.hp_max > 0:
            self.hp_percent             = self.hp / self.hp_max
        else:
            self.hp_percent = 0
        
        #print(f"Player Id: {player_id}  hp_percent: {self.hp_percent}")
        self.charge                 = pm.read_float(PLY_PTR + 0x30) # from 0 to 5000
        self.charge_max             = pm.read_float(PLY_PTR + 0x34) # constant 5000
        if self.charge_max > 0:
            self.charge_percent         = self.charge / self.charge_max
        else:
            self.charge_percent = 0

        self.stamina                = pm.read_float(PLY_PTR + 0x38) # from 0 to 10000
        self.stamina_max            = pm.read_float(PLY_PTR + 0x3C) # constant 10000
        if self.stamina_max > 0:
            self.stamina_percent         = self.stamina / self.stamina_max
        else:
            self.stamina_percent = 0

        self.awakening              = pm.read_float(PLY_PTR + 0x40) # from 0 to 10000
        self.awakening_max          = pm.read_float(PLY_PTR + 0x44) # constant 10000
        self.awakening_percent      = pm.read_float(PLY_PTR + 0x80) # from 0.0 to 1.0
        self.time_till_recovery     = pm.read_float(PLY_PTR + 0x54) # float value never bigger than 2.0 (usually around 0.5)
        self.tiredness              = pm.read_float(PLY_PTR + 0x5c) # big float value (from 0 to  8500 and above) limit not yet observed
        
        self.charge_level           = pm.read_float(PLY_PTR + 0x78) # Visual from 0.0 to 5.0
        self.combo                  = pm.read_int(PLY_PTR + 0x88)   # integer usually from 0 to 200, has no limit
        self.dmg_dealt              = pm.read_float(PLY_PTR + 0x8C) # float usually from 0 to 20000, has no limit
        
        #print(self.dmg_dealt)
        self.isHalfAwakenON     = pm.read_int(PLY_PTR + 0xC4) # 0 or 1
        self.isFullAwakenON     = pm.read_int(PLY_PTR + 0xC8) # 0 or 1
        self.isGod              = pm.read_int(PLY_PTR + 0xDC) # 0 or 1 - can't be hit
        
        # 1 can - 0 can not
        self.canUseSkillSquare      = pm.read_int(PLY_PTR + 0x270)
        self.canUseSkillTriangle    = pm.read_int(PLY_PTR + 0x274)
        self.canUseSkillCircle      = pm.read_int(PLY_PTR + 0x278)
        self.canUseSkillUlt         = pm.read_int(PLY_PTR + 0x27C)
        
        # For some reason the game tracks them all equally, choose one
        # 0.0 can - >0 can not (from 0.0 to 1.0)
        self.switchCharacterTimer1    = pm.read_int(PLY_PTR + 0x28C)
        self.switchCharacterTimer2    = pm.read_int(PLY_PTR + 0x290)
        self.switchCharacterTimer3    = pm.read_int(PLY_PTR + 0x294)
        

        # simplified and raw actions + current action frame
        self.PLAYER_ACTION, self.PLAYER_ACTION_PREVIOUS, self.PLAYER_RAW_ACTION, self.PLAYER_RAW_ACTION_PREVIOUS, self.PLAYER_ACTION_FRAME = self.getAction()

        # coords
        COORD_PTR = pm.read_longlong(AddressList + 0x40)
        if self.id == 2:
            COORD_PTR = pm.read_longlong(AddressList + 0x48)
        
        self.x = pm.read_float(COORD_PTR + 0x0)
        self.y = pm.read_float(COORD_PTR + 0x4)
        self.z = pm.read_float(COORD_PTR + 0x8)

        # virtual pad inputs (in game controller)
        VPAD_PTR = pm.read_longlong(AddressList + 0x50)
        if self.id == 2:
            VPAD_PTR = pm.read_longlong(AddressList + 0x58)
        
        self.vpad            = pm.read_short(VPAD_PTR + 0x8)
        self.vpad_left_right = pm.read_float(VPAD_PTR + 0x10)
        self.vpad_up_down    = pm.read_float(VPAD_PTR + 0x18)

        


    def clone(self):
        """Creates a snapshot copy of the current state values."""
        new_obj = PlayerStatus.__new__(PlayerStatus) # Create empty object without calling __init__
        
        # Copy standard attributes (floats, ints, bools)
        # We explicitly copy the dict to ensure we have value-copies, not references
        new_obj.__dict__ = self.__dict__.copy() 
        
        return new_obj
    # Function to retrieve the action of a given player
    # Raw action ids are the true id of the action, while non-raw are a "summary"
    # Eg. RAW: 41, 42 and 43 is a sequence of attacks that gets summaized into "10" meaning "Attacking"
    # "_PREVIOUS" will store the previous frame's action, given a potential delay, this would give hints on a previous state
    def getAction(self):
        
        PLAYER_ACTION = 0
        PLAYER_ACTION_PREVIOUS = 0
        PLAYER_RAW_ACTION = 0
        PLAYER_RAW_ACTION_PREVIOUS = 0
        PLAYER_ACTION_FRAME = 0

        if self.id == 1:
            ACTION_PTR = pm.read_longlong(AddressList + 0x10)
            
            PLAYER_ACTION = pm.read_int(ACTION_PTR + 0x00)
            PLAYER_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x08)
            PLAYER_RAW_ACTION = pm.read_int(ACTION_PTR + 0x10)
            PLAYER_RAW_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x1C)
            
            ACTION_PTR = pm.read_longlong(AddressList + 0xB0)
            PLAYER_ACTION_FRAME = pm.read_int(ACTION_PTR + 0x00)

        elif self.id == 2:
            ACTION_PTR = pm.read_longlong(AddressList + 0x18)
            
            PLAYER_ACTION = pm.read_int(ACTION_PTR + 0x00)
            PLAYER_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x08)
            PLAYER_RAW_ACTION = pm.read_int(ACTION_PTR + 0x10)
            PLAYER_RAW_ACTION_PREVIOUS = pm.read_int(ACTION_PTR + 0x1C)
            
            ACTION_PTR = pm.read_longlong(AddressList + 0xB8)
            PLAYER_ACTION_FRAME = pm.read_int(ACTION_PTR + 0x00)
        
        print(PLAYER_ACTION_FRAME)
        return PLAYER_ACTION, PLAYER_ACTION_PREVIOUS, PLAYER_RAW_ACTION, PLAYER_RAW_ACTION_PREVIOUS, PLAYER_ACTION_FRAME

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
        isBattleComplete = pm.read_int(STAT_PTR + 0x18)
        PauseTriggered = pm.read_int(STAT_PTR + 0x1C)
        CombatTimer = pm.read_int(STAT_PTR + 0x20)

        return InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, isBattleComplete, PauseTriggered, CombatTimer
    
    def isGameOn():
        InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, isBattleComplete, PauseTriggered, CombatTimer = PlayerStatus.getGameStatus()

        if InGame < 50 or StartAllowed == 0 or StartAllowed2 == 0 or Paused == 1 or isBattleComplete == 1:
            return False
        
        return True
    
    def isBattleComplete():
        InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, isBattleComplete, PauseTriggered, CombatTimer = PlayerStatus.getGameStatus()
        return isBattleComplete
    
    def killPlayer(self):
        
        PLY_PTR = pm.read_longlong(AddressList + 0x20)
        PLY_PTR = pm.read_longlong(PLY_PTR)
        
        if self.id == 2:
            PLY_PTR = pm.read_longlong(AddressList + 0x28)
            PLY_PTR = pm.read_longlong(PLY_PTR)
        
        pm.write_float(PLY_PTR + 0x28, 0.0)
        


    def sendInput(self, input=12345, stick_x=12345.0, stick_y=12345.0):

        CONTROLLER_PTR = pm.read_longlong(AddressList + 0x30)
        if self.id == 2:
            CONTROLLER_PTR = pm.read_longlong(AddressList + 0x38)
        
        #print(f"Player {self.id} Controller PTR: {hex(CONTROLLER_PTR)}")
        pm.write_int(CONTROLLER_PTR, input)

        pm.write_float(CONTROLLER_PTR + 0x8, stick_x)
        pm.write_float(CONTROLLER_PTR + 0x10, stick_y)


    def sendPS4Input(self, CustomInput=0, RequestedL2=0, RequestedR2=0, RequestedLeftRight=0.0, RequestedUpDown=0.0):
        # Section dedicated to ps4 controller inputs (player 1 only)
        if self.id == 1:
            CustomInput_PTR = pm.read_longlong(AddressList + 0x80)
            
            pm.write_short(CustomInput_PTR, CustomInput)
            
            pm.write_uchar(CustomInput_PTR + 0x8, RequestedL2)
            pm.write_uchar(CustomInput_PTR + 0x10, RequestedR2)

            pm.write_float(CustomInput_PTR + 0x18, RequestedLeftRight)
            pm.write_float(CustomInput_PTR + 0x20, RequestedUpDown)
            


