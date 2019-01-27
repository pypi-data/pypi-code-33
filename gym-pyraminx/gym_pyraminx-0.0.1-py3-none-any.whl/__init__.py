from gym.envs.registration import register

register(
    id='pyraminx-v0',
    entry_point='gym_pyraminx.envs:PyraminxEnv',
)
