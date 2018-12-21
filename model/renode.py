# import pdb

from model.utils import ConcatSet
from model.node import Node

class ReNode(Node):
	def __init__(self, opr, *nodes):
		self._check(opr, nodes)
		self.opr = opr
		self.nodes = list(nodes)
		if opr == '|':
			self.nodes.sort(key=lambda node: node.__str__())

	def __str__(self):
		if self.opr == '*':
			s = self.nodes[0].__str__()
			if len(s) == 1 or (s.startswith('(') and s.endswith(')')):
				return s + '*'
			return '(' + s + ')*'
		a,b = self.nodes
		if self.opr == '|':
			return "{}|{}".format(a.__str__(), b.__str__())
		elif self.opr == '+':
			return "{}{}".format(a._parenthesis_str(['|']), b._parenthesis_str(['|']))
		else:
			raise Exception

	def _parenthesis_str(self, scope):
		if isinstance(self, ReLeaf):
			return self.__str__()
		if self.opr in scope:
			return '(' + self.__str__() + ')'
		return self.__str__()

	def _check(self, opr, nodes):
		assert opr in ['|', '+', '*']
		for node in nodes:
			assert not (isinstance(node, ReLeaf) and node.val is None)
		if opr == '*':
			assert len(nodes) == 1
		else:
			assert len(nodes) == 2

	def enum(self, num=3):
		if isinstance(self, ReLeaf):
			if self.val is None:
				return set(), False
			if self.val == 'ε':
				return {''}, False
			return {self.val}, False
		if self.opr == '|':
			enumSet, infinite = set(), False
			for node in self.nodes:
				tmpSet, tmpInfinite = node.enum(num)
				enumSet |= tmpSet
				infinite |= tmpInfinite
		elif self.opr == '+':
			aSet, aInfinite = self.nodes[0].enum(num)
			if aInfinite:
				bSet, bInfinite = self.nodes[1].enum(0)
				if bInfinite:
					enumSet, infinite = ConcatSet(aSet, bSet), True
					for k in range(1, num+1):
						aSet, aInfinite = self.nodes[0].enum(num-k)
						bSet, bInfinite = self.nodes[1].enum(k)
						enumSet |= ConcatSet(aSet, bSet)
				else:
					enumSet, infinite = ConcatSet(aSet, bSet), True
			else:
				bSet, bInfinite = self.nodes[1].enum(num)
				enumSet = ConcatSet(aSet, bSet)
				infinite = bInfinite
		elif self.opr == '*':
			infinite = True
			enumSet = {''}
			ISet, __ = self.nodes[0].enum(num)
			for k in range(num):
				enumSet |= ConcatSet(enumSet, ISet)
		return enumSet, infinite

	def Or(self, b):
		a = self
		if isinstance(a, ReLeaf):
			if a.val is None:
				return b
			bSet, bInfinite = b.enum()
			if len(bSet) == 0:
				return a
			if a.val == 'ε' and '' in bSet:
				return b
			if a.val in bSet:
				return b
			return ReNode('|', a, b)
		else:
			bSet, bInfinite = b.enum(2)
			if len(bSet) == 0:
				return a
			if bInfinite:
				aSet, aInfinite = a.enum(2)
				if aInfinite:
					superASet, __ = a.enum(2+1)
					if superASet >= bSet:
						return a
					superBSet, __ = b.enum(2+1)
					if superBSet >= aSet:
						return b
					return ReNode('|', a, b)
				else:
					if bSet>=aSet:
						return b
					return ReNode('|', a, b)
			else:
				aSet, aInfinite = a.enum(2)
				if aSet>=bSet:
					return a
				return ReNode('|', a, b)

	def Star(self):
		a = self
		if isinstance(a, ReLeaf):
			if a.val is None:
				return ReLeaf(None)
			if a.val == 'ε':
				return ReLeaf('ε')
			return ReNode('*', a)
		elif a.opr == '*':
			return a.nodes[0].Star()
		elif a.opr == '|':
			a1, a2 = a.nodes
			a1Set, a1Infinite = ReNode('*', a1).enum()
			a2Set, a2Infinite = ReNode('*', a2).enum()
			if len(a2Set - a1Set) == 0:
				return a1.Star()
			if len(a1Set - a2Set) == 0:
				return a2.Star()
			a1 = a1.Star().nodes[0]
			a2 = a2.Star().nodes[0]
			return ReNode('*', ReNode('|', a1, a2))
		elif a.opr == '+':
			return ReNode('*', a)
		raise Exception

	def Concat(self, b):
		a = self
		if isinstance(a, ReLeaf):
			if a.val is None:
				return ReLeaf(None)
			if a.val == 'ε':
				return b
			bSet, bInfinite = b.enum()
			if len(bSet) == 0:
				return ReLeaf(None)
			if len(bSet) == 1 and "" in bSet:
				return a
			if not isinstance(b, ReLeaf) and b.opr == '|':
				b1, b2 = b.nodes
				return a.Concat(b1).Or(a.Concat(b2))
			return ReNode('+', a, b)
		elif a.opr=='|':
			a1, a2 = a.nodes
			return a1.Concat(b).Or(a2.Concat(b))
		elif a.opr=='+':
			a1, a2 = a.nodes
			return a1.Concat(a2.Concat(b))
		elif a.opr=='*':
			if isinstance(b, ReLeaf):
				if b.val is None:
					return ReLeaf(None)
				if b.val == 'ε':
					return a.nodes[0].Star()
				return ReNode('+', a, b)
			elif b.opr == '|':
				b1, b2 = b.nodes
				return a.Concat(b1).Or(a.Concat(b2))
			elif b.opr == '+':
				b1, b2 = b.nodes
				lst = b._getLeftMostEle()
				aSet, aInfinite = a.enum()
				for item in lst:
					iSet, iInfinite = item.enum()
					if aSet>=iSet and iSet>=aSet:
						return b1.Concat(b2)
				return ReNode('+', a, b)
				# return a.Concat(b1).Concat(b2)
			elif b.opr == '*':
				aSet, aInfinite = a.enum()
				bSet, bInfinite = b.enum()
				if aSet>=bSet and bSet>=aSet:
					return a.nodes[0].Star()
				return ReNode('+', a, b)

	def _getLeftMostEle(self):
		a = self
		if isinstance(a, ReLeaf):
			return [a]
		if a.opr=='|':
			return a.nodes[0]._getLeftMostEle() + a.nodes[1]._getLeftMostEle()
		if a.opr=='*':
			return [a]
		if a.opr == '+':
			return a.nodes[0]._getLeftMostEle()
		raise Exception

class ReLeaf(ReNode):
	def __init__(self, val):
		self.val = val

	def __str__(self):
		if self.val is None:
			return "None"
		return self.val