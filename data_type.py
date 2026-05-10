from enum import Enum, IntFlag

class Vpad(IntFlag):
    AWAKEN         = 0x8000
    ESCAPE         = 0x4000
    FOLLOW         = 0x2000
    GUARD          = 0x1000
    ULTIMATE       = 0x0800
    SKILL_CIRCLE   = 0x0400
    SKILL_TRIANGLE = 0x0200
    SKILL_SQUARE   = 0x0100
    SWAP           = 0x0080
    CHARGE         = 0x0040
    HEAVY          = 0x0020
    LIGHT          = 0x0010
    GRAB           = 0x0008
    JUMP           = 0x0004
    MOVE           = 0x0002
    UNKNOWN        = 0x0001 # this has no impact



class Xinput(IntFlag):
    Idle            = 0x0000               # 
    Up              = 0x0001               #   
    Down            = 0x0002               #   
    Left            = 0x0004               #   
    Right           = 0x0008               #   
    Jump            = 0x1000               # XBOX: Button A  -  PS4:  Button X
    Grab            = 0x2000               # XBOX: Button B  -  PS4:  Button CIRCLE
    Light           = 0x4000               # XBOX: Button X  -  PS4:  Button SQUARE
    Heavy           = 0x8000               # XBOX: Button Y  -  PS4:  Button TRIANGLE
    Charge          = 0x0010               # XBOX: Button .  -  PS4:  Button R2
    Support         = 0x0020               # XBOX: Button .  -  PS4:  Button L2
    SKILL_1         = 0x0010 | 0x4000      # Charge  +  Light
    SKILL_2         = 0x0010 | 0x2000      # Charge  +  Grab
    SKILL_3         = 0x0010 | 0x8000      # Charge  +  Heavy
    ULTIMATE        = 0x0010 | 0x1000      # Charge  +  Jump
    Awakening       = 0x0080               # 
    Parry           = 0x0200               # 
    Follow          = 0x0100               #  This handles both the follow and the escape (situational)


# 34 states
class ActionType(Enum):
    #  General
    Nothing = 0
    Moving = 1
    Jumping = 2
    Charging = 3
    SwappedCharacter = 4
    Incoming = 5
    StandingUp = 6
    ComboStarted = 7
    Follow = 8
    AreaChange = 9
    
    #  Damaging
    Attacking = 10
    ChargedAttack = 11
    UsingSkill = 12
    BrokenGuard = 13
    HighSpDodge = 14
    HighSpCounterAttack = 15
    HighSpCombatEscape = 16

    #  Getting damaged
    GettingHit = 20
    GuardBroke = 21
    VulnerableFramePerfect = 22
    VulnerableSecondFrame = 23
    Thrown = 24

    #  Defensive
    Guarding = 30
    GuardDodge = 31
    Awakening = 32
    SuccessfulGuard = 33
    OnGround = 34

    #  After ground
    GroundAttack = 100
    GroundMove = 101
    GroundJump = 102
    Ground = 103
    
    #  Jumping combos
    JumpLightAttack = 120
    JumpLightAttackCharged = 121
    JumpHeavyAttack = 122
    JumpHeavyAttackCharged = 123
