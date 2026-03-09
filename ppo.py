import time
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from jumpforce_rl import PlayerStatus
from data_type import ActionType
from helper_functions import *

# ---------------------------------------------------------------------------
# Observation (21 dims)
# ---------------------------------------------------------------------------
#  0   p1 hp_percent           0–1
#  1   p2 hp_percent           0–1
#  2   p1 charge_percent       0–1
#  3   p1 stamina_percent      0–1
#  4   p1 awakening_percent    0–1
#  5   p2 awakening_percent    0–1
#  6   p1 combo                / 200
#  7   p1 action               / 50
#  8   p2 action               / 50
#  9   p1 canUseSkillSquare    0 or 1
#  10  p1 canUseSkillTriangle  0 or 1
#  11  p1 canUseSkillCircle    0 or 1
#  12  p1 canUseSkillUlt       0 or 1
#  13  p1 isHalfAwakenON       0 or 1
#  14  p1 isFullAwakenON       0 or 1
#  15  delta x (p1-p2)         / 50, clipped -1..1
#  16  delta y                 / 50, clipped -1..1
#  17  delta z                 / 50, clipped -1..1
#  18  distance 3D             / 200, clipped 0..1
#  19  combat timer            / 100
#  20  p2 stamina_percent      0–1
# ---------------------------------------------------------------------------

OBS_DIM    = 49
MAX_COMBO  = 200.0
MAX_ACTION = 50.0
MAX_DELTA  = 50.0
MAX_TIMER  = 100.0

# ---------------------------------------------------------------------------
# Button bitmasks (post-assembly-patch layout)
# ---------------------------------------------------------------------------
BTN_UP    = 0x0001   # DPAD_UP    -> analog stick up    (asm patch)
BTN_DOWN  = 0x0002   # DPAD_DOWN  -> analog stick down  (asm patch)
BTN_LEFT  = 0x0004   # DPAD_LEFT  -> analog stick left  (asm patch)
BTN_RIGHT = 0x0008   # DPAD_RIGHT -> analog stick right (asm patch)
BTN_R2    = 0x0010   # START      -> R2 byte 255        (asm patch)
BTN_L2    = 0x0020   # BACK       -> L2 byte 255        (asm patch)
BTN_L1    = 0x0100   # LEFT_SHOULDER
BTN_R1    = 0x0200   # RIGHT_SHOULDER
BTN_A     = 0x1000
BTN_B     = 0x2000
BTN_X     = 0x4000   # Square in JF layout
BTN_Y     = 0x8000   # Triangle in JF layout
BTN_R3    = 0x0080

# ---------------------------------------------------------------------------
# Direction head - Discrete(5)
# Only one direction bit fires at a time, no conflicts.
# ---------------------------------------------------------------------------
DIR_MAP = [
    0x0000,    # 0 - No movement
    BTN_UP,    # 1 - Up
    BTN_DOWN,  # 2 - Down
    BTN_LEFT,  # 3 - Left
    BTN_RIGHT, # 4 - Right
]
N_DIR = len(DIR_MAP)

# ---------------------------------------------------------------------------
# Action head - Discrete(N_ACTIONS)
# R2 combos follow Budokai Tenkaichi style (hold R2 + face button = skill)
# ---------------------------------------------------------------------------
ACTION_MAP = [
    (0x0000,          "Idle"),
    (BTN_X,           "Attack/Counter"),
    (BTN_Y,           "Heavy"),
    (BTN_B,           "Grab"),
    (BTN_A,           "Jump"),
    (BTN_R2,          "Charge"),
    (BTN_R2 | BTN_X,  "Skill Square"),
    (BTN_R2 | BTN_Y,  "Skill Triangle"),
    (BTN_R2 | BTN_B,  "Skill Circle"),
    (BTN_R2 | BTN_A,  "Ultimate"),
    (BTN_R1,          "Guard/Vanish"),
    (BTN_L2,          "Support/Swap"),
    (BTN_L1,          "Escape/Follow/Escape counter"),
    (BTN_R3,          "Awaken"),
]
N_ACTIONS = len(ACTION_MAP)

IDX_IDLE          = 0
IDX_LIGHT         = 1
IDX_HEAVY         = 2
IDX_GRAB          = 3
IDX_JUMP          = 4
IDX_CHARGE        = 5
IDX_SKILL_SQUARE  = 6
IDX_SKILL_TRI     = 7
IDX_SKILL_CIRCLE  = 8
IDX_ULTIMATE      = 9
IDX_GUARD_VANISH  = 10
IDX_SWAP_SUPPORT  = 11
IDX_FOLLOW_ESCAPE = 12
IDX_AWAKEN        = 13


class JumpForceEnv(gym.Env):
    """
    MaskablePPO environment for Jump Force.

    Action space : MultiDiscrete([N_DIR, N_ACTIONS])
      Head 0 -> direction  (0=none, 1=up, 2=down, 3=left, 4=right)
      Head 1 -> action index into ACTION_MAP
      Both are OR-combined into a single uint16 for sendXinput.

    Observation  : Box(21,) float32
    """

    metadata = {"render_modes": []}

    def __init__(self, step_delay: float = 0.025, max_steps: int = 3000):
        super().__init__()

        self.step_delay = step_delay
        self.max_steps  = max_steps

        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(OBS_DIM,), dtype=np.float32
        )
        self.action_space = spaces.MultiDiscrete([N_DIR, N_ACTIONS])

        self._p1           = None
        self._p2           = None
        self._prev_p1_hp   = 1.0
        self._prev_p2_hp   = 1.0
        self._prev_combo   = 0
        self._prev_action  = 0
        self._step_count   = 0

    # ------------------------------------------------------------------
    # Required by ActionMasker wrapper
    # ------------------------------------------------------------------
    def action_masks(self) -> np.ndarray:
        """
        Flat mask: first N_DIR bools (direction), then N_ACTIONS bools (actions).
        False = this choice is illegal and will be masked out by MaskablePPO.

        Masking rules:
          - Directions: always all open
          - Skills: only if canUseSkill* == 1
          - Ultimate: only if canUseSkillUlt AND at least half awakened
          - Charge: only if not already full
          - Idle: always allowed (prevents all-False mask)
        """
        dir_mask = np.ones(N_DIR, dtype=bool)
        act_mask = np.ones(N_ACTIONS, dtype=bool)

        p1 = self._p1
        p2 = self._p2

        
        p1_action = ActionType(p1.PLAYER_ACTION)
        p2_action = ActionType(p2.PLAYER_ACTION)

        distance = getDistance(p1, p2)

        if p1 is not None:
            act_mask[IDX_SKILL_SQUARE]  = bool(p1.canUseSkillSquare) and canUseSKills(p1, p2)
            act_mask[IDX_SKILL_TRI]     = bool(p1.canUseSkillTriangle) and canUseSKills(p1, p2)
            act_mask[IDX_SKILL_CIRCLE]  = bool(p1.canUseSkillCircle) and canUseSKills(p1, p2)

            act_mask[IDX_ULTIMATE]      = canUseUlt(p1, p2)

            act_mask[IDX_CHARGE]        = canCharge(p1, p2)
            
            act_mask[IDX_JUMP]          = canJump(p1, p2)

            act_mask[IDX_LIGHT]         = canAttack(p1, p2)
            act_mask[IDX_HEAVY]         = canAttack(p1, p2)
            act_mask[IDX_GRAB]          = canGrab(p1, p2)
            
            

            act_mask[IDX_GUARD_VANISH]   = canGuard(p1, p2) or canHighSpeedDodge(p1, p2)
            act_mask[IDX_AWAKEN]         = canAwaken(p1, p2)
            
            act_mask[IDX_FOLLOW_ESCAPE]  = canFollow(p1, p2) or canEscape(p1, p2)

            act_mask[IDX_SWAP_SUPPORT]  =  canSwap(p1, p2)

        act_mask[IDX_IDLE] = True  # always safe fallback
        return np.concatenate([dir_mask, act_mask])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_obs(self) -> np.ndarray:
        p1 = PlayerStatus(player_id=1)
        p2 = PlayerStatus(player_id=2)
        self._p1, self._p2 = p1, p2

        dx   = np.clip((p1.x - p2.x) / MAX_DELTA, -1.0, 1.0)
        dy   = np.clip((p1.y - p2.y) / MAX_DELTA, -1.0, 1.0)
        dz   = np.clip((p1.z - p2.z) / MAX_DELTA, -1.0, 1.0)
        
        # During area change the distance might increase.
        # Radius or the arena is ~35 units, which means 70 units should be the max distance between the two players
        dist = min(getDistance(p1, p2) / 70, 1.0)

        # 4 distances compared to the arena limits
        # this assumes no area changes will happen (still have to code that)
        p1_sides = getArenaDistance(p1)
        p2_sides = getArenaDistance(p2)

        InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, isBattleComplete, PauseTriggered, CombatTimer, WhoAmI = PlayerStatus.getGameStatus()
        timer_norm = np.clip(float(CombatTimer) / MAX_TIMER, 0.0, 1.0)

        return np.array([
            
            min(p1_sides[0] / 70, 1.0),
            min(p1_sides[1] / 70, 1.0),
            min(p1_sides[2] / 70, 1.0),
            min(p1_sides[3] / 70, 1.0),

            min(p2_sides[0] / 70, 1.0),
            min(p2_sides[1] / 70, 1.0),
            min(p2_sides[2] / 70, 1.0),
            min(p2_sides[3] / 70, 1.0),

            p1.hp_percent,
            p1.charge_percent,
            p1.stamina_percent,
            p1.awakening_percent,

            p2.hp_percent,
            p2.charge_percent,
            p2.stamina_percent,
            p2.awakening_percent,
            
            min(p1.combo / MAX_COMBO, 1.0),
            min(p2.combo / MAX_COMBO, 1.0),

            min(p1.PLAYER_ACTION / MAX_ACTION, 1.0),
            min(p2.PLAYER_ACTION / MAX_ACTION, 1.0),

            min(p1.PLAYER_RAW_ACTION / 500, 1.0),
            min(p2.PLAYER_RAW_ACTION / 500, 1.0),
            
            min(p1.PLAYER_RAW_ACTION_PREVIOUS / 500, 1.0),
            min(p2.PLAYER_RAW_ACTION_PREVIOUS / 500, 1.0),

            min(p1.PLAYER_ACTION_FRAME, 300) / 300,
            min(p2.PLAYER_ACTION_FRAME, 300) / 300,

            p1.current_character_id / 5000,
            p2.current_character_id / 5000,
            p1.next_character_id / 5000,
            p2.next_character_id / 5000,

            p1.switchCharacterTimer1,
            p2.switchCharacterTimer1,

            min(p1.dmg_dealt, 30000) / 30000,
            min(p2.dmg_dealt, 30000) / 30000,

            float(p1.canUseSkillSquare),
            float(p1.canUseSkillTriangle),
            float(p1.canUseSkillCircle),
            float(p1.canUseSkillUlt),
            float(p1.isHalfAwakenON),

            float(p2.canUseSkillSquare),
            float(p2.canUseSkillTriangle),
            float(p2.canUseSkillCircle),
            float(p2.canUseSkillUlt),
            float(p2.isHalfAwakenON),

            dx, dy, dz, dist,
            timer_norm,
            
        ], dtype=np.float32)

    @staticmethod
    def _build_input(dir_idx: int, act_idx: int) -> int:
        """OR direction bits and action bits into a single uint16."""
        return DIR_MAP[dir_idx] | ACTION_MAP[act_idx][0]

    # ------------------------------------------------------------------
    # Gym interface
    # ------------------------------------------------------------------
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, isBattleComplete, PauseTriggered, CombatTimer, WhoAmI = PlayerStatus.getGameStatus()
        while not PlayerStatus.isGameOn():
            time.sleep(0.05)

        time.sleep(0.01)

        obs = self._get_obs()
        #print(len(obs))

        self._prev_p1_hp  = self._p1.hp_percent
        self._prev_p2_hp  = self._p2.hp_percent
        self._prev_combo  = self._p1.combo
        self._prev_action = self._p1.PLAYER_ACTION
        self._step_count  = 0

        return obs, {}

    def step(self, action: np.ndarray):
        dir_idx, act_idx = int(action[0]), int(action[1])

        

        btn = self._build_input(dir_idx, act_idx)
        if PlayerStatus.isGameOn():
            PlayerStatus(player_id=1).sendXinput(btn=btn)
        else:
            PlayerStatus(player_id=1).sendXinput(btn=0)  # release all buttons
        
        time.sleep(self.step_delay)

        obs = self._get_obs()
        #print(len(obs))

        p1, p2 = self._p1, self._p2
        self._step_count += 1
        #print(canGrab(p1, p2))
        # --- Rewards -------------------------------------------------------
        reward = 0.0

        p1_action = ActionType(p1.PLAYER_ACTION)

        p1_hp_delta = self._prev_p1_hp - p1.hp_percent
        p2_hp_delta = self._prev_p2_hp - p2.hp_percent
        reward += (p2_hp_delta - p1_hp_delta) / 100

        combo_delta = p1.combo - self._prev_combo
        if p1.combo <= 30 and p1.combo >= 7 and combo_delta > 0:
            reward += combo_delta * 0.0025

        changed = p1.PLAYER_ACTION != self._prev_action

        if changed:
            if p1_action == ActionType.HighSpCounterAttack:
                reward += 0.5
            
            if p1_action == ActionType.HighSpDodge:
                reward += 0.1
            
            # secret reward (rare)
            if p1_action == ActionType.AreaChange:
                reward += 0.1

        # end
        InGame, Flows, StartAllowed, StartAllowed2, Paused, Paused2, ko_done, PauseTriggered, CombatTimer, WhoAmI = PlayerStatus.getGameStatus()
        timer_expired = CombatTimer <= 0.1
        ko_health = (p1.hp == 0 or p2.hp == 0)
        battle_done   = ko_done or timer_expired or ko_health

        if battle_done:
            time_bonus = min(CombatTimer / 10.0, 5.0)

            hp_diff = (p1.hp_percent - p2.hp_percent) * 10
            
            if p2.hp_percent < p1.hp_percent:
                reward += (20.0 + time_bonus + hp_diff)
            elif p1.hp_percent < p2.hp_percent:
                reward -= (20.0 + time_bonus + hp_diff)


        # --- Update trackers -----------------------------------------------
        self._prev_p1_hp  = p1.hp_percent
        self._prev_p2_hp  = p2.hp_percent
        self._prev_combo  = p1.combo
        self._prev_action = p1.PLAYER_ACTION

        terminated = bool(battle_done)
        truncated  = self._step_count >= self.max_steps

        info = {
            "p1_hp":  p1.hp_percent,
            "p2_hp":  p2.hp_percent,
            "combo":  p1.combo,
            "dir":    hex(DIR_MAP[dir_idx]),
            "action": ACTION_MAP[act_idx][1],
            "btn":    hex(btn),
            "AT_P1":  ActionType(p1.PLAYER_ACTION),
            "AT_P2":  ActionType(p2.PLAYER_ACTION),
        }

        return obs, reward, terminated, truncated, info

    def render(self):
        pass

    def close(self):
        PlayerStatus(player_id=1).sendXinput(btn=0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    from sb3_contrib import MaskablePPO
    from sb3_contrib.common.wrappers import ActionMasker
    from stable_baselines3.common.callbacks import CheckpointCallback

    INFERENCE_ONLY   = False
    SPEED_MULTIPLIER = 10      # 4 = 240fps, 5 = 300fps, 6 = 360fps, 10 = 600fps, 15 = 900fps
    REACTION_MS      = 100     # target reaction time at 60fps
    STEP_DELAY       = (REACTION_MS / 1000) / SPEED_MULTIPLIER  # 0.025s

    CHECKPOINT_DIR    = "./checkpoints/"
    CHECKPOINT_PREFIX = "jumpforce_mppo"
    SAVE_EVERY_STEPS  = 10_000
    TOTAL_TIMESTEPS   = 1_000_000

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    raw_env = JumpForceEnv(step_delay=STEP_DELAY)
    env     = ActionMasker(raw_env, lambda e: e.action_masks())

    def _ckpt_steps(fname):
        try:
            return int(fname.split("_steps")[0].split("_")[-1])
        except ValueError:
            return 0

    existing = sorted([
        f for f in os.listdir(CHECKPOINT_DIR)
        if f.startswith(CHECKPOINT_PREFIX) and f.endswith(".zip")
    ], key=_ckpt_steps)

    if existing:
        latest = os.path.join(CHECKPOINT_DIR, existing[-1])
        print(f"[INFO] Resuming from: {latest}")
        model = MaskablePPO.load(
            latest,
            env=env,
            custom_objects={
                "policy_kwargs": dict(net_arch=[256, 256, 256]),
                "ent_coef": 0.01
            }
        )
        steps_done = _ckpt_steps(existing[-1])
        remaining  = max(TOTAL_TIMESTEPS - steps_done, 0)
    else:
        print("[INFO] Starting fresh.")
        model = MaskablePPO(
            policy="MlpPolicy",
            env=env,
            verbose=1,
            n_steps=2048,
            batch_size=256,
            learning_rate=3e-4,
            ent_coef=0.01,
            policy_kwargs=dict(net_arch=[256, 256, 256]),
            tensorboard_log="./jf_tensorboard/"
        )
        remaining = TOTAL_TIMESTEPS

    if INFERENCE_ONLY:
        obs, _ = env.reset()
        while True:
            action, _ = model.predict(obs, action_masks=env.action_masks(), deterministic=False)
            obs, _, terminated, truncated, info = env.step(action)
            print(f"Dir: {info['dir']}  Action: {info['action']}") #  Btn: {info['btn']}  --  {info['AT_P1']} - {info['AT_P2']}
            if terminated or truncated:
                obs, _ = env.reset()
    else:
        checkpoint_cb = CheckpointCallback(
            save_freq=SAVE_EVERY_STEPS,
            save_path=CHECKPOINT_DIR,
            name_prefix=CHECKPOINT_PREFIX,
            verbose=1,
        )
        model.learn(
            total_timesteps=remaining,
            callback=checkpoint_cb,
            reset_num_timesteps=False
        )
        model.save(os.path.join(CHECKPOINT_DIR, f"{CHECKPOINT_PREFIX}_final"))