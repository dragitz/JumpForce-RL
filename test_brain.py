from jumpforce_rl import *

while True:

    InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2 = PlayerStatus.getGameStatus(1)
    #print(getGameStatus())

    # Simple system check to know if the game is ready to start (aka agent can fight)
    if InGame < 100 or StartAllowed == 0 or StartAllowed2 == 0 or Paused == 1: #or Flows < 100
        print("Waiting for bot game to start... (ensure bot is fighting/moving)")
        time.sleep(1)
        continue
    
    # Get player stats
    Player = PlayerStatus(1)
    
    # test input, charge at interval
    Player.sendInput(1, 65)
    time.sleep(2.150)
    Player.sendInput(1, 12345)
    time.sleep(4.150)