from Simulator import Simulator
from Network import Network
from Camera import Camera
import time
import torch

class PlayerServer:

	CLIENT_PORT = 8081
	SERVER_PORT = 8080

	def __init__(self, agent, playerclient=None, remote=False, clienthost='localhost', serverhost='localhost'):
		self.network = None
		self.playerclient = playerclient
		self.remote = remote
		self.input = {}
		self.output = {}
		if self.remote:
			self.network = Network(host=serverhost, port=PlayerServer.SERVER_PORT, otherhost=clienthost, otherport=PlayerServer.CLIENT_PORT)
			self.network.dataCallback = {"input" : self.update_input}
		# Logic
		self.agent = agent
		self.camera = Camera(self.agent)


	# called by GameServer
	def set_input(self):
		# Get From PlayerClient
		if not self.remote:
			self.input = self.playerclient.input # use input from playerclient object (input is automatically populated for remote)
		# Input Logic
		# R = self.camera.agent_orientation()
		R = torch.eye(3)
		movement = self.input.get("movement", torch.zeros(3))
		self.agent.set_movement(movement=movement, orientation=R)
		# print(movement)


	# called by GameServer
	def get_output(self):
		# Output Logic
		# self.output['img'] = self.camera.get_image()
		# Store in PlayerClient
		if self.remote:
			self.network.send(var=self.output, name="output")
		else:
			self.playerclient.output = self.output


	def update_input(self, data):
		self.input = data