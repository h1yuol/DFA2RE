from model.node import Node

class ReNodeVanilla(Node):
	def __init__(self, val):
		self.val = val

	def __str__(self):
		if self.val is None:
			return 'None'
		return self.val

	def Or(self, b):
		a = self
		if a.val is None:
			return b
		if b.val is None:
			return a
		return ReNodeVanilla('({}|{})'.format(a,b))

	def Star(self):
		if self.val is None:
			return ReNodeVanilla(None)
		return ReNodeVanilla("({})*".format(self))

	def Concat(self, b):
		a = self
		if a.val is None or b.val is None:
			return ReNodeVanilla(None)
		if a == 'ε':
			return b
		if b == 'ε':
			return a
		return ReNodeVanilla("{}{}".format(a,b))