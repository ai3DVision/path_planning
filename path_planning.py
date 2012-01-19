#!/usr/bin/env python

"""
Some path planning algorithms.

This file contains the implementation of some of the path planning algorithms
discused in the book "Planning algorithms", by Steven LaValle.

They have a didactic purpose. No effort is made in terms of efficency or
robustnes.

Alejandro Weinstein 2010
"""

import re
import Queue

class Graph(object):
    """
    Class for basic directed graphs.

    For a much more sophisticated implementation, look at networkx. 
    """
    def __init__(self):
        """Initialize an empty graph."""
        self.G = {}
        
    def __str__(self):
        """Return the dictionary representation of the graph."""
        return str(self.G)
    
    def __iter__(self):
        """Iterate over the vertices."""
        return iter(self.G.keys())    

    def add_node(self, node):
        """Add a vertice to the graph.

        Parameters
        ----------
        node: any inmutable object that can be used as a dictionary key
        """
        if self.G.has_key(node) is False:
            self.G[node] = []

    def add_edge(self, node_tail, node_head):
        """Add a directed edge between two vertices.

        Parameters
        ---------
        node_tail: vertice corresponding to the tail of the edge
        node_head: vertice corresponding to the head of the edge
        """
        if self.G.has_key(node_tail):
            self.G[node_tail].append(node_head)
        else:
            self.G[node_tail] = [node_head]

    def get_nodes(self):
        """Return a list with all the vertices."""
        return self.G.keys()

    def get_n_nodes(self):
        """Return the number of vertices."""
        return len(self.G.keys())

    def successors(self, node):
        """Return a list with all the successors of a vertice."""
        return self.G[node]

        
class Actions(object):
    """Class for the actions that can be taken from a given cell of a
    labyrinth."""
    d = {(-1,0):'Up', (1,0):'Down', (0,-1):'Left', (0,1):'Right'}
    def __init__(self, up=False, down=False, left = False, right = False):
        """Initialize the action with the set of possible actions.

        Parameters
        ----------
        up: A True value indicate that it is possible to move up
        down: A True value indicate that it is possible to move down
        left: A True value indicate that it is possible to move left
        right: A True value indicate that it is possible to move right
        """
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
        """String representation of the possible actions."""
        return '( ' + ', '.join([Actions.d[a] for a in self.actions]) + ' )'

    def __iter__(self):
        """Return an iterator with the list of actions."""
        return iter(self.actions)

class Labyrinth(object):
    """Class for implementing a Labyrinth."""
    def __init__(self, lab):
        """Initialize the class.

        Parameters
        ----------

        lab: Data to initialize the Labyrinth. If lab is a tuple with two
        elements, it indicates the dimensions (number of rows, number of
        columns) of a Labyrinth made of obstacles. If lab is a string, it
        represent the Labyrinth, where an 'X' corresponds to an obstacle, and a
        '.' corresponds to a free cell.

        Example
        -------
        lab = '''\
        xxxxxx
        x..xxx
        xx...x
        xxx.xx
        x...xx
        xxxxxx'''
        l = Labyrinth(lab)
        """
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
        """String representation of the Laberinth."""
        lines = []
        for row in self.cells:
            lines.append(''.join([('x','.')[r] for r in row]))
        return '\n'.join(lines)

    def get_action_space(self):
        """Return a 2-dimensional list with the actions for each cell."""
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
        """Return the graph representation of the Labyrinth."""
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
    """ Compute a path between two nodes of a graph.

    The search is implimented as a forward search, based on the algorithm
    of Figure 2.4 (p. 28) of LaValle's book.

    Parameters
    ----------
    G: Graph to search
    x_I: Initial vertice in the Graph
    x_G: Goal vertice

    Returns
    -------
    If a path is found, a list with the plan for going from x_I to x_G.
    If a path is not found, None
    """
    unvisited = 'unvisited' #0
    dead = 'dead' #1
    alive = 'alive' #2
    print 'Initial state:', x_I, 'Goal:', x_G
    states = dict(zip(G.get_nodes(),[unvisited]*G.get_n_nodes()))
    q = Queue.Queue()
    q.put(x_I)
    states[x_I] = alive
    orig = []
    dest = []
    while q.not_empty:
        x = q.get()
        if x == x_G:
            print 'success!'
            return plan_to_path((orig, dest))
        for node in G.successors(x):
            orig.append(x)
            dest.append(node)
            if states[node] == unvisited:
                states[node] = alive
                q.put(node)
            else:
                pass # resolve duplicate ?
                #print 'We have a duplicate. What do we do?'
    print 'Failure :('
    return None

def plan_to_path(plan):
    """Convert the pair of origin->destinations computed by the forward search
    into a path.

    Parameters
    ----------
    plan: A tuple with two lists. The fisrt list contains the origins, and the
    second one the destinations.

    Return
    ------
    A list with the path from the origin to the goal
    """
    (o, d) = plan
    i = d.index(x_G)
    path = [x_G]
    while True:
        prev_node = o[i]
        if prev_node == x_I:
            break
        path.append(prev_node)
        i = d.index(prev_node)
        while o.count(prev_node) > 0:
            j = o.index(prev_node)
            del(o[j])
            del(d[j])
    path.append(x_I)
    path.reverse()
    return path
    
    
if __name__ == '__main__':
    print 'Testing path planning algorithms...'
    lab = ('xxxxxx\n'
           'x..xxx\n'
           'xx...x\n'
           'xxx.xx\n'
           'x...xx\n'
           'xxxxxx\n')

    l = Labyrinth(lab)
    x_I = (1,1)
    x_G = (4,3)
    plan = forward_search(l.G, x_I, x_G)
    print plan

