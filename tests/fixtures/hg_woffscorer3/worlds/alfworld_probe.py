import json,traceback
from pathlib import Path
F=Path(__file__).resolve().parent
try:
 import textworld,textworld.gym
 from alfworld.agents.environment.alfred_tw_env import AlfredDemangler,AlfredInfos
 env_id=textworld.gym.register_games([str(F/'alfworld-game.tw-pddl')],textworld.EnvInfos(won=True,admissible_commands=True,extras=['gamefile']),batch_size=1,asynchronous=False,max_episode_steps=4,wrappers=[AlfredDemangler(shuffle=False),AlfredInfos])
 env=textworld.gym.make(env_id)
 print(repr(env.reset()))
 print(repr(env.step(['take apple 1 from countertop 1'])))
 env.close()
except Exception:
 print(traceback.format_exc())
 raise
