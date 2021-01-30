import numpy as np
import torch
from enum import IntEnum


def totensor(x):
	if isinstance(x, torch.Tensor):
		return x
	else:
		return torch.tensor(x)


# returns a unit vector representing the direction of the target from the camera position (in world coordinates)
def pix2world(vpix, hpix, height, aspect, fov, forward, up, pos):
	forward = totensor(forward)
	up = totensor(up)
	pos = totensor(pos)
	width = int(height * aspect)
	fov_scaler = np.tan(np.pi/180 * fov/2)
	pos_view = torch.tensor([1.0, fov*aspect*(1.0-(hpix/width)*2), fov*(1.0-(vpix/height)*2)])
	camera_forward = forward / forward.norm()
	camera_up = up / up.norm()
	camera_left = torch.cross(camera_up, camera_forward)
	R = torch.stack([camera_forward, camera_left, camera_up], dim=1)
	pos_world = R @ pos_view + pos
	vec = pos_world - pos; vec = vec / vec.norm()
	return vec


class Key(IntEnum):
	# special
	left = 65295
	right = 65296
	up = 65297
	down = 65298
	shift = 65306
	ctrl = 65307
	option = 65308
	enter = 65309
	space = 32
	tab = 9
	delete = 8
	# other
	minus = 45
	plus = 61
	left_bracket = 91
	right_bracket = 93
	semicolon = 59
	quote = 39
	comma = 44
	period = 46
	slash = 47
	tilde = 96
	backslash = 92
	# alphanumeric
	a = 97
	b = 98
	c = 99
	d = 100
	e = 101
	f = 102
	g = 103
	h = 104
	i = 105
	j = 106
	k = 107
	l = 108
	m = 109
	n = 110
	o = 111
	p = 112
	q = 113
	r = 114
	s = 115
	t = 116
	u = 117
	v = 118
	w = 119
	x = 120
	y = 121
	z = 122
	zero = 48
	one = 49
	two = 50
	three = 51
	four = 52
	five = 53
	six = 54
	seven = 55
	eight = 56
	nine = 57

