from pprint import pprint
from IPython import embed

def re_or(a, b):
	if a is None:
		if b is None:
			return None
		return b
	if b is None:
		return a
	return '({}|{})'.format(a,b)

def re_star(a):
	if a is None:
		return None
	return "({})*".format(a)

def re_concat(*items):
	result = ''
	for item in items:
		if item is None:
			return None
		result += item
	return result

def dfa2re(graph):
	n = len(graph)
	for k in range(n):
		for i in range(n):
			for j in range(n):
				graph[i][j] = re_or(graph[i][j], re_concat(graph[i][k], re_star(graph[k][k]), graph[k][j]))
	return graph

def build_graph():
	n = int(input('#states: '))
	graph = {}
	for i in range(n):
		graph[i] = {}
		for j in range(n):
			if i==j:
				graph[i][j] = 'ε'
			else:
				graph[i][j] = None

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
		graph[i][j] = re_or(graph[i][j], line[2])

	return graph, start, accepts, state2idx

if __name__ == '__main__':
	graph = build_graph()
	graph, start, accepts, state2idx = dfa2re(graph)
	i = state2idx[start]
	j = state2idx[accepts[0]]
	pprint(graph[i][j])
	embed()
