from PlayerClient import PlayerClient
from GameServer import GameServer
from Visualiser import Visualiser
import torch
import threading
import time


class GameClient:

	def __init__(self, remote=False, gameserver=None, clienthost='localhost', serverhost='localhost'):
		self.playerclient = PlayerClient(remote=remote, gameserver=gameserver, clienthost=clienthost, serverhost=serverhost)
		# self.visualiser = Visualiser()

	def run(self):
		for t in range(100000):
			data = {"movement" : torch.tensor([t/10,0.,0.])}
			# self.visualiser.get_input()
			self.playerclient.set_input(data)
			# img = self.playerclient.get_output().get('img', None)
			# self.visualiser.update(img)
			time.sleep(1/240)






def run_local():
	server = GameServer()
	thread = threading.Thread(target=server.run)
	thread.start()
	client = GameClient(remote=False, gameserver=server)
	client.run()


def run_remote():
	# server = GameServer(serverhost='localhost')
	# thread = threading.Thread(target=server.run)
	client = GameClient(remote=True, clienthost='localhost', serverhost='localhost')
	thread.start()
	# client.run()


if __name__ == '__main__':
	run_local()