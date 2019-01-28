from bzflag.networking.game_data import GameData
from bzflag.networking.network_protocol import Vector3F

DeadStatus = 0  # not alive, not paused, etc.
Alive = 1 << 0  # player is alive
Paused = 1 << 1  # player is paused
Exploding = 1 << 2  # currently blowing up
Teleporting = 1 << 3  # teleported recently
FlagActive = 1 << 4  # flag special powers active
CrossingWall = 1 << 5  # tank crossing building wall
Falling = 1 << 6  # tank accel'd by gravity
OnDriver = 1 << 7  # tank is on a physics driver
UserInputs = 1 << 8  # user speed and angvel are sent
JumpJets = 1 << 9  # tank has jump jets on
PlaySound = 1 << 10  # play one or more sounds


class PlayerStateData(GameData):
    __slots__ = (
        'position',
        'velocity',
        'azimuth',
        'angular_velocity',
        'physics_driver',
        'user_speed',
        'user_ang_vel',
        'jump_jets_scale',
        'sounds',
    )

    def __init__(self):
        self.position: Vector3F = (0.0, 0.0, 0.0)
        self.velocity: Vector3F = (0.0, 0.0, 0.0)
        self.azimuth: float = 0.0
        self.angular_velocity: float = 0.0
        self.physics_driver: int = -1
        self.user_speed: float = 0.0
        self.user_ang_vel: float = 0.0
        self.jump_jets_scale: float = 0.0
        self.sounds: int = -1
