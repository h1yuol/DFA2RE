import pickle
import pdb
from IPython import embed

def ConcatSet(st1, st2):
	tmp = set()
	for a in st1:
		for b in st2:
			tmp.add(a+b)
	return tmp

class ReNode:
	def __init__(self, opr, *nodes):
		assert len(nodes) <= 2
		lst = []
		for node in nodes:
			assert not (isinstance(node, ReLeaf) and node.val is None)
		self.opr = opr
		if opr == '*':
			assert len(nodes) == 1
		else:
			assert len(nodes) > 1
		if opr == '|':
			self.nodes = sorted(nodes, key=lambda node: node.__str__())
		else:
			self.nodes = nodes

	def __str__(self):
		if self.opr == '|':
			return '(' + '|'.join([node.__str__() for node in self.nodes]) + ')'
		if self.opr == '*':
			assert len(self.nodes) == 1
			s = self.nodes[0].__str__()
			if len(s) == 1 or (s.startswith('(') and s.endswith(')')):
				return s + '*'
			return '(' + s + ')*'
		if self.opr == '+':
			return ''.join([node.__str__() for node in self.nodes])
		raise Exception

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
			# pdb.set_trace()
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
			# return a1.Star().Or(a2.Star())
		elif a.opr == '+':
			return ReNode('*', a)
		raise Exception

	def getLeftMostEle(self):
		a = self
		if isinstance(a, ReLeaf):
			return [a]
		if a.opr=='|':
			return a.nodes[0].getLeftMostEle() + a.nodes[1].getLeftMostEle()
		if a.opr=='*':
			return [a]
		if a.opr == '+':
			return a.nodes[0].getLeftMostEle()
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
				lst = b.getLeftMostEle()
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


			



			# if isinstance(b, ReLeaf):
			# 	return b.Concat(a, reverse=True)
			# aSet, aInfinite = a.enum()
			# bSet, bInfinite = b.enum()
			# abSet = ConcatSet(aSet, bSet)
			# aLen = max(map(len, aSet))
			# bLen = max(map(len, bSet))
			# aSet, aInfinite = a.enum(3+bLen)
			# bSet, bInfinite = b.enum(3+aLen)
			# if len(abSet - bSet) == 0 and len(bSet - abSet) == 0:
			# 	return b
			# if len(abSet - aSet) == 0 and len(aSet - abSet) == 0:
			# 	return a
			# return ReNode('+', a, b)

class ReLeaf(ReNode):
	def __init__(self, val):
		self.val = val

	def __str__(self):
		if self.val is None:
			return "None"
		return self.val


def build_graph():
	n = int(input('#states: '))
	graph = {}
	for i in range(n):
		graph[i] = {}
		for j in range(n):
			if i==j:
				graph[i][j] = ReLeaf('ε')
			else:
				graph[i][j] = ReLeaf(None)

	states = set()
	lines = []
	while True:
		line = input('src dst value (end up with "EOF"):\n')
		if line=="EOF":
			break
		line = line.split(' ')
		assert len(line)==3, 'bad input: {}'.format(' '.join(line))
		states.add(line[0])
		states.add(line[1])
		lines.append(line)
	start = input('name of start state: ')
	assert start in states
	accepts = input('list of accept states: ').split(' ')
	for acc in accepts:
		assert acc in states

	states = sorted(list(states))
	state2idx = {state:idx for idx,state in enumerate(states)}
	for line in lines:
		i = state2idx[line[0]]
		j = state2idx[line[1]]
		graph[i][j] = graph[i][j].Or(ReLeaf(line[2]))

	return graph, start, accepts, state2idx

from utils import InteractiveIf

@InteractiveIf('New State Machine?')
def InputStateMachine():
	graph, start, accepts, state2idx = build_graph()
	with open('cache.pkl', 'wb') as hd:
		pickle.dump((graph, start, accepts, state2idx), hd)

if __name__ == '__main__':
	InputStateMachine()
	graph, start, accepts, state2idx = pickle.load(open('cache.pkl', 'rb'))
	for i in range(len(graph)):
		for j in range(len(graph)):
			print(graph[i][j], end=' ')
		print('')

	for k in range(len(graph)):
		for i in range(len(graph)):
			for j in range(len(graph)):
				print("k={}, i={}, j={}".format(k,i,j))
				a = graph[i][k].Concat(graph[k][k].Star())
				print("graph[{}][{}] + graph[{}][{}]* = {} + {} = {}".format(i,k,k,k,graph[i][k],graph[k][k].Star(),a))
				b = a.Concat(graph[k][j])
				print("a + graph[{}][{}] = {} + {} = {}".format(k,j,a,graph[k][j],b))
				# if k==2 and i==0 and j==2:
				# 	pdb.set_trace()
				c = graph[i][j].Or(b)
				print("graph[{}][{}] | b = {} | {} = {}".format(i,j,graph[i][j],b,c))
				graph[i][j] = c
				print('-'*10)
		print('='*20)

	for i in range(len(graph)):
		for j in range(len(graph)):
			print(graph[i][j], end=' ')
		print('')

	print('+'*20)
	node = graph[state2idx[start]][state2idx[accepts[0]]]
	for acc in accepts[1:]:
		node = node.Or(graph[state2idx[start]][state2idx[acc]])
	print(node)	

	embed()