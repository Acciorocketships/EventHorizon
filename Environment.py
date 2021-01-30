from Simulator import DefaultSim

class Environment:

	GRAVITY_CONSTANT = 0.01

	def __init__(self, sim=DefaultSim()):
		self.sim = sim
		self.objects = {}
		self.players = {}


	def update_gravity(self):
		for obj1 in self.objects.values():
			for obj2 in self.objects.values():
				if obj1 != obj2:
					pos1 = obj1.get_pos()
					pos2 = obj2.get_pos()
					r = (pos1 - pos2).norm()
					m1 = obj1.mass
					m2 = obj2.mass
					g = Environment.GRAVITY_CONSTANT * m1 * m2 / (r**2)
					dir1 = (pos2 - pos1) / r
					dir2 = -dir1
					obj1.set_force(force = g * dir1)
					obj2.set_force(force = g * dir2)