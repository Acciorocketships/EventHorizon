from Simulator import Simulator
from Network import Network
import time

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
		self.agent = agent


	# called by GameServer
	def set_input(self):
		# Get From PlayerClient
		if not self.remote:
			self.input = self.playerclient.input # use input from playerclient object (input is automatically populated for remote)
		# Input Logic


	# called by GameServer
	def get_output(self):
		# Output Logic
		output = None
		# Store in PlayerClient
		if self.remote:
			self.network.send(var=output, name="output")
		else:
			self.playerclient.output = output


	def update_input(self, data):
		self.input = data