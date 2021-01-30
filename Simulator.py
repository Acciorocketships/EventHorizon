import pybullet as p
from Util import *
import torch
import numpy as np

class Simulator:

	def __init__(self, objects={}):
		self.id = p.connect(p.GUI)
		self.debug_names = {}
		self.objects = objects
		self.time = 0


	def step(self):
		p.stepSimulation(physicsClientId=self.id)
		self.time += 1/240 # todo: getPhysicsEngineParameters


	def get_image(self, pos, forward, up=None, fov=90., aspect=4/3, height=720):
		pos = totensor(pos)
		forward = totensor(forward)
		if up is not None:
			up = totensor(up)
		else:
			left = torch.cross(torch.tensor([0.,0.,1.]), forward)
			up = torch.cross(forward, left)
		view_mat = p.computeViewMatrix(cameraEyePosition=pos.tolist(), cameraTargetPosition=forward.tolist(), cameraUpVector=up.tolist(), physicsClientId=self.id)
		NEAR_PLANE = 0.01
		FAR_PLANE = 1000.0
		proj_mat = p.computeProjectionMatrixFOV(fov=fov, aspect=aspect, nearVal=NEAR_PLANE, farVal=FAR_PLANE, physicsClientId=self.id)
		_, _, img, depth, mask = p.getCameraImage(width=int(aspect * height), height=height, viewMatrix=view_mat, projectionMatrix=proj_mat, physicsClientId=self.id)
		img = torch.tensor(img)
		depth = FAR_PLANE * NEAR_PLANE / (FAR_PLANE - (FAR_PLANE-NEAR_PLANE)*torch.tensor(depth))
		mask = torch.tensor(mask)
		return {"img": img, "depth": depth, "mask": mask}


	def get_keyboard_events(self):
		events = p.getKeyboardEvents(physicsClientId=self.id)
		keys = {}
		for keycode, valcode in events.items():
			if valcode == 3:
				val = 1
			elif valcode == 1:
				val = 0
			elif valcode == 4:
				val = -1
			else:
				continue
			key = Key(keycode)
			keys[key] = val
		return keys


	def get_mouse_events(self):
		events = p.getMouseEvents(physicsClientId=self.id)
		for event in events:
			if event[4] == 3:
				_, x, y, _, _ = event
				camera_params = p.getDebugVisualizerCamera(physicsClientId=self.id)
				width = camera_params[0]
				height = camera_params[1]
				aspect = width/height
				pos_view = torch.tensor([1.0, aspect*(1.0-(x/width)*2), 1.0-(y/height)*2])
				camera_forward = torch.tensor(camera_params[5])
				camera_left = -torch.tensor(camera_params[6]); camera_left /= camera_left.norm()
				camera_up = torch.tensor(camera_params[7]); camera_up /= camera_up.norm()
				R = torch.stack([camera_forward, camera_left, camera_up], dim=1)
				camera_target = torch.tensor(camera_params[-1])
				target_dist = camera_params[-2]
				camera_pos_world = camera_target - target_dist * camera_forward
				pos_world = R @ pos_view + camera_pos_world
				vec = pos_world - camera_pos_world; vec = vec / vec.norm()
				ray = p.rayTest(rayFromPosition=camera_pos_world.tolist(), rayToPosition=(100.0*vec+camera_pos_world).tolist(), physicsClientId=self.id)
				hit_pos = torch.tensor(ray[0][3])
				results = {}
				results['camera_pos'] = camera_pos_world
				results['target_pos'] = torch.tensor(ray[0][3])
				results['target_obj'] = self.objects.get(ray[0][0], ray[0][0])
				results['target_normal'] = torch.tensor(ray[0][4])
				return results


	def get_camera_pos(self):
		camera_params = p.getDebugVisualizerCamera(physicsClientId=self.id)
		camera_forward = torch.tensor(camera_params[5])
		camera_left = -torch.tensor(camera_params[6]); camera_left /= camera_left.norm()
		camera_up = torch.tensor(camera_params[7]); camera_up /= camera_up.norm()
		R = torch.stack([camera_forward, camera_left, camera_up], dim=1)
		camera_target = torch.tensor(camera_params[-1])
		target_dist = camera_params[-2]
		camera_pos_world = camera_target - target_dist * camera_forward
		return camera_pos_world, R


	def set_camera(self, pos=None, target=torch.zeros(3)):
		if pos is None:
			camera_params = p.getDebugVisualizerCamera(physicsClientId=self.id)
			camera_forward = torch.tensor(camera_params[5])
			camera_target = torch.tensor(camera_params[-1])
			target_dist = camera_params[-2]
			pos = camera_target - target_dist * camera_forward
		pos = totensor(pos)
		target = totensor(target)
		disp = target - pos
		dist = disp.norm()
		yaw = np.arctan2(-disp[0],disp[1]) * 180/np.pi
		pitch = np.arctan2(disp[2],np.sqrt(disp[0]**2+disp[1]**2)) * 180/np.pi
		p.resetDebugVisualizerCamera(cameraDistance=dist, cameraYaw=yaw, cameraPitch=pitch, cameraTargetPosition=target.tolist(), physicsClientId=self.id)


	def add_line(self, start, end, parent=None, name="line", width=1.0, lifetime=0., colour=[0.,0.,0.]):
		if isinstance(start, Object):
			start = start.get_pos()
		if isinstance(end, Object):
			end = end.get_pos()
		start = totensor(start)
		end = totensor(end)
		colour = totensor(colour)
		uid = self.debug_names.get(name, -1)
		if parent is not None:
			new_uid = p.addUserDebugLine(lineFromXYZ=start.tolist(), lineToXYZ=end.tolist(), lineColorRGB=colour.tolist(), lineWidth=width, lifeTime=lifetime, parentObjectUniqueId=parent.uid, replaceItemUniqueId=uid, physicsClientId=self.id)
		else:
			new_uid = p.addUserDebugLine(lineFromXYZ=start.tolist(), lineToXYZ=end.tolist(), lineColorRGB=colour.tolist(), lineWidth=width, lifeTime=lifetime, replaceItemUniqueId=uid, physicsClientId=self.id)
		self.debug_names[name] = new_uid


	def add_text(self, text, pos=None, poscam=[1,1.25,-0.95], parent=None, name="text", size=1.0, lifetime=0., colour=[0.,0.,0.]):
		# TODO: set pos to right in front of the camera if it is None
		if pos is None:
			camera_pos, R = self.get_camera_pos()
			forward = R[:,0]
			left = R[:,1]
			up = R[:,2]
			pos = camera_pos + poscam[0] * forward + poscam[1] * left + poscam[2] * up
		else:
			pos = totensor(pos)
		colour = totensor(colour)
		uid = self.debug_names.get(name, -1)
		if parent is not None:
			new_uid = p.addUserDebugText(text=text, textPosition=pos.tolist(), textColorRGB=colour.tolist(), textSize=size, lifeTime=lifetime, parentObjectUniqueId=parent.uid, replaceItemUniqueId=uid, physicsClientId=self.id)
		else:
			new_uid = p.addUserDebugText(text=text, textPosition=pos.tolist(), textColorRGB=colour.tolist(), textSize=size, lifeTime=lifetime, replaceItemUniqueId=uid, physicsClientId=self.id)
		self.debug_names[name] = new_uid


	def add_param(self, name, low=0., high=1., start=None):
		if start is None:
			start = low
		new_uid = p.addUserDebugParameter(paramName=name, rangeMin=low, rangeMax=high, startValue=start, physicsClientId=self.id)
		self.debug_names[name] = new_uid


	def read_param(self, name):
		uid = self.debug_names[name]
		value = p.readUserDebugParameter(itemUniqueId=uid, physicsClientId=self.id)
		return value


	def remove_item(self, name):
		if name in self.debug_names:
			uid = self.debug_names[name]
			p.removeUserDebugItem(itemUniqueId=uid, physicsClientId=self.id)
			del self.debug_names[name]
			return True
		return False


	def set_colour(self, obj, colour=None):
		if colour is not None:
			colour = totensor(colour)
			p.setDebugObjectColor(objectUniqueId=obj.uid, linkIndex=-1, objectDebugColorRGB=colour.tolist(), physicsClientId=self.id)
		else: # if colour is none, it is reset to the default
			p.setDebugObjectColor(objectUniqueId=obj.uid, linkIndex=-1, physicsClientId=self.id)


	def record(self, filename="demo.mp4"):
		p.startStateLogging(loggingType=p.STATE_LOGGING_VIDEO_MP4, fileName=filename, physicsClientId=self.id)



class DefaultSim:

	def __init__(self):
		self.id = 0
		self.time = 0

