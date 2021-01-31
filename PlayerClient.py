from Network import Network
import time

class PlayerClient:

	CLIENT_PORT = 8081
	SERVER_PORT = 8080
	CONNECT_PORT = 6000

	def __init__(self, remote=False, gameserver=None, clienthost='localhost', serverhost='localhost'):
		self.remote = remote
		self.input = {}
		self.output = {}
		if self.remote:
			self.network = Network(host=clienthost, port=PlayerClient.CLIENT_PORT, otherhost=serverhost, otherport=PlayerClient.SERVER_PORT)
			self.network.dataCallback = {"output" : self.update_output}
			self.network.send(var={"host": clienthost, "port": PlayerClient.CLIENT_PORT}, name="connection", host=serverhost, port=PlayerClient.CONNECT_PORT)
			while not self.network.get("connected"):
				time.sleep(0.1)
				print('...')
			print('connected')
		else:
			gameserver.new_connection({'host': 'local', 'playerclient': self})

	# called by GameClient
	def set_input(self, data):
		self.input = data
		if self.remote:
			self.network.send(var=data, name="input")


	# called by GameClient
	def get_output(self):
		return self.output # create callback to set self.output when new data arrives


	def update_output(self, data):
		self.output = data