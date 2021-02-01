from scipy.spatial.transform import Rotation
import torch


class Camera:

	CAMERA_OFFSET = torch.tensor([-10.,0.,10.])
	LOOK_OFFSET = torch.tensor([0.,0.,1.])
	SPEED = 0.5
	FOV = 90.
	ASPECT = 4/3
	HEIGHT = 720

	def __init__(self, agent):
		self.agent = agent
		self.currpos = None
		self.R = torch.eye(3)
		self.time = self.agent.sim.time


	def is_current(self):
		if self.agent.sim.time != self.time:
			self.time = self.agent.sim.time
			return False
		return True


	def agent_orientation(self):
		if self.is_current():
			return self.R
		# down
		accel_mag = self.agent.accel.norm()
		if accel_mag != 0:
			up = -self.agent.accel / accel_mag
		else:
			up = self.R[:,2]
		# left
		disp = self.currpos - self.agent.get_pos()
		direction = disp / disp.norm()
		left = torch.cross(direction, up)
		if left.norm() == 0:
			left = self.R[:,1]
		# forward
		forward = torch.cross(left, up)
		# Rotation
		R = torch.stack([forward, left, up])
		self.R = R
		return R


	def target_orientation(self):
		vel = self.agent.get_vel()
		R = self.agent_orientation()
		left = torch.cross(R[:,2], vel)
		left_mag = left.norm()
		if left_mag == 0:
			left = R[:,1]
		else:
			left = left / left_mag
		forward = torch.cross(left, R[:,2])
		return torch.stack([forward, left, R[:,2]])


	def update_camera_state(self):
		R = self.target_orientation()
		agent_pos = self.agent.get_pos()
		target_camera_position = agent_pos + R @ Camera.CAMERA_OFFSET
		look_position = agent_pos + R @ Camera.LOOK_OFFSET
		if self.currpos is None:
			self.currpos = target_camera_position
		camera_position = Camera.SPEED * (target_camera_position - self.currpos) + self.currpos
		forward = look_position - camera_position; forward /= forward.norm()
		left = torch.cross(R[:,2], forward)
		up = torch.cross(forward, left)
		self.currpos = camera_position
		return {'pos': camera_position, 'target': look_position, 'forward': forward, 'left': left, 'up': up}


	def get_image(self):
		state = self.update_camera_state()
		imgs = self.agent.sim.get_image(pos=state['pos'], forward=state['forward'], up=state['up'], fov=Camera.FOV, aspect=Camera.ASPECT, height=Camera.HEIGHT)
		return imgs['img'].numpy()

