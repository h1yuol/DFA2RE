class Node:
	def __str__(self):
		raise NotImplementedError

	def Or(self, b):
		raise NotImplementedError

	def Star(self):
		raise NotImplementedError

	def Concat(self, b):
		raise NotImplementedError