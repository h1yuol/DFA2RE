import pickle
import pdb
from IPython import embed

def cartesian(st, currStr, currSet, k):
	if k == 0:
		currSet.add(currStr)
		return 
	for item in st:
		cartesian(st, currStr+item, currSet, k-1)

class ReNode:
	def __init__(self, opr, *nodes):
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
		# if isinstance(self, ReLeaf):
		# 	return self.val
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
				tmpInfinite |= tmpInfinite
		elif self.opr == '+':
			enumSet, infinite = self.nodes[0].enum(num)
			for node in self.nodes[1:]:
				tmpSet, tmpInfinite = node.enum(num)
				if len(tmpSet) == 0:
					return set(), False
				tmpSet2 = set()
				for a in enumSet:
					for b in tmpSet:
						c = a+b
						tmpSet2.add(c)
				enumSet = tmpSet2
				infinite |= tmpInfinite
		elif self.opr == '*':
			enumSet, infinite = self.nodes[0].enum(num)
			infinite = True
			enumSet.add("")
			tmp = set()
			cartesian(enumSet, "", tmp, num)
			enumSet = tmp

			# lst = list(enumSet)
			# for i in range(2, num+1):
			# 	for a in list(enumSet):
			# 		for b in lst:
			# 			enumSet.add(a+b)
			# 			enumSet.add(b+a)

			# for a in list(enumSet):
			# 	for i in range(2, num+1):
			# 		enumSet.add(a*i)
		return enumSet, infinite

	def eq(self, b):
		if isinstance(self, ReLeaf) and isinstance(b, ReLeaf):
			return self.__str__() == b.__str__()
		if isinstance(self, ReLeaf) or isinstance(b, ReLeaf):
			return False
		if self.opr != b.opr:
			return False
		return self.__str__() == b.__str__()

	def Or(self, *nodes):
		lst = []
		nodes = [self] + list(nodes)
		idx = 0
		strSet = set()
		while idx < len(nodes):
			node = nodes[idx]
			if isinstance(node, ReLeaf) and node.val is None:
				idx += 1
				continue
			if not isinstance(node, ReLeaf) and node.opr == '|':
				nodes.extend(node.nodes)
			else:
				s = node.__str__()
				if s not in strSet:
					strSet.add(s)
					lst.append(node)
			idx += 1

		# strSet = set()
		# for node in lst:
		# 	if not isinstance(node, ReLeaf) and node.opr == '*':
		# 		strSet.add(node.nodes[0].__str__())
		# lst2 = []
		# for node in lst:
		# 	if node.__str__() in strSet:
		# 		continue
		# 	lst2.append(node)

		# if len(lst2) == 0:
		# 	return ReLeaf(None)
		# elif len(lst2) == 1:
		# 	return lst2[0]
		# else:
		# 	return ReNode('|', *lst2)

		if len(lst) == 0:
			return ReLeaf(None)
		elif len(lst) == 1:
			return lst[0]

		enumList = []
		for idx, node in enumerate(lst):
			enumSet, infinite = node.enum(num=5)
			enumList.append((node, enumSet, infinite, idx))
		enumList.sort(key=lambda tup: len(tup[1]), reverse=True)
		newNodes = []
		currSet = set()
		for node, enumSet, infinite, idx in enumList:
			# if infinite:
			# 	newNodes.append(node)
			# 	currSet |= enumSet
			if len(enumSet - currSet) > 0:
				currSet |= enumSet
				newNodes.append(node)
		assert len(newNodes)>0
		if len(newNodes) == 1:
			return newNodes[0]
		return ReNode('|', *newNodes)

	def Star(self):
		if isinstance(self, ReLeaf):
			if self.val is None:
				return ReLeaf(None)
			if self.val == 'ε':
				return self
			return ReNode('*', self)
		if self.opr == '*':
			return self
		if self.opr == '|':
			lst = list(filter(lambda node: not(isinstance(node, ReLeaf) and node.__str__() == 'ε'), self.nodes))
			assert len(lst)>0
			if len(lst) == 1:
				return ReNode('*', lst[0])
			return ReNode('*', ReNode('|', *lst))
		if self.opr == '+':
			return ReNode('*', self)
		raise Exception



	def Concat2(self, b):
		a = self
		lst = []
		for node in [a, b]:
			if isinstance(node, ReLeaf) and node.val is None:
				return ReLeaf(None)
		if isinstance(a, ReLeaf) and a.val == 'ε':
			return b
		elif isinstance(b, ReLeaf) and b.val == 'ε':
			return a
		aSet, aInfinite = a.enum()
		bSet, bInfinite = b.enum()
		if aInfinite:
			if a.__str__() == b.__str__():
				return a
			if bInfinite:
				# pdb.set_trace()
				# abSet, abInfinite = ReNode('+', a, b).enum()
				# aLen = max(map(len, aSet))
				# bLen = max(map(len, bSet))
				# aSet, aInfinite = a.enum(3+bLen)
				# bSet, bInfinite = b.enum(3+aLen)
				# if len(abSet - aSet) == 0:
				# 	return a
				# elif len(abSet - bSet) == 0:
				# 	return b
				return ReNode('+', a, b)
			abSet, abInfinite = ReNode('+', a, b).enum()
			bLen = max(map(len, bSet))
			aSet, aInfinite = a.enum(3+bLen)
			if len(abSet - aSet) == 0 and len(aSet - abSet)==0:
				return a
			return ReNode('+', a, b)
		else:
			if bInfinite:
				abSet, abInfinite = ReNode('+', a, b).enum()
				aLen = max(map(len, aSet))
				bSet, bInfinite = b.enum(3+aLen)
				if len(abSet - bSet) == 0:
					return b
				return ReNode('+', a, b)
			if len(aSet - bSet)==0:
				return a
			return ReNode('+', a, b)

	# def Concat(self, *nodes):
	# 	lst = []
	# 	for node in ([self] + list(nodes)):
	# 		if isinstance(node, ReLeaf):
	# 			if node.val is None:
	# 				return ReLeaf(None)
	# 			if node.val == 'ε':
	# 				continue
	# 		lst.append(node)
	# 	if len(lst) == 0:
	# 		return ReLeaf('ε')
	# 	if len(lst) == 1:
	# 		return lst[0]
	# 	for i in range(len(lst)-1):
	# 		lst[i+1] = ReNode('+', lst[i], lst[i+1])
	# 	return lst[len(lst)-1]



	# def Concat(self, *nodes):
		# lst = []
		# starList = []
		# for node in ([self] + list(nodes)):
		# 	if isinstance(node, ReLeaf):
		# 		if node.val is None:
		# 			return ReLeaf(None)
		# 		if node.val == 'ε':
		# 			continue
		# 	if not isinstance(node, ReLeaf) and node.opr == '*':
		# 		starList.append(node)
		# 	lst.append(node)
		# if len(lst) == 0:
		# 	return ReLeaf('ε')
		# if len(lst) == 1:
		# 	return lst[0]




	# 	enumList = []
	# 	for idx, node in enumerate(lst):
	# 		enumSet, infinite = node.enum()
	# 		enumList.append((node, enumSet, infinite, idx))
	# 	enumList.sort(key=lambda tup: len(tup[1]), reverse=True)
	# 	newNodes = []
	# 	currSet = set()
	# 	for node, enumSet, infinite, idx in enumList:
	# 		if infinite:
	# 			newNodes.append((idx, node))
	# 			currSet |= enumSet
	# 		elif len(enumSet - currSet) > 0:
	# 			currSet |= enumSet
	# 			newNodes.append((idx, node))
	# 	newNodes.sort(key=lambda tup: tup[0])
	# 	newNodes = list(map(lambda tup: tup[1], newNodes))
	# 	assert len(newNodes)>0
	# 	if len(newNodes) == 1:
	# 		return newNodes[0]
	# 	return ReNode('+', *newNodes)

class ReLeaf(ReNode):
	def __init__(self, val):
		self.val = val

	def __str__(self):
		if self.val is None:
			return "None"
		return self.val

def dfa2re(graph):
	n = len(graph)
	for k in range(n):
		for i in range(n):
			for j in range(n):
				graph[i][j] = graph[i][j].Or(graph[i][k].Concat2(graph[k][k].Star()).Concat2(graph[k][j]))
				# graph[i][j] = graph[i][j].Or(graph[i][k].Concat(graph[k][k].Star(), graph[k][j]))
	return graph

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
	# a = ReLeaf(None)
	# # pdb.set_trace()
	# a = a.Or(ReLeaf('0'))
	# a = a.Or(ReLeaf('1'))
	# a = a.Star()
	# a = a.Concat(ReLeaf('0'))

	# b = ReLeaf('ε')
	# b = b.Or(ReLeaf('1'))
	# print(b)
	# b = b.Star()

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
				if k==2:
					pdb.set_trace()
				a = graph[i][k].Concat2(graph[k][k].Star())
				print("graph[{}][{}] + graph[{}][{}]* = {} + {} = {}".format(i,k,k,k,graph[i][k],graph[k][k].Star(),a))
				b = a.Concat2(graph[k][j])
				print("a + graph[{}][{}] = {} + {} = {}".format(k,j,a,graph[k][j],b))
				c = graph[i][j].Or(b)
				print("graph[{}][{}] | b = {} | {} = {}".format(i,j,graph[i][j],b,c))
				graph[i][j] = c
				print('-'*10)
		print('='*20)

	# embed()
	# graph = dfa2re(graph)
	for i in range(len(graph)):
		for j in range(len(graph)):
			print(graph[i][j], end=' ')
		print('')

	# a = ReLeaf('ε')
	# b = a.Or(ReLeaf('0'))
	# # pdb.set_trace()
	# c = b.Or(ReLeaf('1'))

	# a = ReLeaf('1')
	# print("a={}".format(a))
	# b = a.Or(ReLeaf('ε'))
	# print("b={}".format(b))
	# c = a.Star()
	# print("c={}".format(c))
	# d = c.Concat2(b)
	# print("1* + (1|ε) = {}".format(d))
	# # pdb.set_trace()
	# e = b.Concat2(c)
	# print("(1|ε) + 1* = {}".format(e))

	embed()