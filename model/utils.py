def get_dfa():
    n = int(input('#states: '))

    states = set()
    edges = []
    while True:
        line = input('src dst value (input "EOF" to break):\n')
        if line=="EOF":
            break
        line = line.split(' ')
        assert len(line)==3, 'bad input: {}'.format(' '.join(line))
        states.add(line[0])
        states.add(line[1])
        edges.append(line)
    start = input('name of start state: ')
    assert start in states
    accepts = input('list of accept states: (separated by white space)\n').split(' ')
    for acc in accepts:
        assert acc in states

    states = sorted(list(states))
    state2idx = {state:idx for idx,state in enumerate(states)}

    return n, edges, start, accepts, state2idx

def ConcatSet(st1, st2):
    tmp = set()
    for a in st1:
        for b in st2:
            tmp.add(a+b)
    return tmp