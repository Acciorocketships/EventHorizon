from Simulator import Simulator
from GameEnvironment import GameEnvironment
from Camera import Camera
from Util import *
import time


def main():
	sim = Simulator()
	env = GameEnvironment(sim=sim)
	sim.objects = env.objects
	player = list(env.players.values())[0]
	cam = Camera(player=player, sim=sim)

	xctrl = 0
	yctrl = 0
	for t in range(10000):
		# get input
		keys = sim.get_keyboard_events()
		xctrl += keys.get(Key.up, 0)
		xctrl -= keys.get(Key.down, 0)
		yctrl += keys.get(Key.left, 0)
		yctrl -= keys.get(Key.right, 0)
		# set action
		player.set_movement(movement=[xctrl,yctrl])
		# calc gravity
		env.update_gravity()
		# update camera
		sim.set_camera(target=player.get_pos(), pos=player.get_pos()+torch.tensor([-3.,-3.,3.]))
		# step sim
		sim.step()
		time.sleep(1/240)




if __name__ == '__main__':
	main()