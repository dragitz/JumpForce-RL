from enum import Enum

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