import torch
from Simulator import DefaultSim
from ObjectCreator import *


class Agent(Object):

	RADIUS = 0.5
	MASS = 5.0
	MOVETORQUE = 200.0 * MASS
	FRICTION = 50.0
	ROLLING_FRICTION = 1.0
	BOUNCE = 0.5


	def __init__(self, pos=[0,0,0], objects={}, sim=DefaultSim()):
		super().__init__(0, objects, sim)
		self.create_agent(pos)


	def create_agent(self, pos):
		collision_uid = p.createCollisionShape(p.GEOM_SPHERE, radius=Agent.RADIUS, physicsClientId=self.sim.id)
		uid = p.createMultiBody(baseMass=Agent.MASS, baseCollisionShapeIndex=collision_uid, physicsClientId=self.sim.id)
		self.uid = uid
		self.set_state(pos=pos)
		p.changeDynamics(self.uid, linkIndex=-1, restitution=Agent.BOUNCE, lateralFriction=Agent.FRICTION, spinningFriction=-Agent.FRICTION, rollingFriction=Agent.ROLLING_FRICTION, physicsClientId=self.sim.id)
		# print(p.getDynamicsInfo(self.uid, -1, self.sim.id))


	def set_movement(self, movement=[0,0]):
		torque = torch.tensor([-movement[1], movement[0], 0]) * Agent.MOVETORQUE
		self.set_torque(torque=torque)
