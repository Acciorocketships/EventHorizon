import pygame
import numpy as np

class Visualiser:

	HEIGHT = 720
	ASPECT = 4/3

	def __init__(self):
		pygame.init()
		self.display = pygame.display.set_mode((int(Visualiser.ASPECT*Visualiser.HEIGHT), Visualiser.HEIGHT))


	def get_input(self):
		states = pygame.key.get_pressed()
		return states


	def update(self, img):
		if img is None:
			return
		pygame_img = np.transpose(img[:,:,:3], (1, 0, 2))
		pygame.surfarray.blit_array(self.display, pygame_img)
		pygame.display.update()