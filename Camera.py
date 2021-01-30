from Simulator import DefaultSim
from scipy.spatial.transform import Rotation
import torch


class Camera:

	TRANSFORM = Rotation.from_euler('y', 30, degrees=True)
	OFFSET = torch.tensor([0,0,0.0])
	DIST = 3.0

	def __init__(self, player, sim=DefaultSim()):
		self.player = player
		self.sim = sim
		self.last_up = torch.tensor([0.,0.,1.])
		self.last_forward = torch.tensor([1.,0.,0.])
		self.curr_quat = torch.tensor([0,0,0,1])


	def orientation(self):
		# get up
		up = -self.player.accel.float()
		up_mag = up.norm()
		if up_mag != 0:
			up /= up_mag
		else:
			up = self.last_up
		# get forward
		forward = self.player.get_vel().float()
		forward_mag = forward.norm()
		if forward_mag != 0:
			forward /= forward_mag
		else:
			forward = self.last_forward
		# calc left
		left = torch.cross(up, forward)
		left_mag = left.norm()
		if left_mag == 0:
			_, R = self.sim.get_camera_pos()
		else:
			# compose R
			R = torch.stack([forward, left, up], dim=1)
		return R


	def target_quat(self):
		R0 = self.orientation()
		r0 = Rotation.from_matrix(R0)
		r1 = r0 * Camera.TRANSFORM
		R1 = torch.tensor(r1.as_quat())
		return R1


	def update(self):
		target_quat = self.target_quat()
		current = self.curr_quat
		t = 0.2
		new = (torch.dot(target_quat.float(),self.curr_quat.float()) ** t) * current
		r = Rotation.from_quat(new)
		forward = torch.tensor(r.as_matrix())[:,0]
		target_pos = self.player.get_pos() + Camera.OFFSET
		camera_pos = target_pos - forward * Camera.DIST
		self.sim.set_camera(pos=camera_pos, target=target_pos)

		


