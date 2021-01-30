from Environment import Environment
from Agent import Agent
from ObjectCreator import *


class GameEnvironment(Environment):


	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.setup()


	def setup(self):
		# Create and add player
		player = Agent(pos=[0,0,4], objects=self.objects, sim=self.sim)
		self.players[player.uid] = player
		self.objects[player.uid] = player
		# Create and add ground
		ground = create_box(dim=[10,10,2], mass=2000, collisions=True, objects=self.objects, sim=self.sim)
		p.changeDynamics(ground.uid, linkIndex=-1, restitution=1.0, physicsClientId=self.sim.id)
		self.objects[ground.uid] = ground