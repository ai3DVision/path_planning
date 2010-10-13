#!/usr/bin/env python

import re
import Queue

class Graph(object):
    def __init__(self, data=None):
        if data is None:
            self.G = {}
        else:
            print 'Not implemented yet'
    def __str__(self):
        return str(self.G)
    
    def __iter__(self):
        return iter(self.G.keys())    

    def add_node(self, node):
        if self.G.has_key(node) is False:
            self.G[node] = []

    def add_edge(self, node_tail, node_head):
        if self.G.has_key(node_tail):
            self.G[node_tail].append(node_head)
        else:
            self.G[node_tail] = [node_head]

    def get_nodes(self):
        return self.G.keys()

    def get_n_nodes(self):
        return len(self.G.keys())

    def successors(self, node):
        return self.G[node]

        
class Actions(object):
    d = {(-1,0):'Up', (1,0):'Down', (0,-1):'Left', (0,1):'Right'}
    def __init__(self, up=False, down=False, left = False, right = False):
        actions = []
        if up:
            actions.append((-1,0))
        if down:
            actions.append((1,0))
        if left:
            actions.append((0,-1))
        if right:
            actions.append((0,1))
        self.actions = tuple(actions)

    def __str__(self):
        return '( ' + ', '.join([Actions.d[a] for a in self.actions]) + ' )'

    def __iter__(self):
        return iter(self.actions)

class Labyrinth(object):
    def __init__(self, lab):
        if isinstance(lab, tuple):
            self.m = lab[0]
            self.n = lab[1]
            self.cells = [self.n * [0] for x in range(self.m)]
        elif isinstance(lab, str):
            rows = lab.split()
            if len(set([len(r) for r in rows])) != 1:
                raise Exception, 'all the rows must have the same length'
            self.m = len(rows)
            self.n = len(rows[0])
            cells = [self.n * [0] for x in range(self.m)]
            for i,row in enumerate(rows):
                js = [m.start() for m in re.finditer(re.escape('.'), row)]
                for j in js:
                    cells[i][j] = 1
            self.cells = cells
        else:
            raise Exception, 'lab must be a tuple or string'

        self.get_action_space()
        self.G = self.get_graph()
        
    def __str__(self):
        lines = []
        for row in self.cells:
            lines.append(''.join([('x','.')[r] for r in row]))
        return '\n'.join(lines)

    def get_action_space(self):
        actions = [self.n * [None] for x in range(self.m)]
        m = self.m
        n = self.n
        # First check the interior
        for i in range(1,m-1):
            for j in range(1,n-1):
                actions[i][j] = Actions(up = self.cells[i-1][j] == 1,
                                        down = self.cells[i+1][j] == 1,
                                        left = self.cells[i][j-1] == 1,
                                        right = self.cells[i][j+1] == 1)
        # First column
        j = 0
        for i in range(1,m-1):
            actions[i][j] = Actions(up = self.cells[i-1][j] == 1,
                                    down = self.cells[i+1][j] == 1,
                                    right = self.cells[i][j+1] == 1)
        # Last column
        j = self.n - 1
        for i in range(1,m-1):
            actions[i][j] = Actions(up = self.cells[i-1][j] == 1,
                                    down = self.cells[i+1][j] == 1,
                                    left = self.cells[i][j-1] == 1)
        # First row
        i = 0
        for j in range(1,n-1):
            actions[i][j] = Actions(down = self.cells[i+1][j] == 1,
                                    left = self.cells[i][j-1] == 1,
                                    right = self.cells[i][j+1] == 1)
        # Last row
        i = m - 1
        for j in range(1,n-1):
            actions[i][j] = Actions(up = self.cells[i-1][j] == 1,
                                    left = self.cells[i][j-1] == 1,
                                    right = self.cells[i][j+1] == 1)
        # The four corners
        actions[0][0] = Actions(down = self.cells[1][0] == 1,
                                right = self.cells[0][1] == 1)
        actions[m-1][0] = Actions(up = self.cells[m-2][0] == 1,
                                  right = self.cells[m-1][1] == 1)
        actions[0][n-1] = Actions(down = self.cells[1][n-1] == 1,
                                        left = self.cells[0][n-2] == 1)
        actions[m-1][n-1] = Actions(up = self.cells[m-2][n-2] == 1,
                                    left = self.cells[m-1][n-2] == 1)
        self.actions = actions

    def get_graph(self):
        G = Graph()
        for i in range(self.m):
            for j in range(self.n):
                if self.cells[i][j] == 1:
                    G.add_node((i,j))
                    actions = self.actions[i][j]
                    for action in actions:
                        i_e = i + action[0]
                        j_e = j + action[1]
                        G.add_edge((i,j),(i_e,j_e))
                    
        return G

def forward_search(G, x_I, x_G):
    unvisited = 'unvisited' #0
    dead = 'dead' #1
    alive = 'alive' #2
    print 'Initial state:', x_I, 'Goal:', x_G
    states = dict(zip(G.get_nodes(),[unvisited]*G.get_n_nodes()))
    q = Queue.Queue()
    q.put(x_I)
    states[x_I] = alive
    plan = []
    while q.not_empty:
        x = q.get()
        if x == x_G:
            print 'success!'
            return plan
        for node in G.successors(x):
            #plan[x] = node
            #plan[node] = x
            plan.append((x,node))
            if states[node] == unvisited:
                states[node] = alive
                q.put(node)
            else:
                pass # resolve duplicate ?
    print 'Failure :('
    return None
    
if __name__ == '__main__':
    print 'Testing path planning algorithms...'
    lab = '''\
xxxxxx
x..xxx
xx...x
xxx.xx
x...xx
xxxxxx'''
    l = Labyrinth(lab)
    #print l
    #print l.actions[4][2]
    #print l.G
    #forward_search(l.G, (1,1), (1,1))
    x_I = (1,1)
    x_G = (4,3)
    plan = forward_search(l.G, x_I, x_G)
    a = [x_G]
    #prev_node = x_G
    ## while a[-1] != x_I:
    ##     a.append(plan[a[-1]])
    ##     print a
    ##     break
    ##     #prev_node = a[-1]
    #print a
