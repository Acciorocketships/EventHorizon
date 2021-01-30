import pybullet as p
import torch
from Simulator import DefaultSim
from Object import *

def create_sphere(radius=0.5, pos=[0,0,0], mass=0, collisions=True, objects={}, sim=DefaultSim()):
	if collisions:
		uid = p.createCollisionShape(p.GEOM_SPHERE, radius=radius, physicsClientId=sim.id)
		uid = p.createMultiBody(baseMass=mass, baseCollisionShapeIndex=uid, physicsClientId=sim.id)
	else:
		uid = p.createVisualShape(p.GEOM_SPHERE, radius=radius, physicsClientId=sim.id)
		uid = p.createMultiBody(baseMass=mass, baseVisualShapeIndex=uid, physicsClientId=sim.id)
	obj = Object(uid=uid, objects=objects, sim=sim)
	obj.set_state(pos=pos)
	return obj


def create_box(dim=[1,1,1], pos=[0,0,0], ori=[0,0,0], mass=0, collisions=True, objects={}, sim=DefaultSim()):
	if isinstance(dim, torch.Tensor):
		dim = dim.tolist()
	if collisions:
		uid = p.createCollisionShape(p.GEOM_BOX, halfExtents=dim, physicsClientId=sim.id)
		uid = p.createMultiBody(baseMass=mass, baseCollisionShapeIndex=uid, physicsClientId=sim.id)
	else:
		uid = p.createVisualShape(p.GEOM_BOX, halfExtents=dim, physicsClientId=sim.id)
		uid = p.createMultiBody(baseMass=mass, baseVisualShapeIndex=uid, physicsClientId=sim.id)
	obj = Object(uid=uid, objects=objects, sim=sim)
	obj.set_state(pos=pos, ori=ori)
	return obj


def load_urdf(path, pos=[0,0,0], ori=[0,0,0], objects={}, sim=DefaultSim(), inpackage=True):
	# position
	if isinstance(pos, torch.Tensor):
		pos = pos.tolist()
	# orientation
	if isinstance(ori, list):
		ori = torch.tensor(ori)
	if ori.shape == (3,3):
		r = R.from_matrix(ori)
	elif ori.shape == (3,):
		r = R.from_euler('xyz', ori, degrees=True)
	elif ori.shape == (4,):
		r = R.from_quat(ori)
	ori = r.as_quat()
	ori = ori.tolist()
	# path
	# if inpackage:
	# 	directory = os.path.join(os.path.dirname(mrsgym.__file__), 'models')
	# 	path = os.path.join(directory, path)
	# load
	uid = p.loadURDF(fileName=path, basePosition=pos, baseOrientation=ori, physicsClientId=sim.id)
	obj = Object(uid=uid, objects=objects, sim=sim)
	return obj