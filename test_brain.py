from helper_functions import *
from jumpforce_rl import *
import time
import math
import numpy as np

# Frame diff
Frame = {
    "Dist": 0,
    "Charge": 0,
    "Stamina": 0
}


while True:

    time.sleep(0.05)

    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2 = PlayerStatus.getGameStatus()
    #print(getGameStatus())

    # Simple system check to know if the game is ready to start (aka agent can fight)
    if InGame < 50 or StartAllowed == 0 or StartAllowed2 == 0 or Paused == 1: #or Flows < 100
        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(0.5)
        continue
    
    # Get player stats
    my_state = PlayerStatus(1)
    rival_state = PlayerStatus(2)

    # Delta stats
    Distance = getDistance(my_state, rival_state)
    DeltaDistance = round(Distance - Frame["Dist"], 3)
    Frame["Dist"] = Distance

    Charge = my_state.charge
    DeltaCharge = round(Charge - Frame["Charge"], 3)
    Frame["Charge"] = Charge

    Stamina = my_state.stamina
    DeltaStamina = round(Stamina - Frame["Stamina"], 3)
    Frame["Stamina"] = Stamina

    print(DeltaStamina)
    
    #my_state.sendInput(player_id=1, input=65)
    #if canGuardBreak(my_state, rival_state):
        #my_state.sendInput(17)
        #time.sleep(2.150)
    
    #print( math.floor(getDistance(my_state, rival_state)) )
    #print(my_state.x)
    
    # test input, charge at interval
    
    my_state.sendInput(input=12345)
    