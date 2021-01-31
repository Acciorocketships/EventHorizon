import pybullet as p
from Simulator import Simulator
from GameEnvironment import GameEnvironment
from PlayerServer import PlayerServer
from Network import Network
import time

class GameServer:

	CONNECT_PORT = 6000

	def __init__(self, serverhost='localhost'):
		physicsid = p.connect(p.DIRECT)
		self.sim = Simulator(physicsid=physicsid)
		self.env = GameEnvironment(sim=self.sim)
		self.sim.objects = self.env.objects
		self.serverhost = serverhost
		self.network = Network(port=GameServer.CONNECT_PORT, host=self.serverhost)
		self.network.dataCallback = {"connection": self.new_connection}
		self.network.run()
		self.playerservers = []


	def new_connection(self, connection):
		if connection['host'] is 'local':
			playerclient = connection['playerclient']
			remote = False
		else:
			address = connection['host']
			port = connection['port']
			remote = True
		agent = self.env.add_player()
		if remote:
			playerserver = PlayerServer(agent=agent, remote=True, clienthost=address, serverhost=self.serverhost)
		else:
			playerserver = PlayerServer(agent=agent, playerclient=playerclient, remote=False)
		self.playerservers.append(playerserver)
		if remote:
			self.network.send(True, "connected", host=address, port=port)


	def run(self):
		while True:
			# Get State and Output Render
			for playerserver in self.playerservers:
				playerserver.set_input()
				playerserver.get_output()
			# update gravity
			self.env.update_gravity()
			# step sim
			self.sim.step()
			time.sleep(1/240)


if __name__ == '__main__':
	server = GameServer()
	server.run()